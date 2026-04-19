#coding: utf-8
from __future__ import division
from collections import Counter, defaultdict
import math, random, re, glob, codecs

def split_data(data, prob):
    """split data into fractions [prob, 1 - prob]"""
    results = [], []
    for row in data:
        results[0 if random.random() < prob else 1].append(row)
    return results


def tokenize(message):
    message = message.lower()                       # convert to lowercase
    patt = re.compile(ur"[a-záéíóú'-]+", re.UNICODE)
    all_words = re.findall(patt, message)
    return set(all_words)                           # remove duplicates


def count_words(training_set):
    """training set consists of pairs (message, is_true)"""
    counts = defaultdict(lambda: [0, 0])
    for message, is_true in training_set:
        for word in tokenize(message):
            counts[word][0 if is_true else 1] += 1
    return counts

def word_probabilities(counts, total_true, total_false, k=0.5):
    """turn the word_counts into a list of triplets 
    w, p(w | true) and p(w | false)"""
    return [(w,
             (truec + k) / (total_true + 2 * k),
             (falsec + k) / (total_false + 2 * k))
             for w, (truec, falsec) in counts.iteritems()]

def true_probability(word_probs, message):
    message_words = tokenize(message)
    log_prob_if_true = log_prob_if_false = 0.0

    for word, prob_if_true, prob_if_false in word_probs:

        # for each word in the message, 
        # add the log probability of seeing it 
        if word in message_words:
            log_prob_if_true += math.log(prob_if_true)
            log_prob_if_false += math.log(prob_if_false)

        # for each word that's not in the message
        # add the log probability of _not_ seeing it
        else:
            log_prob_if_true += math.log(1.0 - prob_if_true)
            log_prob_if_false += math.log(1.0 - prob_if_false)
            
    ans = 1.0 / (1.0 + math.exp(log_prob_if_false - log_prob_if_true))
    return ans
    #prob_if_true = math.exp(log_prob_if_true)
    #prob_if_false = math.exp(log_prob_if_false)
    #return prob_if_true / (prob_if_true + prob_if_false)


class NaiveBayesClassifier:

    def __init__(self, k=0.5):
        self.k = k
        self.word_probs = []

    def train(self, training_set):
    
        num_trues = len([is_true 
                         for message, is_true in training_set 
                         if is_true])
        num_falses = len(training_set) - num_trues

        # run training data through our "pipeline"
        word_counts = count_words(training_set)
        self.word_probs = word_probabilities(word_counts, 
                                             num_trues, 
                                             num_falses,
                                             self.k)
                                             
    def classify(self, message):
        return true_probability(self.word_probs, message)


def load_labeled_data():

    data = []

    with codecs.open('irish-happy.txt','r','utf-8') as file:
        for line in file:
            data.append((line, True))

    with codecs.open('irish-sad.txt','r','utf-8') as file:
        for line in file:
            data.append((line, False))

    return data

def p_true_given_word(word_prob):
    word, prob_if_true, prob_if_false = word_prob
    return prob_if_true / (prob_if_true + prob_if_false)

def classify_test_set(classifier):
    
    with codecs.open('test.txt','r','utf-8') as file:
        for line in file:
            pieces = line.split("\t")
            sentence_number = pieces[0]
            sentence = pieces[1]
            label = '0'
            if classifier.classify(sentence) > 0.5:
                label = '1'
            print sentence_number + ',' + label


def train_and_test_model():

    data = load_labeled_data()
    train_data, test_data = split_data(data, 0.75)    

    classifier = NaiveBayesClassifier()
    classifier.train(train_data)

    classified = [(subject, is_true, classifier.classify(subject))
              for subject, is_true in test_data]

    counts = Counter((is_true, true_probability > 0.5) # (actual, predicted)
                     for _, is_true, true_probability in classified)

    print counts

    classified.sort(key=lambda row: row[2])
    truest_falses = filter(lambda row: not row[1], classified)[-5:]
    falsest_trues = filter(lambda row: row[1], classified)[:5]

    print "truest_falses"
    for t in truest_falses:
      print t[0].encode('utf-8')
    print "falsest_trues"
    for t in falsest_trues:
      print t[0].encode('utf-8')

    words = sorted(classifier.word_probs, key=p_true_given_word)

    truest_words = words[-10:]
    falsest_words = words[:10]

    print "truest_words:"
    for t in truest_words:
      print t[0].encode('utf-8')
    print
    print "falsest_words:"
    for t in falsest_words:
      print t[0].encode('utf-8')

    #classify_test_set(classifier)

if __name__ == "__main__":
    train_and_test_model()
