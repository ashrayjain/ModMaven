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
            modPosts = Post.query(Post.moduleName==modName).order(-Post.created).fetch(20)

            self.render("modulepage.html",
                        isModpost=False if modPosts==[] else True,
                        modName=modName,
                        modTitle=data[modName]["title"],
                        modDesc=data[modName]["description"] if "description" in data[modName] else "Not Available",
                        modPosts=modPosts,
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
                        modTitle=data[modName]["title"],
                        modDesc=data[modName]["description"] if "description" in data[modName] else "Not Available",
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
                               ('/logout/?', Logout),
                               ('/getmod/?', RequestMod),
                               ('/gettree/?', RequestTree),
                               ('/addModPost/?', AddPost),
                               ('/addPostReply/?', AddReply),
                               ('/.*', MainPage)
                              ],
                              config=config,
                              debug=True)
