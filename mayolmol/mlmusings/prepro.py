# -*- coding: utf-8 -*-
from numpy import *

def center(x):
    """ Remove the mean from the data. """
    return x - mean(x, axis=0)

def normalize01(x):
    """ Normalize the columns of a numpy array between 0 and 1. """
    maxes = x.max(axis=0)
    mines = x.min(axis=0)
    return (x - mines[newaxis,:]) / (maxes - mines)[newaxis,:]

def normalizeab(x, min=0, max=1):
    return min + max * normalize01(x)

def standardize(x):
    """ Zero mean unit variance"""
    #just subtract the mean if the standard deviation is zero or fail?
    return center(x) / std(x, 0)

def network_ratio_profile(x, epsilon=1):
    """ Normalize motif counts like in Pads paper """
    means = x.mean(axis=0)
    rp = (x - means) / (x + means + epsilon)
    return rp / sqrt((rp ** 2).sum(axis=0))