# -*- coding: utf-8 -*-
#Created by Santi, a few additional functions by Flo
from __future__ import with_statement
import os.path as op
import os
import pybel
import glob
import csv
import operator
import sys

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
    input = select_columns(master_file, (1, 0, 2))[1:] #Remove the header
    with open(dest_file, 'w') as output:
        output = csv.writer(output, delimiter=' ')
        for values in input:
            output.writerow(values)
            
def desalt(dataset, output):
    """Reading and if necessary remove salts in dataset and write a
    new output .sdf with pybel module StripSalts() from OBMol class""" 
    mols = pybel.readfile("sdf", dataset)
    outputf = pybel.Outputfile("sdf", output, overwrite=True)
    for mol in mols:
        if mol.OBMol.StripSalts():
            #print "removing salts."
            outputf.write(mol)
        else:
            outputf.write(mol)
    outputf.close()
    return output
    
def keep_unique(mols):
    '''NB: The pb of the dictionary is that it doesn't keep the order of
    the original file, which can be a pain for the user... -> SOLVED'''
    seen_can = {}
    unique = []
    for mol in mols:
        mol.addh()
        can = mol.write("can")
        if not can in seen_can:
            seen_can[can] = mol
            unique.append(mol)
    return unique

def removeMissingValue(mols, field):
    #In case the user wants to learn a property of his dataset for which 
    #some molecule don't have a value, we should get read of those useless 
    #molecules.
    to_keep = []
    for mol in mols:
        if mol.data.has_key(field) and mol.data[field] not in [None, "NULL", "ERR", "?", "MISSING", " "]:
            to_keep.append(mol)
    return to_keep    

def prepare_user_dataset(root, dataset_name, field, dest=None, overwrite=False):
    """ This method bootstraps the analysis of the user input data.
       - Remove salts
       - Delete duplicated molecules
       - Remove molecules with missing class
       - Rename the compounds
       - Generate 3D conformations
       - Save "master" and "saliviewer" tables
       - Redirects stdout/stderr to a "prepare.log" file
    """
    if not dest: dest = root
    dataset = op.join(root, dataset_name)
    dest_sdf = op.join(dest, dataset_name[:-4] + "_prepared.sdf")
    if op.exists(dest_sdf) and not overwrite:
        print '%s is already there and not overwriting requested' % dest_sdf
        return

    print "Desalting molecules..."
    dataset = desalt(dataset, op.splitext(dataset)[0] + "_desalted.sdf")
    print 'Reading dataset into pybel molecules...'
    mols = pybel.readfile('sdf', dataset)
    print 'Removing duplicated molecules...'
    unique_mols = keep_unique(mols)
    print 'Removing missing values in the field of interest...'
    unique_mols = removeMissingValue(unique_mols, field) 
    print 'Re-indexing the compounds...'
    rename_mols_by_index(unique_mols)

    print '\tGenerating conformations'
    for mol in unique_mols:
        #Some molecules may produce segfault on make3D
        #See bug report at https://sourceforge.net/tracker/?func=detail&aid=3374324&group_id=40728&atid=428740
        #Train 3988: OC(=O)[C@]1(C)CCC[C@]2(C1CC[C@]13C2CC[C@](C3)([C@]2(C1)OC2)O)C
        #Train 4205: CC(CCC[C@H]([C@H]1CC[C@@H]2[C@]1(C)CC[C@H]1[C@H]2CC2([C@@H]3[C@]1(C)CC[C@@H](C3)Br)S(=O)(=O)CCS2(=O)=O)C)C
        #This kind of fatal errors are worrying, is there any robust way of controlling them in python/java? Will need to create one
        try:
            print 'Conformation for %s' % mol.title
            mol.make3D()
        except Exception:
            print 'Error computing a 3D conformation for %s' % mol.title

    print '\tSaving compounds'
    save_mols(unique_mols, dest_sdf)

    master_table = op.join(dest_sdf[:-4] + '_master.csv')
    print '\tCreating \"master\" table: %s' % master_table
    create_master_table(dest_sdf, master_table, [field])

    sali_table = op.join(dest_sdf[:-4] + '_saliviewer.csv')
    print '\tCreating \"saliviewer\" table: %s' % sali_table
    create_saliviewer_input(master_table, sali_table)

if __name__ == '__main__':
    if len(sys.argv) > 3:
        user_data = sys.argv[1] #the name of the sdf file
        to_predict = sys.argv[2] #the name of the column with the values to predict 
        directory = sys.argv[3] #where to find the dataset and store the results
    #prepare_user_dataset("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example/", "1000mol_dirty.sdf", "tPSA")
        if op.exists(op.join(directory, user_data)) and to_predict != "":
            prepare_user_dataset(directory, user_data, to_predict)
        else:
            print "Problem with the input. Try again."
    else:
            print "Problem with the input. Try again."
