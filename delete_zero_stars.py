#!/usr/bin/env python3
from sqlalchemy import create_engine
from app.models.repository import Repository
from app.models.trend import Trend
from sqlalchemy.orm import sessionmaker

# Set up database connection
engine = create_engine('sqlite:///./github_trending.db')
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Find and delete repositories with 0 stars
zero_star_repos = session.query(Repository).filter_by(stars=0).all()
for repo in zero_star_repos:
    print(f'Deleting repo {repo.name} with 0 stars')
    # First delete related trends to avoid foreign key constraint errors
    session.query(Trend).filter_by(repository_id=repo.id).delete()
    # Then delete the repository itself
    session.delete(repo)

# Commit changes
session.commit()
print("Database cleaned successfully")