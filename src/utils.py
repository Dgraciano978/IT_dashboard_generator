"""
Utility functions for IT Dashboard Generator
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

def load_config(config_path: str) -> Dict:
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")

def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def cleanup_old_files(directory: Path, max_files: int, pattern: str = "*") -> None:
    try:
        files = list(directory.glob(pattern))
        if len(files) > max_files:
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_file in files[max_files:]:
                old_file.unlink()
                logging.info(f"Cleaned up old file: {old_file}")
    except Exception as e:
        logging.warning(f"Error cleaning up files in {directory}: {e}")

def validate_repositories(repositories: List[str]) -> List[str]:
    valid_repos = []
    for repo in repositories:
        if "/" in repo and len(repo.split("/")) == 2:
            valid_repos.append(repo)
        else:
            logging.warning(f"Invalid repository format: {repo}")
    return valid_repos

def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_next_run_time(schedule_time: str) -> datetime:
    try:
        hour, minute = map(int, schedule_time.split(':'))
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        return next_run
    except ValueError:
        raise ValueError(f"Invalid schedule time format: {schedule_time}. Use HH:MM format.")

def create_status_file(status: str, message: str, output_dir: Path) -> None:
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "message": message
    }
    status_file = output_dir / "last_run_status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)

def get_environment_info() -> Dict:
    return {
        "python_version": os.sys.version,
        "platform": os.name,
        "working_directory": str(Path.cwd()),
        "environment_variables": {
            k: v for k, v in os.environ.items() 
            if k.startswith(('GITHUB_', 'IT_DASHBOARD_'))
        }
    }

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default
