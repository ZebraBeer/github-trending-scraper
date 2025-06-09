from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func
import os
from datetime import datetime

app = Flask(__name__, template_folder='app/templates')
app.config['SECRET_KEY'] = 'your_secret_key'

# Database setup
DATABASE_URL = "sqlite:///./github_trending.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

# Import models after Base is defined
from app.models.repository import Repository
from app.models.trend import Trend

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    session = SessionLocal()
    search_query = request.args.get('search', '')
    language_filter = request.args.get('language', '')

    # Build query based on filters
    query = session.query(Repository)

    if search_query:
        query = query.filter(
            (Repository.name.ilike(f"%{search_query}%")) |
            (Repository.url.ilike(f"%{search_query}%"))
        )

    if language_filter:
        query = query.filter(Repository.language == language_filter)

    repositories = query.all()
    session.close()

    # Get unique languages for filter dropdown
    languages = session.query(Repository.language).distinct().all()
    languages = sorted([lang[0] for lang in languages if lang[0] is not None])

    return render_template('index.html', repositories=repositories, languages=languages)

@app.route('/repository/<int:repo_id>')
def repository_detail(repo_id):
    session = SessionLocal()

    # Get repository details
    repo = session.query(Repository).get(repo_id)

    if not repo:
        session.close()
        return "Repository not found", 404

    # Get trend data for this repository
    trends = session.query(Trend).filter_by(repository_id=repo.id).order_by(Trend.date.asc()).all()

    # Convert to dictionaries for charting
    trend_data = {
        'dates': [trend.date.strftime('%Y-%m-%d') for trend in trends],
        'stars': [trend.stars if trend.stars is not None else 0 for trend in trends]
    }

    session.close()

    return render_template('repository_detail.html', repo=repo, trend_data=trend_data)

@app.route('/run_tasks')
def run_tasks():
    from app.scheduler import run_scheduled_tasks
    run_scheduled_tasks()
    return "Scheduled tasks executed", 200

@app.route('/trending/history')
def trending_history():
    session = SessionLocal()
    selected_date = request.args.get('date')

    # If a specific date is selected, filter by that date
    if selected_date:
        try:
            # Parse the date from string to datetime.date object
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

            # Get repositories and their trend data for the selected date
            query = session.query(Repository, Trend).join(
                Trend, Repository.id == Trend.repository_id
            ).filter(Trend.date == selected_date)

            repositories = query.all()
        except ValueError:
            # If date format is invalid, show all repositories with trends
            repositories = []
    else:
        # Get the most recent trend data for each repository
        subquery = session.query(
            Trend.repository_id,
            func.max(Trend.date).label('max_date')
        ).group_by(Trend.repository_id).subquery()

        query = session.query(Repository, Trend).join(
            Trend, Repository.id == Trend.repository_id
        ).join(
            subquery, (Trend.repository_id == subquery.c.repository_id) &
                      (Trend.date == subquery.c.max_date)
        )

        repositories = query.all()

    # Get all unique dates with trend data for the dropdown filter
    dates = session.query(Trend.date.distinct()).order_by(Trend.date.desc()).all()
    date_options = [date[0] for date in dates]

    session.close()

    return render_template('history.html', repositories=repositories, selected_date=selected_date, date_options=date_options)

import threading

def run_scheduler():
    from app.scheduler import run_scheduler
    run_scheduler()

if __name__ == '__main__':
    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Get the port from environment variable or use default
    import os
    port = int(os.environ.get('PORT', 56568))  # Using a different port
    app.run(host='0.0.0.0', port=port)