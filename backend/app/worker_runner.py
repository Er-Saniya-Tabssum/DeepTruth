import time
from backend.app.worker import worker
from backend.app.config import settings

# Simple CLI to run worker loops for development

def run_worker_loop(poll_seconds: float | None = None):
    poll_seconds = settings.worker_poll_interval_seconds if poll_seconds is None else poll_seconds
    print(f"Starting analysis worker loop (poll={poll_seconds:.2f}s). Press Ctrl+C to stop.")
    try:
        while True:
            processed = worker.process_once()
            if processed:
                print(f"Processed analysis {processed}")
            time.sleep(poll_seconds)
    except KeyboardInterrupt:
        print("Worker loop stopped")

if __name__ == '__main__':
    run_worker_loop()
