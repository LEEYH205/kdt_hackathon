from fastapi import FastAPI
from pydantic import BaseModel
from pipeline_mvp import add_idea, df        # add_idea : 7단계에서 만든 함수, df도 같이 import

app = FastAPI()

class IdeaIn(BaseModel):
    idea_id: str
    title: str
    body: str = ""

@app.post("/submit")
def submit(idea: IdeaIn):
    sim = add_idea(idea.dict())              # [(idx, np.float32), ...]
    results = [
        {
            "idea_id": str(df.loc[int(idx), "idea_id"]),
            "title": df.loc[int(idx), "title"],
            "body": (df.loc[int(idx), "body"][:120] + "...") if len(df.loc[int(idx), "body"]) > 120 else df.loc[int(idx), "body"],
            "score": round(float(score), 3)
        }
        for idx, score in sim if score > 0.7
    ]
    return {"similar": results}