import schedule
import time
from pkg import create_app
from pkg.task import check_expired_properties
from dotenv import load_dotenv

load_dotenv()

app = create_app()

schedule.every(5).minutes.do(check_expired_properties,app)

while True:
    schedule.run_pending()
    time.sleep(1)