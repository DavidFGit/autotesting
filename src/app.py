from fastapi import FastAPI, Request, Body
from kendra_retriever import get_kendra_doc_retriever, perform_qa
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import warnings
from langchain._api import LangChainDeprecationWarning
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

warnings.simplefilter("ignore", category=LangChainDeprecationWarning)

app = FastAPI()
app.mount("/static", StaticFiles(directory="img"), name="static")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "templates"))

@app.post("/query")
async def process_query(data: dict = Body(...)):
    query = data.get("query")
    if query:
        try:
            retriever = get_kendra_doc_retriever()
            response = perform_qa(query, retriever)
            if "error" in response:
                return {"error": response["error"]}
            else:
                formatted_response = response["result"]
                source_documents = response["source_documents"]
                print(f"Query: {query}")
                print(f"Response: {formatted_response}")  # Imprimir la respuesta en la consola
                return {"result": formatted_response, "source_documents": source_documents}
        except Exception as e:
            error_message = f"Error during query processing: {str(e)}"
            return {"error": error_message}
    else:
        return {"error": "Query not provided"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8095)