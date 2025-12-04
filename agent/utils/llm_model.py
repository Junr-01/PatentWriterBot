from langchain.chat_models import init_chat_model

llm_temp_low = None
llm_temp_high = None


def _openai_model(model_name: str, temperature: float):
    return init_chat_model(model=model_name, model_provider="openai", temperature=temperature)


def _deepseek_model(model_name: str, temperature: float):
    return init_chat_model(model=model_name, model_provider="deepseek", temperature=temperature)


def update_llm_model(model_name):
    global llm_temp_low, llm_temp_high
    if model_name == "deepseek-chat":
        llm_temp_low = _deepseek_model(model_name, 0)
        llm_temp_high = _deepseek_model(model_name, 1)
    elif model_name == "gpt-5" or model_name == "gpt-5-mini":
        llm_temp_low = _openai_model(model_name, 0.1)
        llm_temp_high = _openai_model(model_name, 0.3)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

