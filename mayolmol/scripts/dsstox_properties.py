# -*- coding: utf-8 -*-
""" Generate spectrophores for the DSSTox datasets """
import multiprocessing
import os
import os.path as op
import pybel
import argparse
import numpy
from mayolmol.descriptors import ob
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def spectrophores(dataset):
    try:
        print 'Computing spectrophores for dataset %s' % dataset
        specs = ob.spectrophores(pybel.readfile('sdf', dataset))
        datasetRoot, datasetName = op.split(dataset)
        datasetName = op.splitext(datasetName)[0]
        numpy.savetxt(op.join(datasetRoot, datasetName + '-spectrophores.csv'),
                      specs, fmt='%.6f', delimiter=',')
        print 'Spectrophores for dataset %s computed succesfully' % dataset
    except Exception, e:
        print 'Damn, there has been a problem computing the pharmacophores...'
        print 'Research into this...'
        print e.message

if __name__ == '__main__':
    #######################################
    # Parse options
    #######################################
    parser = argparse.ArgumentParser(description='DSSTox properties computation script')
    parser.add_argument('-r', '--root',
                        type=argparse.FileType(),
                        help='Root directory from where the original data will be read')
    args = parser.parse_args()

    root = args.root
    if not root:
        root = DEFAULT_DSSTOX_DIR
    dest = args.root

    #######################################
    # Compute properties
    #######################################
    datasets = sorted([name for name in os.listdir(root) if op.isdir(op.join(root, name))])
    datasets = map(lambda dataset: op.join(root, dataset, dataset + '.sdf'), datasets)
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(spectrophores, datasets)