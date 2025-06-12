from flask import Blueprint, render_template, request

# Create blueprints
repository_bp = Blueprint('repository', __name__)
trending_history_bp = Blueprint('trending_history', __name__)
trending_compare_bp = Blueprint('trending_compare', __name__)
from sqlalchemy.sql import func
from datetime import datetime
from .models.repository import Repository
from .models.trend import Trend
from sqlalchemy.orm import scoped_session, sessionmaker
# Import database configuration from .database
from .database import engine, SessionLocal

@repository_bp.route('/repository/<int:repo_id>')
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

@repository_bp.route('/run_tasks')
def run_tasks():
    from app.scheduler import run_scheduled_tasks
    run_scheduled_tasks()
    return "Scheduled tasks executed", 200

@trending_compare_bp.route('/trending/compare')
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

@trending_history_bp.route('/trending/history')
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
            subquery = session.query(
                Trend.repository_id,
                func.max(Trend.id).label('max_trend_id')
            ).filter(Trend.date == selected_date).group_by(Trend.repository_id).subquery()

            query = session.query(Repository).join(
                Trend, Repository.id == Trend.repository_id
            ).filter(
                Trend.id == subquery.c.max_trend_id
            )
        except ValueError:
            # If date format is invalid, show error message and all repositories with trends
            return render_template('history.html',
                                  repositories=[],
                                  selected_date=None,
                                  date_options=[],  # We need to get this from the database
                                  search_query=search_query,
                                  languages=[],  # We need to get this from the database
                                  error_message="Invalid date format. Please use YYYY-MM-DD.")
    else:
        # Get the most recent trend data for each repository
        subquery = session.query(
            Trend.repository_id,
            func.max(Trend.date).label('max_date')
        ).group_by(Trend.repository_id).subquery()

        query = session.query(Repository).join(
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
            pass  # Ignore invalid values

    repositories = query.all()

    # Now get the trend data for these repositories
    repo_ids = [repo.id for repo in repositories]
    trends = {}

    if selected_date:
        trend_query = session.query(Trend).filter(
            Trend.repository_id.in_(repo_ids),
            Trend.date == selected_date
        ).all()
    else:
        # Get the most recent trend for each repository
        trend_subquery = session.query(
            Trend.repository_id,
            func.max(Trend.date).label('max_date')
        ).filter(Trend.repository_id.in_(repo_ids)).group_by(Trend.repository_id).subquery()

        trend_query = session.query(Trend).join(
            trend_subquery,
            (Trend.repository_id == trend_subquery.c.repository_id) &
            (Trend.date == trend_subquery.c.max_date)
        ).all()

    # Organize trends by repository ID
    for trend in trend_query:
        trends[trend.repository_id] = trend

    # Get all unique dates with trend data for the dropdown filter
    dates = session.query(Trend.date.distinct()).order_by(Trend.date.desc()).all()
    date_options = [date[0] for date in dates]

    # Get unique languages for filter dropdown
    languages = session.query(Repository.language).distinct().all()
    languages = sorted([lang[0] for lang in languages if lang[0] is not None])

    session.close()

    return render_template('history.html',
                          repositories=repositories,
                          trends=trends,  # Pass trends separately
                          selected_date=selected_date,
                          date_options=date_options,
                          search_query=search_query,
                          languages=languages)