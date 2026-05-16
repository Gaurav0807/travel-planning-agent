import os
import json
import boto3
import logging
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, ConfigDict

load_dotenv()

logger = logging.getLogger(__name__)

BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")

logger.info(f"Using Bedrock Model: {BEDROCK_MODEL}")
logger.info(f"Using Region: {REGION}")


class BedrockLLM(BaseChatModel):
    """Bedrock LLM using Converse API (boto3)"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_id: str = Field(default=BEDROCK_MODEL)
    region_name: str = Field(default=REGION)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    client: object = Field(default=None)

    def __init__(self, model_id: str = BEDROCK_MODEL, region_name: str = REGION, **kwargs):
        super().__init__(
            model_id=model_id,
            region_name=region_name,
            client=boto3.client("bedrock-runtime", region_name=region_name),
            **kwargs
        )

    def _generate(self, messages, stop=None, **kwargs):
        """Generate response using Bedrock Converse API"""
        system_messages = []
        converse_messages = []

        for msg in messages:
            if msg.type == "system":
                system_messages.append({"text": msg.content})
            elif msg.type == "human":
                converse_messages.append({
                    "role": "user",
                    "content": [{"text": msg.content}],
                })
            elif msg.type == "ai":
                converse_messages.append({
                    "role": "assistant",
                    "content": [{"text": msg.content}],
                })

        try:
            logger.info(f"Invoking {self.model_id} via Converse API")

            # Ensure messages alternate between user/assistant
            cleaned_messages = []
            for msg in converse_messages:
                if not cleaned_messages or cleaned_messages[-1]["role"] != msg["role"]:
                    cleaned_messages.append(msg)
                else:
                    cleaned_messages[-1]["content"][0]["text"] += "\n" + msg["content"][0]["text"]

            # Must start with user message
            if cleaned_messages and cleaned_messages[0]["role"] != "user":
                cleaned_messages.insert(0, {"role": "user", "content": [{"text": "Continue."}]})

            # Must not be empty
            if not cleaned_messages:
                cleaned_messages = [{"role": "user", "content": [{"text": "Continue."}]}]

            request = {
                "modelId": self.model_id,
                "messages": cleaned_messages,
                "inferenceConfig": {
                    "maxTokens": self.max_tokens,
                    "temperature": self.temperature,
                },
            }

            if system_messages:
                request["system"] = system_messages

            response = self.client.converse(**request)

            content = response["output"]["message"]["content"][0]["text"]

            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=content))]
            )

        except Exception as e:
            logger.error(f"Error invoking Bedrock: {str(e)}")
            raise

    @property
    def _llm_type(self):
        return "bedrock-converse"

    @property
    def _identifying_params(self):
        return {"model_id": self.model_id, "region": self.region_name}


def get_llm(model_id: str = BEDROCK_MODEL):
    """Get Bedrock LLM instance using Converse API"""
    logger.info(f"Creating BedrockLLM with model_id={model_id}, region={REGION}")
    return BedrockLLM(
        model_id=model_id,
        region_name=REGION,
        temperature=0.7,
        max_tokens=2000,
    )


def get_model_for_agent(agent_name: str) -> str:
    """Get model override for specific agent"""
    return BEDROCK_MODEL


def get_bedrock_client():
    """Get raw Bedrock client for KB operations"""
    return boto3.client("bedrock-runtime", region_name=REGION)
