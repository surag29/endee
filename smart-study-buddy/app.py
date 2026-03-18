import streamlit as st
from endee_client import store_chunks, search_chunks
from pdf_utils import extract_chunks, get_summary, get_suggested_questions
from ui_components import show_result, show_how_it_works, show_pipeline

st.set_page_config(
    page_title="Smart Study Buddy",
    page_icon="📚",
    layout="wide"
)

for key, val in [
    ("chat_history", []),
    ("indexed_files", []),
    ("summary", []),
    ("suggested_questions", []),
    ("total_chunks", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = val

with st.sidebar:
    st.title("📚 Smart Study Buddy")
    st.divider()

    st.markdown("**Vector Database**")
    st.markdown("Endee — cosine similarity, INT8D")

    st.markdown("**Embeddings**")
    st.markdown("Cohere text-embedding-004")

    st.markdown("**Dimensions**")
    st.markdown("384")

    st.divider()

    if st.session_state.total_chunks > 0:
        st.metric("Vectors in Endee", st.session_state.total_chunks)
        st.metric("PDFs Indexed", len(st.session_state.indexed_files))
        st.metric("Questions Asked", len(st.session_state.chat_history))
        st.divider()

    if st.session_state.indexed_files:
        st.markdown("**Indexed Documents**")
        for f in st.session_state.indexed_files:
            st.markdown(f"✅ {f}")
        st.divider()

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

st.title("📚 Smart Study Buddy")
st.caption("RAG-powered PDF Q&A using Endee Vector Database + Cohere Embeddings")
st.divider()

show_how_it_works()
show_pipeline()
st.divider()

uploaded_files = st.file_uploader(
    "Upload your PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    new_files = [f.name for f in uploaded_files]
    if new_files != st.session_state.indexed_files:
        st.session_state.chat_history = []
        st.session_state.indexed_files = []
        st.session_state.summary = []
        st.session_state.suggested_questions = []
        all_chunks = []
        filenames = []
        for f in uploaded_files:
            chunks = extract_chunks(f)
            all_chunks.extend(chunks)
            filenames.append(f.name)
        with st.spinner(f"Indexing {len(all_chunks)} chunks into Endee..."):
            success = store_chunks(all_chunks, ", ".join(filenames))
        if success:
            st.session_state.indexed_files = new_files
            st.session_state.total_chunks = len(all_chunks)
            st.session_state.summary = get_summary(all_chunks)
            st.session_state.suggested_questions = get_suggested_questions(all_chunks)
            st.success(f"✅ {len(all_chunks)} vectors stored in Endee successfully!")
        else:
            st.error("Could not connect to Endee. Make sure Docker is running.")

if st.session_state.summary:
    with st.expander("Document Summary", expanded=True):
        for i, point in enumerate(st.session_state.summary):
            st.markdown(f"**{i+1}.** {point}")

if st.session_state.suggested_questions:
    st.markdown("**Suggested Questions**")
    cols = st.columns(3)
    for i, q in enumerate(st.session_state.suggested_questions):
        with cols[i % 3]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                results = search_chunks(q)
                st.session_state.chat_history.append({
                    "question": q,
                    "results": results
                })
                st.rerun()

st.divider()
st.subheader("Ask a Question")

for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["question"])
    with st.chat_message("assistant"):
        for i, r in enumerate(chat["results"]):
            show_result(r, i)

query = st.chat_input("Ask anything from your documents...")
if query:
    if not st.session_state.indexed_files:
        st.warning("Please upload a PDF first.")
    else:
        with st.chat_message("user"):
            st.write(query)
        with st.chat_message("assistant"):
            with st.spinner("Searching Endee..."):
                results = search_chunks(query)
            for i, r in enumerate(results):
                show_result(r, i)
        st.session_state.chat_history.append({
            "question": query,
            "results": results
        })