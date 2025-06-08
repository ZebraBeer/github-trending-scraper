# GitHub Trending Repositories Scraper

This is a web application that scrapes and displays trending repositories from GitHub.

## Features

- Periodically scrapes the current list of trending repositories from GitHub
- Displays trending repositories with filtering by language and stars
- Detailed page for each repository including historical trend charts
- Search functionality by repository name or owner
- Option to view current and past weekly trending lists

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/openhandsai/github-trending-scraper.git
   cd github-trending-scraper
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Initialize the database:**

   ```bash
   python init_db.py
   ```

4. **Run the application:**

   ```bash
   export FLASK_APP=app.py
   flask run --host=0.0.0.0 --port=51780
   ```

5. **Access the application:**

   Open your browser and go to http://localhost:51780

## Background Tasks

The application uses a scheduler to periodically update repository data. The scheduler runs every day at midnight by default.

You can manually run the scheduled tasks for testing:

```bash
python -c "from app.scheduler import run_scheduled_tasks; run_scheduled_tasks()"
```

## Project Structure

- `app.py`: Main Flask application
- `app/models/`: Database models (Repository, Trend)
- `app/scrapers/`: Web scrapers to extract data from GitHub
- `app/templates/`: HTML templates for the web interface
- `init_db.py`: Script to initialize the database
- `requirements.txt`: Python dependencies

## License

This project is open source and available under the MIT License.