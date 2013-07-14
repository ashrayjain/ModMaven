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
                    FacebookAppID=FACEBOOK_APP_ID,
                    IVLEKey=IVLE_LAPI_KEY)


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
                        modDesc=data[modName]["description"] if "description" in data[modName] else "Not Available",
                        CurrentUser=self.current_user,
                        FacebookAppID=FACEBOOK_APP_ID)
        else:
            self.response.headers.add_header('Set-Cookie', 'error=true; Path=/')
            self.redirect('/')


class RequestMod(Handler):
    """ AXAJ Handler for responding to module data requests """
    def get(self):

        modName=self.request.get('modName').upper()
        self.response.headers['Content-Type'] = "application/json"
        if modName in data:
            self.response.out.write(json.dumps(data[modName]))
            return
        self.response.out.write(json.dumps({}))
        return

class RequestTree(Handler):
    def get(self):
        modName = self.request.get('modName').upper()
        self.response.headers['Content-Type'] = "application/json"
        if modName in data:
            self.response.out.write(json.dumps(data[modName]['tree']))
            return
        self.response.out.write(json.dumps({}))
        return

class IVLEVerify(Handler):
    """ Handler for IVLE API """

    # Get Method for allowing AJAX Post call and improve UX
    def get(self):
        self.response.out.write("")

    # Update IVLE Token and Mods Taken
    def post(self):
        token = self.request.get('token')
        if token:
            user = User.get_by_id(self.current_user['id'])
            user.ivle_token = token
            user.mods_done = self.__userMods__(token)
            print user.mods_done
            user.put()

    def __userMods__(self, token):
        modsDone = json.loads(urllib2.urlopen(
            "https://ivle.nus.edu.sg/api/Lapi.svc/Modules_Taken?APIKey={0}&AuthToken={1}&StudentID={2}".format(
                IVLE_LAPI_KEY,
                token,
                urllib2.urlopen("https://ivle.nus.edu.sg/api/Lapi.svc/UserID_Get?APIKey={0}&Token={1}".format(
                    IVLE_LAPI_KEY,
                    token)
                ).read()[1:-1]
            )
        ).read())
        return [mod['ModuleCode'] for mod in modsDone['Results']]

class RequestModList(Handler):
    def get(self):
        self.response.out.write(json.dumps(data["modlist"]))

app = webapp2.WSGIApplication([('/modpage/?', ModPage),
                               ('/modlist/?', RequestModList),
                               ('/logout/?', Logout),
                               ('/getmod/?', RequestMod),
                               ('/ivle/?', IVLEVerify),
                               ('/gettree/?', RequestTree),
                               ('/.*', MainPage)
                              ],
                              config=config,
                              debug=True)
