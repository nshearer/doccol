
from .engine import pick_engine

from Document import Document


class PropertyDataTypes(object):
    '''Simple container for data types to use for property values'''



class DocumentCollection(object):
    '''Interface to the DocumentCollection folder for CRUD'''

    def __init__(self, path):
        '''
        :param path: Path to document collection to work in
        '''
        self.__path = path
        self.__engine = pick_engine(path)

        self.data_types = PropertyDataTypes()
        for type_name, type_class in self.__engine.DATA_TYPES.items():
            self.data_types.__setattr__(type_name, type_class)


    def new(self, domain, name):
        '''
        Create a new document

        :param domain: Domain for the document
        :param name: Unique name for the document (in the domain)
        :return: Document
        '''
        doc_id = self.__engine.create_new_doc(domain, name)
        doc = Document(self.__engine, doc_id)
        return doc


    def list_docs(self, domain):
        '''
        List documents in the collection

        :param domain: Name of domain, or None for all domains
        :return: Document objects
        '''
        for doc_id in self.__engine.list_all_docs(domain):
            yield Document(self.__engine, doc_id)


    def get(self, domain, name):
        '''
        Retrieve a document

        :param domain: Name of the domain to get document from
        :param name: Name of the document to retrieve (within domain)
        :return: Document objects
        '''
        doc_id = self.__engine.get_document_id(domain, name)
        if doc_id is None:
            raise KeyError("Document doesn't exist: %s \ %s" % (
                domain, name))
        return Document(self.__engine, doc_id)


    def del_doc(self, domain, name):
        '''
        Delete a document out of the collection

        :param domain: Name of the domain to get document from
        :param name: Name of the document to retrieve (within domain)
        '''
        doc_id = self.__engine.get_document_id(domain, name)
        if doc_id is None:
            raise KeyError("Document doesn't exist: %s \ %s" % (
                domain, name))
        self.__engine.del_document(doc_id)


