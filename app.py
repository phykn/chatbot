import gradio as gr
from src.event import user, assistant, update_obj
from src.uuid import UUID, update_uuid
from src.misc import load_yaml


cfg = load_yaml("src/config/front.yaml")


with gr.Blocks(title = "Simple Chatbot") as demo:
    option = gr.State(cfg["option"])
    uuid = gr.State(UUID())

    with gr.Sidebar(open = True):
        model = gr.Dropdown(
            label = "Model",
            choices = cfg["model"].keys(),
            value = cfg["option"]["model"],
            interactive = True
        )

        do_think = gr.Dropdown(
            label = "Thinking",
            choices = [False, True],
            value = cfg["option"]["do_think"],
            interactive = True
        )

        max_token = gr.Dropdown(
            label = "Maximum Token Limit",
            choices = [1024, 2048, 4096, 8192],
            value = cfg["option"]["max_token"],
            interactive = True
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


    model.change(
        fn = lambda obj, value: update_obj(obj=obj, key="model", value=value),
        inputs = [option, model],
        outputs = option
    )

    do_think.change(
        fn = lambda obj, value: update_obj(obj=obj, key="model", value=value),
        inputs = [option, do_think],
        outputs = option
    )

    max_token.change(
        fn = lambda obj, value: update_obj(obj=obj, key="model", value=value),
        inputs = [option, max_token],
        outputs = option
    )

    user_input.submit(
        fn = user,
        inputs = [history, user_input],
        outputs = [history, user_input]
    ).then(
        fn = assistant,
        inputs = [history, option, uuid],
        outputs = history,
        queue = True
    )

    stop_btn.click(
        fn = update_uuid,
        inputs = [uuid]
    )

    clear_btn.click(
        fn = lambda: [],
        outputs = history,
    )


if __name__ == "__main__":
    demo.launch(**cfg["launch"])