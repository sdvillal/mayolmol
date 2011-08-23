"""
 Some data transformations to allow easy read of the properties in data analysis tools
 like weka or orange.
"""
import argparse
import os
import os.path as op
import numpy as np
import glob
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def infer_classes(y):
    """ Return the present classes in y or None if this is a regression problem.
        Just for the DSSToX data.
    """
    yunique = np.unique(y)
    if len(yunique) > 10:
        return None
    return sorted(yunique)


def read_y(root, dataset):
    with open(op.join(root, dataset + '-master.csv')) as master:
        master.next()
        y = [float(line.split(',')[2]) for line in master]
        return np.array(y)

if __name__ == '__main__':

    root = DEFAULT_DSSTOX_DIR
    datasets = sorted([name for name in os.listdir(root) if op.isdir(op.join(root, name))])

    for dataset in datasets:
        y = read_y(dataset, root)
        classes = infer_classes(y)
        #Process ob spectrophores
        specs = glob.glob(op.join(root, '*ob-spec*.csv'))


