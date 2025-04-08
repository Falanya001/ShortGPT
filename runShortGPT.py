from gui.gui_gradio import ShortGptUI

app = ShortGptUI(colab=False)
# Define the normalization helper
def normalize_chat_history(chat_history):
    normalized = []
    for msg in chat_history:
        if isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            normalized.append({"role": role.lower(), "content": content})
        else:
            normalized.append(msg)
    return normalized

# Monkey-patch the initialize_conversation method
original_initialize = app.initialize_conversation
def new_initialize_conversation(*args, **kwargs):
    history = original_initialize(*args, **kwargs)
    return normalize_chat_history(history)
app.initialize_conversation = new_initialize_conversation

# Monkey patch the .launch() method to inject your own logic
def custom_launch():
    ui = app.create_interface()  # This builds the gr.Interface
    ui.launch(
        server_name="0.0.0.0",  # So it binds to all interfaces (needed on Hugging Face)
        server_port=7860,       # Any available port on HF (can be 7860, 7861, etc.)
        share=True              # This exposes a public URL
    )

# Replace the original method with your custom one
app.launch = custom_launch

# Call it
app.launch()
