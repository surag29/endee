import fitz

def extract_chunks(uploaded_file, chunk_size=400):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    chunks = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size].strip()
            if chunk:
                chunks.append((chunk, page_num))
    return chunks

def get_summary(chunks):
    sample = " ".join([c[0] for c in chunks[:10]])
    for sep in [".", "!", "?"]:
        sample = sample.replace(sep, sep + "|")
    sentences = [s.strip() for s in sample.split("|") if len(s.strip()) > 60]
    return sentences[:3] if sentences else ["Document indexed successfully."]

def get_suggested_questions(chunks):
    questions = []
    for chunk, _ in chunks:
        words = chunk.split()
        if len(words) > 8:
            q = "Explain: " + " ".join(words[:7]) + "..."
            if q not in questions:
                questions.append(q)
        if len(questions) >= 3:
            break
    return questions or [
        "What is the main topic?",
        "What are the key concepts?",
        "Summarize the important points."
    ]