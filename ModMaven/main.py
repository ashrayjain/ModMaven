FACEBOOK_APP_ID = "579845202048952"

import facebook
import webapp2
import jinja2
import os
import json
import urllib2

from google.appengine.ext import db
from webapp2_extras import sessions

template_dir = os.path.join(os.path.dirname(__file__), 'templates')

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                       autoescape = True)

class Handler(webapp2.RequestHandler):
    """Handler Class with Utility functions for Templates"""
    def __write__(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def __render_str__(self, template, **params):
        t = jinja_environment.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.__write__(self.__render_str__(template, **kw))


class MainPage(Handler):
    """ Handler for the front page."""
    def get(self):
        isError = self.request.cookies.get('error')
        error = ""
        if isError:
            error = "The Module You Requested Was Not Found"
            self.response.headers.add_header('Set-Cookie', 'error=false; Path=/; Expires=Thu, 01-Jan-1970 00:00:00 GMT')
        self.render('main.html', NotFoundError=error)


class ModPage(Handler):
    """ Handler for the module page."""
    def get(self):
        modName = self.request.get('modName').upper()
        json_data = open("modInfo.json")
        data = json.load(json_data, encoding='latin1')
        if modName in data:
            self.render("modulepage.html", modName=modName, modTitle=data[modName]["title"], modDesc=data[modName]["description"])
            json_data.close()
        else:
            json_data.close()
            self.response.headers.add_header('Set-Cookie', 'error=true; Path=/')
            self.redirect('/')

app = webapp2.WSGIApplication([('/modpage/?', ModPage),
                               ('/.*', MainPage)],
                              debug=True)
