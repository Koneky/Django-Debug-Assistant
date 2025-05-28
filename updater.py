import os
import json
from git import Repo, GitCommandError


REPO_DIR = './django_debug_assistant_repo'
REPO_URL = 'https://github.com/Koneky/django-errors-db.git'
ERRORS_JSON = 'errors.json'


def update_errors():
    """
    Клонирует репозиторий, если нет, или делает git pull.
    Возвращает обновлённые данные из errors.json или бросает исключение.
    """
    if not os.path.exists(REPO_DIR):
        Repo.clone_from(REPO_URL, REPO_DIR)
    
    repo = Repo(REPO_DIR)
    origin = repo.remotes.origin
    origin.pull()

    src = os.path.join(REPO_DIR, ERRORS_JSON)
    if not os.path.exists(src):
        raise FileNotFoundError(f'{ERRORS_JSON} не найден в репозитории')
    
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(ERRORS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data
