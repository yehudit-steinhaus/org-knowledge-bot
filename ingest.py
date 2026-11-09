"""
טעינת המסמכים מתיקיית data, חלוקה ל-chunks, יצירת וקטורים ושמירה ב-ChromaDB.
הרצה: python ingest.py
"""
import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore

import config
from models import init_models


def build_index() -> int:
    """בונה את האינדקס מחדש ומחזירה את מספר ה-chunks שנשמרו."""
    init_models()

    documents = SimpleDirectoryReader(
        config.DATA_DIR,
        recursive=True,
        required_exts=config.SUPPORTED_EXTS,
    ).load_data()
    if not documents:
        raise RuntimeError(f"לא נמצאו מסמכים בתיקייה {config.DATA_DIR}")

    client = chromadb.PersistentClient(path=config.CHROMA_DIR)

    # מוחקים את האוסף הקודם, אחרת כל הרצה מוסיפה עותק כפול של אותם chunks
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass  # האוסף עוד לא קיים

    collection = client.get_or_create_collection(
        config.COLLECTION_NAME,
        metadata={"hnsw:space": config.DISTANCE_METRIC},
    )
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # חלוקה לפי טוקנים, תוך שמירה על גבולות משפטים, עם חפיפה
    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )
    return collection.count()


if __name__ == "__main__":
    count = build_index()
    print(f"נשמרו {count} chunks ב-ChromaDB")
