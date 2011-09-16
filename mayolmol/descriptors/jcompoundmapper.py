import subprocess
from mayolmol.others import othersoft

class JCompoundMapperCLIDriver():
    """
    Driver for using the the JCompoundMapperCLI. Here is the help of the command (2011/09/16):

    usage: jCMapper
    -a     Atom Type: CDK_ATOM_TYPES, ELEMENT_NEIGHBOR,
                      ELEMENT_NEIGHBOR_RING, ELEMENT_SYMBOL, CUSTOM, DAYLIGHT_INVARIANT,
                      DAYLIGHT_INVARIANT_RING
    -c     Fingerprinting algorithm: DFS, ASP, AP2D, AT2D, AP3D, AT3D,
           CATS2D, CATS3D, PHAP2POINT2D, PHAP3POINT2D, PHAP2POINT3D, PHAP3POINT3D,
           ECFP, ECFPVariant, LSTAR, SHED, RAD2D, RAD3D
    -d     Distance cutoff / search depth
    -f     MDL SD file
    -ff    Output format: LIBSVM_SPARSE, LIBSVM_MATRIX, FULL_CSV,
           STRING_PATTERNS, WEKA_HASHED, WEKA_NOMINAL, BENCHMARKS
    -h     Print help
    -hs    Hash space size (default=2^18)
    -l     Label (MDL SD Property)
    -lt    Label threshold
    -m     Distance measure (matrix format): TANIMOTO, MINMAX
    -o     Output file
    -s     Stretching factor (3D fingerprints)
    """
    ATOM_TYPES = ('CDK_ATOM_TYPES',
                  'ELEMENT_NEIGHBOR', 'ELEMENT_NEIGHBOR_RING',
                  'ELEMENT_SYMBOL',
                  'CUSTOM',
                  'DAYLIGHT_INVARIANT', 'DAYLIGHT_INVARIANT_RING')

    FINGERPRINTS = ('DFS', 'ASP', 'AP2D', 'AT2D', 'AP3D', 'AT3D',
                    'CATS2D', 'CATS3D', 'PHAP2POINT2D', 'PHAP3POINT2D', 'PHAP2POINT3D', 'PHAP3POINT3D',
                    'ECFP', 'ECFPVariant', 'LSTAR', 'SHED', 'RAD2D', 'RAD3D')

    OUTPUT_FORMATS = ('LIBSVM_SPARSE', 'LIBSVM_MATRIX', 'FULL_CSV',
                      'STRING_PATTERNS', 'WEKA_HASHED', 'WEKA_NOMINAL', 'BENCHMARKS')

    DISTANCE_MEASURES = ('TANIMOTO', 'MINMAX')

    def __init__(self,
                 java_command='java',
                 jcompoundmapperjar=None):
        if not jcompoundmapperjar: jcompoundmapperjar = othersoft.OtherSoft().jcompoundmapper
        self.command = java_command + ' -jar ' + jcompoundmapperjar

    def fingerprint(self,
                    input_file,
                    output_file,
                    fingerprint='ECFP',
                    output_format='WEKA_HASHED',
                    distance_cutoff=None,
                    atom_type=None,
                    label=None,
                    label_threshold=None,
                    distance_measure=None,
                    hash_space_size = 2**8,
                    stretching_factor = None):
        #TODO: check the input parameters
        input_file = ' -f ' + input_file
        log_file = output_file + '.err'
        output_file = ' -o ' + output_file
        output_format = ' -ff ' + output_format
        atom_type = ' -l ' + atom_type if atom_type else ''
        fingerprint = ' -c ' + fingerprint
        distance_cutoff = ' -d ' + distance_cutoff if distance_cutoff else ''
        hash_space_size = ' -hs ' +str(hash_space_size)
        label = ' -l ' + label if label else ''
        label_threshold = ' -lt ' + label_threshold if label_threshold else ''
        distance_measure = ' -m ' +distance_measure if distance_measure else ''
        stretching_factor = ' -s ' +stretching_factor if stretching_factor else '' #TODO: what is this?
        command = self.command +\
                  atom_type +\
                  fingerprint +\
                  distance_cutoff +\
                  label + label_threshold +\
                  input_file +\
                  hash_space_size +\
                  output_file + output_format +\
                  distance_measure +\
                  stretching_factor
        with open(log_file, 'w') as stderr:
            subprocess.call(command, shell=True, stdout=stderr, stderr=stderr)