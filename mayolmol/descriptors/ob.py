""" Molecular descriptors using openbabel. Author: Santi. Slightly modified by Flo."""
import pybel
import numpy

def spectrophores(mols):
    """
    Compute the spectrophores of the molecules and return a numpy array.
    We use default settings for the spectrophores.
    We assume the molecules have already 3D coordinates.
    """
    spectromaker = pybel.ob.OBSpectrophore()
    specs = []
    for mol in mols:
        try:
            spec = spectromaker.GetSpectrophore(mol.OBMol)
            spec = list(spec)
            spec.insert(0, mol.title)
            spec = tuple(spec)
            specs.append(spec)
        except Exception, e:
            print 'failed to compute the spectrophore for mol %s' % mol.title
            print e
    #Check if any spectrophore computation failed and if so fill the corresponding vector with NaNs
    for i, spec in enumerate(specs):
        if len(spec) ==1:
            print spec
            specs[i][1:] = [float('NaN')] * 48
    #a = [('id', numpy.str_, len(specs[0][0]))]
    a = [('id', 'a'+str(len(specs[0][0])))]
    for i in xrange(48):
        a.append(('spec_' + str(i) , '<f8'))
    return numpy.array(specs, dtype=a)

