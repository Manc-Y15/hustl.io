import django
django.setup()

# -------- API Funcs -------
from stock_updater import update_stocks
from scheduler import run_continuously
import schedule

# Every 12 hours starting from the time the script is executed.
schedule.every(12).hours.do(update_stocks)

# Run this to force update:
# update_stocks()

# Start the background thread
stop_run_continuously = run_continuously()
