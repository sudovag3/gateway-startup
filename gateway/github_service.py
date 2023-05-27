from github import Github
import datetime


class GitHubService:
    def __init__(self):
        self.github = Github()

    def get_repository(self, repo_url):
        repo_name = repo_url.split("/")[-1]
        user_name = repo_url.split("/")[-2]
        repo = self.github.get_user(user_name).get_repo(repo_name)
        return repo

    def has_commit_after_date(self, repo_url, date):
        if repo_url and date:
            repo = self.get_repository(repo_url)
            latest_commit = repo.get_commits()[0]
            latest_commit_date = latest_commit.commit.author.date
            return latest_commit_date > date
        return False

    def has_string_in_description(self, repo_url, string):
        repo = self.get_repository(repo_url)
        description = repo.description
        return string in description


