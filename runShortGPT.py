from gui.gui_gradio import ShortGptUI

app = ShortGptUI(colab=False)
app.launch(server_name="0.0.0.0", server_port=7860, share=True)
