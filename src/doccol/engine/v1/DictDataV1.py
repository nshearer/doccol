from .ModelDataTypeV1 import ModelDataTypeV1, safe_del_prop_value

from prop_pickle import encode_prop_value_for_disk, decode_prop_value_from_disk

class DictDataV1(ModelDataTypeV1):
    '''
    A property within a document that is a dictionary of which can be a collection types
    '''

    def __init__(self, value=None):

        self.__values = dict()

        if value is not None:
            self.update(value)


    @property
    def type_code(self):
        '''The key to put in the value when saved to file'''
        return 'dict'


    # -- Standard list access ----------------------------------------------------------

    def __setitem__(self, key, value):
        # Make sure previous value at key is cleaned up
        try:
            del self[key]
        except KeyError:
            pass

        # Set new value
        self.__values[key] = value


    def __delitem__(self, key):
        safe_del_prop_value(self.__values[key])
        del self.__values[key]


    def __getitem__(self, key):
        return self.__values[key]


    def keys(self):
        return self.__values.keys()


    def values(self):
        return self.__values.values()


    def items(self):
        return self.__values.items()


    def has_key(self, key):
        return self.__values.has_key(key)


    def __contains__(self, key):
        return key in self.__values


    # -- Storing ----------------------------------------------------------------------

    def prep_for_store(self, store_path, store_prefix):
        '''
        Prepare working value for storage

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: value ready to be encoded into the file storing the document properties
        '''
        store_values = dict()

        # Recurse store logic
        for name, value in self.__values.items():
            store_values[name] = encode_prop_value_for_disk(
                prop_value = value,
                store_path = store_path,
                store_prefix = store_prefix)

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
        decoded_values = dict()

        # Recurse decode logic
        for name, item in value.items():
            decoded_values[name] = decode_prop_value_from_disk(
                stored_value = item,
                store_path=store_path,
                store_prefix=store_prefix,
                col_data_types=col_data_types)

        return DictDataV1(decoded_values)


    def delete_value(self):
        '''
        Called when a value is deleted or replaced

        (sorry, you'll have to figure out the prefix and storage dir elsewise)
        '''
        for value in self.__values.values():
            safe_del_prop_value(value)

