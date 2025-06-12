from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func, distinct as DISTINCT
import os
from datetime import datetime

def create_app():
    app = Flask(__name__, template_folder='/workspace/github-trending-scraper/app/templates')
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Import database configuration from .database
    from .database import engine, SessionLocal, Base

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

        # Get trend data for all repositories
        repo_ids = [repo.id for repo in repositories]
        trends_by_date = {}

        if repo_ids:
            # Get all trend dates for these repositories
            date_query = session.query(
                Trend.date.distinct()
            ).filter(Trend.repository_id.in_(repo_ids)).order_by(Trend.date.asc()).all()

            # For each date, get the star counts for all repositories
            for date in date_query:
                date_str = date[0].strftime('%Y-%m-%d')
                trends_by_date[date_str] = {}

                # Get trend data for this date
                trend_query = session.query(
                    Trend.repository_id,
                    Trend.stars
                ).filter(
                    Trend.date == date[0],
                    Trend.repository_id.in_(repo_ids)
                ).all()

                # Organize by repository ID
                for repo_id, stars in trend_query:
                    trends_by_date[date_str][repo_id] = stars

        session.close()

        # Get unique languages for filter dropdown
        languages = session.query(Repository.language).distinct().all()
        languages = sorted([lang[0] for lang in languages if lang[0] is not None])

        return render_template('index.html',
                               repositories=repositories,
                               languages=languages,
                               trends_by_date=trends_by_date)

    # Import and register blueprints
    from app.routes import repository_bp, trending_history_bp, trending_compare_bp
    app.register_blueprint(repository_bp)
    app.register_blueprint(trending_history_bp)
    app.register_blueprint(trending_compare_bp)

    return app

import threading

def run_scheduler():
    from app.scheduler import run_scheduler
    run_scheduler()

if __name__ == '__main__':
    # Create the app instance
    app = create_app()

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Get the port from environment variable or use default
    import os
    port = int(os.environ.get('PORT', 8000))  # Using a different port
    app.run(host='0.0.0.0', port=port, debug=False)
