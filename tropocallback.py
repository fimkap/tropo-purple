from tropo import Tropo
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
        username = self.request.params.get("name")
        logging.info("User name is %s" % username)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write('Hello, webapp World!')
        self.response.out.write(json.dumps(username))

    def post (self):
        tropo = Tropo()
        tropo.transfer("sip:d6561a48-b069-4f31-9166-d0d32f0e8fe4@phono3-ext.voxeolabs.net")
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
        # TODO don't return signed in user's own name
        q = db.GqlQuery("SELECT * FROM PurpleUser ")
        users = q.fetch(limit=None)
        usersDict = {}
        for user in users:
            usersDict[user.username] = { 'name' : user.username, 'sid' : user.phonosid, 'presence' : user.presence }
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
