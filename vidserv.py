import pdb
import json
import os.path, time
from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode
import lastfm
import pylast
import vidquery
import minifb
import config

class Controller(resource.Resource):

  def __init__(self, directory=""):
    if not directory:
      directory = '/home/philippp/vidtunes/static'    
    self.directory = directory

  def template(self, view, **kwargs):
    """
    Render the template specified by view as a string. Template variables
    are specified as kwargs.
    view is the package name of the template: hello.index for views/hello/index.py
    """
    
    # We parse out periods to support nested modules within templates.
    target = "templates.%s" % view
    components = target.split('.')
    mod = __import__(target)
    for comp in components[1:]:
      mod = getattr(mod, comp)

    # Cheetah guarantees that the template class is named the same as the template module.
    tmpl = getattr(mod, components[-1])()
    [setattr(tmpl, k, v) for k,v in kwargs.items()]
    return str(tmpl)

  def childFactory( self, ctx, name ):
    ''' Find and serve static files '''
    fullpath = os.path.join(self.directory, name)
    if os.path.isdir(fullpath):
      return self.__class__(fullpath)
    elif os.path.isfile(fullpath):
      return static.File(fullpath)
    return None

class JSONController(Controller, resource.PostableResource):
  creation_time = time.time()
  content_type = http_headers.MimeType('text','json')

  def respond(self, ctx):
    pass

  def render(self, ctx):
    return http.Response(
      responsecode.OK,
      {'last-modified': self.creation_time,
      'content-type': self.content_type},
      json.dumps(self.respond(ctx)))

class HTMLController(Controller, resource.PostableResource):
  creation_time = time.time()
  content_type = http_headers.MimeType('text','html')

  def respond(self, ctx):
    pass

  def render(self, ctx):
    return http.Response(
      responsecode.OK,
      {'last-modified': self.creation_time,
      'content-type': self.content_type},
      self.respond(ctx))

  
class FindVideos(JSONController):  
  def respond(self, ctx):
    artists = ctx.args.get('artist',[])
    artistVids = []

    ip_addr = ctx.remoteAddr.host
    for artist in artists:
      artistVids.append( vidquery.fetchVideos(artist, ip_addr) )
    return artistVids

class FindSimilar(JSONController):  
  def respond(self, ctx):
    artist = ctx.args.get('artist')[0]
    try:
      similar = lastfm.get_similar(artist)
    except pylast.WSError:
      similar = []
    return similar

class Toplevel(Controller):
  addSlash = True
  def render(self, ctx):
    return http.Response(
      200, 
      {'content-type': http_headers.MimeType('text', 'html')},
      self.template("index")
      )

class FBIndex(HTMLController):
  content_type = http_headers.MimeType('text', 'html')
  addSlash = True

  def respond(self, ctx):

    arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )
    arguments = minifb.validate(config.FB_API_SECRET,
                                arguments)

    print arguments
    if arguments['added'] != '0':
      flist = minifb.call("facebook.friends.get",
                          config.FB_API_KEY,
                          config.FB_API_SECRET,
                          session_key = arguments['session_key'])
      
      result = minifb.call("facebook.users.getInfo",
                           config.FB_API_KEY,
                           config.FB_API_SECRET,
                           fields = "name,pic_square,music",
                           uids = flist,
                           session_key = arguments['session_key'])

    return self.template("index")

class FBUserAdded(HTMLController):
  addSlash = True
  def respond(self, ctx):
    arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )
    arguments = minifb.validate(config.FB_API_SECRET,
                                arguments)
    auth_token = arguments["auth_token"]
    result = minifb.call("facebook.auth.getSession",
                         config.FB_API_KEY,
                         config.FB_API_SECRET,
                         auth_token = auth_token)
    uid = result["uid"]
    session_key = result["session_key"]
    usersInfo = minifb.call("facebook.users.getInfo",
                            config.FB_API_KEY,
                            config.FB_API_SECRET,
                            session_key=session_key,
                            call_id=True,
                            fields="name,pic_square",
                            uids=uid) # uids can be comma separated list
    name = usersInfo[0]["name"]
    photo = usersInfo[0]["pic_square"]
    

    # Set the users profile FBML
    fbml = "<p>Welcome, new user, <b>%s</b></p>" % name
    minifb.call("facebook.profile.setFBML",
                config.FB_API_KEY,
                config.FB_API_SECRET,
                session_key=session_key,
                call_id=True, uid=uid, markup=fbml)


root = Toplevel()
root.putChild("findvideos", FindVideos())
root.putChild("findsimilar", FindSimilar())
root.putChild("fb_user_added", FBUserAdded())
root.putChild("fb_index", FBIndex())
site = server.Site(root)


# Standard twisted application Boilerplate
from twisted.application import service, strports
application = service.Application("demoserver")
s = strports.service('tcp:8080', channel.HTTPFactory(site))
s.setServiceParent(application)
