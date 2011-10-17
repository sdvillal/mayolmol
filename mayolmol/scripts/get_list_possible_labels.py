from mayolmol.mlmusings import mlio
import sys
import os.path as op

if __name__ == "__main__":
    if len(sys.argv) == 3:
        directory = sys.argv[1]
        dataset = sys.argv[2]
        if op.exists(op.join(directory, dataset)):
            print mlio.data_fields(directory, dataset)
        else:
            print "No such file or directory: %s."%op.join(directory, dataset)
    else:
        print "Error with the arguments. Reminder: \n - Argument 1 is the absolute path of the directory where the sdf file is stored \n - Argument 2 is the name of the sdf file."
