"""
BEDROCK_CLIENT.PY - Talks to AWS Bedrock (Claude AI)

This sends messages to Claude and gets responses.
"""

import os
import boto3
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, ConfigDict

load_dotenv()

# Which Claude model to use
MODEL = os.getenv("BEDROCK_MODEL", "us.anthropic.claude-haiku-4-5-20251001-v1:0")
REGION = os.getenv("AWS_REGION", "us-east-1")


class BedrockLLM(BaseChatModel):
    """Sends messages to Claude via AWS Bedrock"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_id: str = Field(default=MODEL)
    region_name: str = Field(default=REGION)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    client: object = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(
            model_id=MODEL,
            region_name=REGION,
            client=boto3.client("bedrock-runtime", region_name=REGION),
            **kwargs
        )

    def _generate(self, messages, stop=None, **kwargs):
        """Send messages to Claude and get response"""

        # Separate system message from conversation
        system_messages = []
        chat_messages = []

        for msg in messages:
            if msg.type == "system":
                system_messages.append({"text": msg.content})
            elif msg.type == "human":
                chat_messages.append({
                    "role": "user",
                    "content": [{"text": msg.content}],
                })
            elif msg.type == "ai":
                chat_messages.append({
                    "role": "assistant",
                    "content": [{"text": msg.content}],
                })

        # Clean up messages (must alternate user/assistant)
        cleaned = []
        for msg in chat_messages:
            if not cleaned or cleaned[-1]["role"] != msg["role"]:
                cleaned.append(msg)
            else:
                # Merge if same role
                cleaned[-1]["content"][0]["text"] += "\n" + msg["content"][0]["text"]

        # Must start with user message
        if cleaned and cleaned[0]["role"] != "user":
            cleaned.insert(0, {"role": "user", "content": [{"text": "Continue."}]})

        if not cleaned:
            cleaned = [{"role": "user", "content": [{"text": "Hello"}]}]

        # Build request
        request = {
            "modelId": self.model_id,
            "messages": cleaned,
            "inferenceConfig": {
                "maxTokens": self.max_tokens,
                "temperature": self.temperature,
            },
        }

        if system_messages:
            request["system"] = system_messages

        # Call Claude
        response = self.client.converse(**request)

        # Get the text response
        content = response["output"]["message"]["content"][0]["text"]

        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=content))]
        )

    @property
    def _llm_type(self):
        return "bedrock"

    @property
    def _identifying_params(self):
        return {"model_id": self.model_id}


def get_llm():
    """Get a Claude instance"""
    return BedrockLLM()
