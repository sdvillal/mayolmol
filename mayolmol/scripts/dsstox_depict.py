# -*- coding: utf-8 -*-
""" Generate spectrophores for the DSSTox datasets """
import multiprocessing
import os
import os.path as op
import pybel
import argparse
import math
import numpy
from mayolmol.descriptors import ob
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def depicter(dataset):
    print 'Depicting %s' % dataset
    if not op.exists(dataset):
        print '\tSDF file does not exist, skipping...'
        return
    dataset_root, _ = op.split(dataset)
    depictions_dir=op.join(dataset_root, 'depictions')
    if not op.exists(depictions_dir):
        os.makedirs(depictions_dir)
    for mol in pybel.readfile('sdf', dataset):
        mol.removeh()
        mol.write('svg', op.join(depictions_dir, mol.title +'.svg'), overwrite=True)
    print 'Depicting %s done' % dataset

if __name__ == '__main__':
    #######################################
    # Parse options
    #######################################
    parser = argparse.ArgumentParser(description='DSSTox depicter script')
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
    pool.map(depicter, datasets)
    pool.close()