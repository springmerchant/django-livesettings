from pymongo import *

class LiveSettingBackend(object):
    def __init__(self, siteid=-1):

        self.is_editable = True
        self.siteid = siteid

        self.settings = {}
        self.document = None

        connection = Connection()
        db = connection.settings

        self.collection = db.application_settings
        
        self.document = self.collection.find_one({'siteid': siteid})

        self.settings = self.document['SETTINGS']

    def save_value(self, group_key, key, value):
        try:
            self.settings[group_key][key] = value
        except KeyError:
            self.settings[group_key] = {key:value}
            
        self.collection.save(self.document)

        return True

    def get_value(self, group_key, key):
        return self.settings[group_key][key]

    
