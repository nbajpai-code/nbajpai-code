#!/usr/bin/env python3
"""
Auto-update profile README.md with dynamic repository information.
Fetches repository data from GitHub API and updates the README.
"""

import os
import re
import requests
from datetime import datetime


def fetch_repositories(username, token=None):
    """Fetch all public repositories for the user."""
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    repos = []
    page = 1
    
    while True:
        url = f'https://api.github.com/users/{username}/repos?page={page}&per_page=100&sort=updated'
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}")
            break
        
        page_repos = response.json()
        if not page_repos:
            break
        
        repos.extend(page_repos)
        page += 1
    
    return repos


def categorize_repositories(repos):
    """Categorize repositories into featured and all repos."""
    # Filter out forks and archived repos for featured
    featured = []
    all_repos = []
    
    # Define featured repos (you can customize this)
    featured_names = ['my-starred-repos', 'games', 'tb']
    
    for repo in repos:
        if not repo['fork']:
            all_repos.append(repo)
            if repo['name'] in featured_names:
                featured.append(repo)
    
    # Sort by stars and updated date
    featured.sort(key=lambda x: (x['stargazers_count'], x['updated_at']), reverse=True)
    all_repos.sort(key=lambda x: x['updated_at'], reverse=True)
    
    return featured, all_repos


def generate_repo_cards(repos, max_cards=6):
    """Generate repository cards for the README."""
    cards = []
    for repo in repos[:max_cards]:
        card = f"[![Repo Card](https://github-readme-stats.vercel.app/api/pin/?username=nbajpai-code&repo={repo['name']}&theme=tokyonight&hide_border=true)](https://github.com/nbajpai-code/{repo['name']})"
        cards.append(card)
    
    # Arrange in rows of 2
    result = []
    for i in range(0, len(cards), 2):
        if i + 1 < len(cards):
            result.append(f"{cards[i]}\n{cards[i+1]}")
        else:
            result.append(cards[i])
    
    return "\n\n".join(result)


def generate_repo_list(repos):
    """Generate a list of all repositories with descriptions."""
    lines = []
    
    # Group by primary language
    by_language = {}
    for repo in repos:
        lang = repo.get('language') or 'Other'
        if lang not in by_language:
            by_language[lang] = []
        by_language[lang].append(repo)
    
    # Sort languages by repo count
    sorted_languages = sorted(by_language.items(), key=lambda x: len(x[1]), reverse=True)
    
    for lang, lang_repos in sorted_languages[:5]:  # Top 5 languages
        lines.append(f"\n#### {lang}")
        for repo in lang_repos[:3]:  # Top 3 repos per language
            desc = repo.get('description', 'No description')
            stars = repo['stargazers_count']
            star_badge = f"⭐ {stars}" if stars > 0 else ""
            lines.append(f"- **[{repo['name']}](https://github.com/nbajpai-code/{repo['name']})** {star_badge}")
            if desc and desc != 'No description':
                lines.append(f"  - {desc}")
    
    return "\n".join(lines)


def update_readme():
    """Update the README.md file with current repository data."""
    
    username = 'nbajpai-code'
    token = os.environ.get('GITHUB_TOKEN')
    
    print(f"Fetching repositories for {username}...")
    repos = fetch_repositories(username, token)
    print(f"Found {len(repos)} repositories")
    
    featured, all_repos = categorize_repositories(repos)
    print(f"Featured: {len(featured)}, All: {len(all_repos)}")
    
    # Generate dynamic content
    repo_cards = generate_repo_cards(all_repos, max_cards=6)
    repo_list = generate_repo_list(all_repos)
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Read current README
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
    
    # Update repository cards section
    # Find the "All Repositories" section and update the cards
    cards_pattern = r'(### 📁 All Repositories\n\n<div align="center">\n\n)(.*?)(\n\n</div>)'
    if re.search(cards_pattern, readme, re.DOTALL):
        readme = re.sub(
            cards_pattern,
            f'\\1{repo_cards}\\3',
            readme,
            flags=re.DOTALL
        )
        print("✅ Updated repository cards")
    
    # Update last commit badge timestamp (it's already dynamic via badge, but we can add a footer)
    footer_pattern = r'(\*\*Thank you for visiting!\*\* 🚀)'
    footer_replacement = f'*Last auto-updated: {timestamp}*\n\n\\1'
    
    if re.search(footer_pattern, readme):
        readme = re.sub(footer_pattern, footer_replacement, readme)
        print("✅ Updated timestamp")
    else:
        # Add timestamp before closing div
        readme = readme.replace(
            '**Thank you for visiting!** 🚀',
            f'*Last auto-updated: {timestamp}*\n\n**Thank you for visiting!** 🚀'
        )
        print("✅ Added timestamp")
    
    # Write updated README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"\n✅ README.md updated successfully!")
    print(f"   - Total repositories: {len(repos)}")
    print(f"   - Featured repositories: {len(featured)}")
    print(f"   - Timestamp: {timestamp}")


if __name__ == '__main__':
    update_readme()
