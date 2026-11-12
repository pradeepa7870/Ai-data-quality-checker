import streamlit as st
import pandas as pd
from backend.quality import analyze_dataframe
from backend.rag import retrieve_rules, build_knowledge_base
from backend.llm import explain_with_ollama

st.set_page_config(page_title="DataGuard AI", page_icon="🛡️", layout="wide")

st.title("🛡️ DataGuard AI")
st.caption("Beginner-friendly AI-powered enterprise data quality checker")

with st.sidebar:
    st.header("Settings")
    st.info("Start by uploading a CSV or Excel file. The sample employee dataset is included.")
    use_sample = st.checkbox("Use sample employee dataset", value=True)
    st.markdown("---")
    st.markdown("**Local AI model**")
    model_name = st.text_input("Ollama model", value="gemma3:1b")
    st.caption("Install and start Ollama before asking AI questions.")

uploaded = st.file_uploader("Upload a business dataset", type=["csv", "xlsx"])

df = None
try:
    if uploaded is not None:
        if uploaded.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded)
        else:
            df = pd.read_csv(uploaded)
    elif use_sample:
        df = pd.read_csv("data/sample_employees.csv")
except Exception as exc:
    st.error(f"Could not read the file: {exc}")

if df is not None:
    st.subheader("1. Dataset preview")
    st.write(f"Rows: **{len(df)}** · Columns: **{len(df.columns)}**")
    st.dataframe(df.head(100), use_container_width=True)

    if st.button("🔎 Analyze dataset", type="primary", use_container_width=True):
        with st.spinner("Checking data quality..."):
            st.session_state["analysis"] = analyze_dataframe(df)

    result = st.session_state.get("analysis")
    if result:
        st.subheader("2. Data quality results")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows scanned", result["total_rows"])
        c2.metric("Issues found", result["issue_count"])
        c3.metric("Quality score", f'{result["quality_score"]}%')
        c4.metric("Issue types", len(set(x["issue_type"] for x in result["issues"])))

        if result["issues"]:
            issue_df = pd.DataFrame(result["issues"])
            st.dataframe(issue_df, use_container_width=True)
            csv_bytes = issue_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download issues CSV", csv_bytes, "data_quality_issues.csv", "text/csv")
        else:
            st.success("No issues found by the configured checks.")

        st.subheader("3. Ask the AI data assistant")
        question = st.text_input(
            "Ask a question about the scan",
            placeholder="Why is employee 103 flagged?"
        )
        if st.button("✨ Ask AI", disabled=not bool(question.strip())):
            with st.spinner("Retrieving business rules and asking the local LLM..."):
                try:
                    context = retrieve_rules(question)
                    answer = explain_with_ollama(
                        question=question,
                        analysis=result,
                        retrieved_rules=context,
                        model=model_name
                    )
                    st.session_state["last_answer"] = answer
                except Exception as exc:
                    st.session_state["last_answer"] = (
                        "The local AI could not be reached. Check that Ollama is running "
                        f"and that model '{model_name}' is installed.\n\nTechnical detail: " + str(exc)
                    )
        if st.session_state.get("last_answer"):
            st.info(st.session_state["last_answer"])
else:
    st.warning("Upload a CSV/XLSX file or select the sample dataset in the sidebar.")

st.markdown("---")
st.caption("Prototype note: the validation engine detects issues. The LLM explains results; it does not modify your source data.")
