import os
import glob
import shutil
from string import ascii_letters, digits
from bunch import Bunch

from ..DocColEngine import DocColEngine
from ..DoccumentId import DocumentId

from ..utils.LookupFile import LookupFile
from ..utils.PropertyFile import PropertyFile
from ..utils.Cache import Cache

from ..exceptions import PropertyValueDecodeError

from ModelDataTypeV1 import safe_del_prop_value
from ListDataV1 import ListDataV1
from DictDataV1 import DictDataV1
from FileAttachmentV1 import FileAttachmentV1

from prop_pickle import encode_prop_value_for_disk, decode_prop_value_from_disk

SANITIZE_FOLD_SAFE_CHARS=set(ascii_letters + digits + '_')

def sanitize_folder_name(name):
    def _get_safe_folder_name_chars(name):
        global SANITIZE_FOLD_SAFE_CHARS
        for c in name:
            if c in SANITIZE_FOLD_SAFE_CHARS:
                yield c
            else:
                yield '_'
    return ''.join(list(_get_safe_folder_name_chars(name))[:40])


class V1DocumentDomain(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.fold_name = os.path.basename(self.path)
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.properties = PropertyFile(os.path.join(self.path, 'domain.yml'))
        self.properties.def_property('name')

        if self.properties.name is None:
            self.properties.name = name


class V1DocumentId(DocumentId):
    def __init__(self, domain, domain_folder, name, doc_folder):
        self.__domain = domain
        self.__domain_folder = domain_folder
        self.__doc_name = name
        self.__doc_folder = doc_folder
    @property
    def domain(self):
        return self.__domain
    @property
    def domain_folder(self):
        return self.__domain_folder
    @property
    def doc_name(self):
        return self.__doc_name
    @property
    def doc_folder(self):
        return self.__doc_folder
    def __str__(self):
        return "%s\\%s (%s)" % (self.domain_folder, self.doc_folder, self.doc_name)


class DocColEngineV1(DocColEngine):
    '''
    Engine for storing and retrieving documents from disk.

    The goals of this first engine are:
      - Documents can be created and removed on the fly very easily
        (just delete the folder.  No need to update indexes...)
      - Git repo friendly.
      - Don't scan all the documents on load.  Scan while needed
      - KISS.  We'll improve performance where needed in the future
        (may add index later and compare against file times)
    '''

    def __init__(self, path):
        self.__path = path
        self.__domains = dict()

        self.__prop_file_cache = Cache(100)     # [prop_file_path] = PropertyFile
        self.__doc_path_cache = Cache(10000)    # [(domain_name, doc_name)] = path to doc folder


    DATA_TYPES = {
        'list':         ListDataV1,
        'dict':         DictDataV1,
        'attachment':   FileAttachmentV1,
    }


    # -- Domains -------------------------------------------------------------

    def _get_domain_properties_file(self, domain_path):
        '''
        Read properties file from a domain

        :param domain_path: Path to the folder for this domain
        :return: PropertyFile
        '''
        path = os.path.join(domain_path, 'domain.properties')
        props = PropertyFile(path)
        props.def_property('name')
        return props


    def _get_domain_dir_path(self, domain, must_exist=False):
        '''
        Determine which directory to save documents in for a domain name (create if needed)

        :param domain: Name of domain
        :param must_exist: If False, then folder will be created
        :return: Full path to folder for domain
        '''
        base_fold_name = sanitize_folder_name(domain)

        # See if folder already exists
        for path in glob.glob(os.path.join(self.documents_path, base_fold_name) + '*'):
            try:
                path_domain_props = self._get_domain_properties_file(path)
            except Exception, e:
                print "WARNING: For %s: %s" % (path, str(e))
                continue

            if path_domain_props['name'] == domain:
                return path

        # -- If not found, need to create --
        if not must_exist:

            # Make folder unique
            i=0
            fold_name = base_fold_name
            path = os.path.join(self.documents_path, fold_name)
            while os.path.exists(path):
                i += 1
                fold_name = '%s_%d' % (base_fold_name, i)
                path = os.path.join(self.documents_path, fold_name)
            os.mkdir(path)

            # Create properties file
            props = self._get_domain_properties_file(path)
            props['name'] = domain

            return path


    # -- Documents -----------------------------------------------------------


    @property
    def documents_path(self):
        return os.path.join(self.__path, 'documents')


    def _calc_doc_prop_file_path(self, doc_fold_path):
        return os.path.join(doc_fold_path, 'doc.properties')


    def _get_doc_prop_file(self, doc_fold_path, must_exist=False):
        '''
        Read properties file from a domain

        (Warning: Don't pass this PropertyFile out of the class.  Since we cache
                  this file, we don't want an instance staying live and caching
                  other values of the properties)

        :param doc_fold_path: Path the the folder for this document
        :return: PropertyFile
        '''
        path = self._calc_doc_prop_file_path(doc_fold_path)

        # Use cache to avoid re-opening if possible
        if self.__prop_file_cache.has(path):
            return self.__prop_file_cache.get(path)

        # Open it up
        if os.path.exists(path) or not must_exist:

            # Open property file
            props = PropertyFile(path)
            props.def_property('name')
            props.def_property('properties')

            # Cache
            self.__prop_file_cache.add(path, props)

            # Return
            return props

        # Property file doesn't exist
        return None


    def create_new_doc(self, domain, name):
        '''
        Initialize a new document in the collection

        :param domain: Domain (like a folder) of documents
        :param name: Unique ID of document in the domain
        :return: Internal Document ID
        '''
        domain_path = self._get_domain_dir_path(domain)
        base_doc_name = sanitize_folder_name(name)

        # See if folder already exists
        for path in glob.glob(os.path.join(domain_path, base_doc_name) + '*'):
            try:
                path_doc_props = self._get_doc_prop_file(path)
            except Exception, e:
                print "WARNING: For %s: %s" % (path, str(e))
                continue

            if path_doc_props['name'] == name:
                raise KeyError("Document already exists in domain (%s): %s" % (domain, name))


        # -- If not found, need to create --

        # Make document folder unique
        i=0
        fold_name = base_doc_name
        path = os.path.join(domain_path, fold_name)
        while os.path.exists(path):
            i += 1
            fold_name = '%s.%d' % (base_doc_name, i)
            path = os.path.join(domain_path, fold_name)
        os.mkdir(path)

        # Create properties file
        props = self._get_doc_prop_file(path)
        props['name'] = name
        props['properties'] = dict()

        # Cache
        self.__doc_path_cache.add((domain, name), path)

        return V1DocumentId(
            domain = domain,
            domain_folder = os.path.basename(domain_path),
            name = name,
            doc_folder = os.path.basename(path))


    def list_all_domains(self):
        '''
        List all domains in the collection

        :return: Generator listing domain names
        '''
        for fold_name in os.listdir(self.documents_path):
            domain_props = self._get_domain_properties_file(os.path.join(
                self.documents_path, fold_name))
            yield domain_props['name']


    def list_all_docs(self, domain=None):
        '''
        List all documents in a domain in the collection

        :param domain: Name of the domain (None for all domains)
        :return: Generator listing document ids
        '''
        if domain is None:
            for domain in self.list_all_domains():
                for doc in self.list_all_docs(domain):
                    yield doc

        else:
            domain_fold_path = self._get_domain_dir_path(domain, must_exist=True)
            if domain_fold_path is None:
                return
            for doc_fold_name in os.listdir(domain_fold_path):
                doc_fold_path = os.path.join(domain_fold_path, doc_fold_name)
                if os.path.isdir(doc_fold_path):
                    doc_props = self._get_doc_prop_file(doc_fold_path, must_exist=True)
                    if doc_props is not None:
                        doc_name = doc_props['name']
                        self.__doc_path_cache.add((domain, doc_name), doc_fold_path)
                        yield V1DocumentId(
                            domain = domain,
                            domain_folder = os.path.basename(domain_fold_path),
                            name = doc_name,
                            doc_folder = os.path.basename(doc_fold_path))


    def get_document_id(self, domain, name):
        '''
        Retrieve document from collection

        :param domain: Domain (like a folder) of documents
        :param name: Unique ID of document in the domain
        :return: Internal Document ID
        '''
        domain_path = self._get_domain_dir_path(domain, must_exist=True)
        if domain_path is None:
            return None

        doc_fold_basename = sanitize_folder_name(name)

        for path in glob.glob(os.path.join(domain_path, doc_fold_basename) + '*'):
            doc_props = self._get_doc_prop_file(path, must_exist=True)
            if doc_props is None:
                print "WARNING: Can't find document properties: " + path
            if doc_props['name'] == name:
                return V1DocumentId(
                    domain = domain,
                    domain_folder = os.path.basename(domain_path),
                    name = name,
                    doc_folder = os.path.basename(path))

        return None



    def _calc_prop_file_prefix(self, prop_name):
        return sanitize_folder_name(prop_name) + '-' + str(abs(hash(prop_name)))


    def get_document_properties(self, doc_id):
        '''
        Get all of the properties for a document

        :param doc_id: Internal Document ID
        :return: dict of properties (safe to modify)
        '''
        # Retrieve values stored in file
        doc_fold_path = os.path.join(self.documents_path, doc_id.domain_folder, doc_id.doc_folder)
        doc_prop_file = self._get_doc_prop_file(doc_fold_path, must_exist=True)
        stored_prop_values = doc_prop_file['properties']

        # Cache Note: Value of property is stored in-mem in PropertyFile returned
        #             by _get_doc_prop_file() which caches the files.
        #             This call should return values from in-mem if file has been
        #             loaded

        # Decode according to property value type
        prop_values = dict()
        for prop_name, prop_value in stored_prop_values.items():
            try:
                prop_values[prop_name] = decode_prop_value_from_disk(
                    stored_value = prop_value,
                    store_path = doc_fold_path,
                    store_prefix = self._calc_prop_file_prefix(prop_name),
                    col_data_types = self.DATA_TYPES)
            except PropertyValueDecodeError, e:
                raise PropertyValueDecodeError(
                    "Unable to decode property '%s' for document %s: %s" % (
                        prop_name, str(doc_id), str(e)))

        return prop_values



    def update_properties(self, doc_id, properties):
        '''
        For each key in the properties, set the value in the document

        :param doc_id: Internal Document ID
        :param properties: Dictionary of properties to set
        '''
        doc_dir = os.path.join(self.documents_path, doc_id.domain_folder, doc_id.doc_folder)
        doc_props = self._get_doc_prop_file(doc_dir)

        existing_properties = self.get_document_properties(doc_id)
        props_to_delete = list()

        # Convert property values for storage
        saved_props = doc_props['properties'].copy()
        for prop_name, prop_value in properties.items():

            try:
                props_to_delete.append(existing_properties[prop_name])
            except KeyError:
                pass

            # None means delete property value
            if prop_value is None:
                try:
                    del saved_props[prop_name]
                except KeyError:
                    pass

            # Else, encoed eit
            else:
                saved_props[prop_name] = encode_prop_value_for_disk(
                    prop_value = prop_value,
                    store_path = doc_dir,
                    store_prefix = self._calc_prop_file_prefix(prop_name))

        # Save properties
        doc_props['properties'] = saved_props

        # Delete old values
        for value in props_to_delete:
            safe_del_prop_value(value)


    def del_property(self, doc_id, name):
        '''
        Replace all properties in document with these ones

        :param doc_id: Internal Document ID
        :param name: Name of property to delete
        '''
        values = dict()
        values[name] = None
        self.update_properties(doc_id, values)


    def replace_properties(self, doc_id, properties):
        '''
        Replace all properties in document with these ones

        :param doc_id: Internal Document ID
        :param properties: Dictionary of properties to set
        '''
        raise NotImplementedError()


    def del_document(self, doc_id):
        '''
        Delete a document from the collection

        :param doc_id: Internal Document ID
        '''
        path = os.path.join(self.documents_path, doc_id.domain_folder, doc_id.doc_folder)
        prop_file_path = self._calc_doc_prop_file_path(path)
        if os.path.exists(path):
            shutil.rmtree(path)

        # Clean cache
        self.__doc_path_cache.remove(prop_file_path)
        self.__doc_path_cache.remove((doc_id.domain, doc_id.doc_name))



