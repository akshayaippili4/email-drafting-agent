"""
Email Drafting Agent using LangChain.

A two-step LangChain workflow that analyzes the email requirement
and then drafts a professional email.

Usage:
    python agent.py
    python agent.py --context "Follow up on the Q3 proposal sent last week" --tone "professional"
"""

import argparse
import os

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

load_dotenv()

DEFAULT_MODEL = "gpt-oss:120b-cloud"
DEFAULT_BASE_URL = "http://localhost:11434"


def get_llm(
    model: str | None = None,
    base_url: str | None = None
) -> ChatOllama:
    """
    Create the Ollama LLM.

    Local:
        OLLAMA_BASE_URL=http://localhost:11434

    Render / Ollama Cloud:
        OLLAMA_BASE_URL=https://ollama.com
        OLLAMA_API_KEY=your_api_key
    """

    model_name = model or os.getenv(
        "OLLAMA_MODEL",
        DEFAULT_MODEL
    )

    ollama_url = base_url or os.getenv(
        "OLLAMA_BASE_URL",
        DEFAULT_BASE_URL
    )

    api_key = os.getenv("OLLAMA_API_KEY")

    client_kwargs = {}

    if api_key:
        client_kwargs["headers"] = {
            "Authorization": f"Bearer {api_key}"
        }

    return ChatOllama(
        model=model_name,
        base_url=ollama_url,
        temperature=0.3,
        client_kwargs=client_kwargs,
    )


def build_email_workflow(
    context: str,
    tone: str,
    recipient: str
) -> str:

    llm = get_llm()

    # Step 1: Analyze the email requirement
    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert business communication analyst "
                "who turns email requests into a clear brief.",
            ),
            (
                "human",
                """Analyze this email requirement:

Context: {context}
Recipient: {recipient}
Desired tone: {tone}

Extract:

1. Purpose
2. Key points to cover
3. Call to action
4. Suggested subject line
""",
            ),
        ]
    )

    # Step 2: Draft the email
    draft_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional copywriter specializing "
                "in concise, persuasive business emails.",
            ),
            (
                "human",
                """Using the analysis below, draft a complete professional email.

Analysis:
{analysis}

Tone: {tone}
Recipient: {recipient}

Include:

- Subject line
- Greeting
- Body paragraphs
- Closing
- Signature placeholder

Keep the email body under 200 words.
""",
            ),
        ]
    )

    analysis_chain = (
        analysis_prompt
        | llm
        | StrOutputParser()
    )

    draft_chain = (
        draft_prompt
        | llm
        | StrOutputParser()
    )

    # Analyze the request
    analysis = analysis_chain.invoke(
        {
            "context": context,
            "tone": tone,
            "recipient": recipient,
        }
    )

    # Generate the final email
    email = draft_chain.invoke(
        {
            "analysis": analysis,
            "tone": tone,
            "recipient": recipient,
        }
    )

    return email


def build_email_crew(
    context: str,
    tone: str,
    recipient: str
) -> str:
    """
    Compatibility wrapper used by app.py.
    """

    return build_email_workflow(
        context,
        tone,
        recipient
    )


def main():

    parser = argparse.ArgumentParser(
        description="Email Drafting Agent"
    )

    parser.add_argument(
        "--context",
        default=(
            "Follow up on our product demo from last Tuesday. "
            "They seemed interested but haven't responded."
        ),
        help="Email context/purpose",
    )

    parser.add_argument(
        "--tone",
        default="professional and friendly",
        help="Email tone",
    )

    parser.add_argument(
        "--recipient",
        default="a potential client",
        help="Who the email is for",
    )

    args = parser.parse_args()

    print("\n✉️ Drafting email...\n")

    email = build_email_crew(
        args.context,
        args.tone,
        args.recipient
    )

    print("=" * 60)
    print("📧 DRAFTED EMAIL")
    print("=" * 60)
    print(email)


if __name__ == "__main__":
    main()
