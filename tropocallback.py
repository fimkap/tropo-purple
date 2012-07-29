from tropo import Tropo, Session
import logging
import json
import webapp2
from google.appengine.ext import db
from tropopals import *

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("In get")

    def post (self):
        tropo = Tropo()
        s = Session(self.request.body)
        #logging.info("session: %s " % self.request.body)
        callerID = s.fromaddress['id']
        logging.info ("Caller ID: %s " % callerID)
        if 'x-username' in s.headers:
            pal = s.headers['x-username']
            logging.info ("Pal : %s " % pal)

            # Find sid for this pal
            sipendpoint = ''
            user = TropoPals.get_record("1",pal)
            if user:
                sipendpoint = ':'.join(("sip", user.phonosid))

            logging.info ("sip endpoint: %s " % sipendpoint)
            if len(sipendpoint) != 0:
                tropo.transfer(sipendpoint)
                #tropo.say("User is found")
            else:
                tropo.say("User is not found")
        else:
            tropo.say("This is a purple application!")

        json = tropo.RenderJson()
        logging.info ("Sending json back to Tropo")
        self.response.out.write(json)


class UserBook(webapp2.RequestHandler):
    def post(self):
        username = self.request.params.get("name")
        sid = self.request.params.get("sid")
        logging.info ("name: %s " % username)
        logging.info ("sid: %s " % sid)
        # TODO now just use default for user_id and context
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

