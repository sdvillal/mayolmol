# -*- coding: utf-8 -*-
""" Some methods for working with neighborhoods of data points """
import os
import numpy as np

def nns(x, k=5):
    """NNs under Euclidean distance
       Note that by default we are using an stable sort to get the points sorted,
       so we are subject to order artifacts in the original data (like having
       the points sorted by class). To avoid them, pre-shuffle x.
    """
    nns = []
    for ex in range(x.shape[0]): #At least lets not keep the whole ne x ne distance matrix in memory
        distances = ((x - x[ex,:]) ** 2).sum(1) #Oh well, n² distance computations, we could do half using heaps...
        distances[ex] = np.PINF
        nns.append(np.argsort(distances)[0:k])
    return nns

def count_holding(collection, *predicates):
    counts = [0] * len(predicates)
    for element in collection:
        for i, predicate in enumerate(predicates):
            if predicate(element):
                counts[i] += 1
    return tuple(counts)

def nn_error(nns, y, k=None):
    if not k:
        k = len(nns[0])
    error = 0.0
    for i, nn in enumerate(nns):
        right, = count_holding(nn[:k], lambda a: y[a] == y[i])
        if right <= k / 2.0:
            error += 1
    return error / len(nns)

def nn_acc(nns, y, k=None):
    return 1.0 - nn_error(nns, y, k)

def vizrank(x, y, k=10):
    """ Naive vizrank implementation """
    _, nf = x.shape
    scores = []
    for i in range(nf):
        for j in range(i + 1, nf):
            scores.append([nn_acc(nns(x[:, (i, j)], k), y), i, j])
    return sorted(scores, key=lambda a: a[0], reverse=True)

def hubness(neighbors):
    hub_scores = [0] * len(neighbors)
    for nn in neighbors:
        for neighbor in nn:
            hub_scores[neighbor] += 1
    return hub_scores

def bad_neighborhoodness(neighbors, y):
    bad_neighbor_count = [0] * len(neighbors)
    for ego, nn in enumerate(neighbors):
        for neighbor in nn:
            if y[ego] != y[neighbor]:
                bad_neighbor_count[neighbor] += 1
    return bad_neighbor_count

def good_neighborhoodness(neighbors, y):
    #Oh well, 2 passes...
    return [hub - bad for hub, bad in zip(hubness(neighbors), bad_neighborhoodness(neighbors, y))]