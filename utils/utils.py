import os
import git
from pathlib import Path


repo_root = Path(git.Repo(os.getcwd(), search_parent_directories=True).git.rev_parse("--show-toplevel"))
def get_path(x, repo_root=repo_root):
    return f"{repo_root}/data/raw/{x}"