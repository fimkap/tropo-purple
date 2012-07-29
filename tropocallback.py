"""
Tropo Callback main entry point
"""
from tcb_logic import TCBLogic
import logging
import json
import webapp2
from google.appengine.ext import db
from tropopals import *

# This is what Tropo should be configured to call as POST (server-ip:8080/)
class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("In get")
        self.response.out.write(TCBLogic.TropoCallbackGet(self))

    def post(self):
        logging.info ("Calling Tropo Callback")
        self.response.out.write(TCBLogic.TropoCallback(self))


# Sign a user and return a list of pals to call
# TODO Probably in integration with the main 3-rings app we will tansform it in a new refresh_pals API
class UserBook(webapp2.RequestHandler):
    def post(self):
        username = self.request.params.get("name")
        sid = self.request.params.get("sid")
        logging.info ("name: %s " % username)
        logging.info ("sid: %s " % sid)

        # TODO now just use default for user_id and context
        # We need to update the session ID a user got from Tropo (a form of sip:SID used to call him)
        rec = TropoPals.create_record("1", username, "context", sid)
        if rec is None:
            TropoPals.update_record("1", username, sid)

        # Return all users but the caller TODO check timestamp not to return offline users
        self.response.out.write(json.dumps(TropoPals.ToDict(TropoPals.all())))

    def get(self):
        return self.post()


app = webapp2.WSGIApplication(
                                     [('/', MainPage),
                                     ('/sign', UserBook)],
                                     debug=True)

