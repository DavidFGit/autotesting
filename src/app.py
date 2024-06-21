from fastapi import FastAPI, Request, Form, UploadFile, File
from kendra_retriever import get_kendra_doc_retriever, perform_qa
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import warnings
from langchain._api import LangChainDeprecationWarning
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from claude_vision2 import describe_image, bedrock_client, bedrock_region

warnings.simplefilter("ignore", category=LangChainDeprecationWarning)

app = FastAPI()

app.mount("/static", StaticFiles(directory="img"), name="static")

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory="src/templates")

@app.post("/query")
async def process_query(query: str = Form(...), model_id: str = Form(...), image: UploadFile = File(None)):
    if query or image:
        try:
            retriever = get_kendra_doc_retriever()
            image_description = None
            if image:
                image_content = await image.read()
                image_description = describe_image("anthropic.claude-3-sonnet-20240229-v1:0", image_content, bedrock_client, bedrock_region)
            response = perform_qa(query, retriever, model_id, image_description)
            if "error" in response:
                return {"error": response["error"]}
            else:
                formatted_response = response["result"]
                print(f"Query: {query}")
                print(f"Response: {formatted_response}")
                return {"result": formatted_response}
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