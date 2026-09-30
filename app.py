import streamlit as st

from main import SAMPLE_QUESTIONS, setup_logging
from src.pipeline import ask

setup_logging()

st.set_page_config(page_title="E-commerce Knowledge Graph", page_icon="🛒", layout="wide")
st.title("E-commerce Knowledge Graph Q&A")
st.caption("Question → LLM → Cypher → Neo4j → LLM → Answer. Answers come only from the graph.")

# Sidebar buttons fill the question box with a sample question.
clicked_sample = None
with st.sidebar:
    st.header("Sample questions")
    for sample in SAMPLE_QUESTIONS:
        if st.button(sample, use_container_width=True):
            clicked_sample = sample

if clicked_sample:
    st.session_state["question"] = clicked_sample

question = st.text_input("Ask a question about products, brands, vendors, customers or orders", key="question")
ask_clicked = st.button("Ask", type="primary")

if (ask_clicked or clicked_sample) and question.strip():
    with st.spinner("Thinking..."):
        result = ask(question.strip())

    st.subheader("1. Question")
    st.write(result["question"])

    st.subheader("2. Cypher query written by the LLM")
    st.code(result["cypher"] or "NO_QUERY", language="cypher")

    st.subheader(f"3. Rows retrieved from Neo4j ({len(result['rows'])})")
    if result["rows"]:
        st.dataframe(result["rows"], use_container_width=True)
    else:
        st.info("No rows returned.")

    st.subheader("4. Answer (based only on the rows above)")
    st.success(result["answer"])