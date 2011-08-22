# -*- coding: utf-8 -*-
""" Simple I/O without dependencies to any non-standard package other than numpy.
    mldata-utils, arff, orange and the like could be useful here.
    Requires python >= 2.6
"""
import os.path as op
import shlex
import csv
import numpy as np

def generate_names(num, prefix='f-'):
    num_digits = len(str(num - 1))
    return [prefix + str(fNum).zfill(num_digits) for fNum in range(num)]

def load_arff(src):
    """ Load a dense arff with continuous features and a class as the last attribute.
        No support for sparsity, string, nominal or date attributes, missing values,
        weights, comments and other goodies, no error checking, but this will do for the moment.
        There are many alternatives, the only one that does not add dependencies is
        scipy's arffloader, but it is quite buggy.
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
        for line in src:
            data = line.strip().split(',')
            if len(data) == len(attributes):  #Lame check
                x.append(map(float, data[:-1]))
                y.append(classes[data[-1]])

        return name, attributes, classes, np.array(x), np.array(y)

def save_tab(x, y, dest, format='%.8g'):
    ne, nf = x.shape
    writer = csv.writer(open(dest, "w"))
    writer.writerow(['C#feature-' + str(i) for i in range(nf)] + ['c#class'])
    for i in range(ne):
        row = []
        for j in range(nf):
            row += [format % x[i][j]]
        row += [int(y[i])]
        writer.writerow(row)

def save_arff(x, y, dest, relation_name='Unknown', feature_names=None, format='%.8g', classes=None):
    ne, nf = x.shape
    if not feature_names: feature_names = generate_names(nf)
    with open(dest, 'w') as dest:
        dest.write('@relation ' + relation_name + '\n\n')
        for fName in feature_names:
            dest.write('@attribute ' + fName + ' real\n')
        classes = ",".join(map(str, map(int, sorted(np.unique(y)))))
        dest.write('@attribute class {' + classes + '}\n')
        dest.write('@data\n')
        for row in xrange(ne):
            dest.write(','.join((format % val for val in x[row,:])))
            dest.write(',' + str(int(y[row])) + '\n')

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
                    if line.strip()=='@data':
                        break
                for line in src:
                    dest.write(line)