# -*- coding: utf-8 -*-
import pybel
from numpy import *
import pca_module

def read_edu_table(filepath):
    molecules = []
    with open(filepath) as input:
        for line in input:
            fields = line.split(',')
            smiles = fields[0][1:-1]
            name = fields[1]
            activity = float(fields[2])
            molecule = pybel.readstring('smi', smiles)  #Analiza los smiles para obtener una molecula en el ordenador
            maccs = molecule.calcfp("MACCS")
            molecules.append((smiles, name, activity, molecule, maccs.bits))
    return molecules

molecules = read_edu_table()

activities = array([molecule[2] for molecule in molecules]).reshape(-1,1)