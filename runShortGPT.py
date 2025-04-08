from gui.gui_gradio import ShortGptUI
import gradio as gr

# Patch the postprocess method of gr.Chatbot to auto-normalize data
_original_postprocess = gr.Chatbot.postprocess

def patched_postprocess(self, value):
    # If it's a callable (function), call it
    if callable(value):
        value = value()
    # Normalize conversation messages
    normalized = []
    for msg in value:
        if isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            normalized.append({"role": role.lower(), "content": content})
        else:
            normalized.append(msg)
    return _original_postprocess(self, normalized)

gr.Chatbot.postprocess = patched_postprocess

# Create the ShortGPT app instance
app = ShortGptUI(colab=False)

# Custom launch method for Hugging Face Spaces
def custom_launch():
    ui = app.create_interface()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )

app.launch = custom_launch
app.launch()
