from github import Github, GithubException
from github_database import engine, Commit, File, Repository
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from ConfigParser import ConfigParser
from time import time, sleep
from urllib2 import urlopen, URLError
from socket import error

PAGE_MAX_SIZE = 100
START_PAGE = 1


def _get_missing_commits_from_db(db_session, repo):
    """
    Get a page of commits not in database
    :param db_session: Database session
    :param repo: Repository API
    :return: List of commits not in the database
    """
    db_commits = db_session \
        .query(Commit.sha) \
        .filter(Commit.repository.has(name=repo.name, owner_login=repo.owner.login)) \
        .all()
    page_num = len(db_commits)/PAGE_MAX_SIZE + START_PAGE
    commits = []

    try:
        commits = repo.get_commits().reversed.get_page(page_num)
    except GithubException as e:
        if e.status != 409 or e.data['message'] != u'Git Repository is empty.':
            raise e

    return [commit for commit in commits
            if commit.sha not in [db_commit.sha for db_commit in db_commits]]


def _get_new_commits(db_session, commit_api):
    """
    Get all commits not in the database
    :param db_session: Database session
    :param commit_api: Commit API
    :return: List of all commits not in the database
    """
    commits = _get_missing_commits_from_db(db_session, commit_api)
    while commits:
        for commit in commits:
            yield commit
        commits = _get_missing_commits_from_db(db_session, commit_api)


def _get_or_create(db_session, model, model_args):
    """
    Get the model based on the model arguments, otherwise create a new one and return it
    :param db_session: Database session
    :param model: Database model
    :param model_args: Arguments for the database model to search/create
    :return: Database instance of model
    """
    db_instance = db_session.query(model).filter_by(**model_args).first()
    if not db_instance:
        db_instance = model(**model_args)
        db_session.add(db_instance)
        db_session.commit()
    return db_instance


def run():
    config = ConfigParser()
    config.read('config.ini')
    github_api = Github(login_or_token=config.get('Main', 'GithubAccessToken'), per_page=PAGE_MAX_SIZE)
    db_session = sessionmaker(bind=engine)()

    org_name_i = 0
    org_names = [u'google', u'airbnb']

    while org_name_i < len(org_names):
        try:
            organization = github_api.get_organization(org_names[org_name_i])
            for repo in organization.get_repos():
                # It would make it easier to train the algorithm by limiting our data to one language
                if repo.language and repo.language.lower() == u'python':
                    db_repo_args = {
                        'name': repo.name,
                        'owner_login': repo.owner.login
                    }
                    db_repo = _get_or_create(db_session, Repository, db_repo_args)

                    for commit in _get_new_commits(db_session, repo):
                        db_commit = Commit(
                            sha=commit.sha,
                            date=commit.last_modified,
                            message=commit.commit.message,
                            committer_email=commit.committer.email if commit.committer else u'',
                            repository_id=db_repo.id)
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
        except GithubException as e:
            if e.status != 403 or u'API rate limit exceeded for ' not in e.data['message']:
                raise e
            else:
                wait_ratelimit_reset_seconds = github_api.rate_limiting_resettime-(int(time()))
                print 'Hit rate limit.  Waiting {} second(s)'.format(wait_ratelimit_reset_seconds)
                sleep(wait_ratelimit_reset_seconds)
                print 'Wait over.'
        except error:
            wait_for_github_connection_seconds = 60
            github_url = 'https://www.github.com'
            gihub_connection_down = True

            while gihub_connection_down:
                try:
                    urlopen(github_url)
                except URLError:
                    print 'Connection to Github down.  Waiting {} second(s)'.format(wait_for_github_connection_seconds)
                    sleep(wait_for_github_connection_seconds)
                    print 'Wait over.  Trying again...'
                else:
                    print 'Reconnected to Github.'
                    gihub_connection_down = False
        except OperationalError as e:
            if e.message == "(sqlite3.OperationalError) database is locked":
                wait_time_seconds = 60
                print 'DB locked.  Waiting {} second(s)'.format(wait_time_seconds)
                sleep(wait_time_seconds)
                print 'Wait over.'
        else:
            org_name_i += 1


if __name__ == "__main__":
    run()
