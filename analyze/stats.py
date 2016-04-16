from sklearn.feature_extraction.text import CountVectorizer
from github_database import engine, Commit, File
from sqlalchemy.orm import sessionmaker
from numpy import mean
from collections import Counter
from analyze.helper import extract_commit_components, extract_commit_file_components
from re import compile


def _get_word_frequency(lines):
    count_vect = CountVectorizer()

    X_train_counts = count_vect.fit_transform(lines)
    word_rates = [(word, X_train_counts.getcol(idx).sum()) for word, idx in count_vect.vocabulary_.items()]
    return sorted(word_rates, key=lambda x: -x[1])


def _get_string_frequency(strings):
    counter = Counter(strings)
    return zip(counter.keys(), counter.values())


def _print_general_stats(sample_size=100):
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .all()
    commit_files = db_session \
        .query(File) \
        .all()

    commit_components = extract_commit_components(commits[:sample_size])
    commit_file_components = extract_commit_file_components(commit_files[:sample_size])

    print "Commit Message Word Frequency"
    print _get_word_frequency(commit_components['messages'])
    print "Commit Repo Frequency"
    print _get_string_frequency(commit_components['repositories'])
    print "Committer Email Frequency"
    print _get_string_frequency(commit_components['emails'])
    # Get Freq of dates
    print "Mean of File Changes in a Commit"
    print mean(commit_components['changed_files'])
    print "\n"

    print "File Path Word Frequency"
    print _get_word_frequency([patch for patch in commit_file_components['patches'] if patch])
    print "Mean of Additions for a File"
    print mean(commit_file_components['additions'])
    print "Mean of Changes for a File"
    print mean(commit_file_components['changes'])
    print "Mean of Deletions for a File"
    print mean(commit_file_components['deletions'])
    # Do something with filename
    print "File Status Frequency"
    print _get_string_frequency(commit_file_components['statuses'])
    print "\n"


def _print_first_word_commit_message_frequency():
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .all()
    regex_search = compile('^([\s]+)?([^\s]+)')

    commit_message_first_words = [regex_search.match(commit.message).group().strip() for commit in commits]

    print "Commit Message First Word Frequency"
    print _get_word_frequency(commit_message_first_words)


def run():
    _print_general_stats()
    _print_first_word_commit_message_frequency()

if __name__ == "__main__":
    run()
