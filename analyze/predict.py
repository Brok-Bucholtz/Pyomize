from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from analyze.dimension_reduction import get_data_for_linear_regression


def run():
    clf = SVC()
    label_encoder = LabelEncoder()
    X_all, y_all = get_data_for_linear_regression()
    y_all = label_encoder.fit_transform(y_all)

    num_all = len(X_all)
    num_train = num_all * 0.25
    X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, train_size=(num_train / float(num_all)))
    clf.fit(X_train, y_train)

    print "Training set size: {}".format(len(X_train))
    print "Accuracy for training set:"
    print classification_report(
            y_train,
            clf.predict(X_train),
            target_names=label_encoder.classes_)
    print "Accuracy for test set:"
    print classification_report(
            y_test,
            clf.predict(X_test),
            target_names=label_encoder.classes_)

if __name__ == "__main__":
    run()
