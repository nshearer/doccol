import os

from .exceptions import DocCollectionOperationError

def is_doc_col_folder(path):
    '''Is the given directory a valid collection?'''
    return os.path.exists(os.path.join(path, 'DOCCOL.txt'))

LATEST_DOC_COL_VER=1


def create_doccol(path):
    '''Create a new collection'''
    global LATEST_DOC_COL_VER

    if not os.path.isdir(path):
        raise DocCollectionOperationError("Not a directory: " + path)

    if os.path.exists(os.path.join(path, 'DOCCOL.txt')):
        raise DocCollectionOperationError("Collection already exists: " + path)

    with open(os.path.join(path, 'DOCCOL.txt'), 'wt') as fh:
        print >>fh, "This is a marker file to designate this folder as a Document Collection"
        print >>fh, "meant to be managed by the doccol tool"

    os.mkdir(os.path.join(path, 'documents'))

    with open(os.path.join(path, 'VERSION'), 'wt') as fh:
        print >>fh, str(LATEST_DOC_COL_VER)


def pick_engine(col_path):
    '''Pick an egine to use for the given path'''

    # Make sure this is one of our colections
    if not os.path.exists(os.path.join(col_path, 'DOCCOL.txt')):
        raise DocCollectionOperationError("Not a document colection root: " + col_path)

    # Load version
    path = os.path.join(col_path, 'VERSION')
    if not os.path.exists(path):
        raise DocCollectionOperationError("Missing version file: " + path)
    with open(path, 'rt') as fh:
        try:
            version = int(fh.read())
        except ValueError:
            raise DocCollectionOperationError("Version file appears to be corrupt: " + path)

    # Pick engine
    if version == 1:
        from .v1.DocColEngineV1 import DocColEngineV1
        return DocColEngineV1(col_path)

    else:
        raise DocCollectionOperationError("Unsupported Document Collection Version: " + str(version))
