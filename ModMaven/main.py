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
            modPosts = Post.query(Post.moduleName==modName).order(-Post.created).fetch(20)

            self.render("modulepage.html",
                        isModpost=False if modPosts==[] else True,
                        modName=modName,
                        modTitle=data[modName]["ModuleTitle"],
                        modDesc=data[modName]["ModuleDescription"] if "ModuleDescription" in data[modName] else "Not Available",
                        modPosts=modPosts,
                        CurrentUser=self.current_user,
                        FacebookAppID=FACEBOOK_APP_ID,
                        IVLEKey=IVLE_LAPI_KEY)
        else:
            self.response.headers.add_header('Set-Cookie', 'error=true; Path=/')
            self.redirect('/')


class RequestMod(Handler):
    """ AXAJ Handler for responding to module data requests """
    def get(self):
        modName=self.request.get('modName').upper()
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Cache-Control'] = "max-age=600"
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
            self.response.out.write(json.dumps(self.__personalizeTree__(data[modName]['Tree'])))
            return
        self.response.out.write(json.dumps({}))
        return


    def __personalizeTree__(self, tree):
        if self.current_user:
            user = User.get_by_id(self.current_user['id'])
            tree['done'] = True if tree['name'] in user.mods_done else False
            self.__getVal__(tree, user.mods_done)
            self.__prune__(tree)
            print tree
        return tree

    def __prune__(self, tree):
        if tree['children']:
            minval=min([child['cost'] for child in tree['children']])
            tree['children'] = [child for child in tree['children'] if child['cost'] == minval]
            for child in tree['children']:
                self.__prune__(child)

    def __getVal__(self, tree, modsDone):
        if tree['children']:
            for child in tree['children']:
                self.__getVal__(child, modsDone)
                child['done'] = True if child['name'] in modsDone else False
            tree['cost'] = min([child['cost'] for child in tree['children']]) + (0 if tree['name'] in modsDone else 1)
        else:
            tree['cost'] = 0 if tree['name'] in modsDone else 1





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
            user.put()

    def __userMods__(self, token):
        modsDone = json.loads(urlfetch.fetch(
            "https://ivle.nus.edu.sg/api/Lapi.svc/Modules_Taken?APIKey={0}&AuthToken={1}&StudentID={2}".format(
                IVLE_LAPI_KEY,
                token,
                urlfetch.fetch("https://ivle.nus.edu.sg/api/Lapi.svc/UserID_Get?APIKey={0}&Token={1}".format(
                    IVLE_LAPI_KEY,
                    token),
                               deadline=60
                ).content[1:-1]
            ),
            deadline=60
        ).content)
        return [mod['ModuleCode'] for mod in modsDone['Results'] if not (mod['AcadYear'] == CURRENT_SEM[0] and mod['Semester'] == CURRENT_SEM[1])]


class RequestModList(Handler):
    def get(self):
        self.response.headers['Cache-Control'] = "max-age=3600"
        self.response.out.write(json.dumps(data["ModList"]))


class ModTaken(Handler):
    def get(self):
        userID = self.request.get('user')
        modUrl = self.request.get('mod')
        modAdded = Module.get_by_id(modUrl)
        if modAdded:
            modAdded['users'] += [userID]
        else:
            modAdded = Module(id=modUrl, users=[userID])
            modAdded.put()


class AddPost(Handler):
    def post(self):
        modName = self.request.get('module').upper()
        #print modName
        postcontent = self.request.get('PostContent')
        #print self.current_user
        CurrentUserName = self.current_user['name']
        post = Post(moduleName=modName, askingUser=CurrentUserName, question=postcontent)
        post.put()
        modPosts = Post.query(Post.moduleName==modName).order(-Post.created).fetch(20)
        self.render("modulepage.html",
                        modName=modName,
                        modTitle=data[modName]["ModuleTitle"],
                        modDesc=data[modName]["ModuleDescription"] if "ModuleDescription" in data[modName] else "Not Available",
                        modPosts=modPosts,
                        isModpost=True,
                        CurrentUser=self.current_user,
                        postSuccess=True,
                        FacebookAppID=FACEBOOK_APP_ID )

class AddReply(Handler):
    def post(self):
        modName = self.request.get('module').upper()
        modquestion = self.request.get('modpost')
        ans = self.request.get('answerBox')
        CurrentUserName = self.current_user['name']
        reply = Reply(answer=ans,answeringUser=CurrentUserName)
        posts = Post.query(Post.moduleName==modName).fetch()
        for post in posts :
            if post.question==modquestion:
                post.replies.append(reply)
                post.put()
        #postkey = ndb.Key('Post',postkeystring[11:-1])
        #post = postkey.get()
        modPosts = Post.query(Post.moduleName==modName).order(-Post.created).fetch(20)
        self.render("modulepage.html",
                        modName=modName,
                        modTitle=data[modName]["title"],
                        modDesc=data[modName]["description"] if "description" in data[modName] else "Not Available",
                        modPosts=modPosts,
                        isModpost=True,
                        CurrentUser=self.current_user,
                        postSuccess=True,
                        FacebookAppID=FACEBOOK_APP_ID )




app = webapp2.WSGIApplication([('/modpage/?', ModPage),
                               ('/modlist/?', RequestModList),
                               ('/addModPost/?', AddPost),
                               ('/modtaken/?', ModTaken),
                               ('/logout/?', Logout),
                               ('/getmod/?', RequestMod),
                               ('/ivle/?', IVLEVerify),
                               ('/gettree/?', RequestTree),
                               ('/addModPost/?', AddPost),
                               ('/addPostReply/?', AddReply),
                               ('/.*', MainPage)
                              ],
                              config=config,
                              debug=True)
