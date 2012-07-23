from tropo import Tropo
import logging
import json
import webapp2
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp.util import run_wsgi_app

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
    

app = webapp2.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

#def main():
#    run_wsgi_app(application)
#
#if __name__ == "__main__":
#    main()
