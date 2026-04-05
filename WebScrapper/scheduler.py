import asyncio
import logging
import schedule
import time
from scrap import main


logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def job():
    logging.info("Scraper job started")
    try:
        asyncio.run(main())
        logging.info("Scraper job finished successfully")
    except Exception as e:
        logging.error(f"Scraper job failed: {e}")

if __name__ == "__main__":
    logging.info("Scheduler started — running daily at midnight")

    schedule.every().day.at("00:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)