import tiktoken
from .misc import load_yaml


encoding = tiktoken.get_encoding("cl100k_base")
cfg_llm = load_yaml("src/config/llm.yaml")
cfg_mcp = load_yaml("src/config/mcp.yaml")
cfg_web = load_yaml("src/config/web.yaml")