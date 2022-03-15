import django
django.setup()

# -------- API Funcs -------
from stock_updater import update_db
from scheduler import run_continuously
import schedule

# Every 12 hours starting from the time the script is executed.
schedule.every(5).minutes.do(update_db)

# Run this to force update:
#update_db()

# Start the background thread
stop_run_continuously = run_continuously()
