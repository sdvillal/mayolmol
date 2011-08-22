""" Molecular descriptors using openbabel. """
import pickle
import pybel
import numpy

def spectrophores(mols):
    """
    Compute the spectrophores of the molecules and return a numpy array.
    We use default settings for the spectrophores.
    We assume the molecules have already 3D coordinates.
    TODO: make robust / more defensive
    """
    spectromaker = pybel.ob.OBSpectrophore()
    specs = []
    for mol in mols:
        try:
            print mol.title
            #if mol.title != 'Density-train-6878':  #TODO: research into this molecule: OBSpectrophore::GetSpectrophore() error: not enough atoms in molecule
            specs.append(spectromaker.GetSpectrophore(mol.OBMol))
        except Exception, e:
            print 'failed to compute the spectrophore for mol %s' % mol.title
            print e

    #Check if any spectrophore computation failed and if so fill the corresponding vector with NaNs
    for i, spec in enumerate(specs):
        if not len(spec):
            specs[i] = [float('NaN')] * len(specs[0]) #TODO: Q&D, this fails if the first spec has failed itself, fix

    return numpy.array(specs)