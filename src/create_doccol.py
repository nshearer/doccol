'''Create a new Document Collection'''
import os
import sys

from doccol.engine import create_doccol, DocCollectionOperationError

def abort(msg = None):
    print ""
    if msg is not None:
        print "ERROR: " + msg
    print "ABORTING"
    sys.exit(2)

if __name__ == '__main__':

    # Get arguments
    if len(sys.argv) != 2:
        abort ("Usage: %s colection_path" % (os.path.basename(sys.argv[0])))
    path = sys.argv[1].strip()

    # Create directory if doesn't exists
    if not os.path.exists(path):
        parent = os.path.dirname(os.path.abspath(path))
        if os.path.exists(parent):
            os.mkdir(path)
        else:
            abort("Path doesn't exists: " + parent)

    # Do creation
    try:
        create_doccol(path)
    except DocCollectionOperationError, e:
        abort("Failed:\n" + str(e))

    print "Finished"
