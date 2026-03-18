from endee import Endee, Precision
import requests
import time

import os
from dotenv import load_dotenv
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")

client = Endee()
INDEX_NAME = "study_buddy"
EMBED_DIM = 384

def text_to_vector(text, dim=EMBED_DIM):
    try:
        r = requests.post(
            "https://api.cohere.ai/v1/embed",
            headers={
                "Authorization": f"Bearer {COHERE_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "texts": [text],
                "model": "embed-english-light-v3.0",
                "input_type": "search_document"
            },
            timeout=10
        )
        return r.json()["embeddings"][0]
    except:
        vec = [0.0] * dim
        for i, char in enumerate(text):
            idx = (ord(char) * (i + 1)) % dim
            vec[idx] += 1.0
        norm = sum(x**2 for x in vec) ** 0.5
        return [x / norm if norm > 0 else 0.0 for x in vec]

def delete_index():
    try:
        client.delete_index(INDEX_NAME)
        time.sleep(2)
    except:
        pass

def create_index():
    for _ in range(5):
        try:
            client.create_index(
                name=INDEX_NAME,
                dimension=EMBED_DIM,
                space_type="cosine",
                precision=Precision.INT8D
            )
            time.sleep(2)
            return True
        except:
            time.sleep(1)
    return False

def get_index():
    for _ in range(5):
        try:
            return client.get_index(name=INDEX_NAME)
        except:
            time.sleep(1)
    return None

def store_chunks(chunks, filename):
    delete_index()
    create_index()
    index = get_index()
    if index is None:
        return False
    items = []
    for i, (chunk, page_num) in enumerate(chunks):
        items.append({
            "id": str(i),
            "vector": text_to_vector(chunk),
            "meta": {
                "text": chunk,
                "page": page_num,
                "source": filename
            },
            "filter": {}
        })
    index.upsert(items)
    return True

def search_chunks(query, top_k=4):
    index = get_index()
    if index is None:
        return []
    results = index.query(
        vector=text_to_vector(query),
        top_k=top_k
    )
    output = []
    for item in results:
        try:
            meta = item["meta"]
            score = round(item.get("similarity", 0) * 100, 1)
        except:
            meta = item.meta
            score = round(getattr(item, "similarity", 0) * 100, 1)
        output.append({
            "text": meta.get("text", ""),
            "page": meta.get("page", "?"),
            "source": meta.get("source", "?"),
            "score": score
        })
    return output