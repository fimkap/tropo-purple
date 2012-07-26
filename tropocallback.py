from tropo import Tropo, Session
import logging
import json
import webapp2
from google.appengine.ext import db

class PurpleUser(db.Model):
    username = db.StringProperty()
    phonosid = db.StringProperty()
    presence = db.IntegerProperty()

def userbook_key(username):
  return db.Key.from_path('Userbook', username)
    

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("In get")
        #logging.info("fullname %s" % fullname)
        #username = self.request.params.get("name")
        #logging.info("User name is %s" % username)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request.params)
        #self.response.out.write(json.dumps(username))

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
            users = PurpleUser.all()
            users.filter("username == ", pal)
            #TODO look for single user - more than one possible?
            sipendpoint = ''
            for user in users:
                sipendpoint = ':'.join(("sip", user.phonosid))

            logging.info ("sip endpoint: %s " % sipendpoint)
            if len(sipendpoint) != 0:
                tropo.transfer(sipendpoint)
                #tropo.say("User is found")
            else:
                tropo.say("User is not found")
        else:
            tropo.say("This is a purple application!")

        #tropo.transfer("sip:d6561a48-b069-4f31-9166-d0d32f0e8fe4@phono3-ext.voxeolabs.net")
        json = tropo.RenderJson()
        logging.info ("Sending json back to Tropo")
        self.response.out.write(json)


class UserBook(webapp2.RequestHandler):
    def post(self):
        username = self.request.params.get("name")
        purpleuser = PurpleUser(parent=userbook_key(username))
        purpleuser.username = username;
        sid = self.request.params.get("sid")
        purpleuser.phonosid = sid;
        purpleuser.presence = 1
        purpleuser.put()
        # TODO hide JSON conversion in model class
        users = PurpleUser.all()
        users.filter("username != ", username)
        usersDict = dict((user.username, {'sid' : user.phonosid, 'presence' : user.presence }) for user in users)

        #q = db.GqlQuery("SELECT * FROM PurpleUser ")
        #users = q.fetch(limit=None)
        #usersDict = {}
        #for user in users:
        #    usersDict[user.username] = { 'name' : user.username, 'sid' : user.phonosid, 'presence' : user.presence }
        self.response.out.write(json.dumps(usersDict))

    def get(self):
        return self.post()


app = webapp2.WSGIApplication(
                                     [('/', MainPage),
                                     ('/sign', UserBook)],
                                     debug=True)

#def main():
#    run_wsgi_app(application)
#
#if __name__ == "__main__":
#    main()
