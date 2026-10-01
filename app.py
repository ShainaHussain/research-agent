"""
app.py
------
Core prototype loop: Topic -> arXiv papers -> Claude gap table -> Cross-paper synthesis

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from services.arxiv_client import search_arxiv

# ---- Pick your AI provider by uncommenting ONE of these three lines ----
#from claude_client import analyze_papers, synthesize_gaps   # needs ANTHROPIC_API_KEY (paid)
from services.gemini_client import analyze_papers, synthesize_gaps  # needs GEMINI_API_KEY (free)
# from groq_client import analyze_papers, synthesize_gaps    # needs GROQ_API_KEY (free)

load_dotenv()  # loads GEMINI_API_KEY from .env

st.set_page_config(page_title="Research Partner", page_icon="🔎", layout="wide")

# ---------- Session state ----------
if "papers" not in st.session_state:
    st.session_state.papers = []
if "synthesis" not in st.session_state:
    st.session_state.synthesis = None

# ---------- Header ----------
st.title("🔎 Research Partner")
st.caption("Give a topic. Get papers, plain-language summaries, and the gaps between them.")

# ---------- Onboarding inputs ----------
with st.container(border=True):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        topic = st.text_input("What's your research topic?", placeholder="e.g. Federated Learning in IoT")
    with col2:
        experience = st.selectbox("Experience level", ["beginner", "intermediate", "advanced"])
    with col3:
        max_results = st.slider("Papers to fetch", 3, 15, 8)

    search_clicked = st.button("🔍 Find Papers & Analyze", type="primary", use_container_width=True)

# ---------- Search + Analyze ----------
if search_clicked:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.synthesis = None
        with st.spinner("Searching arXiv..."):
            papers = search_arxiv(topic, max_results=max_results)

        if not papers:
            st.error("No papers found. Try a broader topic.")
        else:
            with st.spinner(f"Analyzing {len(papers)} papers with Gemini..."):
                try:
                    papers = analyze_papers(papers, experience_level=experience)
                    st.session_state.papers = papers
                    st.session_state.topic = topic
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

# ---------- Results Table ----------
if st.session_state.papers:
    st.subheader(f"📚 Papers on: {st.session_state.get('topic', topic)}")

    df = pd.DataFrame([{
        "Title": p["title"],
        "Difficulty": p.get("difficulty", "-"),
        "What it does": p.get("plain_summary", ""),
        "Method": p.get("method", ""),
        "Future Work (stated)": p.get("future_work", ""),
        "Gap (inferred)": p.get("gap", ""),
        "Link": p["url"],
    } for p in st.session_state.papers])

    st.dataframe(
        df,
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn()},
        hide_index=True,
    )

    st.divider()

    # ---------- Cross-paper gap synthesis ----------
    st.subheader("🎯 Gap Analysis Across All Papers")
    if st.button("Generate Cross-Paper Gap Synthesis"):
        with st.spinner("Looking across all papers for patterns and gaps..."):
            try:
                st.session_state.synthesis = synthesize_gaps(
                    st.session_state.papers, st.session_state.get("topic", topic)
                )
            except Exception as e:
                st.error(f"Synthesis failed: {e}")

    if st.session_state.synthesis:
        synthesis = st.session_state.synthesis

        st.markdown("#### Cross-cutting gaps")
        for g in synthesis.get("cross_cutting_gaps", []):
            with st.container(border=True):
                st.markdown(f"**{g['gap']}**")
                st.write(g.get("why_it_matters", ""))
                supporting = ", ".join(g.get("supporting_papers", []))
                if supporting:
                    st.caption(f"Based on: {supporting}")

        st.markdown("#### 💡 Suggested research questions")
        for q in synthesis.get("suggested_questions", []):
            with st.container(border=True):
                st.markdown(f"**{q['question']}**")
                st.write(q.get("rationale", ""))

        # Export
        st.divider()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download table as CSV", csv, "gap_analysis.csv", "text/csv")
else:
    st.info("Enter a topic above and click 'Find Papers & Analyze' to get started.")