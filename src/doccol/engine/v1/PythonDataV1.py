from .ModelDataTypeV1 import ModelDataTypeV1

class PythonDataV1(ModelDataTypeV1):
    '''A property within a document that is any type that can be serialized to the file storage'''

    def __init__(self, value=None):
        self.__value = value

    @property
    def type_code(self):
        '''The key to put in the value when saved to file'''
        return 'python'


    def prep_for_store(self, store_path, store_prefix):
        '''
        Prepare working value for storage

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: value ready to be encoded into the file storing the document properties
        '''
        return self.__value


    def decode_retrieved_value(self, value, store_path, store_prefix):
        '''
        Decode value prepared by prep_for_store() back to working value

        :param value: value from file (simple structure)
        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: anything
        '''
        return value # Don't leave value encapsulated by this class
