from sklearn.feature_extraction.text import CountVectorizer
from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from numpy import mean
from collections import Counter


def get_word_frequency(lines):
    count_vect = CountVectorizer()

    X_train_counts = count_vect.fit_transform(lines)
    word_rates = [(word, X_train_counts.getcol(idx).sum()) for word, idx in count_vect.vocabulary_.items()]
    return sorted(word_rates, key=lambda x: -x[1])


def get_string_frequency(strings):
    counter = Counter(strings)
    return zip(counter.keys(), counter.values())


def run():
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .all()
    commit_files = db_session \
        .query(File) \
        .all()

    commit_stats = {
        'messages': [],
        'repositories': [],
        'emails': [],
        'dates': [],
        'changed_files': []
    }
    commit_file_stats = {
        'patches': [],
        'additions': [],
        'changes': [],
        'deletions': [],
        'filenames': [],
        'statuses': []
    }

    for commit in commits:
        commit_stats['messages'].append(commit.message)
        commit_stats['repositories'].append(commit.repository_name)
        commit_stats['emails'].append(commit.committer_email)
        commit_stats['dates'].append(commit.date)
        commit_stats['changed_files'].append(len(commit.files))

    for commit_file in commit_files:
        commit_file_stats['patches'].append(commit_file.patch)
        commit_file_stats['additions'].append(commit_file.additions)
        commit_file_stats['changes'].append(commit_file.changes)
        commit_file_stats['deletions'].append(commit_file.deletions)
        commit_file_stats['filenames'].append(commit_file.filename)
        commit_file_stats['statuses'].append(commit_file.status)

    print "Commit Patch Word Frequency"
    print get_word_frequency(commit_stats['messages'])
    print "Commit Repo Frequency"
    print get_string_frequency(commit_stats['repositories'])
    print "Committer Email Frequency"
    print get_string_frequency(commit_stats['emails'])
    # Get Freq of dates
    print "Mean of File Changes in a Commit"
    print mean(commit_stats['changed_files'])
    print "\n"

    print "File Path Word Frequency"
    print get_word_frequency([patch for patch in commit_file_stats['patches'] if patch])
    print "Mean of Additions for a File"
    print mean(commit_file_stats['additions'])
    print "Mean of Changes for a File"
    print mean(commit_file_stats['changes'])
    print "Mean of Deletions for a File"
    print mean(commit_file_stats['deletions'])
    # Do something with filename
    print "File Status Frequency"
    print get_string_frequency(commit_file_stats['statuses'])


if __name__ == "__main__":
    run()
