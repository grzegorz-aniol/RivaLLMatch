import os

from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


def get_model_name(model):
    if hasattr(model, 'model'):
        return model.model
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
    llm = ChatGroq(model=model, temperature=temperature)
    return llm


def build_model(model_name, temperature=1.0):
    if 'gpt' in model_name:
        return get_open_ai_llm(model_name, temperature)
    if 'claude' in model_name:
        return get_claude_llm(model_name, temperature)
    if 'gemini' in model_name:
        return get_gemini_llm(model_name, temperature)
    if 'llama' in model_name:
        return get_llama3(model_name, temperature)
    if 'mixtral' in model_name:
        return get_mixtral(model_name, temperature)
    if 'gemma' in model_name:
        return ChatGroq(modle=model_name, temperature=temperature)
    raise Exception(f'Cannot build model "{model_name}"')
