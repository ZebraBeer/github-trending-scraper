# GitHub Trending Repositories Scraper

This is a web application that scrapes and displays trending repositories from GitHub.

## Features

- Periodically scrapes the current list of trending repositories from GitHub
- Displays trending repositories with filtering by language and stars
- Detailed page for each repository including historical trend charts (stars over time)
- Search functionality by repository name or owner
- Option to view current and past weekly trending lists:
  - View most recent trends
  - Filter by specific dates to see which repositories were trending on those days
  - Advanced filtering options in history page (language, minimum stars)
  - Search functionality within historical data
- Side-by-side comparison of trend charts for different repositories

## Setup Instructions

**Note:** If you encounter a Server Error 500 when running the application, it's likely due to database path issues. Make sure you're using the correct database path in `app/database.py` and that the directory exists with proper permissions.

### Using Docker Compose (Recommended)

The easiest way to run this application is using Docker Compose:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ZebraBeer/github-trending-scraper.git
   cd github-trending-scraper
   ```

2. **Run with Docker Compose:**

   ```bash
   docker-compose up -d
   ```

3. **Access the application:**

   If you encounter a "Server Error 500" after starting with Docker, it's likely due to database initialization issues. The Dockerfile now includes steps to create the database directory and initialize the database schema.

   Open your browser and go to http://localhost:8000

### Manual Setup (Without Docker)

If you prefer not to use Docker, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ZebraBeer/github-trending-scraper.git
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

   You can run the application using Flask's built-in server or directly with Python.
   The default port is 8000, but you can specify a different port using the PORT environment variable.

   Using Flask CLI:
   ```bash
   export FLASK_APP=app.py
   flask run --host=0.0.0.0 --port=8000
   ```

   Or directly with Python:
   ```bash
   python app.py
   ```

5. **Access the application:**

   Open your browser and go to http://localhost:8000 (or the port you specified)

## Background Tasks

The application uses a scheduler to periodically update repository data. The scheduler runs every day at midnight by default.

When you start the application, the scheduler runs in a separate thread automatically. You don't need to manually start it.

You can manually run the scheduled tasks for testing:

```bash
python -c "from app.scheduler import run_scheduled_tasks; run_scheduled_tasks()"
```

## How It Works

1. **Data Scraping**: The application uses web scrapers to extract data from GitHub's trending page.
2. **Database Storage**: Repository information is stored in a SQLite database for persistence.
3. **Scheduling**: A scheduler periodically updates the repository data to keep it current.
4. **Web Interface**: A Flask-based web interface displays the trending repositories with filtering and search capabilities.

## Project Structure

- `app/main.py`: Main Flask application
- `app/models/`: Database models (Repository, Trend)
  - `repository.py`: Repository model definition
  - `trend.py`: Trend data model definition
- `app/scrapers/`: Web scrapers to extract data from GitHub
  - `github_scraper.py`: Main scraper implementation
- `app/templates/`: HTML templates for the web interface
  - `index.html`: Home page template
  - `repository_detail.html`: Detailed repository view template
  - `history.html`: Template for viewing historical trending data
  - `compare.html`: Template for comparing trends between repositories
- `app/scheduler.py`: Scheduling logic to periodically update data
- `init_db.py`: Script to initialize the database
- `requirements.txt`: Python dependencies
- `Dockerfile`: Docker configuration for containerization
- `.dockerignore`: Files and directories to exclude from Docker build
- `docker-compose.yml`: Docker Compose configuration for easy deployment

## License

This project is open source and available under the MIT License.