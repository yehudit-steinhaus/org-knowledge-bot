"""
קליינט Streamlit פשוט.
הרצה: streamlit run app.py
"""
import hmac
import os

import streamlit as st

import config
from ingest import build_index
from rag import answer_question, load_index

st.set_page_config(page_title="בוט מוסד הלימודים", page_icon="📚")

# יישור לימין עבור עברית
st.markdown(
    """<style>
    .stApp, .stChatMessage, .stMarkdown, p, li, h1, h2, h3, label, textarea, input
    { direction: rtl; text-align: right; }
    </style>""",
    unsafe_allow_html=True,
)

st.title("📚 בוט מוסד הלימודים \"נתיבות\"")
st.caption("שאלות על תקנון, היעדרויות, בחינות, חופשות ושכר לימוד. התשובות מבוססות רק על מסמכי המוסד.")


@st.cache_resource
def get_index():
    return load_index()


def is_admin(password: str) -> bool:
    """בודקת את סיסמת המנהלת. אם לא הוגדרה סיסמה ב-.env, אין גישת ניהול בכלל."""
    if not config.ADMIN_PASSWORD or not password:
        return False
    return hmac.compare_digest(password, config.ADMIN_PASSWORD)


# ברירת מחדל למשתמשות רגילות
allow_expansion = True

# --- סרגל צד: כניסת מנהלת ---
with st.sidebar:
    st.header("כניסת מנהלת")
    password = st.text_input("סיסמה", type="password")

    if password and not is_admin(password):
        st.error("סיסמה שגויה")

    if is_admin(password):
        st.success("מחוברת כמנהלת")

        st.subheader("הגדרות")
        allow_expansion = st.toggle("הרחבת שאלות קצרות", value=True)

        st.subheader("מסמכים")
        uploaded = st.file_uploader(
            "הוספת מסמכים",
            type=[e.strip(".") for e in config.SUPPORTED_EXTS],
            accept_multiple_files=True,
        )
        if st.button("טעינה מחדש של המסמכים"):
            for f in uploaded or []:
                # basename מונע שמירה מחוץ לתיקיית data
                safe_name = os.path.basename(f.name)
                with open(os.path.join(config.DATA_DIR, safe_name), "wb") as out:
                    out.write(f.getbuffer())
            with st.spinner("יוצר וקטורים..."):
                count = build_index()
            get_index.clear()
            st.success(f"נשמרו {count} קטעים")

# --- היסטוריית השיחה ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("לדוגמה: כמה היעדרויות מותר? מתי חופשת פסח?")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("מחפש במסמכים..."):
                result = answer_question(get_index(), question, allow_expansion)
            st.markdown(result.answer)
            answer = result.answer
        except Exception as e:
            answer = f"שגיאה: {e}"
            st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
