import os
import dotenv

dotenv.load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from arena import Arena
from contests.problem_solving_templates import ProblemSolvingTemplates

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


if __name__ == '__main__':
    llms = [
        # get_claude_llm(),
        get_open_ai_llm(),
        # get_gemini_llm(),
        get_llama3(),
        get_mixtral()
    ]
    arena = Arena(ProblemSolvingTemplates(), llms)
    arena.run(n_rounds=6, n_problems=3)
