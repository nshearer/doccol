import os
import json

from collections import MutableMapping

class LookupFileError(Exception): pass

class LookupFile(MutableMapping):
    '''A lookup table that gets saved to disk'''

    def __init__(self, path):
        self.__path = path
        self.__fh = None
        self.__values = dict()

        # Load lookups
        if os.path.exists(self.__path):
            self._load(self.__path)

        # Hold file open to append updates
        if os.path.exists(self.__path):
            self.__fh = open(self.__path, 'a')
        else:
            self.__fh = open(self.__path, 'w')


    def _load(self, path):
        self.__values = dict()
        for segment in self._read_segments(path):
            if segment['entry'] == 'list':
                self.__values.update(segment['values'])
            elif segment['entry'] == 'set':
                self.__values[segment['key']] = segment['value']
            elif segment['entry'] == 'del':
                del self.__values[segment['key']]


    def save(self):
        '''Will re-save the output file (flattening it as well)'''
        self.__fh.close()
        self.__fh = open(self.__path, 'w')
        self.__fh.write(self._build_segment({'entry': 'list', 'values': self.__values}))


    # -- Dictionary Interfaces -----------------------------------------------

    def __getitem__(self, key):
        return self.__values[key]


    def __setitem__(self, key, value):
        self.__fh.write(self._build_segment(self.ADD_ENTRY, {'entry': 'set', 'key': key, 'value': value}))
        self.__values[key] = value


    def __delitem__(self, key):
        self.__fh.write(self._build_segment(self.DEL_ENTRY, {'entry': 'del', 'key': key}))
        del self.__values[key]


    def __contains__(self, key):
        return key in self.__values


    def keys(self):
        return self.__values.keys()


    # -- File segments -------------------------------------------------------

    '''
    In order to support appending changes quickly, segments are appended onto
    the file as changes are made (instead of rewriting the whole file).

    Each segment looks like:
      \\n(length_of_segment)\\n(json segment contents)
    '''

    def _build_segment(self, segment_content):
        '''
        Format data to store in file

        :param segment_content: Content of the segment
        :return: string to write to file
        '''
        content = json.dumps(segment_content)
        content_len = len(content)
        return "\n%d\n%s" % (content_len, content)


    def _read_segments(self, path):
        '''
        Get segment_content back out from string created by content()

        :param path: File to read segments out of
        :return: generator for structured data
        '''
        try:
            with open(path, 'r') as fh:
                content = fh.read()
        except Exception, e:
            raise LookupFileError("Failed to read lookup file: %s" % (path))

        if len(content) < 4:
            raise LookupFileError("File too short %s" % (path))

        segment_start = 0
        while segment_start < len(content):

            # First char should be \n
            if content[segment_start] != '\n':
                raise LookupFileError(
                    "Structure error on %s: segment @%d needs to start with newline" % (path, segment_start+1))

            # Get digits that represent length of segment
            next_newline = content.find("\n", segment_start+1)
            if next_newline == -1:
                raise LookupFileError(
                    "Structure error on %s: Couldn't find newline after segment length @%d" % (path, segment_start+1))
            seg_len_str = content[segment_start+1, next_newline]
            try:
                seg_len = int(seg_len_str)
            except ValueError:
                raise LookupFileError(
                    "Structure error on %s: Segment length not an in @%d: %s" % (path, segment_start+1, seg_len_str))

            # Get segment contents
            segment_json = content[next_newline+1, next_newline+1+seg_len]
            try:
                yield json.loads(segment_json)
            except Exception, e:
                 raise LookupFileError(
                    "Structure error on %s: JSON decode error on @%d" % (path, next_newline+1))

            # Get ready for next segment
            segment_start = next_newline+1+seg_len