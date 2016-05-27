import os
import json


class PropertyFile(object):
    '''General purpose preoprty storage file'''

    def __init__(self, path):
        self.__path = path
        self.__property_defs = dict()
        self.__property_values = dict()

        if os.path.exists(self.__path):
            with open(self.__path, 'r') as fh:
                self.__property_values = json.load(fh)


    def save(self):
        try:
            with open(self.__path, 'w') as fh:
                json.dump(self.__property_values, fh, indent=4)
        except Exception, e:
            raise Exception("Failed to save properties to %s:\n%s" % (self.__path, str(e)))


    def def_property(self, name, default=None, value=None):
        self.__property_defs[name] = {
            'name': name,
            'default': default,
        }
        if value is not None:
            setattr(self, name, value)


    def __getitem__(self, name):
        if self.__property_values.has_key(name):
            return self.__property_values[name]
        if self.__property_defs.has_key(name):
            return self.__property_defs[name]['default']
        raise AttributeError("Not a defined property: " + name)


    def __setitem__(self, name, value):
        if not self.__property_defs.has_key(name):
            raise AttributeError("Not a defined property: " + name)
        self.__property_values[name] = value
        self.save()


    def update(self, values):
        for name, value in values.items():
            if not self.__property_defs.has_key(name):
                raise AttributeError("Not a defined property: " + name)
            self.__property_values[name] = value
        self.save()
