from collections import deque
import threading
import time
import sched

class ExpiringMetricQueue:
    def __init__(self, expiry_seconds=60, cleanup_interval=5):
        self.queue = deque()
        self.expiry_seconds = expiry_seconds
        self.cleanup_interval = cleanup_interval
        self.lock = threading.Lock()
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self._start_cleanup()
    
    def put(self, metric):
        metric['timestamp'] = time.time()
        with self.lock:
            self.queue.append(metric)
    
    def pop_all(self):
        with self.lock:
            items = list(self.queue)
            self.queue.clear()
            cleaned_items = []
            for item in items:
                cleaned_item = {k: v for k, v in item.items() if k != 'timestamp'}
                cleaned_items.append(cleaned_item)

            return cleaned_items
    
    def _start_cleanup_thread(self):
        thread = threading.Thread(target=self._cleanup, daemon=True)
        thread.start()
    
    def _start_cleanup(self):
        def scheduled_cleanup():
            self._cleanup()
            # Schedule next run
            self.scheduler.enter(self.cleanup_interval, 1, scheduled_cleanup)

        # Schedule first run immediately
        self.scheduler.enter(0, 1, scheduled_cleanup)
        threading.Thread(target=self.scheduler.run, daemon=True).start()

    def _cleanup(self):
        current_time = time.time()
        with self.lock:
            original_len = len(self.queue)
            self.queue = deque(
                [item for item in self.queue if current_time - item['timestamp'] <= self.expiry_seconds]
            )
            cleaned = original_len - len(self.queue)
            if cleaned > 0:
                print(f"[MetricQueue] Cleaned {cleaned} expired metrics")

metric_queue = ExpiringMetricQueue(expiry_seconds=60, cleanup_interval=60)