import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Type, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage

from tafin.prompts import DEFAULT_SYSTEM_PROMPT


class LLMUnavailableError(RuntimeError):
    """Raised when the OpenAI client is unavailable or rejects authentication."""


# Initialize the OpenAI client lazily so the CLI can fall back to non-LLM modes.
OPENAI_API_KEY = os.getenv("TAFIN_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
_llm: Optional[ChatOpenAI] = None


def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        if not OPENAI_API_KEY:
            raise LLMUnavailableError(
                "OpenAI API key is not configured. Set TAFIN_OPENAI_API_KEY or OPENAI_API_KEY to enable agent mode."
            )
        _llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=OPENAI_API_KEY)
    return _llm


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
) -> AIMessage:
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", final_system_prompt),
        ("user", "{prompt}")
    ])

    llm = _get_llm()
    runnable = llm
    if output_schema:
        runnable = llm.with_structured_output(output_schema)
    elif tools:
        runnable = llm.bind_tools(tools)

    chain = prompt_template | runnable
    try:
        return chain.invoke({"prompt": prompt})
    except Exception as exc:
        message = str(exc)
        if "Incorrect API key" in message or "invalid_api_key" in message or "401" in message:
            raise LLMUnavailableError("OpenAI authentication failed.") from exc
        raise
