from mayolmol.scripts import dsstox_prop4da as prop4da
import sys
import os.path as op

if __name__ == "__main__":
    if len(sys.argv) == 4:
        directory = sys.argv[1]
        file = sys.argv[2]
        label = sys.argv[3]
        if op.exists(op.join(directory, file)):
            counts = prop4da.analyze_class(directory, file, label)
            print "Number of molecules in the file: %i"%counts[0]
            if len(counts) > 1:
                print counts[1]
        else: 
            print "No such file or directory: %s."%op.join(directory, file)
    else:
        print "Error with the arguments. Reminder: \n - Argument 1 is the absolute path of the directory where the sdf file is stored \n - Argument 2 is the name of the sdf file \n - Argument 3 is the name of the label for the data."
