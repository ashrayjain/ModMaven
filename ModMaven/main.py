import webapp2
import jinja2
import os
import json
import cgi

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

class MainPage(webapp2.RequestHandler):
    """ Handler for the front page."""
    def get(self):
        template = jinja_environment.get_template('main.html')
        self.response.out.write(template.render())
        
class ModPage(webapp2.RequestHandler):
    """ Handler for the module page."""
    def post(self):
        input = self.request.get('modName')
        json_data = open("modInfo.json")
        data = json.load(json_data, encoding='latin1')
        if input in data:
            template = jinja_environment.get_template('modulepage.html')
        
            template_values = {
                'modName': input,
                'modTitle': data[input]["title"],
                'modDesc': data[input]["description"]
            }
            self.response.out.write(template.render(template_values))
        else:
            template = jinja_environment.get_template('main.html')
            template_values = {
                'NotFoundError': "The Module You Requested Was Not Found",
            }
            self.response.out.write(template.render(template_values))
        json_data.close()    
       

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/modpage', ModPage)],
                              debug=True)
