from init_config import *


class MainPage(Handler):
    """Handler for the front page"""

    def get(self):
        isError = self.request.cookies.get('error')
        error = ""
        if isError:
            error = "The Module You Requested Was Not Found"
            self.response.headers.add_header('Set-Cookie', 'error=false; Path=/; Expires=Thu, 01-Jan-1970 00:00:00 GMT')
        self.render('main.html',
                    NotFoundError=error,
                    CurrentUser=self.current_user,
                    FacebookAppID=FACEBOOK_APP_ID)


class Logout(Handler):
    """Handler for AJAX calls for clearing session (logging out)"""

    def get(self):
        if self.current_user is not None:
            # Close the session
            self.session['user'] = None
        return


class ModPage(Handler):
    """ Handler for the module page."""

    def get(self):
        modName = self.request.get('modName').upper()
        if modName in data:
            self.render("modulepage.html",
                        modName=modName,
                        modTitle=data[modName]["title"],
                        modDesc=data[modName]["description"],
                        CurrentUser=self.current_user,
                        FacebookAppID=FACEBOOK_APP_ID)
        else:
            self.response.headers.add_header('Set-Cookie', 'error=true; Path=/')
            self.redirect('/')

class RequestMod(Handler):
    def get(self):
        modName=self.request.get('modName').upper()
        if modName in data:
            return data[modName]
        return None

class TreeData(Handler):
    def get(self):
        modName = self.request.get('modName')
        if modName in data:
            retJSON = {'name': modName, 'children': self.getPrereq(data[modName]['prerequisite'])}
            return retJSON
        return None

    def getPrereq(self, prereq):
        """Given a prereq, returns all prereqs of that prereq"""
        retList = []
        if isinstance(prereq, dict):
            for prereqs in prereq:


        elif len(prereq) < 9:
            if 'prerequisite' in data[prereq]:
                retList.append({'name': prereq, 'children': self.getPrereq(data[prereq]['prerequisite'])})
            else:
                retList.append({'name': prereq, 'children': []})
        else:
            return prereq




app = webapp2.WSGIApplication([('/modpage/?', ModPage),
                               ('/logout/?', Logout),
                               ('/gettree/?', TreeData),
                               ('/getmod/?', RequestMod),
                               ('/.*', MainPage)
                              ],
                              config=config,
                              debug=True)
