import schedule
import time
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.scrapers.github_scraper import update_database_from_scrape

def job():
    print("Starting scheduled scrape...")
    db = SessionLocal()
    try:
        update_database_from_scrape(db)
        print("Scrape completed successfully.")
    except Exception as e:
        print(f"Error during scrape: {e}")
    finally:
        db.close()

# Schedule the job every day at midnight
schedule.every().day.at("00:00").do(job)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to run all pending scheduled tasks immediately (for testing)
def run_scheduled_tasks():
    print("Running all pending scheduled tasks...")
    job()  # Run the scrape job directly