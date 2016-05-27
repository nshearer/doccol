from abc import ABCMeta, abstractmethod, abstractproperty
import os
import glob

class ModelDataTypeV1(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def type_code(self):
        '''The key to put in the value when saved to file'''


    @abstractmethod
    def prep_for_store(self, store_path, store_prefix):
        '''
        Prepare working value for storage

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: value ready to be encoded into the file storing the document properties
        '''


    @abstractmethod
    def decode_retrieved_value(self, value, store_path, store_prefix):
        '''
        Decode value prepared by prep_for_store() back to working value

        :param value: value from file (simple structure)
        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: anything
        '''


    def handles_type_code(self, code):
        '''
        Check to see if this class can decode the given type code

        :param code: type_code value of ModelDataType when value was saved
        :return: True or False
        '''
        return code == self.type_code


    # -- Utils ---------------------------------------------------------------

    def _calc_distinct_filename(self, store_path, store_prefix, filename):
        '''
        Determine a filename that can be used in prep_for_store()

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names (without prefix)
        :param filename: Desired filename to store
        :return: str path
        '''
        path = os.path.join(store_path, "%s.%s" % (store_prefix, filename))
        if not os.path.exists(path):
            return path

        i=len(list(self._list_files(store_path, store_prefix)))
        while os.path.exists(path):
            i = i + 1
            path = os.path.join(store_path, "%s.%d.%s" % (store_prefix, i, filename))
        return path


    def _list_files(self, store_path, store_prefix):
        '''
        List all files in the store that can be used by this property

        To be used in decode_retrieved_value()

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names (without prefix)
        :return: generator of paths are stored
        '''
        for path in glob.glob(os.path.join(store_path, store_prefix) + '*'):
            yield path
