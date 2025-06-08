import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session

# Import models from the app package
from app import Repository, Trend

GITHUB_TRENDING_URL = "https://github.com/trending?since=weekly"

def scrape_github_trending():
    response = requests.get(GITHUB_TRENDING_URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch GitHub trending page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    repo_list = []

    # Find all repository containers
    repo_containers = soup.find_all('article', class_='Box-row')

    for container in repo_containers:
        try:
            # Skip sponsor cards
            if container.get('data-testid') == 'sponsor-card':
                continue

            # Extract rank - it's the number of stars this week (third link)
            repo_info_links = container.find_all('a', class_='Link--muted d-inline-block mr-3')
            if len(repo_info_links) >= 2:
                # Second link is usually "stars this week"
                stars_text = repo_info_links[1].text.strip()
                star_count = ''.join([c for c in stars_text if c.isdigit()])
                rank = int(star_count)
            else:
                rank = None

            # Extract repository info - full name and URL
            # Find the h2 tag with the repo name (usually contains owner/repo format)
            h2_tag = container.find('h2')
            if not h2_tag or not h2_tag.find('a'):
                continue  # Skip if no link found in h2

            # Extract full name and URL
            repo_link = h2_tag.find('a')
            repo_url = f"https://github.com{repo_link['href']}"

            # Clean up the name (remove newlines and extra spaces)
            raw_name = repo_link.text.strip()
            # The format is usually "owner /\n\n      repo"
            if ' /' in raw_name:
                name_parts = raw_name.split(' /')
                owner = name_parts[0].strip()
                repo = name_parts[1].strip().split('\n')[0].strip()  # Remove newlines
                name = f"{owner}/{repo}"
            else:
                name = raw_name

            # Extract description
            description_p = container.find('p', class_='col-9')
            if not description_p:
                description_p = container.find('p', class_='color-fg-muted')

            description = description_p.text.strip() if description_p else ''

            # Extract language - might be in a span with specific classes
            language_span = None
            for span in container.find_all('span'):
                if 'itemprop' in span.attrs and span['itemprop'] == 'programmingLanguage':
                    language_span = span
                    break

            language = language_span.text.strip() if language_span else None

            # Extract stars (total) and forks from the container
            # Look for star count - usually in a span with specific classes
            stars = None  # Use None as default to indicate we need to find it
            for span in container.find_all('a'):
                if 'stargazers' in span.get('href', ''):
                    stars_text = span.text.strip()
                    star_count = ''.join([c for c in stars_text if c.isdigit()])
                    stars = int(star_count)
                    break  # Found the star count, no need to continue

            # If we couldn't find a specific star count link, try to get it from any text
            if stars is None:
                for text in container.stripped_strings:
                    if 'k' in text and ('star' in text.lower() or 'stars' in text.lower()):
                        star_count = ''.join([c for c in text if c.isdigit()])
                        # Handle "1.2k" format
                        if '.' in star_count:
                            parts = star_count.split('.')
                            star_count = str(int(parts[0]) * 1000 + int(parts[1]))
                        stars = int(star_count)
                        break

            # If we still don't have a star count, default to 0 (but we'll filter these out later)
            if stars is None:
                stars = 0

            # Look for fork count - usually in a span with specific classes
            forks = None  # Use None as default to indicate we need to find it
            for span in container.find_all('a'):
                if 'forks' in span.get('href', ''):
                    forks_text = span.text.strip()
                    fork_count = ''.join([c for c in forks_text if c.isdigit()])
                    forks = int(fork_count)
                    break  # Found the fork count, no need to continue

            # If we couldn't find a specific fork count link, try to get it from any text
            if forks is None:
                for text in container.stripped_strings:
                    if 'k' in text and ('fork' in text.lower() or 'forks' in text.lower()):
                        fork_count = ''.join([c for c in text if c.isdigit()])
                        # Handle "1.2k" format
                        if '.' in fork_count:
                            parts = fork_count.split('.')
                            fork_count = str(int(parts[0]) * 1000 + int(parts[1]))
                        forks = int(fork_count)
                        break

            # If we still don't have a fork count, default to 0
            if forks is None:
                forks = 0

            # Add to our list
            repo_list.append({
                'rank': rank,
                'name': name,
                'url': repo_url,
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks
            })
        except Exception as e:
            print(f"Error processing repository: {e}")
            continue  # Skip this repo and continue with the next one

    return repo_list

def update_database_from_scrape(db: Session):
    # Get current date
    today = datetime.now().date()

    # First, scrape the latest data
    repositories = scrape_github_trending()

    if not repositories:
        print("No repositories found to update")
        return

    # Create a dictionary of existing repos by URL for quick lookup
    existing_repos = {repo.url: repo for repo in db.query(Repository).all()}

    # Filter out repositories with zero stars (likely incomplete data)
    valid_repositories = [repo for repo in repositories if repo['stars'] > 0]

    print(f"Found {len(repositories)} repositories, filtering out {len(repositories) - len(valid_repositories)} with 0 stars")

    # Process each scraped repository
    for repo_data in valid_repositories:
        repo_url = repo_data['url']

        if repo_url in existing_repos:
            # Update existing repository with new star count
            repo = existing_repos[repo_url]
            repo.stars = repo_data['stars']
            repo.forks = repo_data['forks']
        else:
            # Create a new repository entry
            repo = Repository(
                name=repo_data['name'],
                description=repo_data['description'],
                language=repo_data['language'],
                stars=repo_data['stars'],
                forks=repo_data['forks'],
                url=repo_url
            )
            db.add(repo)
            # Make sure the repository is saved and has an ID before adding trends
            db.flush()

        # Add or update trend data
        if repo.id:  # Only add trend if repository has been properly saved
            trend = Trend(
                repository_id=repo.id,
                rank=repo_data['rank'],
                date=today
            )
            db.add(trend)

    # Commit all changes to the database
    try:
        db.commit()
        print(f"Successfully updated database with {len(repositories)} repositories")
    except Exception as e:
        db.rollback()
        print(f"Error updating database: {e}")