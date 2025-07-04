# 1~7단계 전체 코드 (df, emb, embedder, index, clean, add_idea) 정의
import pandas as pd, numpy as np, faiss, re
from sentence_transformers import SentenceTransformer

# ---------- 1. 데이터 & 전처리 ----------
df = pd.read_csv("./data/ideas_sample.csv").fillna("")
def clean(txt): return re.sub(r"\s+", " ", re.sub(r"[^\w가-힣 ]", " ", txt)).strip().lower()
df["clean"] = df["title"] + " " + df["body"]
df["clean"] = df["clean"].apply(clean)

# ---------- 2. 임베딩 ----------
embedder = SentenceTransformer("jhgan/ko-sbert-sts")
emb = embedder.encode(df["clean"].tolist(), normalize_embeddings=True).astype("float32")

# ---------- 3. FAISS ----------
index = faiss.IndexFlatIP(emb.shape[1])
index.add(emb)

# ---------- 4. add_idea 함수 ----------
def add_idea(row: dict, top_k: int = 5):
    global df, emb, index
    new_clean = clean(row["title"] + " " + row.get("body", ""))
    vec = embedder.encode([new_clean], normalize_embeddings=True).astype("float32")
    D, I = index.search(vec, top_k)
    index.add(vec)                       # 실시간 반영
    emb = np.vstack([emb, vec])
    df = pd.concat([df, pd.DataFrame([row | {"clean": new_clean}])], ignore_index=True)
    return list(zip(I[0], D[0]))         # [(idx, score), ...]

# add_idea() 함수가 글로벌 df/emb/index 를 수정하도록 선언
__all__ = ["add_idea"]