"""
Email Drafting Agent using LangChain.

A two-step LangChain workflow that analyzes the email requirement and then drafts a professional email.

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


def get_llm(model: str | None = None, base_url: str | None = None) -> ChatOllama:
    model_name = model or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)
    return ChatOllama(
        model=model_name,
        base_url=base_url or os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL),
        temperature=0.3,
    )


def build_email_workflow(context: str, tone: str, recipient: str) -> str:
    llm = get_llm()

    analysis_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert business communication analyst who turns email requests into a clear brief.",
            ),
            (
                "human",
                """Analyze this email requirement:
Context: {context}
Recipient: {recipient}
Desired tone: {tone}

Extract: purpose, key points to cover, call to action, and a suggested subject line.""",
            ),
        ]
    )

    draft_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a professional copywriter specializing in concise, persuasive business emails.",
            ),
            (
                "human",
                """Using the analysis below, draft a complete professional email.
Analysis:
{analysis}

Tone: {tone}
Recipient: {recipient}

Include: subject line, greeting, body paragraphs, closing, and a signature placeholder.
Keep the body under 200 words.""",
            ),
        ]
    )

    analysis_chain = analysis_prompt | llm | StrOutputParser()
    draft_chain = draft_prompt | llm | StrOutputParser()

    analysis = analysis_chain.invoke({"context": context, "tone": tone, "recipient": recipient})
    email = draft_chain.invoke({"analysis": analysis, "tone": tone, "recipient": recipient})
    return email


def build_email_crew(context: str, tone: str, recipient: str) -> str:
    return build_email_workflow(context, tone, recipient)


def main():
    parser = argparse.ArgumentParser(description="Email Drafting Agent")
    parser.add_argument(
        "--context",
        default="Follow up on our product demo from last Tuesday. They seemed interested but haven't responded.",
        help="Email context/purpose",
    )
    parser.add_argument("--tone", default="professional and friendly", help="Email tone")
    parser.add_argument("--recipient", default="a potential client", help="Who the email is for")
    args = parser.parse_args()

    print("\n✉️  Drafting email...\n")
    email = build_email_crew(args.context, args.tone, args.recipient)

    print("=" * 60)
    print("📧 DRAFTED EMAIL")
    print("=" * 60)
    print(email)


if __name__ == "__main__":
    main()
