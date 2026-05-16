import schedule
import time
from dotenv import load_dotenv

load_dotenv("/home/danieljoe903/PEA_bridge/.env")

from pkg import create_app
from pkg.task import check_expired_properties

app = create_app()

schedule.every(5).minutes.do(check_expired_properties, app)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)