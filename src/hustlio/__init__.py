import django
django.setup()

# -------- API Funcs -------
from stock_updater import update_db
from scheduler import run_continuously
import schedule
from data_gen import gen_data

# Generate randomised users
#gen_data(50)


# Every 12 hours starting from the time the script is executed.
schedule.every(30).seconds.do(update_db)

# Run this to force update:
#update_db()

# Start the background thread
stop_run_continuously = run_continuously()
