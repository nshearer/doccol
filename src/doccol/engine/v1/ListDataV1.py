from .ModelDataTypeV1 import ModelDataTypeV1, safe_del_prop_value

from prop_pickle import encode_prop_value_for_disk, decode_prop_value_from_disk

class ListDataV1(ModelDataTypeV1):
    '''A property within a document that is a list of which can be a collection types'''

    def __init__(self, value=None):

        self.__values = list()

        if value is not None:
            self.extend(value)


    @property
    def type_code(self):
        '''The key to put in the value when saved to file'''
        return 'list'


    # -- Standard list access ----------------------------------------------------------

    def append(self, item):
        self.__values.append(item)

    def extend(self, seq):
        self.__values.extend(seq)


    def __contains__(self, item):
        for col_item in self.__values:
            if col_item == item:
                return True
        return False

    def remove(self, item):
        for i, col_item in enumerate(self.__values):
            if col_item == item:
                del self[i]
                return


    def __getitem__(self, i):
        return self.__values[i]


    def __setitem__(self, i, value):
        del self[i]
        self.__values[i] = value


    def __delitem__(self, i):
        safe_del_prop_value(self.__values[i])
        del self.__values[i]


    def pop(self, i=None):
        if i is None:
            return self.__values.pop()
        return self.__values.pop(i)


    # -- Storing ----------------------------------------------------------------------

    def prep_for_store(self, store_path, store_prefix):
        '''
        Prepare working value for storage

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: value ready to be encoded into the file storing the document properties
        '''
        store_values = list()

        # Recurse store logic
        for value in self.__values:
            store_values.append(encode_prop_value_for_disk(
                prop_value = value,
                store_path = store_path,
                store_prefix = store_prefix))

        return store_values


    def decode_retrieved_value(self, value, store_path, store_prefix, col_data_types):
        '''
        Decode value prepared by prep_for_store() back to working value

        :param value: value from file (simple structure)
        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :param col_data_types: Dictionary of property data type handlers in collection
        :return: anything
        '''
        decoded_values = list()

        # Recurse decode logic
        for item in value:
            decoded_values.append(decode_prop_value_from_disk(
                stored_value = item,
                store_path=store_path,
                store_prefix=store_prefix,
                col_data_types=col_data_types))

        return ListDataV1(decoded_values)


    def delete_value(self):
        '''
        Called when a value is deleted or replaced

        (sorry, you'll have to figure out the prefix and storage dir elsewise)
        '''
        for value in self.__values():
            safe_del_prop_value(value)

