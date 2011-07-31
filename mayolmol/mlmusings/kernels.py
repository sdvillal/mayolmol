# -*- coding: utf-8 -*-
''' A few kernel functions '''

from numpy import *

def linear_kernel(x, y):
    return dot(x, y)

def polynomial_kernel(x, y, degree=3):
    return (1 + dot(x, y)) ** degree

def gaussian_kernel(x, y, sigma=2.0):
    return exp(-sum((x - y) ** 2) ** 2 / (2 * sigma ** 2))

def kernel_matrix(x, kernel=gaussian_kernel, **kernel_params):
    numE = shape(x)[0]
    K = zeros((numE, numE))
    for i in range(numE):
        for j in range(i, numE):  #Let's not assume K[i][i] == 1
            K[i,j] = K[j,i] = kernel(x[i], x[j], **kernel_params) #Slow, optimize this by inlining and using matix ops
    return K