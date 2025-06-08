# GitHub Trending Web Application

This web application scrapes data from the GitHub trending page and provides a user interface to explore trending repositories.

## Features
- List trending repositories, filterable by language and stars
- Detailed page for each repository with historical trend charts (stars/rank over time)
- Search functionality by repository name or owner
- View current and past weekly trending lists

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/github-trending.git
   cd github-trending
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Initialize the database with initial data:**
   ```bash
   python init_db.py
   ```

4. **Run the application:**
   ```bash
   export FLASK_APP=app.py
   flask run --host=0.0.0.0 --port=51780
   ```

5. **Access the web application:**
   Open your browser and go to http://localhost:51780

## Background Tasks

The application uses a simple scheduler to scrape GitHub trending data every day at midnight. The scraped data is stored in an SQLite database.

## Project Structure

- `app.py`: Main Flask application
- `app/models/`: Database models (Repository, Trend)
- `app/scrapers/`: Web scraping logic for GitHub trending page
- `app/templates/`: HTML templates
- `app/static/`: Static files (CSS, JS)
- `init_db.py`: Script to initialize the database with initial data

## Dependencies

- Flask: Web framework
- SQLAlchemy: ORM for database interactions
- BeautifulSoup4: HTML parsing library
- Requests: HTTP requests library
- Schedule: Job scheduling library