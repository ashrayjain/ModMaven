import webapp2
import jinja2
import sys
import os
import json
import copy
from google.appengine.api import urlfetch


# Google DataStore
from google.appengine.ext import ndb
# webapp2 Sessions
from webapp2_extras import sessions
# External Libraries -
# Facebook SDK for Python
# http://github.com/pythonforfacebook/facebook-sdk
sys.path.append(os.path.join(os.path.dirname(__file__), 'libs'))
import facebook

# Constants
# FACEBOOK_APP_ID = "579845202048952"
# FACEBOOK_APP_SECRET = "97246d17b224a43c322cbca33bff0261"
FACEBOOK_APP_ID = "211279135690183"
FACEBOOK_APP_SECRET = "0a49fe29d02a7995563486ac95ba5a50"
IVLE_LAPI_KEY = "nR7o7vzmqBA3BAXxPrLLD"
SESSIONS_SECRET = "QR2YKc1ktlIvd9SvAI01PUFKVY7vso5sfSrDir5ebDbUoC3X7mgp2wNZkWCzlfVG"
CURRENT_SEM = ["2013/2014", "1"]

# Set up webapp2 Sessions
config = {'webapp2_extras.sessions': dict(secret_key=SESSIONS_SECRET)}

# Set up template directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                       autoescape=True)

data = json.load(open("data/modInfo.json"), encoding='latin1')


class User(ndb.Model):
    """DataStore Model Class for User Table"""
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    name = ndb.StringProperty("n", required=True)
    profile_url = ndb.StringProperty("pu", required=True)
    access_token = ndb.StringProperty("at", required=True)
    ivle_token = ndb.StringProperty("it")
    mods_done = ndb.JsonProperty("md")
    mods_precluded = ndb.JsonProperty("mp")


class Module(ndb.Model):
    users = ndb.JsonProperty("u", required=True)
    usersDone = ndb.JsonProperty("ud")

class Reply(ndb.Model):
    """Datastore Model Class for replies to posts"""
    created = ndb.DateTimeProperty(auto_now_add=True)
    answer = ndb.TextProperty(required=True)
    answeringUser = ndb.StringProperty(required=True)


class Post(ndb.Model):
    """Datastore Model Class for Posts"""
    moduleName=ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    question = ndb.TextProperty(required=True)
    askingUser = ndb.StringProperty(required=True)
    replies = ndb.StructuredProperty(Reply, repeated=True)


class Handler(webapp2.RequestHandler):
    """Handler Class with Utility functions for Templates"""

    def __write__(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def __render_str__(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.__write__(self.__render_str__(template, **kw))

    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in

            # for debugging
            # print "Retreived from session", self.session.get("user")

            return self.session.get("user")
        else:
            # for debugging
            #print "In cookie", self.session.get("user")

            # Either user just logged in or logged in for the first time
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                # Facebook authentication complete
                # Check to see if existing user
                user = User.get_by_id(cookie["uid"])
                #print user
                if not user:
                    # Not an existing user so get user info and
                    # create DataStore entry
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(
                        id=profile["id"],
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"]
                    )
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    # User already exists, update to the latest access token
                    user.access_token = cookie["access_token"]
                    user.put()

                # Start a session for the user
                self.session["user"] = dict(
                    name=user.name.split(None, 1)[0],
                    profile_url=user.profile_url,
                    id=user.key.id(),
                    access_token=user.access_token,
                )
                return self.session.get("user")
                # User didn't complete FB authentication
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()
