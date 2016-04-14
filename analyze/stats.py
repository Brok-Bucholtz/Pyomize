from sklearn.feature_extraction.text import CountVectorizer
from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from numpy import mean
from collections import Counter
from analyze.helper import extract_commit_components, extract_commit_file_components


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

    commit_components = extract_commit_components(commits)
    commit_file_components = extract_commit_file_components(commit_files)

    print "Commit Patch Word Frequency"
    print get_word_frequency(commit_components['messages'])
    print "Commit Repo Frequency"
    print get_string_frequency(commit_components['repositories'])
    print "Committer Email Frequency"
    print get_string_frequency(commit_components['emails'])
    # Get Freq of dates
    print "Mean of File Changes in a Commit"
    print mean(commit_components['changed_files'])
    print "\n"

    print "File Path Word Frequency"
    print get_word_frequency([patch for patch in commit_file_components['patches'] if patch])
    print "Mean of Additions for a File"
    print mean(commit_file_components['additions'])
    print "Mean of Changes for a File"
    print mean(commit_file_components['changes'])
    print "Mean of Deletions for a File"
    print mean(commit_file_components['deletions'])
    # Do something with filename
    print "File Status Frequency"
    print get_string_frequency(commit_file_components['statuses'])


if __name__ == "__main__":
    run()
