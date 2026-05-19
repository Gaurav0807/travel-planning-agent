import mlflow
import time
from datetime import datetime


class EvalTracker:
    """Tracks evaluation results in MLflow"""

    def __init__(self, experiment_name="travel-agent-evals"):
        # Set up MLflow (stores in SQLite database)
        mlflow.set_tracking_uri("sqlite:////Users//Travel-planning-agent/eval/mlflow.db")
        mlflow.set_experiment(experiment_name)

    def start_run(self, description=""):
        """Start a new tracking run"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{description}_{timestamp}" if description else timestamp

        mlflow.start_run(run_name=run_name)

        # Log basic info
        mlflow.log_param("description", description)
        mlflow.log_param("timestamp", timestamp)
        mlflow.log_param("model", "us.anthropic.claude-haiku-4-5-20251001-v1:0")

    def log_scores(self, test_results):
        """Log scores from DeepEval results"""
        # Try to extract scores from results
        scores = []
        if hasattr(test_results, 'test_results'):
            for i, result in enumerate(test_results.test_results):
                score = result.metrics[0].score if result.metrics else 0
                mlflow.log_metric(f"score_q{i}", score)
                scores.append(score)
        self._log_summary(scores)

    def log_scores_direct(self, scores):
        """Log scores directly from a list"""
        for i, score in enumerate(scores):
            mlflow.log_metric(f"score_q{i}", score)
        self._log_summary(scores)

    def _log_summary(self, scores):
        """Log summary metrics"""
        if scores:
            avg_score = sum(scores) / len(scores)
            pass_count = sum(1 for s in scores if s >= 0.7)
            fail_count = len(scores) - pass_count
            pass_rate = pass_count / len(scores)

            mlflow.log_metric("avg_score", round(avg_score, 3))
            mlflow.log_metric("pass_rate", round(pass_rate, 3))
            mlflow.log_metric("pass_count", pass_count)
            mlflow.log_metric("fail_count", fail_count)
            mlflow.log_metric("total_tests", len(scores))

    def log_duration(self, duration_seconds):
        """Log how long the eval took"""
        mlflow.log_metric("eval_duration_seconds", round(duration_seconds, 1))

    def log_latency(self, index, duration):
        """Log per-question latency"""
        mlflow.log_metric(f"latency_q{index}", round(duration, 2))

    def log_latency_summary(self, latencies):
        """Log latency stats (mean, min, max, p95)"""
        if not latencies:
            return
        sorted_lat = sorted(latencies)
        mlflow.log_metric("latency_mean", round(sum(sorted_lat) / len(sorted_lat), 2))
        mlflow.log_metric("latency_min", round(sorted_lat[0], 2))
        mlflow.log_metric("latency_max", round(sorted_lat[-1], 2))
        # P95
        p95_index = int(len(sorted_lat) * 0.95)
        mlflow.log_metric("latency_p95", round(sorted_lat[min(p95_index, len(sorted_lat) - 1)], 2))

    def log_rouge_scores(self, index, rouge):
        """Log ROUGE-1 scores for a question"""
        mlflow.log_metric(f"rouge1_recall_q{index}", rouge["recall"])
        mlflow.log_metric(f"rouge1_precision_q{index}", rouge["precision"])
        mlflow.log_metric(f"rouge1_f1_q{index}", rouge["f1"])


    def log_token_usage(self, index, tokens):
        """Log token usage for a question"""
        mlflow.log_metric(f"tokens_input_q{index}", tokens.get("input", 0))
        mlflow.log_metric(f"tokens_output_q{index}", tokens.get("output", 0))

    def log_token_summary(self, all_tokens):
        """Log total token usage"""
        if not all_tokens:
            return
        total_input = sum(t.get("input", 0) for t in all_tokens)
        total_output = sum(t.get("output", 0) for t in all_tokens)
        mlflow.log_metric("tokens_input_total", total_input)
        mlflow.log_metric("tokens_output_total", total_output)
        mlflow.log_metric("tokens_total", total_input + total_output)

    def end_run(self):
        """End the tracking run"""
        mlflow.end_run()