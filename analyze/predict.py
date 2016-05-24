from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.cross_validation import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
from analyze.dimension_reduction import get_file_stats_data, get_file_patch_data
import tensorflow as tf
import numpy as np


def _run_svc_on_file_stats():
    clf = SVC()
    label_encoder = LabelEncoder()
    X_all, y_all = get_file_stats_data()
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


def _get_batch(x, y, step, batch_size):
    assert len(x) == len(y)
    start = step*batch_size
    return x[start:start+batch_size], y[start:start+batch_size]


def _run_simple_net_on_patch():
    def simple_model(X, w_h, w_o):
        h = tf.nn.sigmoid(tf.matmul(X, w_h))
        return tf.matmul(h, w_o)

    def init_weights(shape):
        return tf.Variable(tf.random_normal(shape, stddev=0.01))

    patches_stats, labels = get_file_patch_data()
    patches, file_stats = zip(*patches_stats)
    patch_vectorizer = CountVectorizer()
    patch_vectorizer.fit(patches)
    label_vectorizer = CountVectorizer()
    label_vectorizer.fit(labels)

    # Use patch data and file stats for features
    patches = patch_vectorizer.transform(patches).toarray()
    features = np.asarray([np.concatenate((patch_file_stat[0], patch_file_stat[1])) for patch_file_stat in zip(patches, file_stats)])

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        label_vectorizer.transform(labels).toarray(),
        test_size=0.25)

    x_tf = tf.placeholder("float", [None, x_train.shape[1]])
    y_tf = tf.placeholder("float", [None, y_train.shape[1]])

    weight_h = init_weights([x_train.shape[1], 625])
    weight_o = init_weights([625, y_train.shape[1]])

    py_x = simple_model(x_tf, weight_h, weight_o)

    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(py_x, y_tf))
    train_op = tf.train.GradientDescentOptimizer(0.05).minimize(cost)
    predict_op = tf.argmax(py_x, 1)

    with tf.Session() as sess:
        tf.initialize_all_variables().run()

        for i in range(100):
            for start, end in zip(range(0, len(x_train), 128), range(128, len(x_train), 128)):
                sess.run(train_op, feed_dict={x_tf: x_train[start:end], y_tf: y_train[start:end]})
            print('{}\t{}'.format(
                i,
                np.mean(np.argmax(y_test, axis=1) == sess.run(predict_op, feed_dict={x_tf: x_test, y_tf: y_test}))))


def run():
    _run_svc_on_file_stats()
    _run_simple_net_on_patch()

if __name__ == "__main__":
    run()
