import base64
from langchain_core.messages import HumanMessage
from langchain_aws import ChatBedrock
import boto3

bedrock_region = 'us-east-1'
bedrock_client = boto3.client("bedrock-runtime", region_name=bedrock_region)

def describe_image(model_id, image_content, bedrock_client, bedrock_region):
    encoded_image = base64.b64encode(image_content).decode('utf-8')
    
    messages = [
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encoded_image}",
                    },
                },
                {"type": "text", "text": "¿De qué se trata la imagen? Responde en español."},
            ]
        )
    ]

    chat = ChatBedrock(model_id=model_id, region_name=bedrock_region, client=bedrock_client)

    response = chat.invoke(messages)
    return response.content