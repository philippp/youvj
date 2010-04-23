import base64
import hmac
import pdb
import hashlib
import json
import os.path
import time

from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode
from twisted.web2.http_headers import Cookie

import lastfm
import pylast
import vidquery
import config
import vidlogger
from lib import memcache, facebook, minifb

class Controller(resource.Resource):

  def __init__(self, directory=""):
    if not directory:
      directory = config.path+"/static"
    self.directory = directory
    self.mem = memcache.Client([config.memcache_host])
    self._fbUser = None

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

  def setCookie(self, response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    print "Trying to set %s to %s" % (name, value)
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = self._cookieSignature(value, timestamp)
    value = "|".join([value, timestamp, signature])
    cookie = Cookie(name, value, path=path, expires=expires, domain=domain)
    response.headers.setHeader('Set-Cookie', [cookie])

  def getCookie(self, ctx, name):
    cookies = ctx.headers.getHeader('cookie') or []
    for c in cookies:
      if c.name == name:
        return self._parseCookie(c.value)
    return ''

  def getLoggedInFB(self, ctx):
    if not getattr(self,'_fbUser',None):
      fb_id = self.getCookie(ctx, 'fb_user')
      if fb_id:
        profile = self.mem.get('fb_profile_%s' % fb_id)
        self._fbUser = profile
    return self._fbUser

  def _cookieSignature(self, *parts):
    """Generates a cookie signature.

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(config.FB_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()
    
  def _parseCookie(self, value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    if self._cookieSignature(parts[0], parts[1]) != parts[2]:
      logging.warning("Invalid cookie signature %r", value)
      return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
      logging.warning("Expired cookie %r", value)
      return None
    try:
      return base64.b64decode(parts[0]).strip()
    except:
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
      vidlogger.log(data_1=1,text_info=artist)
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
    arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )

    profile = self.getLoggedInFB(ctx)
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
    arguments = minifb.validate(config.FB_APP_SECRET,
                                arguments)

    print arguments
    if arguments['added'] != '0':
      flist = minifb.call("facebook.friends.get",
                          config.FB_APP_KEY,
                          config.FB_APP_SECRET,
                          session_key = arguments['session_key'])
      
      result = minifb.call("facebook.users.getInfo",
                           config.FB_APP_KEY,
                           config.FB_APP_SECRET,
                           fields = "name,pic_square,music",
                           uids = flist,
                           session_key = arguments['session_key'])

    return self.template("index")

class FBUserAdded(HTMLController):
  addSlash = True
  def respond(self, ctx):
    arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )
    arguments = minifb.validate(config.FB_APP_SECRET,
                                arguments)
    auth_token = arguments["auth_token"]
    result = minifb.call("facebook.auth.getSession",
                         config.FB_APP_KEY,
                         config.FB_APP_SECRET,
                         auth_token = auth_token)
    uid = result["uid"]
    session_key = result["session_key"]
    usersInfo = minifb.call("facebook.users.getInfo",
                            config.FB_APP_KEY,
                            config.FB_APP_SECRET,
                            session_key=session_key,
                            call_id=True,
                            fields="name,pic_square",
                            uids=uid) # uids can be comma separated list
    name = usersInfo[0]["name"]
    photo = usersInfo[0]["pic_square"]
    

    # Set the users profile FBML
    fbml = "<p>Welcome, new user, <b>%s</b></p>" % name
    minifb.call("facebook.profile.setFBML",
                config.FB_APP_KEY,
                config.FB_APP_SECRET,
                session_key=session_key,
                call_id=True, uid=uid, markup=fbml)


