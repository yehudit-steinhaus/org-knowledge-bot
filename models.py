"""אתחול המודלים ב-LlamaIndex (נקרא פעם אחת בתחילת הריצה)."""
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import config


def init_models():
    Settings.embed_model = OpenAIEmbedding(model=config.EMBED_MODEL)
    Settings.llm = OpenAI(model=config.LLM_MODEL, temperature=config.LLM_TEMPERATURE)
