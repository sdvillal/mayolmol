import pybel

#Add MACCS to pybel
pybel.fps.append("MACCS")
pybel._fingerprinters = pybel._getplugins(pybel.ob.OBFingerprint.FindFingerprint, pybel.fps)

def spectrophores(mols):
    spectromaker = pybel.ob.OBSpectrophore()
    specs = []
    for mol in mols:
        mol.make3D()
        specs.append(spectromaker.GetSpectrophore(mol.OBMol))
    return specs