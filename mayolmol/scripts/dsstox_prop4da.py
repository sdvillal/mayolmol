"""
 Some data transformations to allow easy read of the properties in data analysis tools
 like weka or orange.
"""
from __future__ import with_statement
import glob
import os
import os.path as op
import numpy as np
from mayolmol.mlmusings import mlio
from mayolmol.scripts.dsstox_prep import DEFAULT_DSSTOX_DIR
import itertools
import pybel

def infer_classes(y, max_distinct=10):
    """ Return the present classes in y or None if this is a regression problem.
        Just for the DSSToX data.
    """
    yunique = np.unique(y)
    if len(yunique) > max_distinct:
        return None
    return sorted(yunique)
    
def infer_classes_from_initial_data(y, idfun=None, max_distinct=10):
    """ Return the present classes in y or None if this is a regression 
    problem. Doesn't use numpy, y is a simple python list. Thanks to 
    http://www.peterbe.com/plog/uniqifiers-benchmark"""
    if not idfun:
        def idfun(x): return x
    seen = {}
    result = []
    for val in y:
        marker = idfun(val)
        if marker in seen: continue
        seen[marker] = 1
        result.append(val)    
    if len(result) > max_distinct:
        return None
    return result
        
def read_y(root, dataset):
    return read_y_from_master(op.join(root, dataset, dataset + '-master.csv'))
            
def read_y_from_initial_data(root, dataset, label):
    mols = pybel.readfile("sdf", op.join(root, dataset))
    y = []
    for mol in mols:
        y.append(mol.data[label])
    return y

def read_y_from_master(masterfile):
    with open(masterfile) as master:
        master.next()
        try:
            y = [float(line.split(',')[2]) for line in master]
        except ValueError:
            y = [line.split(',')[2] for line in master]
        return np.array(y)
        
def from_class_to_index(y, directory):
    classes = infer_classes_from_initial_data(y)
    index1 = {} 
    index2 = {}
    f = open(op.join(directory, "class_index.txt"), 'w')
    for classe in classes:
        index1[classe] = classes.index(classe)
        index2[classes.index(classe)] = classe
    for key,value in index1.iteritems():
        f.write(key)
        f.write("\t")
        f.write(str(value))
        f.write("\n")
    f.close()
    return index1, index2
    
def read_index(directory):
    f = open(op.join(directory, "class_index.txt"), 'r')
    index1 = {}
    index2 = {}
    for line in f:
        index1[line.split()[0]] = int(line.split()[1])
        index2[int(line.split()[1])] = line.split()[0]
    return index1, index2
            
def rename_classes(y, directory):
    y2 = []
    index, _ = read_index(directory)
    for classe in y:
        y2.append(index[classe])
    return np.array(y2), index

def cdkdeskuifps2dense(cdkdescui_fpfile, sep=' ', keep_id = False):
    with open(cdkdescui_fpfile) as src:
        header = src.next()
        name = header.split()[1]
        num_bits = int(header.split()[2])
        x = []
        if not keep_id:
            for line in src:
                values_str = line.partition(sep)[2].strip()
                values_str = values_str.strip()[1:-1].split(',')
                values = [0] * num_bits
                if len(values_str) and len(values_str[0]):
                    for bit in map(int, values_str):
                        values[bit] = 1
                x.append(values)
            return np.array(x), name
        else:
            for line in src:
                values_str = line.partition(sep)[2].strip()
                values_str = values_str.strip()[1:-1].split(',')
                id = int(line.partition(sep)[0].strip())
                values = [0] * num_bits
                if len(values_str) and len(values_str[0]):
                    for bit in map(int, values_str):
                        values[bit] = 1
                values = [id] + values
                x.append(values)
            return np.array(x), name

def floatOrNaN(string):
    try:
        return float(string)
    except Exception:
        return float('NaN')
        
def numeric_class_proportions(y):
    """This function gives the number of instances for each class (can 
    be boolean or int) in the input dataset. Of course, it should be 
    used only if it is a classification problem with no string values. 
    Thanks to http://stackoverflow.com/questions/4651683/numpy-grouping
    -using-itertools-groupby-performance"""
    total = len(y)
    y.sort()
    diff = np.concatenate(([1],np.diff(y)))
    idx = np.concatenate((np.where(diff)[0],[len(y)]))
    index = np.empty(len(idx)-1, dtype='u2,u2')
    index['f0']=y[idx[:-1]]
    index['f1']=np.diff(idx)
    return total, index
    
def string_class_proportions(y):
    """Here, the class values are strings or a mix of real and string 
    values. Thanks to http://stackoverflow.com/questions/4651683/numpy-
    grouping-using-itertools-groupby-performance"""
    total = len(y)
    y.sort()
    yunique = np.unique(y)
    groups = ((k,sum(1 for i in g)) for k,g in itertools.groupby(y))
    index = np.fromiter(groups,dtype='|S1,u2')
    return total, index

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

def spectrophores_to_arff(directory, master_file, spec_csv, to_predict):
    y = read_y_from_master(op.join(directory,master_file))
    classes = infer_classes(y)
    specs = op.join(directory, spec_csv)
    f = open(specs, 'r')
    data = []
    for line in f:
        #data.append(map(lambda a: float(a.strip()), line.split(',')))
        if len(line.strip()):
            data.append(map(floatOrNaN, line.strip().split(",")[:-1]))
    x = np.array(data)
    feature_names = ['ID']
    f.close()
    for i in range(48):
        feature_names.append('Spec'+str(i))
    arff_file = op.join(directory, op.splitext(spec_csv)[0] + ".arff")
    mlio.save_arff(x, y, arff_file, relation_name=to_predict, feature_names=feature_names, classes=classes)

def cdk_desc_to_arff(directory, master_file, desc_csv, to_predict):
    y = read_y_from_master(op.join(directory,master_file))
    classes = infer_classes(y)
    descs = op.join(directory, desc_csv)
    f = open(descs, 'r')
    data = []
    line1 = f.readline()
    feature_names = ["ID"] + [name for name in line1.split()[1:]]
    for line in f:
        if len(line.strip()):
            data.append(map(floatOrNaN, line.strip().split("\t")))        
    f.close()
    x = np.array(data)
    arff_file = op.join(directory, op.splitext(desc_csv)[0] + ".arff")
    mlio.save_arff(x, y, arff_file, relation_name=to_predict, feature_names=feature_names, classes=classes)
    
def cdk_fpt_to_arff(directory, master_file, fpt_csv, to_predict, fpt_type):
    y = read_y_from_master(op.join(directory,master_file))
    classes = infer_classes(y)    
    fpts = op.join(directory, fpt_csv)
    f = open(fpts, 'r')
    x, _ = cdkdeskuifps2dense(fpts, keep_id=True)
    feature_names = ['ID']
    if fpt_type == "maccs":
        for i in range(166):
            feature_names.append("maccs" + str(i))
    elif fpt_type == "estate":
        for i in range(79):
            feature_names.append("estate" + str(i))
    elif fpt_type == "extended":
        for i in range(1024):
            feature_names.append("extended" + str(i))
    else: 
        print "Fingerprint type currently not supported."
    arff_file = op.join(directory, op.splitext(fpt_csv)[0] + ".arff")
    mlio.save_arff(x, y, arff_file, relation_name=to_predict, feature_names=feature_names, classes=classes)
    
def analyze_class(directory, dataset, label, max_classes=10):
    y = read_y_from_initial_data(directory, dataset, label)
    yunique = infer_classes_from_initial_data(y, max_classes)
    if yunique:
        print "It is a classification problem, with %i different classes."%len(yunique)
        print "Now renaming the classes into indinces..."
        y, index = rename_classes(y)
        print "The schema followed to rename the classes is the following:"
        print index
        counts = numeric_class_proportions(y)
        return counts
    else:
        print "It is a regression problem." 
        counts = len(y)
        return [counts]
    
if __name__ == '__main__':
    root = DEFAULT_DSSTOX_DIR
    datasets = sorted([name for name in os.listdir(root) if op.isdir(op.join(root, name))])

    for dataset in datasets:
        print dataset
        prop4da(dataset)
    #spectrophores_to_arff("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example", "4mol_prepared_master.csv", "4mol_prepared-ob-spectrophores.csv", "tPSA")
    #cdk_desc_to_arff("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example", "1000mol_dirty_prepared_master.csv", "1000mol_dirty_prepared-cdk.csv", "tPSA")
    #cdk_fpt_to_arff("/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example", "1000mol_dirty_prepared_master.csv", "1000mol_dirty_prepared-cdk-estate.csv", "tPSA", "estate")
    #print string_class_proportions(np.array(["a","a",2,"b","a","a",2]))
    #print numeric_class_proportions(np.array([False, True, False, False, False, True]))
    #print infer_classes_from_initial_data(["1", "1", "1.05", "?", "0.5", "?"])
    #print from_class_to_index(["1", "1", "1.05", "?", "0.5", "?"], "/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example")
    #print rename_classes(["1", "1", "1.05", "?", "0.5", "?"],"/mmb/pluto/fmontanari/Build/FAFDrugs2.2/example")

#TODO: Save the compound ID too
#TODO: be robust to failed description computation
#TODO: more descriptive feature names
#TODO: treatment of missing values
#TODO: sparse ARFFs to the scene
