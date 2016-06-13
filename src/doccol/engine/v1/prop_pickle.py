from ..exceptions import PropertyValueDecodeError


def encode_prop_value_for_disk(prop_value, store_path, store_prefix):
    '''
    Helper method to convert assigned document property to save

    :param prop_value:
        Value that was assigned to property.  This will often be a derived
        from ModelDataTypeV1, and if so that class will be used to
        store the value.
        Otherwise, the Python value will be pickled

    :param store_path:
        Path to directory where additional files can be written

    :param store_prefix:
        Prefix to apply to any file names

    :return: Dictionary to pickle to disk
    '''

    # See if this value is a Model Data Type with store and retrieve handlers
    if hasattr(prop_value, 'type_code') and hasattr(prop_value, 'prep_for_store'):
        value_type = prop_value.type_code
        store_value = prop_value.prep_for_store(store_path, store_prefix)

    # Else, store basic Python value
    else:
        value_type = 'python'
        store_value = prop_value

    # Format for storage to disk
    return {
        'value_type': value_type,
        'value': store_value,
    }



def decode_prop_value_from_disk(stored_value, store_path, store_prefix, col_data_types):
    '''
    Reverse _prep_properties_for_store()

    :param store_path:
        Path to directory where additional files can be written

    :param store_prefix:
        Prefix to apply to any file names
        
    :param col_data_types:
        Dictionary of data types supported by the document collection engine

    :return: Value to return as property value (may be ModelDataTypeV1)
    '''

    prop_value_type_code = stored_value['value_type']

    # Is this just a python object
    if prop_value_type_code == 'python':
        return stored_value

    # Need to determine which class to use to decode value
    prop_value_type = None

    # See if we have a model data type assigned to the value's type code
    if col_data_types.has_key(prop_value_type_code):
        prop_value_type = col_data_types[prop_value_type_code]()

    # Scan through all types to see who can handle it
    else:
        for possible_prop_class in col_data_types.values():
            possible_prop_class = possible_prop_class()
            if possible_prop_class.handles_type_code(prop_value_type_code):
                prop_value_type = possible_prop_class


    if prop_value_type is None:
        raise PropertyValueDecodeError(
            "Unable to decode value type '%s'" % (prop_value_type_code))


    # Decode value
    return prop_value_type.decode_retrieved_value(
        value = stored_value['value'],
        store_path = store_path,
        store_prefix = store_prefix,
        col_data_types = col_data_types)