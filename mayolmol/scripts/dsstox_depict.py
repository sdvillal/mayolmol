# -*- coding: utf-8 -*-
""" Generate an image for each compound of a dataset.
    Note that at the moment none of the tried alternatives is able to generate succesfully
    an image of all compounds, so we stick with openbabel.
"""
import os
import os.path as op
import pybel
import argparse
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def depict(dataset):
    print 'Depicting %s' % dataset
    if not op.exists(dataset):
        print '\tSDF file does not exist, skipping...'
        return
    dataset_root, _ = op.split(dataset)
    depictions_dir=op.join(dataset_root, 'depictions')
    if not op.exists(depictions_dir):
        os.makedirs(depictions_dir)
    for mol in pybel.readfile('sdf', dataset):
        print 'Depicting: %s' %mol.title
        #This fails, need to research more (probably related to the porecomputed conformation)
        #  terminate called after throwing an instance of 'std::out_of_range'
        #    what():  vector::_M_range_check
        if not any(name in mol.title for name in ('LD50-train-2934', 'LD50-train-3306', 'LD50-train-5215', 'LD50-test-0954')):
            mol.removeh()
            mol.write('png', op.join(depictions_dir, mol.title +'.png'), overwrite=True)
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
    for dataset in datasets:
        depict(dataset)