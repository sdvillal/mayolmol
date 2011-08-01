""" Molecular descriptors using openbabel. """
import pybel
import numpy

#Add MACCS to pybel
pybel.fps.append("MACCS")
pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)

def spectrophores(mols):
    """
    Compute the spectrophores of the molecules and return a numpy array.
    We use default settings for the spectrophores.
    We assume the molecules have already 3D coordinates.
    """
    spectromaker = pybel.ob.OBSpectrophore()
    specs = [spectromaker.GetSpectrophore(mol.OBMol) for mol in mols]
    return numpy.array(specs)

#    specs = ob_descriptors.spectrophores(trainMols + testMols)
#    numpy.savetxt(op.join(datasetRoot, name + '-spectrophores.csv'),
#                  specs, fmt='%.6f', delimiter=',')
