from gui.gui_gradio import ShortGptUI
import gradio as gr

# Monkey-patch the Gradio Chatbot constructor to normalize conversation data.
_original_chatbot_init = gr.Chatbot.__init__

def patched_chatbot_init(self, *args, **kwargs):
    # Check if the Chatbot is set to use the "messages" format.
    if kwargs.get("type") == "messages":
        # If the first positional argument is a callable (i.e. a function that returns the initial conversation)
        if args and callable(args[0]):
            original_init_func = args[0]
            # Define a wrapped function that normalizes the output.
            def wrapped_initial(*a, **kw):
                conv = original_init_func(*a, **kw)
                normalized = []
                for msg in conv:
                    if isinstance(msg, tuple) and len(msg) == 2:
                        role, content = msg
                        normalized.append({"role": role.lower(), "content": content})
                    else:
                        normalized.append(msg)
                return normalized
            # Replace the original function with the wrapped version.
            new_args = (wrapped_initial,) + args[1:]
        else:
            new_args = args
    else:
        new_args = args
    # Call the original Chatbot constructor with modified arguments.
    _original_chatbot_init(self, *new_args, **kwargs)

gr.Chatbot.__init__ = patched_chatbot_init

# Create the ShortGPT app instance.
app = ShortGptUI(colab=False)

# Monkey-patch the launch method to inject the desired Gradio parameters.
def custom_launch():
    ui = app.create_interface()  # Builds the gr.Interface
    ui.launch(
        server_name="0.0.0.0",  # Bind to all interfaces (needed on HF Spaces)
        server_port=7860,       # Use port 7860 (or another available port)
        share=True              # Get a public URL for access
    )

app.launch = custom_launch

# Launch the app.
app.launch()
