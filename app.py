import uuid
import gradio as gr
from src.event import user, assistant
from src.config import option_init, model_table


class State:
    def __init__(self):
        self.msg_id = str(uuid.uuid4())
    
    def __hash__(self):
        return hash(self.msg_id)
    
def update_state(state):
    state.msg_id = str(uuid.uuid4())

def update_option(options: dict, key: str, value: any):
    options[key] = value
    return options


with gr.Blocks(title = "Simple Chatbot") as demo:
    option = gr.State(option_init)
    state = gr.State(State())

    with gr.Sidebar(open=False):
        model = gr.Dropdown(
            label = "Model",
            choices = list(model_table.keys()),
            value = option_init["model"],
            interactive = True
        )

        do_think = gr.Dropdown(
            label = "Thinking",
            choices = [None, False, True],
            value = option_init["do_think"],
            interactive = True
        )

        max_token = gr.Dropdown(
            label = "Maximum Token Limit",
            choices = [1024, 2048, 4096, 8192],
            value = option_init["max_token"],
            interactive = True
        )

        model.change(
            fn = lambda option, value: update_option(option, "model", value),
            inputs = [option, model],
            outputs = option
        )

        do_think.change(
            fn = lambda option, value: update_option(option, "do_think", value),
            inputs = [option, do_think],
            outputs = option
        )

        max_token.change(
            fn = lambda option, value: update_option(option, "max_token", value),
            inputs = [option, max_token],
            outputs = option
        )

    history = gr.Chatbot(
        type = "messages",
        container = False,
        autoscroll = True,
        height = "80vh",
        render_markdown = True,
        allow_tags = True
    )

    with gr.Row():
        user_input = gr.Textbox(
            placeholder = "무엇이든 물어보세요",
            show_label = False,
            container = False,
            scale = 10
        )    
        
        stop_btn = gr.Button(
            value = "STOP",
            icon = "assets/stop.png",
            scale = 1
        )

    clear_btn = gr.Button("Clear")

    user_input.submit(
        fn = user,
        inputs = [history, user_input],
        outputs = [history, user_input],
        queue = False
    ).then(
        fn = assistant,
        inputs = [history, option, state],
        outputs = history,
        queue = True
    )

    stop_btn.click(
        fn = update_state,
        inputs = [state],
        queue = False
    )

    clear_btn.click(
        fn = lambda: [], 
        inputs = None, 
        outputs = history, 
        queue = False
    )


if __name__ == "__main__":
    demo.launch(
        server_name = "localhost",
        server_port = 8081,
        share = False
    )