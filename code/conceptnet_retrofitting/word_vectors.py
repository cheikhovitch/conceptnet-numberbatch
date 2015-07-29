import numpy as np

from conceptnet5.nodes import standardized_concept_uri
from conceptnet_retrofitting.builders.label_set import LabelSet
from sklearn.preprocessing import normalize


def conceptnet_standardizer(label, lang='en'):
    return standardized_concept_uri(lang, label)


class WordVectors:
    def __init__(self, labels, vectors, standardizer=conceptnet_standardizer):
        assert(len(labels) == len(vectors))
        self.labels = LabelSet(labels)
        if not isinstance(vectors, np.memmap):
            normalize(vectors, copy=False)
        self.vectors = vectors
        self._standardizer = standardizer


    def similarity(self, word1, word2, lang=None):
        try:
            return self.to_vector(word1, lang).dot(self.to_vector(word2, lang))
        except KeyError:
            print("Unknown Pair: %s %s"%(word1, word2))
            return 0

    def to_vector(self, word, lang=None):
        if self._standardizer is not None:
            if self._standardizer is conceptnet_standardizer and \
                lang is not None:
                word = self._standardizer(word, lang)
            else:
                word = self._standardizer(word)
        vec = self.vectors[self.labels.index(word)]
        if isinstance(vec, np.memmap):
            return normalize(vec)[0]
        return vec

    def similar_to(self, word_or_vector, num=20, only=None):
        if isinstance(word_or_vector, str):
            vec = self.to_vector(word_or_vector)
        else:
            vec = word_or_vector

        sim = self.vectors.dot(vec)
        indices = np.argsort(sim)[::-1]

        out = []
        for index in indices:
            if len(out) == num:
                return out
            if only is not None and not only(self.labels[index]):
                continue
            out.append((self.labels[index], sim[index]))

        return out
