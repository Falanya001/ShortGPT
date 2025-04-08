import os
import subprocess
from pathlib import Path
import ast
import astor

# -----------------------------------------------------------
# [0] Force install the required Gradio versions at runtime.
# -----------------------------------------------------------
print("[INFO] Forcing installation of gradio==5.12.0 and gradio_client==1.5.4...")
os.system("pip install --upgrade --force-reinstall gradio==5.12.0 gradio_client==1.5.4")

# Patch gradio_client's get_type function to handle booleans
import gradio_client.utils as client_utils

_original_get_type = client_utils.get_type

def patched_get_type(schema):
    # If the schema itself is a boolean, return a string "bool"
    if isinstance(schema, bool):
        return "bool"
    # Otherwise, proceed as usual
    return _original_get_type(schema)

client_utils.get_type = patched_get_type
print("[INFO] Patched gradio_client.utils.get_type to handle booleans.")

# -----------------------------------------------------------
# [1] Clone the ShortGPT repository
# -----------------------------------------------------------
REPO_URL = "https://github.com/Falanya001/ShortGPT.git"
CLONE_DIR = "/tmp/shortgpt"

def clone_repo():
    if not Path(CLONE_DIR).exists():
        print("[INFO] Cloning ShortGPT repository...")
        subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)
    else:
        print("[INFO] Repository already cloned. Skipping...")

# -----------------------------------------------------------
# [2] Patch all lambda functions to use (*args, **kwargs)
# -----------------------------------------------------------
def patch_all_lambdas_to_use_args():
    print("[INFO] Patching all lambda functions to use (*args, **kwargs)...")
    patched_files = []

    for root, _, files in os.walk(CLONE_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            modified = False

            class LambdaTransformer(ast.NodeTransformer):
                def visit_Lambda(self, node):
                    # Only patch if not already accepting varargs or kwargs
                    if not node.args.vararg and not node.args.kwarg:
                        node.args.args = []
                        node.args.vararg = ast.arg(arg='args', annotation=None)
                        node.args.kwarg = ast.arg(arg='kwargs', annotation=None)
                        nonlocal modified
                        modified = True
                    return self.generic_visit(node)

            LambdaTransformer().visit(tree)

            if modified:
                new_source = astor.to_source(tree)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_source)
                patched_files.append(path)

    if patched_files:
        print(f"[INFO] Patched {len(patched_files)} files with lambda(*args, **kwargs):")
        for p in patched_files:
            print(f" - {p}")
    else:
        print("[INFO] No lambda patches were needed.")

# -----------------------------------------------------------
# [3] Patch method handlers to adapt expected arguments
# -----------------------------------------------------------
def patch_method_handlers():
    print("[INFO] Patching method handlers to match expected Gradio args...")
    patched_files = []

    for py_file in Path(CLONE_DIR).rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception:
            continue

        modified = False

        class FnHandlerTransformer(ast.NodeTransformer):
            def visit_Call(self, node):
                self.generic_visit(node)
                # Look for calls to Gradio event binding methods
                if isinstance(node.func, ast.Attribute) and node.func.attr in ["select", "click", "change", "submit"]:
                    for kw in node.keywords:
                        if kw.arg == "fn":
                            # Skip lambdas; we already patched them
                            if isinstance(kw.value, ast.Lambda):
                                continue
                            # Wrap with adapt_args if not already wrapped
                            if isinstance(kw.value, ast.Call) and getattr(kw.value.func, 'id', '') == "adapt_args":
                                continue
                            # Wrap function with adapt_args(fn, expected_args=3)
                            kw.value = ast.Call(
                                func=ast.Name(id="adapt_args", ctx=ast.Load()),
                                args=[kw.value, ast.Constant(value=3)],
                                keywords=[]
                            )
                            nonlocal modified
                            modified = True
                return node

        transformer = FnHandlerTransformer()
        transformer.visit(tree)

        # Prepare the adapt_args function code to prepend if needed.
        adapt_args_code = """
def adapt_args(fn, expected_args=3):
    def wrapped(*args, **kwargs):
        if len(args) < expected_args:
            args = args + (None,) * (expected_args - len(args))
        return fn(*args, **kwargs)
    return wrapped
"""
        if modified:
            new_source = astor.to_source(tree)
            if "def adapt_args" not in source:
                new_source = adapt_args_code + "\n" + new_source
            with open(py_file, "w", encoding="utf-8") as f:
                f.write(new_source)
            patched_files.append(str(py_file))

    if patched_files:
        print(f"[INFO] Patched method handlers in {len(patched_files)} files:")
        for f in patched_files:
            print(f" - {f}")
    else:
        print("[INFO] No method handler patches were needed.")

# -----------------------------------------------------------
# [4] Patch gr.Chatbot to normalize chat history
# -----------------------------------------------------------
from gradio.components.chatbot import Chatbot
from gradio.exceptions import Error

def normalize_chat_history(chat_history):
    normalized = []
    for msg in chat_history:
        # Handle tuple format: (role, content)
        if isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            role = role.lower() if role else "user"
            normalized.append({"role": role, "content": content})
        # Handle list format: [role, content]
        elif isinstance(msg, list) and len(msg) == 2:
            role, content = msg
            role = role.lower() if role else "user"
            normalized.append({"role": role, "content": content})
        # Handle proper dict format
        elif isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            normalized.append({"role": msg['role'].lower(), "content": msg['content']})
        else:
            raise Error(f"Unexpected chat format: {msg}")
    return normalized

_original_chatbot_init = Chatbot.__init__

def patched_chatbot_init(self, *args, **kwargs):
    if kwargs.get("type") == "messages" and args:
        first = args[0]
        if callable(first):
            new_first = lambda *a, **kw: normalize_chat_history(first(*a, **kw))
            args = (new_first,) + args[1:]
            print("[INFO] Chatbot init patched to normalize message format.")
    _original_chatbot_init(self, *args, **kwargs)

Chatbot.__init__ = patched_chatbot_init

# -----------------------------------------------------------
# [5] Run ShortGPT with patched repo
# -----------------------------------------------------------
def run_shortgpt():
    import sys
    sys.path.insert(0, CLONE_DIR)
    from gui.gui_gradio import ShortGptUI

    app = ShortGptUI(colab=False)

    def custom_launch():
        ui = app.create_interface()
        ui.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,    # Hugging Face Spaces doesn't support share=True
            inbrowser=False, # Don't try to open a browser
            enable_api=True,   # Force API endpoints to be registered
            enable_queue=True  # Enable a request queue if needed
            
        )

    app.launch = custom_launch
    app.launch()

# -----------------------------------------------------------
# [MAIN]
# -----------------------------------------------------------
if __name__ == "__main__":
    clone_repo()
    patch_all_lambdas_to_use_args()
    patch_method_handlers()
    # Change working directory to the cloned repo so relative paths work correctly.
    os.chdir(CLONE_DIR)
    run_shortgpt()
