import streamlit as st

def show_result(result, index):
    score = result["score"]
    if score > 70:
        label = "High match"
        color = "🟢"
    elif score > 40:
        label = "Good match"
        color = "🟡"
    else:
        label = "Related"
        color = "🔵"

    with st.container():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.caption(f"Result {index + 1}")
        with col2:
            st.caption(f"Page {result['page']}")
        with col3:
            st.caption(f"{color} {label}")
        with col4:
            st.caption(f"{score}% similarity")
        st.info(result["text"])
        st.caption(f"Source: {result['source']}")
        st.divider()

def show_how_it_works():
    st.markdown("#### How it works")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**1. Upload PDF**")
        st.caption("Textbook, notes, resume or any document")
    with col2:
        st.markdown("**2. Chunk & Embed**")
        st.caption("Split into 400-char chunks, embedded via Cohere API")
    with col3:
        st.markdown("**3. Store in Endee**")
        st.caption("384-dim vectors indexed via index.upsert()")
    with col4:
        st.markdown("**4. Search**")
        st.caption("Question vectorized, Endee returns top 4 matches")

def show_pipeline():
    st.code("""
Indexing:  PDF → PyMuPDF → Text Chunks → Cohere Embeddings → Endee index.upsert()
Retrieval: Question → Cohere Embedding → Endee index.query(top_k=4) → Results
    """, language=None)