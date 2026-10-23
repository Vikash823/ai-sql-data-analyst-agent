
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from agent_graph_v2 import agent


app = FastAPI(
    title="AI SQL Data Analyst API",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=500
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_agent(request: QuestionRequest):

    try:
        result = agent.invoke({
            "question": request.question,
            "attempts": 0,
            "error": "",
            "result": {},
            "insight": ""
        })

        if result.get("error"):
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "error": result["error"]
                }
            )

        data = result.get("result", {})

        if not data:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "No query result returned."
                }
            )

        return {
            "success": True,
            "question": request.question,
            "sql": result.get("sql", ""),
            "columns": data.get("columns", []),
            "rows": data.get("rows", []),
            "row_count": data.get("row_count", 0),
            "insight": result.get("insight", ""),
            "attempts": result.get("attempts", 0)
        }

    except Exception as error:
        print("API ERROR:", type(error).__name__)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Agent request failed."
            }
        )
