"""Filesystem locations for the API, overridable by environment variables.

Defaults resolve against the monorepo layout so the service runs from a
checkout without configuration; the Docker image sets explicit paths.
"""
import os
from pathlib import Path

# `.parent` chains (unlike `.parents[n]`) never raise on shallow layouts such
# as the container's /srv/mentor_api, where only env-var paths are used.
API_ROOT: Path = Path(__file__).resolve().parent.parent
REPO_ROOT: Path = API_ROOT.parent.parent


def _path(env: str, default: Path) -> Path:
    value = os.getenv(env, '').strip()
    return Path(value).resolve() if value else default


def curriculum_path() -> Path:
    return _path('CURRICULUM_PATH', REPO_ROOT / 'packages' / 'curriculum' / 'curriculum.json')


def web_dir() -> Path:
    return _path('WEB_DIR', REPO_ROOT / 'apps' / 'web')


def database_path() -> Path:
    return _path('DATABASE_PATH', API_ROOT / 'data' / 'mentor.db')
