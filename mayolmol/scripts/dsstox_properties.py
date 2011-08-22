# -*- coding: utf-8 -*-
""" Generate different properties for the DSSTox datasets """
import os
import os.path as op
import pybel
import argparse
import numpy
from mayolmol.descriptors import cdkdescui, ob
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def spectrophores(dataset):
    """ Compute the spectrophores for a dataset """
    try:
        print '\tSpectrophores'
        specs = ob.spectrophores(pybel.readfile('sdf', dataset))
        dataset_root, dataset_name = op.split(dataset)
        dataset_name = op.splitext(dataset_name)[0]
        numpy.savetxt(op.join(dataset_root, dataset_name + '-ob-spectrophores.csv'),
                      specs, fmt='%.6f', delimiter=',')
        print '\tSpectrophores computed succesfully'
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

    #CDKDescUI based properties
    CDK_DEFAULT_TYPES = ['constitutional', 'geometric']
    CDK_DEFAULT_FINGERPRINTS = ['maccs', 'estate']

    for dataset in datasets:
        print 'Computing properties for %s' % dataset

        for desc_type in CDK_DEFAULT_TYPES:
            print '\t' + desc_type
            cdkdescui.CDKDescUIDriver().compute_type(dataset,
                                                     op.splitext(dataset)[0] + '-cdk-' + desc_type + '.csv',
                                                     desc_type=desc_type,
                                                     addH=True)
        for fingerprint in CDK_DEFAULT_FINGERPRINTS:
            print '\t' + fingerprint
            cdkdescui.CDKDescUIDriver().compute_fingerprint(dataset,
                                                            op.splitext(dataset)[0] + '-cdk-' + fingerprint + '.csv',
                                                            fingerprint=fingerprint,
                                                            addH=True)
        spectrophores(dataset)