"""
 Some data transformations to allow easy read of the properties in data analysis tools
 like weka or orange.
"""
import glob
import os
import os.path as op
import numpy as np
from mayolmol.mlmusings import mlio
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR

def infer_classes(y, max_distinct=10):
    """ Return the present classes in y or None if this is a regression problem.
        Just for the DSSToX data.
    """
    yunique = np.unique(y)
    if len(yunique) > max_distinct:
        return None
    return sorted(yunique)

def read_y(root, dataset):
    return read_y_from_master(op.join(root, dataset, dataset + '-master.csv'))

def read_y_from_master(masterfile):
    with open(masterfile) as master:
        master.next()
        y = [float(line.split(',')[2]) for line in master]
        return np.array(y)

def cdkdeskuifps2dense(cdkdescui_fpfile, sep=' '):
    with open(cdkdescui_fpfile) as src:
        header = src.next()
        name = header.split()[1]
        num_bits = int(header.split()[2])
        x = []
        for line in src:
            values_str = line.partition(sep)[2].strip()
            values_str = values_str.strip()[1:-1].split(',')
            values = [0] * num_bits
            if len(values_str) and len(values_str[0]):
                for bit in map(int, values_str):
                    values[bit] = 1
            x.append(values)
        return np.array(x), name

def floatOrNaN(string):
    try:
        return float(string)
    except Exception:
        return float('NaN')

def cdkdeskui2dense(cdkdescui_fpfile, sep='\t'):
    with open(cdkdescui_fpfile) as src:
        header = src.next().strip()
        features = header.split(sep)[1:]
        x = [map(floatOrNaN, line.strip().split(sep)[1:]) for line in src if len(line.strip())]
        return np.array(x[0:-1]), features

def prop4da(dataset):
    root, name = op.split(dataset)
    name = op.splitext(name)[0]
    masterfile = op.join(root, name + '-master.csv')
    y = read_y_from_master(masterfile)
    classes = infer_classes(y)

    #Process CDK descriptors
    for descs in glob.glob(op.join(root, '*-cdk-*.csv')):
        with open(descs) as reader:
            header = reader.next()
            if header.startswith('Title'):
                x, features = cdkdeskui2dense(descs)
                mlio.save_arff(x, y, op.splitext(descs)[0] + '.arff', feature_names=features, classes=classes)
                mlio.save_tab(x, y, op.splitext(descs)[0] + '.txt', classes=classes)
            else:
                x, relation_name = cdkdeskuifps2dense(descs)
                features = mlio.generate_names(x.shape[0], descs)
                mlio.save_arff(x, y, op.splitext(descs)[0] + '.arff', relation_name=relation_name, classes=classes, feature_names=features)
                mlio.save_tab(x, y, op.splitext(descs)[0] + '.txt', classes=classes)

    #Process ob spectrophores
    specs = op.join(root, name + '-ob-spectrophores.csv')
    with open(specs) as reader:
        specs = []
        for line in reader:
            specs.append(map(lambda a: float(a.strip()), line.split(',')))
        x = np.array(specs)
    feature_names = mlio.generate_names(len(specs[0]))
    mlio.save_arff(x, y, op.join(root, name + '-ob-spectrophores.arff'), classes=classes, feature_names=feature_names)
    mlio.save_tab(x, y, op.join(root, name + '-ob-spectrophores.txt'), classes=classes)

if __name__ == '__main__':
    root = DEFAULT_DSSTOX_DIR
    datasets = sorted([name for name in os.listdir(root) if op.isdir(op.join(root, name))])

    for dataset in datasets:
        print dataset
        prop4da(dataset)

#TODO: Save the compound ID too
#TODO: be robust to failed description computation
#TODO: more descriptive feature names
#TODO: treatment of missing values
#TODO: sparse ARFFs to the scene