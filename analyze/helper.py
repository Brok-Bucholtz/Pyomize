from re import match, sub


def extract_commit_components(commits):
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
    return match('^([\s]+)?([^\s]+)', string).group().strip()


def remove_non_alpha(word):
    return sub('[^a-zA-Z]', '', word)
