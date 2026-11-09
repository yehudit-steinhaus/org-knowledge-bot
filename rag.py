"""
לוגיקת השאלה-תשובה: הרחבת שאלה, חיפוש ב-ChromaDB, ויצירת תשובה רק מתוך המסמכים.
"""
from dataclasses import dataclass, field

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.llms import ChatMessage
from llama_index.vector_stores.chroma import ChromaVectorStore

import config
from models import init_models

NO_ANSWER = "לא מצאתי מידע על כך במסמכי המוסד. מומלץ לפנות למזכירות."

SYSTEM_PROMPT = f"""אתה עוזר של מוסד הלימודים "נתיבות", ועונה לתלמידות ולהורים על סמך מסמכי המוסד בלבד.
כללים:
1. ענה אך ורק על סמך הקטעים שסופקו בתוך <context>.
2. אם התשובה לא מופיעה בקטעים, ענה בדיוק: "{NO_ANSWER}"
3. אל תשתמש בידע כללי ואל תנחש.
4. ענה בשפה שבה נשאלה השאלה, בקצרה ובבהירות.
5. אל תציין שמות קבצים או מקורות בתשובה."""

EXPAND_PROMPT = """נסח מחדש את שאלת המשתמש כשאלת חיפוש מלאה וברורה יותר,
כדי שיהיה קל למצוא אותה במסמכים של מוסד לימודים
(תקנון, היעדרויות, בחינות, חופשות, שכר לימוד).
הוסף מילים נרדפות רלוונטיות. אל תענה על השאלה. החזר שורה אחת בלבד.

שאלה: {question}
שאלה מורחבת:"""


@dataclass
class RagResult:
    answer: str
    search_query: str
    expanded: bool
    sources: list = field(default_factory=list)  # [(file_name, score, text)]


def load_index() -> VectorStoreIndex:
    init_models()
    client = chromadb.PersistentClient(path=config.CHROMA_DIR)
    collection = client.get_or_create_collection(
        config.COLLECTION_NAME,
        metadata={"hnsw:space": config.DISTANCE_METRIC},
    )
    if collection.count() == 0:
        raise RuntimeError("האינדקס ריק. יש להריץ קודם: python ingest.py")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return VectorStoreIndex.from_vector_store(vector_store)


def should_expand(question: str) -> bool:
    return len(question.split()) < config.EXPAND_IF_SHORTER_THAN


def expand_query(question: str) -> str:
    text = Settings.llm.complete(EXPAND_PROMPT.format(question=question)).text
    return text.strip().splitlines()[0] if text.strip() else question


def answer_question(index: VectorStoreIndex, question: str, allow_expansion: bool = True) -> RagResult:
    # שלב 1: הרחבת שאלה (רק לשאלות קצרות)
    expanded = allow_expansion and should_expand(question)
    search_query = expand_query(question) if expanded else question

    # שלב 2: חיפוש וקטורי (דמיון cosine) והחזרת TOP_K תוצאות
    retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    nodes = retriever.retrieve(search_query)
    if config.MIN_SCORE is not None:
        nodes = [n for n in nodes if (n.score or 0) >= config.MIN_SCORE]

    sources = [
        (n.metadata.get("file_name", "לא ידוע"), n.score, n.get_content())
        for n in nodes
    ]
    if not nodes:
        return RagResult(NO_ANSWER, search_query, expanded, sources)

    # שלב 3: יצירת תשובה מתוך הקטעים בלבד (עונים על השאלה המקורית, לא המורחבת)
    context = "\n\n---\n\n".join(f"[קובץ: {name}]\n{text}" for name, _, text in sources)
    messages = [
        ChatMessage(role="system", content=SYSTEM_PROMPT),
        ChatMessage(role="user", content=f"<context>\n{context}\n</context>\n\nשאלה: {question}"),
    ]
    answer = Settings.llm.chat(messages).message.content.strip()
    return RagResult(answer, search_query, expanded, sources)
