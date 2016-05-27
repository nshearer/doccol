import os
import hashlib
import shutil

from .ModelDataTypeV1 import ModelDataTypeV1

class FileAttachmentV1(ModelDataTypeV1):
    '''A property within a document is a file'''

    type_code = 'attachment'

    def __init__(self, attach=None):
        '''
        :param attach:  Path to the file outside the collection to be added
        '''
        self.__col_path = None      # Path to file in the colelction
        self.__ext_path = attach    # Path to the file outside the collection to be added
        self.__hash = None
        self.__orig_filename = None


    def prep_for_store(self, store_path, store_prefix):
        '''
        Prepare working value for storage

        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: value ready to be encoded into the file storing the document properties
        '''
        # Take in new attachments
        if self.__col_path is None:
            if self.__ext_path is not None:

                # Calc hash
                with open(self.__ext_path, 'rb') as fh:
                    hasher = hashlib.md5()
                    contents = fh.read(1024 * 1024)
                    while contents:
                        hasher.update(contents)
                        contents = fh.read(1024 * 1024)
                    self.__hash = hasher.hexdigest()

                # Calc name to save at
                self.__orig_filename = os.path.basename(self.__ext_path)
                self.__col_path = self._calc_distinct_filename(
                    store_path, store_prefix, self.__orig_filename)

                # Copy file in
                shutil.copy(self.__ext_path, self.__col_path)

        return {
            'path': self.__col_path,
            'hash': self.__hash,
            'filename': self.__orig_filename
        }


    def decode_retrieved_value(self, value, store_path, store_prefix):
        '''
        Decode value prepared by prep_for_store() back to working value

        :param value: value from file (simple structure)
        :param store_path: Path to directory where additional files can be written
        :param store_prefix: Prefix to apply to any file names
        :return: anything
        '''
        self.__col_path = value['path']
        self.__hash = value['hash']
        self.__orig_filename = value['filename']
        return self
