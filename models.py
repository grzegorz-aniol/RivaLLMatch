import os

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI


def get_model_name(model):
    if hasattr(model, 'model'):
        return getattr(model, 'model')
    return model.model_name


def get_open_ai_llm(model='gpt-4o', temperature=1.0):
    llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=os.getenv('OPENAI_API_KEY'))
    return llm


def get_claude_llm(model='claude-3-opus-20240229', temperature=1.0):
    llm = ChatAnthropic(model=model, temperature=temperature)
    return llm


def get_gemini_llm(model='gemini-pro', temperature=1.0):
    llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
    return llm


def get_llama3(model='llama3-8b-8192', temperature=1.0):
    llm = ChatGroq(model=model, temperature=temperature)
    return llm


def get_mixtral(model='mixtral-8x7b-32768', temperature=1.0):
    if 'mixtral-8x7b-32768' in model:
        llm = ChatGroq(model=model, temperature=temperature)
    else:
        llm = ChatMistralAI(model=model, temperature=temperature)
    return llm


def build_model(model_name, temperature=1.0):
    if 'gpt' in model_name:
        llm = get_open_ai_llm(model_name, temperature)
    elif 'claude' in model_name:
        llm = get_claude_llm(model_name, temperature)
    elif 'gemini' in model_name:
        llm = get_gemini_llm(model_name, temperature)
    elif 'llama' in model_name:
        llm = get_llama3(model_name, temperature)
    elif 'mixtral' in model_name:
        llm = get_mixtral(model_name, temperature)
    elif 'gemma' in model_name:
        llm = ChatGroq(modle=model_name, temperature=temperature)
    else:
        raise Exception(f'Cannot build model "{model_name}"')
    actual_model_name = get_model_name(llm)
    if actual_model_name != model_name:
        print(f'WARN: model {model_name} resolved to model {actual_model_name}')
    return llm
