import gradio as gr
from src.css import CSS_AVATAR
from src.state import State, update_state
from src.event import add_user_message, add_ai_message
from src.misc import load_yaml


with gr.Blocks(title = "Chat with Tool", css = CSS_AVATAR) as demo:
    do_think = gr.State(False)
    state = gr.State(State())

    chat_history = gr.Chatbot(
        type = "messages",
        container = False,
        autoscroll = True,
        height = "80vh",
        render_markdown = True,
        allow_tags = True,
        avatar_images = ["assets/user.png", "assets/ai.png"]
    )

    with gr.Row():
        user_input = gr.Textbox(
            placeholder = "무엇이든 물어보세요",
            show_label = False,
            container = False,
            scale = 5
        )
        
        stop_btn = gr.Button(
            value = "STOP",
            icon = "assets/stop.png",
            scale = 1
        )

    with gr.Row():
        select_think = gr.Radio(
            choices=[
                ["Think", True],
                ["No Think", False]
            ],
            value = False,
            container = False,
            scale = 5
        )

        clear_btn = gr.Button(
            value = "New Chat",
            scale = 1
        )

    user_input.submit(
        fn = add_user_message,
        inputs = [chat_history, user_input],
        outputs = [chat_history, user_input]
    ).then(
        fn = add_ai_message,
        inputs = [chat_history, do_think, state],
        outputs = chat_history,
        queue = True
    )

    stop_btn.click(
        fn = update_state,
        inputs = state
    )

    select_think.change(
        fn = lambda x: x,
        inputs = select_think,
        outputs = do_think
    )

    clear_btn.click(
        fn = lambda: [],
        outputs = chat_history,
    )


if __name__ == "__main__":
    cfg = load_yaml("src/config/gradio.yaml")
    demo.launch(**cfg["launch"])