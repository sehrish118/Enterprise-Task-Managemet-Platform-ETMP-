# app/rag/relevance_check.py
"""
Gatekeeper that runs BEFORE chunking/embedding a newly uploaded document.
Uses an LLM call to classify whether the document's content is plausibly
related to internal company/work operations — rejects anything clearly
unrelated (recipes, personal files, random internet text, etc.) before it
becomes part of the searchable knowledge base.
"""

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import SecretStr

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Use the larger model here — the small 20b model was misclassifying
# obviously unrelated content (e.g. recipes) as company-related.
CLASSIFIER_MODEL = "openai/gpt-oss-120b"

RELEVANCE_SYSTEM_PROMPT = """You are a strict content classifier for a company's internal knowledge base.

Your job: decide if the document text below is genuinely related to internal company/work operations.

RELATED examples: project specs, requirements docs, meeting notes, internal policies,
technical documentation, HR guidelines, business reports, proposals, contracts,
architecture docs, onboarding guides, SOPs.

NOT RELATED examples (always reject these): recipes, cooking instructions, personal
hobbies, entertainment content, song lyrics, poems, general trivia, news articles
unrelated to the business, personal letters, fiction, homework, or any content with
no plausible connection to running a company or its projects.

Be strict — if you are not confident the document is business/work-related, answer NO.

Reply with EXACTLY one word: YES or NO. No punctuation, no explanation, nothing else.
"""


async def is_company_related(text_sample: str) -> tuple[bool, str]:
    """
    Returns (is_related, reason). reason is only meaningful when
    is_related is False, for logging/display purposes.
    """
    if not text_sample.strip():
        return False, "Document appears to be empty or unreadable."

    llm = ChatGroq(
        model=CLASSIFIER_MODEL,
        api_key=SecretStr(settings.GROQ_API_KEY),
        temperature=0,
    )

    sample = text_sample[:2000]

    response = await llm.ainvoke(
        [
            SystemMessage(content=RELEVANCE_SYSTEM_PROMPT),
            HumanMessage(content=f"Document text:\n\n{sample}"),
        ]
    )
    verdict = str(response.content).strip().upper()

    logger.info(f"Relevance classifier raw verdict: {verdict!r}")

    if verdict.startswith("YES"):
        return True, ""
    return (
        False,
        "This document does not appear to be related to company or work operations.",
    )
