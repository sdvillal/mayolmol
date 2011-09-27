#!/usr/bin/env python
import subprocess
import os.path as op
import time
import croc

def prepare_input(directory, input_file, scoredlabel_file):
    #input file will be a 3-columns file with ID, score (between 0 and 1) and label (the real value, 0 for negative and 1 for positive)
    f = open(op.join(directory, input_file), 'r')
    g = open(op.join(directory, scoredlabel_file), 'a')
    for line in f:
        columns = line.split()
        g.write(columns[1:])
        g.write("\n")
    f.close()
    g.close()
    
def compute_curve(directory, scoredlabel_file, curve_file):
    args = "croc-curve < " + op.join(directory, scoredlabel_file) + " > " + op.join(directory, curve_file)
    curve = subprocess.Popen(args, shell=True)
    curve.wait()

#deprecated    
#def compute_auc(directory, curve_file):
    #args = "croc-area < " + op.join(directory, curve_file) + " > " + op.join(directory, "auc")
    #a = subprocess.Popen(args, shell=True)
    #a.wait()
    #r = open(op.join(directory, "auc"), 'r')
    #auc = r.read()
    #r.close()
    #return auc.rstrip("\n")
    
def compute_auc_with_API(directory, curve_file):
    curser = open(op.join(directory, curve_file),'r')
    curv = croc.Curve.read_from_file(curser)
    auc = curv.area()
    curser.close()
    return auc
    
def compute_enrichment(directory, scoredlabel_file, curve_file):
    curser = open(op.join(directory, scoredlabel_file),'r')
    instances = croc.ScoredData.read_from_file(curser)
    enrichment = croc.SlantedAC(instances.sweep_threshold())
    curser.close()
    out = open(op.join(directory, curve_file), "w")
    enrichment.write_to_file(out) 
    out.close()
 
#print compute_auc_with_API("/mmb/pluto/fmontanari/Escritorio/testCROC", "coordinates.curve")
#print compute_enrichment("/mmb/pluto/fmontanari/Escritorio/testCROC","input.scored-label", "enrichment.curve")        
    
        
    
