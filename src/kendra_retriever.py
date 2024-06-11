import boto3
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_aws import BedrockLLM
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import HtmlFormatter
import re
from gitlab_utils import create_commit

kendra_index = 'e876b289-9a67-4108-ad55-068480b38bce'
bedrock_region = 'us-east-1'
kendra_region = 'us-east-1'


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


def format_response(response, docs):
    formatted_response = "Respuesta:\n"
    formatted_response += response + "\n"
    return formatted_response


def perform_qa(query, retriever):
    bedrock_client = boto3.client("bedrock-runtime", region_name=kendra_region)
    llm = BedrockLLM(model_id="mistral.mistral-large-2402-v1:0", region_name=bedrock_region, 
                     client=bedrock_client)
    
    qa_chain = load_qa_chain(llm, chain_type="stuff")
    
    try:
        docs = retriever.get_relevant_documents(query)
        response = qa_chain.run(input_documents=docs, question=query)
        
        formatted_response = format_response(response, docs)
        
        print(f"Query: {query}")
        print(f"Response: {formatted_response}")
        
        if "realiza un commit de estos cambios" in query.lower():
            # Extraer el código fuente de la respuesta
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
    # Buscar el bloque de código en la respuesta
    start_index = text.find("```java")
    end_index = text.find("```", start_index + 1)

    if start_index != -1 and end_index != -1:
        code_block = text[start_index + 7:end_index].strip()
        return code_block
    else:
        return None