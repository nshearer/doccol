
class DocumentProperties(object):
    '''Helper that can be accessed via document.p & document.properties'''


    def __init__(self, engine, doc_id):
        self.__engine = engine
        self.__doc_id = doc_id


    def get(self, name):
        '''Get parameter value'''
        property_values = self.__engine.get_document_properties(self.__doc_id)
        if property_values.has_key(name):
            return property_values[name]
        return None



    def set(self, **kwargs):
        '''Set multiple parameter values'''
        self.__engine.update_properties(self.__doc_id, kwargs)


    def __getattr__(self, key):
        if not key.startswith('_'):
            return self.get(key)
        else:
            return super(DocumentProperties, self).__getattr__(key)


    def __setattr__(self, key, value):
        if not key.startswith('_'):
            self.set({key: value})
        else:
            super(DocumentProperties, self).__setattr__(key, value)


