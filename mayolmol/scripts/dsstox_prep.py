# -*- coding: utf-8 -*-
"""
Preparation of DSSTox datasets for further processing.
See: http://www.epa.gov/nrmrl/std/cppb/qsar/DataSets.zip
Others:
  - http://www.epa.gov/nrmrl/std/cppb/qsar/
  - http://www.opentox.org/dev/documentation/components/dsstoxlazar
  - http://www.cheminformatics.org/datasets/index.shtml#tox
  - OpenToX and the like

TODO: log per-dataset info
"""
import multiprocessing
import os.path as op
import os
import pybel
import glob
import csv
import operator
import urllib
from zipfile import ZipFile
import argparse

DEFAULT_DSSTOX_DIR = op.join(op.expanduser('~'), 'Proyectos', 'bsc', 'data', 'filtering', 'dsstox')

def rename_mols_by_index(mols, prefix=''):
    num_mols_num_chars = len(str(len(mols)))
    for i, mol in enumerate(mols):
        mol.data['OldTitle'] = mol.title
        mol.title = prefix + str(i).zfill(num_mols_num_chars)

def save_mols(mols, dest, format='sdf'):
    with open(dest, 'w') as dest:
        for mol in mols:
            dest.write(mol.write(format))

def select_columns(csv_file, columns=None):
    projection = []
    with open(csv_file) as reader:
        reader = csv.reader(reader)
        for values in reader:
            if not columns: projection.append(values)
            else: projection.append(operator.itemgetter(*columns)(values))
    return projection

def create_master_table(sdf_file, dest_file, fields=None):
    if not fields: fields = ['Tox']
    reader = pybel.readfile('sdf', sdf_file)  #Need to tell to implement __exit__
    with open(dest_file, 'w') as writer:
        #Header
        writer.write(','.join(['mol_id', 'smiles'] + fields) + '\n')
        #Data
        for mol in reader:
            values = [mol.title, mol.write('can').split()[0]]
            for field in fields:
                if mol.data[field]:
                    values.append(mol.data[field])
                else:
                    values.append('')
            writer.write(','.join(values) + '\n')

def create_saliviewer_input(master_file, dest_file):
    input = select_columns(master_file)[1:] #Remove the header
    with open(dest_file, 'w') as output:
        output = csv.writer(output, delimiter=' ')
        for values in input:
            output.writerow(values)

def prepare_dsstox_dataset(root, name, dest=None):
    """ This method bootstraps the analysis of DSSTox data.
       - Rename the compounds
       - Merge train/test
       - Generate 3D conformations
       - Save "master" and "saliviewer" tables
       - Redirects stdout/stderr to a "prepare.log" file
    """
    if not dest: dest = root

    print 'Reading %s' % name
    trainMols = list(pybel.readfile('sdf', op.join(root, name + '_training.sdf')))
    testMols = list(pybel.readfile('sdf', op.join(root, name + '_prediction.sdf')))

    datasetRoot = op.join(dest, name)
    print '\tCreating dataset root: %s' % datasetRoot
    if not op.exists(datasetRoot):
        os.makedirs(datasetRoot)

    print '\tRenaming the compounds to keep track of the provenance'
    rename_mols_by_index(trainMols, name + '-train-')
    rename_mols_by_index(testMols, name + '-test-')

    print '\tGenerating conformations'
    for mol in trainMols + testMols:
        mol.make3D()

    print '\tSaving compounds'
    destSDF = op.join(datasetRoot, name + '.sdf')
    save_mols(trainMols + testMols, destSDF)

    masterTable = op.join(datasetRoot, name + '-master.csv')
    print '\tCreating \"master\" table: %s' % masterTable
    create_master_table(destSDF, masterTable)

    saliTable = op.join(datasetRoot, name + '-saliviewer.csv')
    print '\tCreating \"saliviewer\" table: %s' % saliTable
    create_saliviewer_input(masterTable, saliTable)

if __name__ == '__main__':
    #######################################
    # Parse options
    #######################################
    parser = argparse.ArgumentParser(description='DSSTox preparation script')
    parser.add_argument('-r', '--root',
                        type=argparse.FileType(),
                        help='Root directory from where the original data will be read')
    args = parser.parse_args()

    root = args.root
    if not root:
        root = DEFAULT_DSSTOX_DIR
    dest = args.root

    #######################################
    # Make sure we have the original data
    #######################################
    def present_datasets(root):
        """ Search the dsstox-like datasets in a directory and return their names """
        datasets = set()
        for fn in glob.glob(op.join(root, '*.sdf')):
            name = op.splitext(op.split(fn)[1])[0].split('_')[0]
            datasets.add(name)
        return sorted(datasets)

    datasets = present_datasets(root)

    if not len(datasets):
        compressedFile = op.join(root, 'DataSets.zip')
        if not op.exists(compressedFile):
            print 'Downloading DSSTox datasets to: %s' % compressedFile
            os.makedirs(root)
            urllib.urlretrieve('http://www.epa.gov/nrmrl/std/cppb/qsar/DataSets.zip',
                               compressedFile)
        print 'Decompressing DSSTox datasets to: %s' % root
        ZipFile(compressedFile).extractall(root)
        datasets = present_datasets(root)

    #######################################
    # Prepare the datasets
    #######################################
    def prepare(dataset):
        prepare_dsstox_dataset(root, dataset, dest)

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(prepare, datasets)