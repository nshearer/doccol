from abc import ABCMeta, abstractproperty

class DocumentId(object):
    "Identifies a document in the collection (specific to engine being used)"

    @abstractproperty
    def name(self):
        '''
        Name/Key of the document

        :return: str
        '''


    @abstractproperty
    def domain(self):
        '''
        Name/Key of the domain

        :return: str
        '''

