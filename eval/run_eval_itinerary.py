import sys
import csv
import time

sys.path.insert(0, ".")

from deepeval.test_case import LLMTestCase
from langchain_core.messages import HumanMessage, SystemMessage

from utils.bedrock_client import get_llm
from utils.prompt_loader import load_system_prompt

sys.path.insert(0, "../eval")
from eval_criteria import build_correctness_metric
from eval_tracker import EvalTracker



def get_itinerary_response(user_input):
    """Run itinerary_planner and get response with token usage"""

    llm = get_llm()
    prompt = load_system_prompt("itinerary_planner")

    messages = []
    if prompt.strip():
        messages.append(SystemMessage(prompt))
    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)

    # Extract token usage
    tokens = {"input": 0, "output": 0}
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        tokens["input"] = response.usage_metadata.get("input_tokens", 0)
        tokens["output"] = response.usage_metadata.get("output_tokens", 0)
    elif hasattr(response, "response_metadata"):
        usage = response.response_metadata.get("usage", {})
        tokens["input"] = usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
        tokens["output"] = usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)

    return response.content, tokens


def load_goldens():
    """Load test cases from CSV"""

    test_cases = []
    with open("../eval/goldens_itinerary.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            test_cases.append({
                "input": row["input"],
                "expected_output": row["expected_output"]
            })
    return test_cases


def run_eval():

    print("\n" + "=" * 60)
    print("  RUNNING ITINERARY PLANNER EVALUATION")
    print("=" * 60)

    goldens = load_goldens()
    print(f"\nLoaded {len(goldens)} test cases")

    metric = build_correctness_metric()

    tracker = EvalTracker()
    tracker.start_run(description="itinerary_planner_eval")

    scores = []
    rouge_scores = []
    latencies = []
    all_tokens = []
    start_time = time.time()

    for i, golden in enumerate(goldens):
        print(f"\n--- Test {i+1}/{len(goldens)} ---")
        print(f"Input: {golden['input'][:50]}...")

        start = time.time()
        actual_output, tokens = get_itinerary_response(golden["input"])
        duration = time.time() - start

        print(f"Response: {actual_output[:80]}...")
        print(f"Time: {duration:.1f}s")
        print(f"Tokens: input={tokens['input']}, output={tokens['output']}")

        # GEval correctness score
        test_case = LLMTestCase(
            input=golden["input"],
            actual_output=actual_output,
            expected_output=golden["expected_output"]
        )
        metric.measure(test_case)
        score = metric.score
        print(f"Correctness: {score}")
        print(f"Reason: {metric.reason}")


        # Collect results
        scores.append(score)
        rouge_scores.append(rouge)
        latencies.append(duration)
        all_tokens.append(tokens)

        # Log per-question metrics
        tracker.log_latency(i, duration)
        tracker.log_token_usage(i, tokens)

    # Log summaries
    total_duration = time.time() - start_time

    tracker.log_scores_direct(scores)
    tracker.log_latency_summary(latencies)

    tracker.log_token_summary(all_tokens)
    tracker.log_duration(total_duration)
    tracker.end_run()

    # Print summary
    avg = sum(scores) / len(scores) if scores else 0
    passed = sum(1 for s in scores if s >= 0.7)
    total_tokens = sum(t["input"] + t["output"] for t in all_tokens)

    print("  RESULTS")
    print("=" * 60)
    print(f"  Correctness Avg: {avg:.2f}")
    print(f"  Pass Rate:       {passed}/{len(scores)}")
    print(f"  Total Tokens:    {total_tokens}")
    print(f"  Avg Latency:     {sum(latencies)/len(latencies):.1f}s")
    print(f"  Duration:        {total_duration:.1f}s")
    print(f"  Saved to MLflow")
    print("=" * 60)


if __name__ == "__main__":
    run_eval()
