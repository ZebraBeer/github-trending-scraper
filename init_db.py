from app.database import engine, SessionLocal, Base
from app.scrapers.github_scraper import update_database_from_scrape

def main():
    print("Initializing database...")
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Scrape and populate the database with initial data
        update_database_from_scrape(db)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()