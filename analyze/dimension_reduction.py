from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from operator import itemgetter


def run():
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .all()
    commit_files = db_session \
        .query(File) \
        .all()

    commit_ignore_words = [u'to', u'the', u'for', u'and', u'in', u'from', u'of']
    python_keywords = [u'and', u'del', u'from', u'not', u'while', u'as', u'elif', u'global', u'or', u'with', u'assert',
                       u'else', u'if', u'pass', u'yield', u'break', u'except', u'import', u'print', u'class', u'exec',
                       u'in', u'raise', u'continue', u'finally', u'is', u'return', u'def', u'for', u'lambda', u'try']
    commit_file_ignore_words = python_keywords

    commit_vectorizer = TfidfVectorizer(stop_words=commit_ignore_words)
    commit_vectorizer.fit_transform([commit.message for commit in commits])

    commit_file_vectorizer = TfidfVectorizer(stop_words=commit_file_ignore_words)
    commit_file_vectorizer.fit_transform([commit_file.patch for commit_file in commit_files if commit_file.patch])

    print sorted(dict(zip(
        commit_vectorizer.get_feature_names(),
        commit_vectorizer.idf_)).items(),
        key=itemgetter(1))
    print sorted(dict(zip(
        commit_file_vectorizer.get_feature_names(),
        commit_file_vectorizer.idf_)).items(),
        key=itemgetter(1))

if __name__ == "__main__":
    run()
