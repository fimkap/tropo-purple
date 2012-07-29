"""
Tropo Callback logic implementation.
"""
from tropo import Tropo, Session
import logging
from tropopals import *

class TCBLogic():
    # Test function
    @staticmethod
    def TropoCallbackGet (rh):
        name = rh.request.params.get("name")
        return name

    @staticmethod
    def TropoCallback (rh):
        tropo = Tropo()

        # Get the session object sent by Tropo
        s = Session(rh.request.body)
        logging.info("session: %s " % rh.request.body)

        callerID = s.fromaddress['id']
        logging.info ("Caller ID: %s " % callerID)

        # Try to find a custom header we use in client app to pass a pal name
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

        return tropo.RenderJson()
