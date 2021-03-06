import threading
import time

import schedule


def run_continuously(interval=1):
    # This is from https://schedule.readthedocs.io/
    # Allows us to run a scheduled task in the background of the server via threading
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()
    return cease_continuous_run

