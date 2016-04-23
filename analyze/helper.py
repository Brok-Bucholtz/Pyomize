from re import match, sub


def extract_commit_components(commits):
    """
    Extract components from individual commits to create lists for each component
    :param commits: List of database commit objects
    :return: Dictionary with all the components from the commits
    """
    commit_components = {
        'messages': [],
        'repositories': [],
        'emails': [],
        'dates': [],
        'changed_files': []
    }

    for commit in commits:
        commit_components['messages'].append(commit.message)
        commit_components['repositories'].append(commit.repository.name)
        commit_components['emails'].append(commit.committer_email)
        commit_components['dates'].append(commit.date)
        commit_components['changed_files'].append(len(commit.files))

    return commit_components


def extract_commit_file_components(commit_files):
    """
    Extract components from individual files to create lists for each component
    :param commit_files: List of database file objects
    :return: Dictionary with all the components from the files
    """
    commit_file_components = {
        'patches': [],
        'additions': [],
        'changes': [],
        'deletions': [],
        'filenames': [],
        'statuses': []
    }

    for commit_file in commit_files:
        commit_file_components['patches'].append(commit_file.patch)
        commit_file_components['additions'].append(commit_file.additions)
        commit_file_components['changes'].append(commit_file.changes)
        commit_file_components['deletions'].append(commit_file.deletions)
        commit_file_components['filenames'].append(commit_file.filename)
        commit_file_components['statuses'].append(commit_file.status)

    return commit_file_components


def get_first_word(string):
    """
    Get the first word in a string
    :param string: The string to extract the first word from
    :return: The first word in the string or empty string
    """
    first_word = match('^([\s]+)?([^\s]+)', string)
    return first_word.group().strip() if first_word else ''


def remove_non_alpha(word):
    """
    Remove non-alphabetical characters from a word
    :param word: The word to remove non-alphabetical characters from
    :return: Word with only alphabetical characters
    """
    return sub('[^a-zA-Z]', '', word)
