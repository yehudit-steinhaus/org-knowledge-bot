"""
הגדרות מרכזיות של המערכת.
כל נקודות ההחלטה של התרגיל מרוכזות כאן, כדי שיהיה קל לשנות ולהסביר אותן.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # טוען את OPENAI_API_KEY מקובץ .env

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("חסר OPENAI_API_KEY. יש ליצור קובץ .env לפי .env.example")

# סיסמת מנהלת להעלאת מסמכים מהממשק. אם לא מוגדרת, אפשרות ההעלאה לא זמינה לאף אחד.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# --- נתיבים ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")          # המסמכים הארגוניים
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")   # היכן ש-ChromaDB שומר את הווקטורים
COLLECTION_NAME = "org_knowledge"

# --- החלטה 7: מודלים ---
EMBED_MODEL = "text-embedding-3-small"   # מודל ליצירת וקטורים
LLM_MODEL = "gpt-4.1-mini"               # מודל ליצירת תשובה
LLM_TEMPERATURE = 0.0                    # 0 = תשובות עקביות וצמודות למקור

# --- החלטות 3+4: חלוקה ל-chunks לפי טוקנים, עם חפיפה ---
CHUNK_SIZE = 512       # טוקנים בכל chunk
CHUNK_OVERLAP = 64     # טוקנים חופפים בין chunks סמוכים (כ-12%)

# --- החלטה 6: כמה chunks להחזיר בכל חיפוש ---
TOP_K = 4

# סף דמיון מינימלי. None = ללא סינון.
# אפשר לכייל אחרי שרואים בממשק את הציונים של תוצאות רלוונטיות ולא רלוונטיות.
MIN_SCORE = None

# --- החלטה 8: הרחבת שאלה ---
# מרחיבים רק שאלות קצרות (פחות מ-X מילים), כדי לא לשלם על קריאה נוספת לכל שאלה.
EXPAND_IF_SHORTER_THAN = 6

# --- החלטה 9: מדד מרחק בחיפוש ---
# ברירת המחדל של Chroma היא l2. עבור embeddings של OpenAI מתאים cosine.
DISTANCE_METRIC = "cosine"

SUPPORTED_EXTS = [".txt", ".md", ".pdf", ".docx"]
