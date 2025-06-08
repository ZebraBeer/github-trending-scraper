import requests
from bs4 import BeautifulSoup

def debug_repo_container(container):
    """Print detailed information about a repository container for debugging"""
    print("\nDEBUG REPO CONTAINER:")
    print(f"Container type: {type(container)}")
    print(f"Container classes: {container.get('class', [])}")

    # Find and print all h1 tags
    h1_tags = container.find_all('h1')
    print(f"Found {len(h1_tags)} h1 tags:")
    for i, tag in enumerate(h1_tags):
        print(f"  h1[{i}]: {tag.text.strip()}")
        print(f"  h1[{i}] attributes: {tag.attrs}")

    # Find and print all h2 tags
    h2_tags = container.find_all('h2')
    print(f"Found {len(h2_tags)} h2 tags:")
    for i, tag in enumerate(h2_tags):
        print(f"  h2[{i}]: {tag.text.strip()}")
        print(f"  h2[{i}] attributes: {tag.attrs}")

    # Find and print all a tags
    a_tags = container.find_all('a')
    print(f"Found {len(a_tags)} a tags:")
    for i, tag in enumerate(a_tags[:5]):  # Limit to first 5 for brevity
        print(f"  a[{i}]: {tag.text.strip()}")
        print(f"  a[{i}] attributes: {tag.attrs}")

    # Find and print all p tags (descriptions)
    p_tags = container.find_all('p')
    print(f"Found {len(p_tags)} p tags:")
    for i, tag in enumerate(p_tags):
        print(f"  p[{i}]: {tag.text.strip()}")
        print(f"  p[{i}] attributes: {tag.attrs}")

if __name__ == "__main__":
    # Test the URL directly
    url = "https://github.com/trending?since=weekly"
    response = requests.get(url)
    print(f"Response status: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find repository containers - try different selectors
        repo_containers = soup.find_all('article', class_='Box-row')
        print(f"Found {len(repo_containers)} repository containers with selector 'article.Box-row'")

        if not repo_containers:
            # Try other common container elements
            repo_containers = soup.find_all('div', class_='col-12')
            print(f"Found {len(repo_containers)} repository containers with selector 'div.col-12'")

        # Print the first few containers to inspect their structure
        if repo_containers:
            for i in range(min(3, len(repo_containers))):
                print(f"\n--- Container {i} ---")
                debug_repo_container(repo_containers[i])