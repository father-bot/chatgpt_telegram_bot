# vault.py

import os
import git

class Vault:
    def __init__(self, repo_url, local_path, branch_name):
        self.repo_url = repo_url
        self.local_path = local_path
        self.branch_name = branch_name
        self.repo = self.clone_or_pull_repo()

    def clone_or_pull_repo(self):
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path)

        git_dir = os.path.join(self.local_path, ".git")

        if os.path.exists(git_dir):
            repo = git.Repo(self.local_path)
            origin = repo.remotes.origin
            origin.pull()
        else:
            repo = git.Repo.clone_from(self.repo_url, self.local_path)

        return repo

    def checkout_branch(self):
        try:
            self.repo.git.checkout(self.branch_name)
        except git.exc.GitCommandError:
            self.repo.git.checkout('-b', self.branch_name)

    def commit_and_push(self, commit_message):
        self.repo.git.add('--all')
        self.repo.git.commit('-m', commit_message)
        origin = self.repo.remotes.origin
        origin.push(self.branch_name)

    def write_file(self, file_path, content):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
