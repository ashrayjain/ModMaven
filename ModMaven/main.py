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
    def post(self):
        if self.current_user is not None:
            # Close the session
            self.session['user'] = None


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
            newtree = copy.deepcopy(tree)
            user = User.get_by_id(self.current_user['id'])
            if user.mods_done:
                newtree['done'] = True if newtree['name'] in user.mods_done else False
                if not newtree['done']:
                    newtree['prec'] = True if newtree['name'] in user.mods_precluded else False
                self.__getVal__(newtree, user.mods_done, user.mods_precluded)
                self.__prune__(newtree)
            return newtree
        else:
            return tree

    def __prune__(self, tree):
        if tree['cost'] == 0 and tree["name"] not in ["and", "or"]:
            tree['children'] = []
            return
        if tree['name'] == "or":
            minval = min([child['cost'] for child in tree['children']])
            indices = []
            for i in range(len(tree['children'])):
                if tree["children"][i]["cost"] == minval:
                    indices.append(i)
            if len(indices) == 1:
                child = tree["children"][indices[0]]
                tree["name"] = child["name"]
                tree["children"] = child["children"]
                if 'done' in child:
                    tree['done'] = child['done']
                if 'prec' in child:
                    tree['prec'] = child['prec']
                self.__prune__(tree)
                return
            else:
                tree['children'] = [tree["children"][index] for index in indices]
        for child in tree['children']:
            self.__prune__(child)

    def __getVal__(self, tree, modsDone, modsPrec):
        if tree['name'] in modsDone or tree['name'] in modsPrec:
            tree['cost'] = 0
        elif tree['children']:
            for child in tree['children']:
                self.__getVal__(child, modsDone, modsPrec)
                if child['name'] not in ['or', 'and']:
                    child['done'] = True if child['name'] in modsDone else False
                    if not child['done']:
                        child['prec'] = True if child['name'] in modsPrec else False
            if tree["name"] == "and":
                tree["cost"] = sum([child["cost"] for child in tree['children']])
            elif tree["name"] == "or":
                tree["cost"] = min([child["cost"] for child in tree['children']])
            else:
                tree["cost"] = tree["children"][0]["cost"] + 1
        elif tree["name"] in data:
            tree['cost'] = 1
        else:
            tree["cost"] = 99


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
            precludedMods = set(user.mods_done)
            for mod in user.mods_done:
                if isinstance(data[mod]["Preclusion"], list):
                    precludedMods.update(data[mod]["Preclusion"])
            user.mods_precluded = list(precludedMods)
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
    def post(self):
        mod = self.request.get('mod').split("modName=")[1].split("&", 1)[0]
        modAdded = Module.get_by_id(mod)
        if modAdded:
            modAdded.users[self.current_user['id']] = ""
        else:
            modAdded = Module(id=mod, users={self.current_user['id']:""})
        modAdded.put()
        #print modAdded.users

    def delete(self):
        mod = Module.get_by_id(self.request.get('mod').split("modName=")[1].split("&", 1)[0])
        del mod.users[self.current_user['id']]
        mod.put()
        #print mod.users


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
        modPosts = [post] + list(modPosts)
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
                    modTitle=data[modName]["ModuleTitle"],
                    modDesc=data[modName]["ModuleDescription"] if "ModuleDescription" in data[
                        modName] else "Not Available",
                    modPosts=modPosts,
                    isModpost=True,
                    CurrentUser=self.current_user,
                    postSuccess=True,
                    FacebookAppID=FACEBOOK_APP_ID)


class GetUsers(Handler):
    def get(self):
        self.response.headers['Content-Type'] = "application/json"
        mod = Module.get_by_id(self.request.get("modName"))
        self.response.out.write(json.dumps({} if mod == None else mod.users))


class JumpPage(Handler):
    def get(self):
        for modName in data:
            self.response.out.write("<a href='http://nusmodmaven.appspot.com/modpage?modName="+modName+"'>"+modName+"</a>")


class ChkIVLE(Handler):
    def get(self):
        self.response.out.write("1" if User.get_by_id(self.current_user['id']).ivle_token else "0")


app = webapp2.WSGIApplication(
    [
        ('/modpage/?', ModPage),
        ('/modlist/?', RequestModList),
        ('/addModPost/?', AddPost),
        ('/modtaken/?', ModTaken),
        ('/logout/?', Logout),
        ('/getmod/?', RequestMod),
        ('/ivle/?', IVLEVerify),
        ('/gettree/?', RequestTree),
        ('/getusers/?', GetUsers),
        ('/addPostReply/?', AddReply),
        ('/chkIVLE', ChkIVLE),
        ('/jumpPage', JumpPage),
        ('/.*', MainPage)
    ],
    config=config,
    debug=True)
