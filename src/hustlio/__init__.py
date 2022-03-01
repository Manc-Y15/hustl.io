import django
django.setup()

# -------- API Funcs -------
from stock_updater import update_stocks
from scheduler import run_continuously
import schedule
schedule.every(12).hours.do(update_stocks)

# Start the background thread
stop_run_continuously = run_continuously()
