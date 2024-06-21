import boto3
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_aws import BedrockLLM, ChatBedrock
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import HtmlFormatter
import re
from gitlab_utils import create_commit
import base64
import json
import magic

kendra_index = '0c226ddc-a112-4197-88aa-50179e634dd5'
bedrock_region = 'us-east-1'
kendra_region = 'us-east-1'
bedrock_client = boto3.client("bedrock-runtime", region_name=bedrock_region)

def get_kendra_doc_retriever():
    kendra_client = boto3.client("kendra", region_name=kendra_region)
    retriever = AmazonKendraRetriever(
        index_id=kendra_index,
        top_k=4,
        client=kendra_client,
        filter={
            "OrAllFilters": [
                {
                    "EqualsTo": {
                        "Key": "_data_source_s3_prefix",
                        "Value": "java-code/"
                    }
                },
                {
                    "EqualsTo": {
                        "Key": "_data_source_s3_prefix",
                        "Value": "documentation/"
                    }
                }
            ]
        }
    )
    return retriever

def format_response(response):
    formatted_response = response
    return formatted_response

def perform_qa(query, retriever, model_id, image_description=None):
    bedrock_client = boto3.client("bedrock-runtime", region_name=kendra_region)
    
    if model_id.startswith("anthropic."):
        llm = ChatBedrock(model_id=model_id, region_name=bedrock_region, client=bedrock_client)
    else:
        llm = BedrockLLM(model_id=model_id, region_name=bedrock_region, client=bedrock_client)
    
    qa_chain = load_qa_chain(llm, chain_type="stuff")
    
    try:
        docs = retriever.get_relevant_documents(query)
        
        # Agregar instrucción para responder en español
        spanish_instruction = "Responde siempre en español. "
        
        if image_description:
            query_with_image = f"{spanish_instruction}Imagen: {image_description}\nConsulta: {query}"
        else:
            query_with_image = f"{spanish_instruction}{query}"
        
        response = qa_chain.run(input_documents=docs, question=query_with_image)
        
        formatted_response = format_response(response)
        
        print(f"Query: {query}")
        print(f"Response: {formatted_response}")
        
        if "realiza un commit de estos cambios" in query.lower():
            code_block = extract_code_block(formatted_response)
            if code_block:
                file_path = 'src/main/java/regresion/personas/menu_transferencias_pagos/TransferTest.java'
                commit_message = 'Cambios realizados desde el asistente de código'
                create_commit(file_path, commit_message, code_block)
            else:
                print("No se encontró un bloque de código en la respuesta.")
        
        return {"result": formatted_response, "source_documents": docs}
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return {"error": error_message}

def extract_code_block(text):
    start_index = text.find("```java")
    end_index = text.find("```", start_index + 1)

    if start_index != -1 and end_index != -1:
        code_block = text[start_index + 7:end_index].strip()
        return code_block
    else:
        return None