# -*- coding: utf-8 -*-
"""
Preparation of DSSTox datasets for further processing.
See: http://www.epa.gov/nrmrl/std/cppb/qsar/DataSets.zip
     http://www.epa.gov/nrmrl/std/cppb/qsar/

Others:
  - http://www.opentox.org/dev/documentation/components/dsstoxlazar
  - http://www.cheminformatics.org/datasets/index.shtml#tox
  - OpenToX and the like
"""
import os.path as op
import os
import pybel
import ob_descriptors
import glob
import csv
import operator
import numpy

def rename_mols_by_index(mols, prefix=''):
    num_mols_num_chars = len(str(len(mols)))
    for i, mol in enumerate(mols):
        mol.title = prefix + str(i).zfill(num_mols_num_chars)

def save_mols(mols, dest, format='sdf'):
    with open(dest, 'w') as dest:
        for mol in mols:
            dest.write(mol.write(format))

def create_master_table(sdf_file, dest_file, fields=None):
    if not fields: fields = ['Tox']
    reader = pybel.readfile('sdf', sdf_file)  #Need to tell to implement __exit__
    with open(dest_file, 'w') as writer:
        #Header
        writer.write(','.join(['molid', 'smiles'] + fields) + '\n')
        #Data
        for mol in reader:
            values = [mol.title, mol.write('can').split()[0]]
            for field in fields:
                if mol.data[field]:
                    values.append(mol.data[field])
                else:
                    values.append('')
            writer.write(','.join(values) + '\n')

def select_columns(csv_file, columns=None):
    projection = []
    with open(csv_file) as reader:
        reader = csv.reader(reader)
        for values in reader:
            if not columns: projection.append(values)
            else: projection.append(operator.itemgetter(*columns)(values))
    return projection

def create_saliviewer_input(master_file, dest_file):
    input = select_columns(master_file)[1:] #Remove the header
    with open(dest_file, 'w') as output:
        output = csv.writer(output, delimiter=' ')
        for values in input:
            output.writerow(values)

def prepare_dsstox_sdfs(root, name):
    #Read molecules
    trainMols = list(pybel.readfile('sdf', op.join(root, name + '_training.sdf')))
    testMols = list(pybel.readfile('sdf', op.join(root, name + '_prediction.sdf')))

    #Rename the compounds to keep track of the provenance
    rename_mols_by_index(trainMols, name + '-train-')
    rename_mols_by_index(testMols, name + '-test-')

    #We will use one dir per dataset
    datasetRoot = op.join(root, name)
    if not op.exists(datasetRoot):
        os.makedirs(datasetRoot)

    #Merge and save
    destSDF = op.join(datasetRoot, name + '.sdf')
    save_mols(trainMols + testMols, destSDF)

    #Create 'master' table
    masterTable = op.join(datasetRoot, name + '-master.csv')
    create_master_table(destSDF, masterTable)

    #Create 'saliviewer' input
    create_saliviewer_input(masterTable, op.join(datasetRoot, name + '-saliviewer.csv'))

    #Spectrophores
    specs = numpy.array(ob_descriptors.spectrophores(trainMols + testMols))
    numpy.savetxt(op.join(datasetRoot, name + '-spectrophores.csv'),
                  specs, fmt='%.6f', delimiter=',')

def present_datasets(root):
    datasets = set()
    for fn in glob.glob(op.join(root, '*.sdf')):
        name = op.splitext(op.split(fn)[1])[0].split('_')[0]
        datasets.add(name)
    return sorted(datasets)

if __name__ == '__main__':
    import sys

    root = '/home/santi/Downloads/______edu/DataSets'
    if len(sys.argv) > 1:
        root = sys.argv[1]

    for dataset in present_datasets(root):
        print 'Processing %s' % dataset
        prepare_dsstox_sdfs(root, dataset)