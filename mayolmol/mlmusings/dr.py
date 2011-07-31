# -*- coding: utf-8 -*-
from numpy import *
from scipy.linalg import eig
from kernels import gaussian_kernel, kernel_matrix
import prepro

def inertia(eigenvalues):
    return[eigenvalue / sum(eigenvalues) for eigenvalue in eigenvalues]

def select_top(eigenvalues, eigenvectors, to_retain=None, top=True):
    if not to_retain:
        to_retain = len(eigenvalues)
    indices = argsort(eigenvalues)
    if top:
        indices = indices[::-1]
    inertias = inertia(real(eigenvalues[indices]))
    indices = indices[:to_retain]
    return real(eigenvalues[indices]), real(eigenvectors[:, indices]), inertias

def pca(x, target_dim=None):
    #Eigendecomposition of the covariance matrix of the centered data
    eigenvalues, eigenvectors = eig(cov(prepro.center(x).T))

    #Selection of the PCs
    eigenvalues, eigenvectors, inertias = select_top(eigenvalues, eigenvectors, target_dim)

    return dot(x, eigenvectors), eigenvectors, eigenvalues, inertias

def center_kernel_matrix(K, mmul=True):
    #Some algebra can optimize this both in time and space, think...
    if mmul:
        num_examples, _ = K.shape
        onen = ones((num_examples, num_examples)) / num_examples
        onenK = dot(onen, K)
        return K - onenK - onenK.T + dot(onenK, onen)

def shuffle_matrix(matrix, seed=0):
    import random
    ne, _ = matrix.shape
    shuffled = range(ne)
    random.Random(seed).shuffle(shuffled)
    km01 = zeros([ne, ne])
    for i in range(ne):
        for j in range (ne):
            km01[i,j]=matrix[shuffled[i], shuffled[j]]
    return km01

def kpca(x, target_dim=None, kernel=gaussian_kernel, shuffle=None, **kernel_params):
    #Recall that in kpca, depending on the kernel, each point can span a new direction in feature space...
    num_examples, num_features = shape(x)
    if not target_dim:
        target_dim = num_features #...we usually do not want that many

    #Compute the kernel matrix
    K = kernel_matrix(x, kernel=kernel, **kernel_params)
    if shuffle:
        K = shuffle_matrix(K, shuffle)

    #Center the data in feature space: K' = K -1nK -K1n +1nK1n
    K = center_kernel_matrix(K)

    #Eigendecomposition
    eigenvalues, eigenvectors = eig(K)

    #Selection of the PCs
    eigenvalues, eigenvectors, inertias = select_top(eigenvalues, eigenvectors, target_dim)

    #Transform
    x = dot(diag(sqrt(eigenvalues)), eigenvectors.T).T

    return x, K, eigenvectors, eigenvalues, inertias