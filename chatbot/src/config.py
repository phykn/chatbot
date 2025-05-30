from transformers import AutoTokenizer
from .misc import load_yaml, build_system_message

cfg_llm = load_yaml("src/config/llm.yaml")

cfg_mcp = load_yaml("src/config/mcp.yaml")

tokenizer = AutoTokenizer.from_pretrained(cfg_llm["tokenizer"])

system_prompt_think = build_system_message(
    do_think = True,
    extension_names = cfg_llm.get("extensions", [])
)

system_prompt_no_think = build_system_message(
    do_think = False,
    extension_names = cfg_llm.get("extensions", [])
)

CSS_AVATAR = """
.gradio-container {
    width: 100% !important;
    max-width: 950px !important;
    margin: 0 auto;
}
.avatar-container {
    width: 60px !important;
    height: 60px !important;
    min-width: 60px !important;
    min-height: 60px !important;
    display: flex;
    align-items: center;
    justify-content: center;
}
.avatar-container img {
    width: 60px !important;
    height: 60px !important;
    border-radius: 100% !important;
    object-fit: cover !important;
}
footer {visibility: hidden}
"""