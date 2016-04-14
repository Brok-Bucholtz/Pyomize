from github import Github, GithubException
from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from ConfigParser import ConfigParser

PAGE_MAX_SIZE = 100
START_PAGE = 1


def _get_missing_commits_from_db(db_session, repo):
    db_commits = db_session \
        .query(Commit.sha) \
        .filter(Commit.repository_name == repo.name) \
        .all()
    page_num = len(db_commits)/PAGE_MAX_SIZE + START_PAGE
    commits = []

    try:
        commits = repo.get_commits().reversed.get_page(page_num)
    except GithubException as e:
        if e.status == 409 and e.data['message'] != unicode('Git Repository is empty.'):
            raise e

    return [commit for commit in commits
            if commit.sha not in [db_commit.sha for db_commit in db_commits]]


def _get_new_commits(db_session, commit_api):
    commits = _get_missing_commits_from_db(db_session, commit_api)
    while commits:
        for commit in commits:
            yield commit
        commits = _get_missing_commits_from_db(db_session, commit_api)


def run():
    config = ConfigParser()
    config.read('config.ini')
    github_api = Github(login_or_token=config.get('Main', 'GithubAccessToken'), per_page=PAGE_MAX_SIZE)
    db_session = sessionmaker(bind=engine)()

    org_name = unicode('google')
    github_google = github_api.get_organization(org_name)

    for repo in github_google.get_repos():
        for commit in _get_new_commits(db_session, repo):
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

if __name__ == "__main__":
    run()