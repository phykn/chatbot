import argparse
import gradio as gr
from src.config import CSS_AVATAR
from src.event import add_user_message, add_ai_message
from src.misc import load_yaml, State, update_state


with gr.Blocks(
    title = "Chat with Tool", 
    css = CSS_AVATAR
) as demo:
    
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
                ["Faster", False],
                ["Reasoning", True]
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


def parse_args():
    parser = argparse.ArgumentParser(description="Chat with Tool")
    parser.add_argument(
        "--server_name", 
        type = str, 
        default = "localhost",
        help = "Server host name (default: localhost)"
    )
    parser.add_argument(
        "--server_port", 
        type = int, 
        default = 8001,
        help = "Server port number (default: 8001)"
    )
    parser.add_argument(
        "--share", 
        action = "store_true",
        help = "Create public link (default: False)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    demo.launch(  
        server_name = args.server_name,
        server_port = args.server_port,
        share = args.share
    )