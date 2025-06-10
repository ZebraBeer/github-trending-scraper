from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func, distinct as DISTINCT
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

@app.route('/trending/compare')
def trending_compare():
    session = SessionLocal()
    repo_id1 = request.args.get('repo1')
    repo_id2 = request.args.get('repo2')

    # Get repository details
    repo1 = None
    repo2 = None

    if repo_id1:
        repo1 = session.query(Repository).get(repo_id1)
        if not repo1:
            return "Repository 1 not found", 404

    if repo_id2:
        repo2 = session.query(Repository).get(repo_id2)
        if not repo2:
            return "Repository 2 not found", 404

    # Get trend data for both repositories
    trends1 = []
    dates = []

    if repo1:
        trends1 = session.query(Trend).filter_by(repository_id=repo1.id).order_by(Trend.date.asc()).all()
        dates = [trend.date.strftime('%Y-%m-%d') for trend in trends1]

    trends2 = []
    stars2 = []

    if repo2:
        trends2 = session.query(Trend).filter_by(repository_id=repo2.id).order_by(Trend.date.asc()).all()
        stars2 = [trend.stars if trend is not None else 0 for trend in trends2]

    # Get all repositories for dropdown selection
    repos = session.query(Repository).all()

    session.close()

    return render_template('compare.html',
                          repo1=repo1,
                          repo2=repo2,
                          dates=dates,
                          stars1=[trend.stars if trend is not None else 0 for trend in trends1],
                          stars2=stars2,
                          repositories=repos)

@app.route('/trending/history')
def trending_history():
    session = SessionLocal()
    selected_date = request.args.get('date')
    search_query = request.args.get('search', '')
    language_filter = request.args.get('language', '')
    min_stars = request.args.get('min_stars', '')

    # Build base query
    if selected_date:
        try:
            # Parse the date from string to datetime.date object
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

            # Get repositories and their trend data for the selected date
            # Use DISTINCT to avoid duplicate entries
            query = session.query(DISTINCT(Repository.id), Repository, Trend).join(
                Trend, Repository.id == Trend.repository_id
            ).filter(Trend.date == selected_date)
        except ValueError:
            # If date format is invalid, show all repositories with trends
            return render_template('history.html',
                                  repositories=[],
                                  selected_date=None,
                                  date_options=[],
                                  search_query=search_query,
                                  languages=[])
    else:
        # Get the most recent trend data for each repository
        subquery = session.query(
            Trend.repository_id,
            func.max(Trend.date).label('max_date')
        ).group_by(Trend.repository_id).subquery()

        query = session.query(Repository, Trend).join(
            Trend, Repository.id == Trend.repository_id
        ).filter(
            Trend.date == subquery.c.max_date,
            Trend.repository_id == subquery.c.repository_id
        )

    # Apply search filter if provided
    if search_query:
        query = query.filter(
            (Repository.name.ilike(f"%{search_query}%")) |
            (Repository.description.ilike(f"%{search_query}%"))
        )

    # Apply language filter if provided
    if language_filter:
        query = query.filter(Repository.language == language_filter)

    # Apply minimum stars filter if provided
    if min_stars:
        try:
            min_stars_int = int(min_stars)
            query = query.filter(Trend.stars >= min_stars_int)
        except ValueError:
            pass  # Invalid value, ignore

    repositories = query.all()

    # Get all unique dates with trend data for the dropdown filter
    dates = session.query(Trend.date.distinct()).order_by(Trend.date.desc()).all()
    date_options = [date[0] for date in dates]

    # Get unique languages for filter dropdown
    languages = session.query(Repository.language).distinct().all()
    languages = sorted([lang[0] for lang in languages if lang[0] is not None])

    session.close()

    return render_template('history.html',
                          repositories=repositories,
                          selected_date=selected_date,
                          date_options=date_options,
                          search_query=search_query,
                          languages=languages)

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
    port = int(os.environ.get('PORT', 8000))  # Using a different port
    app.run(host='0.0.0.0', port=port, debug=False)