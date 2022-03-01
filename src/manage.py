#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


# -------- API Funcs -------
from update_stocks import update_stocks

# -------- Scheduling Modules ---------
from scheduler import run_continuously
import schedule

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hustlio.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    schedule.every().second.do(update_stocks())

    # Start the background thread
    stop_run_continuously = run_continuously()

    # Do some other things...
    for i in range(0, 10):
        print("test")
        time.sleep(1)
    # Stop the background thread
    stop_run_continuously.set()
    main()
