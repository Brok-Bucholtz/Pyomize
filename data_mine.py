from github import Github
from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from ConfigParser import ConfigParser


config = ConfigParser()
config.read('config.ini')
github_api = Github(config.get('Main', 'GithubAccessToken'))
db_session = sessionmaker(bind=engine)()

org_name = unicode('google')
github_google = github_api.get_organization(org_name)
db_org_commits = db_session.query(Commit).all()

for repo in github_google.get_repos():
    for commit in (c for c in repo.get_commits() if c.sha not in [db_c.sha for db_c in db_org_commits]):
        db_commit = Commit(
            sha=commit.sha,
            date=commit.last_modified,
            message=commit.commit.message,
            committer_email=commit.committer.email if commit.committer else unicode(''),
            organization_login=org_name,
            repository_name=repo.name)
        for commit_file in commit.files:
            db_commit.files.append(File(
                filename=commit_file.filename,
                sha=commit_file.sha,
                additions=commit_file.additions,
                deletions=commit_file.deletions,
                changes=commit_file.changes,
                status=commit_file.status,
                patch=commit_file.patch))
        db_session.add(db_commit)
        db_session.commit()
