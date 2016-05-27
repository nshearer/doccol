


from DocumentProperties import DocumentProperties


class Document(object):
    '''A document in the collection'''

    def __init__(self, engine, doc_id):
        '''

        :param engine: Document collection engine which stores doc info
        :param name: Unique ID for the document for the engine
        '''
        self.__engine = engine
        self.__doc_id = doc_id


    @property
    def properties(self):
        return DocumentProperties(self.__engine, self.__doc_id)

    @property
    def p(self):
        return self.properties

    def __str__(self):
        return "%s :: %s" % (self.__doc_id.domain, self.__doc_id.name)
