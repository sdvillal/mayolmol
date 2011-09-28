#!/usr/bin/env python
import subprocess
import os.path as op
import os
import time
import croc
import sys

#Why don't we use the CROC API? -> we do now.

def prepare_input(directory, input_file, scoredlabel_file):
    #input file will be a 3-columns file with ID, score (between 0 and 1) and label (the real value, 0 for negative and 1 for positive)
    f = open(op.join(directory, input_file), 'r')
    g = open(op.join(directory, scoredlabel_file), 'a')
    for line in f:
        columns = line.split()
        for i in columns[1:]:
            g.write(i)
            g.write("\t")
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

def write_GNUplot_file(curve_type, directory, curve_file, params_file, image_file=None):
    if op.exists(op.join(directory, params_file)):
        os.remove(op.join(directory, params_file))
        print "Removing existing drawing parameters file."
    f = open(op.join(directory,params_file), 'a')
    f.write("cd '" + directory + "'\n")
    if image_file:
        f.write("set terminal png\n")
        f.write("set output '" + op.join(directory, image_file) + "'\n")
    f.write("set key left box\n")
    if curve_type == "roc":
        f.write("set xlabel 'False positive rate'; set ylabel 'True positive rate';\n")
        f.write("plot [0:1] '" + curve_file + "' with line title 'ROC of your model', x title 'ROC of a random classifier'\n")
    else:
        f.write("set xlabel 'Fraction of the ranked data tested'; set ylabel 'True positive rate'\n")
        f.write("plot [0:1] '" + curve_file + "' with line title 'Enrichment curve of your model', x title 'Enrichment curve of a random classifier'\n")
    if not image_file:
        f.write("pause -1\n")
    f.close()
                
def depict(directory, curve_type, curve_file, params_file, image_file=None):
    write_GNUplot_file(curve_type, directory, curve_file, params_file, image_file)
    args = "gnuplot '" + op.join(directory, params_file) + "'"
    draw = subprocess.Popen(args, shell=True)
    draw.wait()
        
if __name__ == "__main__":
    #print depict("/mmb/pluto/fmontanari/Escritorio/testCROC", "enrichment", "enrichment.curve", "gnuplot.gp", "nicePlot.png")
    #print write_GNUplot_file("roc", "/mmb/pluto/fmontanari/Escritorio/testCROC", "coordinates.curve", "gnuplot.gp")
    #TODO: check input parameters
    if len(sys.argv) == 4:
        directory = sys.argv[1]
        prediction_file = sys.argv[2]
        if not op.exists(op.join(directory, prediction_file)):
            print "There is not such file: %s"%op.join(directory, prediction_file)
            sys.exit()
        model_name = sys.argv[3]
    
    #TODO checks of file and directory
        prepare_input(directory, prediction_file, model_name + ".scored-label")
        compute_curve(directory, model_name + ".scored-label", model_name + ".roc")
        compute_enrichment(directory, model_name + ".scored-label", model_name + ".enrich")
        auc = compute_auc_with_API(directory, model_name + ".roc")
        depict(directory, "roc", model_name + ".roc", "params" + "_" + model_name + "_roc.gp", model_name + "_rocplot.png")
        depict(directory, "enrichment", model_name + ".enrich", "params" + "_" + model_name + "_enrich.gp", model_name + "_enrichplot.png")
    else:
        print "Too many or too little arguments. Please remember:\n -1st argument is the directory where your model output is stored\n -2nd argument is the name of the prediction file\n -3rd argument is the name you want to give to your model."
