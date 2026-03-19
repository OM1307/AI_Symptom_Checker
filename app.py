import html
import re
import streamlit as st
from rag import generate_response

st.set_page_config(page_title="AI Symptom Checker", layout="wide")

st.markdown(
    """
    <style>
    :root { color-scheme: light; }
    .app-wrap { max-width: 980px; margin: 0 auto; }
    .hero {
        background: radial-gradient(1200px 400px at 10% -20%, #d9f0ff 0%, rgba(217,240,255,0) 60%),
                    radial-gradient(900px 300px at 90% -30%, #ffe6cc 0%, rgba(255,230,204,0) 55%),
                    #f8fafc;
        border: 1px solid #e7eef6;
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 18px;
    }
    .hero h1 { font-family: "Alegreya Sans", "Segoe UI", Arial, sans-serif; font-size: 34px; margin: 0; }
    .hero p { color: #425466; margin: 6px 0 0 0; }
    .chip {
        display: inline-block; padding: 6px 10px; border-radius: 999px;
        background: #e8f4ff; color: #1f4d7a; font-size: 12px; margin-right: 8px;
        border: 1px solid #d7e9ff;
    }
    [data-testid="stSidebar"] { background: #f8fafc; }
    .sidebar-head { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
    .sidebar-logo {
        width: 28px; height: 28px; border-radius: 8px; background: #0f172a;
        display: inline-flex; align-items: center; justify-content: center; color: #fff;
        font-weight: 700; font-size: 14px;
    }
    .sidebar-title { font-weight: 700; color: #0f172a; }
    .history-stack [role="radiogroup"] { gap: 8px; }
    .history-stack label {
        background: #ffffff; border: 1px solid #e9eef5; border-radius: 12px;
        padding: 10px 12px; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        transition: transform .08s ease, box-shadow .2s ease, border-color .2s ease;
    }
    .history-stack label:hover { transform: translateY(-1px); border-color: #c9d8f5; }
    .history-stack label:has(input:checked) {
        border-color: #3b82f6; box-shadow: 0 10px 26px rgba(59, 130, 246, 0.22);
    }
    .history-stack label > div:first-child { display: none; }
    .history-stack input { display: none; }
    [data-testid="stSidebar"] button {
        width: 100%; border-radius: 10px; padding: 8px 10px !important;
        border: 1px solid #dbe4ef; background: #ffffff; font-weight: 600;
    }
    .result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .result-card {
        background: #ffffff; border: 1px solid #e9eef5; border-radius: 18px;
        padding: 16px 16px 14px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    .result-head {
        display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
    }
    .result-icon {
        width: 30px; height: 30px; border-radius: 10px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; font-size: 14px;
        color: #0f172a;
    }
    .result-icon svg { width: 18px; height: 18px; fill: #0f172a; }
    .icon-causes { background: #e7f0ff; }
    .icon-remedies { background: #e9fff0; }
    .icon-otc { background: #fff3e2; }
    .icon-doctor { background: #ffe8e8; }
    .result-title { font-weight: 700; color: #0f172a; }
    .result-list { list-style: none; padding-left: 0; margin: 6px 0 0 0; }
    .result-list li {
        padding: 6px 8px; border-radius: 10px; background: #f8fafc;
        border: 1px solid #eef2f6; margin-bottom: 6px;
    }
    .result-list li:last-child { margin-bottom: 0; }
    .subtle { color: #64748b; font-size: 13px; }
    .stChatMessage { border-radius: 16px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
        <span class="chip">RAG + Gemini</span>
        <span class="chip">Health Info</span>
        <h1>AI Symptom Checker</h1>
        <p>Describe your symptoms in plain language. You will get possible causes,
        home remedies, OTC options, and when to see a doctor.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "current_id" not in st.session_state:
    st.session_state.current_id = None


def _clean_lines(text: str) -> list[str]:
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]


def _parse_sections(text: str) -> tuple[dict[str, list[str]], list[str]]:
    sections = {
        "Possible Causes": [],
        "Home Remedies": [],
        "OTC Medicines": [],
        "When to See a Doctor": [],
    }
    disclaimer_lines: list[str] = []
    current = None
    for line in _clean_lines(text):
        lower = line.lower()
        title_match = re.match(r"^\d+\.\s*(.+?):\s*$", line)
        if title_match:
            title = title_match.group(1).strip()
            for key in sections:
                if key.lower() in title.lower():
                    current = key
                    break
            continue
        if (
            "disclaimer" in lower
            or "not medical advice" in lower
            or re.match(r"^\u26a0", line)
        ):
            disclaimer_lines.append(line.replace("Disclaimer:", "").strip())
            current = None
            continue
        if re.match(r"^[\-\*\u2022]", line):
            item = re.sub(r"^[\-\*\u2022]\s*", "", line).strip()
            if current and item:
                sections[current].append(item)
        elif current:
            sections[current].append(line)
    return sections, [ln for ln in disclaimer_lines if ln]


def _summary_label(text: str) -> str:
    text = text.strip().replace("\n", " ")
    if len(text) <= 36:
        return text
    return text[:33] + "..."


if st.session_state.history:
    st.sidebar.markdown(
        """
        <div class="sidebar-head">
            <div class="sidebar-logo">◎</div>
            <div class="sidebar-title">AI Symptom Checker</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="history-stack">', unsafe_allow_html=True)
    labels = [_summary_label(h["query"]) for h in st.session_state.history]
    ids = [h["id"] for h in st.session_state.history]
    default_index = len(ids) - 1
    if st.session_state.current_id in ids:
        default_index = ids.index(st.session_state.current_id)
    selected = st.sidebar.radio(
        "",
        options=ids,
        index=default_index,
        format_func=lambda i: labels[ids.index(i)],
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    st.session_state.current_id = selected


user_input = st.chat_input("Type your symptoms, duration, and severity")

if user_input:
    with st.spinner("Analyzing your symptoms..."):
        raw_response = generate_response(user_input)

    sections, disclaimer_lines = _parse_sections(raw_response)
    entry_id = len(st.session_state.history) + 1
    st.session_state.history.append(
        {
            "id": entry_id,
            "query": user_input,
            "sections": sections,
            "disclaimer": disclaimer_lines,
        }
    )
    st.session_state.current_id = entry_id


current_entry = None
for item in st.session_state.history:
    if item["id"] == st.session_state.current_id:
        current_entry = item
        break

if current_entry:
    with st.chat_message("user"):
        st.markdown(current_entry["query"])

    with st.chat_message("assistant"):
        st.markdown("Here is a structured summary based on your symptoms:")
        icon_map = {
            "Possible Causes": (
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c4.4 0 8 3.6 8 8 0 5.2-6.2 9.9-7.1 10.6a1.4 1.4 0 0 1-1.8 0C10.2 20.9 4 16.2 4 11c0-4.4 3.6-8 8-8zm0 3a5 5 0 0 0-5 5c0 3 3.2 6 5 7.6 1.8-1.6 5-4.6 5-7.6a5 5 0 0 0-5-5z"/></svg>',
                "icon-causes",
            ),
            "Home Remedies": (
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 6h-5.6L12 2.5 10.6 6H5l3.8 2.7-1.4 4.6 4.6-2.9 4.6 2.9-1.4-4.6L19 6zm-7 8.2c-4.6 0-8.5 3.1-9.7 7.3h19.4c-1.2-4.2-5.1-7.3-9.7-7.3z"/></svg>',
                "icon-remedies",
            ),
            "OTC Medicines": (
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 3h9a3 3 0 0 1 3 3v2.5a3 3 0 0 1-3 3h-9a3 3 0 0 1-3-3V6a3 3 0 0 1 3-3zm0 9h9a3 3 0 0 1 3 3V18a3 3 0 0 1-3 3h-9a3 3 0 0 1-3-3v-3a3 3 0 0 1 3-3zm1.2-6.5h6.6M8.7 15.5h6.6"/></svg>',
                "icon-otc",
            ),
            "When to See a Doctor": (
                '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 3h2v4h4v2h-4v4h-2V9H7V7h4V3zm1 6a7 7 0 1 1-7 7 7 7 0 0 1 7-7z"/></svg>',
                "icon-doctor",
            ),
        }

        cards_html = ['<div class="result-grid">']
        for title, items in current_entry["sections"].items():
            icon, icon_class = icon_map.get(title, ("<span>?</span>", "icon-causes"))
            cards_html.append('<div class="result-card">')
            cards_html.append(
                f'<div class="result-head"><div class="result-icon {icon_class}">{icon}</div>'
                f'<div class="result-title">{html.escape(title)}</div></div>'
            )
            cards_html.append('<ul class="result-list">')
            if items:
                for item in items:
                    cards_html.append(f"<li>{html.escape(item)}</li>")
            else:
                cards_html.append("<li>Not enough information provided.</li>")
            cards_html.append("</ul></div>")
        cards_html.append("</div>")
        st.markdown("\n".join(cards_html), unsafe_allow_html=True)

        disclaimer_text = " ".join(current_entry["disclaimer"]).strip()
        if not disclaimer_text:
            disclaimer_text = (
                "This is not medical advice. If symptoms are severe, worsening, "
                "or persistent, consult a clinician."
            )
        st.markdown(f'<p class="subtle">{html.escape(disclaimer_text)}</p>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
