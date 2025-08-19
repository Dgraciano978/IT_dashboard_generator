"""
GitHub API Data Fetcher for IT Dashboard
Fetches repository statistics, pull requests, and issues data
"""
import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

class GitHubAPIClient:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config["github"]["api_base_url"]
        self.repositories = config["github"]["repositories"]
        self.rate_limit_delay = config["github"]["rate_limit_delay"]
        self.timeout = config["github"]["timeout"]
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "IT-Dashboard-Generator/1.0"
        })
        self.logger = logging.getLogger(__name__)

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                self.logger.warning(f"Rate limit hit for {url}")
                time.sleep(60)
                return self._make_request(url, params)
            else:
                self.logger.error(f"API request failed: {response.status_code} - {url}")
                return None
        except requests.RequestException as e:
            self.logger.error(f"Request error for {url}: {str(e)}")
            return None

    def get_repository_info(self, repo: str) -> Optional[Dict]:
        url = f"{self.base_url}/repos/{repo}"
        return self._make_request(url)

    def get_pull_requests(self, repo: str, state: str = "open") -> List[Dict]:
        url = f"{self.base_url}/repos/{repo}/pulls"
        params = {"state": state, "per_page": 100}
        prs, page = [], 1
        while True:
            params["page"] = page
            response = self._make_request(url, params)
            if not response: break
            prs.extend(response)
            if len(response) < 100: break
            page += 1
        return prs

    def get_issues(self, repo: str, state: str = "open") -> List[Dict]:
        url = f"{self.base_url}/repos/{repo}/issues"
        params = {"state": state, "per_page": 100}
        issues, page = [], 1
        while True:
            params["page"] = page
            response = self._make_request(url, params)
            if not response: break
            filtered_issues = [issue for issue in response if "pull_request" not in issue]
            issues.extend(filtered_issues)
            if len(response) < 100: break
            page += 1
        return issues

    def collect_all_data(self) -> pd.DataFrame:
        all_data = []
        for repo in self.repositories:
            self.logger.info(f"Fetching data for {repo}")
            repo_info = self.get_repository_info(repo)
            if not repo_info: continue
            open_prs = self.get_pull_requests(repo, "open")
            closed_prs = self.get_pull_requests(repo, "closed")
            open_issues = self.get_issues(repo, "open")
            closed_issues = self.get_issues(repo, "closed")
            repo_data = {
                "repository": repo,
                "stars": repo_info.get("stargazers_count", 0),
                "forks": repo_info.get("forks_count", 0),
                "watchers": repo_info.get("watchers_count", 0),
                "open_prs": len(open_prs),
                "closed_prs": len(closed_prs),
                "open_issues": len(open_issues),
                "closed_issues": len(closed_issues),
                "total_prs": len(open_prs) + len(closed_prs),
                "total_issues": len(open_issues) + len(closed_issues),
                "language": repo_info.get("language", "Unknown"),
                "size_kb": repo_info.get("size", 0),
                "created_at": repo_info.get("created_at", ""),
                "updated_at": repo_info.get("updated_at", ""),
                "fetch_timestamp": datetime.now().isoformat()
            }
            all_data.append(repo_data)
            self.logger.info(f"✓ Collected data for {repo}")
        return pd.DataFrame(all_data)

def fetch_github_data(config_path: str) -> pd.DataFrame:
    with open(config_path, 'r') as f:
        config = json.load(f)
    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    client = GitHubAPIClient(config)
    return client.collect_all_data()
