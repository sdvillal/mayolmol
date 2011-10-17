# -*- coding: utf-8 -*-
""" Simple I/O without dependencies to any non-standard package other than numpy.
    mldata-utils, arff, orange and the like could be useful here.
    Requires python >= 2.6
"""
from __future__ import with_statement
import os.path as op
import shlex
import csv
import math
import numpy as np
import pybel

def generate_names(num, prefix='f-'):
    num_digits = len(str(num - 1))
    return [prefix + str(fNum).zfill(num_digits) for fNum in range(num)]

def load_arff(src, rename_classes = True):
    """ Load a dense arff with continuous features and a class as the last attribute.
        No support for sparsity, string, nominal or date attributes, missing values,
        weights, comments and other goodies, no error checking, but this will do for the moment.
        There are many alternatives, the only one that does not add dependencies is
        scipy's arffloader, but it is quite buggy at the moment.
    """
    name = None
    attributes = []
    classes = {}
    x = []
    y = []
    with open(src) as src:
        #Relation name
        for line in src:
            if line.strip().lower().startswith('@relation'):
                name = shlex.split(line.strip())[1]
                break
                #Attributes
        for line in src:
            if line.strip().lower().startswith('@attribute'):
                _, fName, spec = shlex.split(line.strip())
                attributes.append(fName)
                if spec.startswith('{'):
                    for clazz in spec[1:-1].split(','):
                        classes[clazz.strip()] = len(classes)
            elif line.strip().lower().startswith('@data'):
                break
                #Data
        if rename_classes:
            for line in src:
                data = line.strip().split(',')
                if len(data) == len(attributes):  #Lame check
                    x.append(map(float, data[:-1]))
                    y.append(classes[data[-1]])
        else:
            for line in src:
                data = line.strip().split(',')
                if len(data) == len(attributes):  #Lame check
                    x.append(map(float, data[:-1]))
                    y.append(float(data[-1]))
            
    return name, attributes, classes, np.array(x), np.array(y)

def save_tab(x, y, dest, format='%.8g', classes=None):
    """ This should be saved with .txt or .csv extension, it is NOT tab
     See http://orange.biolab.si/doc/reference/tabdelimited.htm
    """
    ne, nf = x.shape
    writer = csv.writer(open(dest, "w"), delimiter='\t')
    writer.writerow(['C#feature-' + str(i) for i in range(nf)] + (['cD#class'] if classes else ['c#class']))
    for i in range(ne):
        row = []
        for j in range(nf):
            row += [format % x[i][j]]
        row += [y[i]]
        writer.writerow(row)

def save_arff(x, y, dest, relation_name=None, feature_names=None, format='%.8g', classes=None):
    #x is the matrix of (instances*descriptors) and y is the vector of classes. The attributes values are reals here.
    ne, nf = x.shape
    if not feature_names: feature_names = generate_names(nf)
    if not relation_name: relation_name = op.splitext(op.split(dest)[1])[0]
    with open(dest, 'w') as dest:
        dest.write('@relation ' + relation_name + '\n\n')
        for fName in feature_names:
            dest.write('@attribute ' + fName + ' real\n')
        if not classes:
            classes = 'REAL'
        else:
            classes = '{' +','.join(map(str,classes)) + '}'
        #        classes = ",".join(map(str, map(int, sorted(np.unique(y)))))
        dest.write('@attribute class ' + classes + '\n')
        dest.write('@data\n')
        for row in xrange(ne):
            instance = map(lambda a: format % a if not np.isnan(a) else '?', x[row, :])
            dest.write(','.join(instance))
            dest.write(',' +(str(y[row]) if not np.isnan(y[row]) else '?') + '\n')

def mergearffs(dest, arff1, *args):
    if not dest:
        dest = op.splitext(arff1)[0] + '-merged.arff'
    with open(dest, 'w') as dest:
        with open(arff1) as src:
            for line in src:
                dest.write(line)
        for other_arff in args:
            with open(other_arff) as src:
                for line in src:
                    if line.strip() == '@data':
                        break
                for line in src:
                    dest.write(line)

def merge_arff2(directory, dest_arff, arff1, arff2, rename_classes):
    """Function to merge 2 .arff files that share: the relation name,
    the class to predict as last column, the id of the instances as 
    first column, the same instances. The files present different 
    features. It is somehow an 'horizontal' merge. NB: there is no
    check realized at the moment, but the order of the instances should
    be the same in both files. In case of a classification prolem and 
    if rename_class is set to True, the class will appear in the last 
    column as 0, 1, ... nb class and refer to the class definition order 
    of @attribute class {}"""
    output_file = op.join(directory, dest_arff)
    file1 = op.join(directory, arff1)
    file2 = op.join(directory, arff2)
    relation, attributes1, classes, x1, y = load_arff(file1, rename_classes)
    _, attributes2, _, x2, _ = load_arff(file2)
    attributes = attributes1[:-1] + attributes2[1:-1]
    x22 = np.delete(x2, 0, 1)
    x = np.hstack((x1,x22))
    save_arff(x, y, output_file, relation_name = relation, feature_names = attributes, classes = classes)
    return  relation, classes, attributes, x, y

def data_fields(directory, sdf_file):
    """This function returns the list of fields (other than atom 
    coordinates) present in an .sdf file"""
    mols = pybel.readfile("sdf", op.join(directory, sdf_file))
    fields = []
    for mol in mols:
        field = mol.data.keys()
        for item in field:
            if item not in fields and item not in ["OpenBabel Symmetry Classes"]:
                fields.append(item)
    return fields        
    
        
    
    
#print merge_arff2("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example", "final.arff", "4mol_prepared-cdk.arff", "4mol_prepared-cdk-estate.arff")
#print load_arff("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example/4mol_prepared-cdk.arff")
#print data_fields("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example", "1000mol.sdf")
