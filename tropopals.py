"""
Tropo Database table definitions.
"""
from google.appengine.ext import db

from pu_utils import *

class TropoPals(db.Model):
    # When the connection was created.
    timestamp = db.DateTimeProperty(auto_now_add=True)

    context = db.StringProperty()

    # session id given by Phono on every new connection
    phonosid = db.StringProperty()

    @property
    def pal_id(self):
        return self.key().name().split(':')[1]

    @property
    def user_id(self):
        return self.key().name().split(':')[0]

    @staticmethod
    def create_record(user_id, pal_id, context, sid):
        """Create a new record and return it or None if already exists"""
        assert ':' not in (user_id + pal_id)
        if type(context) == dict:
            context = json_dump(context)
        key_name = user_id + ':' + pal_id
        def txn():
            if TropoPals.get_by_key_name(key_name):
                return None
            rec = TropoPals(key_name=key_name, context=context, phonosid=sid)
            rec.put()
            return rec
        return db.run_in_transaction(txn)

    @staticmethod
    def update_record(user_id, pal_id, sid):
        key_name = user_id + ':' + pal_id
        def txn():
            # TODO check not syntax
            if TropoPals.get_by_key_name(key_name) is None:
                return None
            rec = TropoPals(key_name=key_name, phonosid=sid)
            rec.put()
            return rec
        return db.run_in_transaction(txn)

    @staticmethod
    def get_record(user_id, pal_id):
        """Return the record if exists else None"""
        return TropoPals.get_by_key_name(user_id + ':' + pal_id)

    @staticmethod
    def delete_record(user_id, pal_id):
        """Delete a record and return True if deleted, False if not found"""
        assert ':' not in (user_id + pal_id)
        key_name = user_id + ':' + pal_id
        rec = TropoPals.get_by_key_name(key_name)
        if rec:
            rec.delete()
            return True
        return False

    @staticmethod
    def get_multi(user_id, pal_ids):
        """Return list of record-or-None per pal id"""
        key_names = [user_id + ':' + pal_id for pal_id in pal_ids]
        return TropoPals.get_by_key_name(key_names)

    @staticmethod
    def ToDict(users):
        # TODO make date JSON serializable
        #usersDict = dict((user.pal_id, {'sid' : user.phonosid, 'timestamp' : user.timestamp }) for user in users)
        usersDict = dict((user.pal_id, {'sid' : user.phonosid }) for user in users)
        return usersDict
