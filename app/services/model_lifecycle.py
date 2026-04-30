import os
import json
import time

class ModelLifecycleManager:
    """
    Manages model versioning and performance metrics tracking.
    Simulates MLflow functionality for the project context.
    """
    def __init__(self, log_dir="instance/model_logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.current_version = "v1.2.0-beta"

    def log_metrics(self, resume_id, job_id, metrics):
        """Log evaluation metrics for a specific match."""
        log_file = os.path.join(self.log_dir, "evaluation_metrics.jsonl")
        log_entry = {
            "timestamp": time.time(),
            "model_version": self.current_version,
            "resume_id": resume_id,
            "job_id": job_id,
            "metrics": metrics
        }
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to log metrics: {e}")

lifecycle_manager = ModelLifecycleManager()
