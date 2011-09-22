#!/usr/bin/env python

import unittest
import dsstox_prep as prep
import pybel
import os.path as op

TDD = op.join(op.split(__file__)[0], "..", "data")

class KnownValues(unittest.TestCase):
    known_desalted = [(op.join(TDD, "mol1_nosalt.sdf") ,op.join(TDD, "mol1_nosalt.sdf")),(op.join(TDD, "mol2_salty.sdf"), op.join(TDD, "mol2_desalted.sdf"))]
    known_duplicate = [(op.join(TDD, "2mols_unique.sdf"),op.join(TDD, "2mols_unique.sdf")),(op.join(TDD, "3mols_dupl.sdf"),op.join(TDD, "2mols_unique.sdf"))]
    known_missingfield = [(op.join(TDD, "2mols_unique.sdf"), op.join(TDD, "2mols_unique.sdf")),(op.join(TDD, "3mols_missingtpsa.sdf"), op.join(TDD, "2mols_tpsa.sdf"))]

    def sdfToMol(self, sdfile):
        mols = list(pybel.readfile("sdf",sdfile))
        return mols

    def molToSmiles(self, mol):
        return mol.write("smi")

    def fileToContent(self, file):
        with open(file, 'r') as f:
            return f.read()

    def test_desalt(self):
        for input, output in self.known_desalted:
            outputfile = prep.desalt(input, op.join(TDD, "test1.sdf"))
            correct = self.sdfToMol(output)
            tocheck = self.sdfToMol(outputfile)
            correctsmiles = [self.molToSmiles(mol) for mol in correct]
            tochecksmiles = [self.molToSmiles(mol) for mol in tocheck]
            self.assertItemsEqual(correctsmiles, tochecksmiles)

    def test_keep_unique(self):
        for input, output in self.known_duplicate:
            molsin = self.sdfToMol(input)
            molsok = self.sdfToMol(output)
            molsout = prep.keep_unique(molsin)
            correctsmiles = [self.molToSmiles(mol) for mol in molsok]
            tochecksmiles = [self.molToSmiles(mol) for mol in molsout]
            self.assertItemsEqual(correctsmiles, tochecksmiles)

    def test_remove_missing(self):
        for input, output in self.known_missingfield:
            molsin = self.sdfToMol(input)
            molsok = self.sdfToMol(output)
            molsout = prep.removeMissingValue(molsin, "tPSA")
            correctsmiles = [self.molToSmiles(mol) for mol in molsok]
            tochecksmiles = [self.molToSmiles(mol) for mol in molsout]
            self.assertItemsEqual(correctsmiles, tochecksmiles)


if __name__ == "__main__":
    unittest.main()
