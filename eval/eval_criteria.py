from deepeval.metrics import GEval
from deepeval.models import AmazonBedrockModel
from deepeval.test_case import LLMTestCaseParams

def build_correctness_metric():

    judge_model = AmazonBedrockModel(
        model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        region="us-east-1",
        generation_kwargs={"temperature": 0.0, "maxTokens": 1024},
    )

     # Steps the judge follows when scoring
    steps = [
            "1. Check if the actual output contains the key information from expected output.",
            "2. Check if the actual output contradicts any facts in expected output.",
            "3. Extra information beyond expected output is acceptable.",
            "4. If all key information is present and nothing is contradicted, score high."
    ]

    metric = GEval(
        name="Correctness",
        criteria="Is the actual output correct based on expected output?",
        evaluation_steps=steps,
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT
        ],
        threshold=0.7, #Pass if score >0.7
        model=judge_model
    )

    return metric


