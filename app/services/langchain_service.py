# app/services/langchain_service.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI

async def summarize_lessons(lessons: list):
    """
    Summarizes internal lessons to short coherent descriptions using LangChain.
    """
    summarized = []
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    for lesson in lessons:
        text = lesson.get("content", lesson.get("title", ""))
        summary = chain.run(text)
        summarized.append({
            "id": lesson["id"],
            "title": lesson["title"],
            "summary": summary,
            "type": lesson.get("type", "pdf"),
            "difficulty": lesson.get("difficulty", 1)
        })
    return summarized
