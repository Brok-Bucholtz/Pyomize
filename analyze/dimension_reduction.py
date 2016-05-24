from collections import OrderedDict, Counter
from analyze.helper import get_first_word, remove_non_alpha
from github_database import engine, Commit
from sqlalchemy.orm import sessionmaker, joinedload
from operator import itemgetter
from nltk.stem.lancaster import LancasterStemmer
from re import compile


def _get_top_frequent_words(words, top_count):
    """
    Return a unique list of words from most frequent to least frequent from a list
    :param words: List of words
    :param top_count: Number of words to return
    :return: Top most frequent words found
    """
    word_occurances = OrderedDict(sorted(Counter(words).items(), key=itemgetter(1), reverse=True))
    return [word_occurances[0] for word_occurances in word_occurances.items()[:top_count]]


def _filter_data_by_labels(X, y, label_filters):
    """
    Filter out features and labels based on label
    :param X: Features
    :param y: Labels
    :param label_filters: Labels to use
    :return: Features and labels that have been a label in label_filters
    """
    assert len(y) == len(X)
    x_ys = zip(X, y)

    return zip(*[x_y for x_y in x_ys if x_y[1] in label_filters])


def _remove_data_by_labels(X, y, label_filters):
    """
    Filter out features and labels based on label
    :param X: Features
    :param y: Labels
    :param label_filters: Labels to filter out
    :return: Features and labels that have been filterd based on label_filters
    """
    assert len(y) == len(X)
    x_ys = zip(X, y)

    return zip(*[x_y for x_y in x_ys if x_y[1] not in label_filters])


def _stem_labels(labels):
    """
    Stem a list of labels
    :param labels: List of labels
    :return: List of stemmed labels
    """
    lancaster_stemmer = LancasterStemmer()
    return [lancaster_stemmer.stem(label) for label in labels]


def _get_file_stats(commit_files):
    """
    Get total additions and deletions from commit_files
    :param commit_files: List of database file objects
    :return: Total additions and deletions for files
    """
    additions = 0
    deletions = 0
    for commit_file in commit_files:
        additions += commit_file.additions
        deletions += commit_file.deletions
    return [additions, deletions]


def _get_first_word_in_commit_message(x, messages):
    y = _stem_labels([remove_non_alpha(get_first_word(message)) for message in messages])
    return _remove_data_by_labels(x, y, ['merg', '', 'issu'])


def get_file_stats_data(label_count=8):
    """
    Get features and labels of commit messages and file stats
    :param label_count: Number of labels to return
    :return: Features of file stats and labels of first words in commit messages
    """
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .options(joinedload(Commit.files)) \
        .all()

    commit_files_list = [commit.files for commit in commits]

    X_all = [_get_file_stats(commit_files) for commit_files in commit_files_list]
    y_all = [commit.message for commit in commits]
    x_filtered, y_filtered = _get_first_word_in_commit_message(X_all, y_all)

    return _filter_data_by_labels(x_filtered, y_filtered, _get_top_frequent_words(y_filtered, label_count))


def get_file_patch_data():
    """
    Get features and labels of commit messages and file patches
    :return: File patch and commit message data
    """
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .options(joinedload(Commit.files)) \
        .all()

    commit_data = zip(*_get_first_word_in_commit_message(
        [commit.files for commit in commits],
        [commit.message for commit in commits]))

    file_patches = []
    first_word_messages = []
    file_stats = []
    regex_context = compile(r'\n[-+].*')
    regex_space = compile(r' +')
    for commit_files, first_word_message in commit_data:
        if commit_files:
            patches = [regex_space.sub(' ', ''.join(regex_context.findall(patch)))[1:] for patch in [
                commit_file.patch for commit_file in commit_files] if patch]
            if patches:
                file_patches.append(''.join(patches))
                first_word_messages.append(first_word_message)
                file_stats.append(_get_file_stats(commit_files))
    return _filter_data_by_labels(zip(file_patches, file_stats), first_word_messages, _get_top_frequent_words(first_word_messages, 3))

