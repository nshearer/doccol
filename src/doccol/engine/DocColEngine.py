from abc import ABCMeta, abstractmethod, abstractproperty

class DocColEngine(object):
    '''Logic for working with Document Collection folder (base components)

    Many of the functions take or return an "Internal Document ID."  This ID can
    be anything that makes sense to the implemented engine for identifying the
    document being described.
    '''
    __metaclass__ = ABCMeta

    @abstractproperty
    def DATA_TYPES(self):
        '''Data types that can be used when setting property values'''


    @abstractmethod
    def create_new_doc(self, domain, name):
        '''
        Initialize a new document in the collection

        :param domain: Domain (like a folder) of documents
        :param name: Unique ID of document in the domain
        :return: Internal Document ID
        '''


    @abstractmethod
    def list_all_domains(self):
        '''
        List all domains in the collection

        :return: Generator listing domain names
        '''


    @abstractmethod
    def list_all_docs(self, domain=None):
        '''
        List all documents in a domain in the collection

        :param domain: Name of the domain (None for all domains)
        :return: Generator listing document ids
        '''


    @abstractmethod
    def get_document_id(self, domain, name):
        '''
        Retrieve document from collection

        :param domain: Domain (like a folder) of documents
        :param name: Unique ID of document in the domain
        :return: Internal Document ID
        '''


    @abstractmethod
    def get_document_properties(self, doc_id):
        '''
        Get all of the properties for a document

        :param doc_id: Internal Document ID
        :return: dict of properties (safe to modify)
        '''


    @abstractmethod
    def update_properties(self, doc_id, properties):
        '''
        For each key in the properties, set the value in the document

        :param doc_id: Internal Document ID
        :param properties: Dictionary of properties to set
        '''


    @abstractmethod
    def replace_properties(self, doc_id, properties):
        '''
        Replace all properties in document with these ones

        :param doc_id: Internal Document ID
        :param properties: Dictionary of properties to set
        '''


    @abstractmethod
    def del_property(self, doc_id, nmae):
        '''
        Replace all properties in document with these ones

        :param doc_id: Internal Document ID
        :param name: Name of property to delete
        '''


    @abstractmethod
    def del_document(self, doc_id):
        '''
        Delete a document from the collection

        :param doc_id: Internal Document ID
        '''



