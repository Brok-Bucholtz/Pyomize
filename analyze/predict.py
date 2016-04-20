from sqlalchemy.orm import sessionmaker, joinedload
from analyze.helper import get_first_word
from github_database import engine, Commit
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from analyze.dimension_reduction import filter_merge_commits, get_top_frequent_words, filter_data_by_labels


def _get_file_stats(commit_files):
    additions = 0
    deletions = 0
    for commit_file in commit_files:
        additions += commit_file.additions
        deletions += commit_file.deletions
    return [additions, deletions]


def run():
    db_session = sessionmaker(bind=engine)()
    commits = db_session \
        .query(Commit) \
        .options(joinedload(Commit.files)) \
        .all()

    commits = filter_merge_commits(commits)
    commit_files_list = [commit.files for commit in commits]
    commit_first_words = [get_first_word(commit.message) for commit in commits]
    top_words = get_top_frequent_words(commit_first_words, 8)
    label_encoder = LabelEncoder()

    X_all = [_get_file_stats(commit_files) for commit_files in commit_files_list]
    y_all = commit_first_words
    X_all, y_all = filter_data_by_labels(X_all, y_all, top_words)
    y_all = label_encoder.fit_transform(y_all)

    num_all = len(X_all)
    num_train = num_all*0.25
    clf = SVC()
    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, train_size=(num_train / float(num_all)))

    print "Training set size: {}".format(len(X_train))
    clf.fit(X_train, y_train)
    print "Accuracy for training set: {}".format(accuracy_score(y_train, clf.predict(X_train)))
    print "Accuracy for test set: {}".format(accuracy_score(y_test, clf.predict(X_test)))

if __name__ == "__main__":
    run()
