import base64
import hmac
import pdb
import hashlib
import json
import os.path
import time
import cgi
import urllib

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

    def __init__(self, *args, **kwargs):
        directory = kwargs.get('directory',None)
        if not directory:
            directory = config.path+"/static"
        self.directory = directory
        self.init_args = kwargs
        self.mem = memcache.Client([config.memcache_host])
        self._fbSession = None

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
            return self.__class__(directory=fullpath)
        elif os.path.isfile(fullpath):
            return static.File(fullpath)
        else:
            return Toplevel(problempath=name)


    def setCookie(self, response, name, value, domain=None, path="/", expires=None):
        """Generates and signs a cookie for the give name/value"""
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = self._cookieSignature(value, timestamp)
        value = "|".join([value, timestamp, signature])
        cookie = Cookie(name, value, path=path, expires=expires, domain=domain)
        response.headers.setHeader('Set-Cookie', [cookie])

    def getCookie(self, name, default=''):
        cookies = self.ctx.headers.getHeader('cookie') or []
        for c in cookies:
            if c.name == name:
                return c.value
        return default

    def getFBSession(self):
        if not getattr(self,'_fbSession',None):
                self._fbSession = self._getFBSessionFromCookie()
        return self._fbSession

    def getFBUser(self):
        if not getattr(self, '_fbUser', None):
            self._fbUser = self.mem.get('_fbUser_%s' % self._fbSession['uid'])
        if not self._fbUser:
            fbApi = facebook.GraphAPI(self._fbSession['access_token'])
            self._fbUser = fbApi.get_object(self._fbSession['uid'])
            musicEntries = fbApi.request_old('users.getInfo',
                                             {'fields':'music',
                                              'uids':self._fbSession['uid'],
                                              'format':'json'
                                              })
            self._fbUser['bands'] = [mE.strip() for mE in musicEntries[0]['music'].split(',')]
            self.mem.set('_fbUser_%s' % self._fbSession['uid'], self._fbUser)

        return self._fbUser

    def getFBFriends(self):
        if getattr(self, '_fbFriends', None):
            return self._fbFriends
        self._fbFriends = self.mem.get('_fbFriends_%s' % self._fbSession['uid'])
        if not self._fbFriends:
            self._fbFriends = self._loadFBFriends()
            self.mem.set('_fbFriends_%s' % self._fbSession['uid'], self._fbFriends)
        return self._fbFriends
            

    def _loadFBFriends(self):
        '''load the fb friends list for a user into memory, along with their
        music preferences'''
        fbApi = facebook.GraphAPI(self._fbSession['access_token'])
        friends = fbApi.get_connections(self._fbSession['uid'], 'friends')['data']
        musicEntries = fbApi.request_old('users.getInfo',
                                         {'fields':'music',
                                          'uids':','.join([f['id'] for f in friends]),
                                          'format':'json'
                                          })
        artistRanking = {}
        for mE in musicEntries:
            if not mE['music']:
                continue
            bands = mE['music'].split(',')
            if len(bands) < 3:
                continue
            for band in bands:
                minBand = vidquery._makeMinTitle(band)
                if artistRanking.get(minBand,None):
                    artistRanking[minBand].append( [mE['uid'], band] )
                else:
                    artistRanking[minBand] = [ [mE['uid'], band] ]
        ranked = sorted( artistRanking.items(), key = lambda k: len(k[1]), reverse = True )
        ranked = [(r[0], len(r[1]), self._mostCommon(r[1])) for r in ranked][:20]
        return [r[2] for r in ranked]

    def _mostCommon(self, uid_artists):
        hits = {}
        for uid_artist in uid_artists:
            n = uid_artist[1].encode('ascii', 'xmlcharrefreplace').strip()

            if getattr(hits, n, None):
                hits[n] += 1
            else:
                hits[n] = 1
        hits = sorted( hits.items(), key = lambda k: k[1], reverse = True )
        return hits[0][0]

    def _getFBSessionFromCookie(self):
        """Parses the cookie set by the official Facebook JavaScript SDK.

        cookies should be a dictionary-like object mapping cookie names to
        cookie values.

        If the user is logged in via Facebook, we return a dictionary with the
        keys "uid" and "access_token". The former is the user's Facebook ID,
        and the latter can be used to make authenticated requests to the Graph API.
        If the user is not logged in, we return None.

        Download the official Facebook JavaScript SDK at
        http://github.com/facebook/connect-js/. Read more about Facebook
        authentication at http://developers.facebook.com/docs/authentication/.
        """
        cookie = self.getCookie("fbs_%s" % config.FB_APP_ID)
        if not cookie: return None
        args = dict((k, v[-1]) for k, v in cgi.parse_qs(cookie.strip('"')).items())
        payload = "".join(k + "=" + args[k] for k in sorted(args.keys())
                          if k != "sig")
        sig = hashlib.md5(payload + config.FB_APP_SECRET).hexdigest()
        if sig == args.get("sig") and time.time() < int(args["expires"]):
            return args
        else:
            return None


    def _cookieSignature(self, *parts):
        """Generates a cookie signature.

        We use the Facebook app secret since it is different for every app (so
        people using this example don't accidentally all use the same secret).
        """
        hash = hmac.new(config.FB_APP_SECRET, digestmod=hashlib.sha1)
        for part in parts: hash.update(part)
        return hash.hexdigest()
        

class JSONController(Controller, resource.PostableResource):
    creation_time = time.time()
    content_type = http_headers.MimeType('text','json')

    def respond(self):
        pass

    def render(self, ctx):
        self.ctx = ctx
        return http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type},
            json.dumps(self.respond()))

class HTMLController(Controller, resource.PostableResource):
    creation_time = time.time()
    content_type = http_headers.MimeType('text','html')

    def respond(self):
        pass

    def render(self, ctx):
        self.ctx = ctx
        return http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type},
            self.respond())

class FindVideos(JSONController):    
    def respond(self):
        artists = self.ctx.args.get('artist',[])
        artistVids = []
        ip_addr = self.ctx.remoteAddr.host
        for artist in artists:
            vidlogger.log(data_1=1,text_info=artist)
            artistVids.append( self.fetchVideos(artist) )
        return artistVids

    def fetchVideos(self, artist):
        cacheKey = 'videos_%s' % vidquery._makeMinTitle(artist)
        cachedRes = self.mem.get(cacheKey)
        if not cachedRes:
            cachedRes = vidquery.fetchVideos(artist)
            self.mem.set(cacheKey, cachedRes)
        return cachedRes

class FindSimilar(JSONController):    
    def respond(self):
        artist = self.ctx.args.get('artist')[0]
        try:
            similar = self.fetchSimilar(artist)
        except pylast.WSError:
            similar = []
        return similar

    def fetchSimilar(self, artist):
        cacheKey = 'similar_%s' % vidquery._makeMinTitle(artist)
        cachedRes = self.mem.get(cacheKey)
        if not cachedRes:
            cachedRes = lastfm.get_similar(artist)
            self.mem.set(cacheKey, cachedRes)
        return cachedRes

class Toplevel(HTMLController):
    addSlash = True
    def respond(self):
        arguments = dict( (k,v[0]) for k,v in self.ctx.args.iteritems() )
        
        template_args = {}
        if self.init_args.get('problempath',None):
             template_args['initialSearch'] = self.init_args['problempath'].split(',')

        if self.getFBSession():
            profile = self.getFBUser()
            if profile:
                template_args['fbSession'] = self._fbSession
                template_args['fbUser'] = profile

        return self.template("index", **template_args)

class FBFriends(JSONController):    
    def respond(self):
        self.getFBSession()
        fbFriends = self.getFBFriends()
        return fbFriends

class FBIndex(HTMLController):
    content_type = http_headers.MimeType('text', 'html')
    addSlash = True

    def respond(self):

        arguments = dict( (k,v[0]) for k,v in self.ctx.args.iteritems() )
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
    def respond(self):
        arguments = dict( (k,v[0]) for k,v in self.ctx.args.iteritems() )
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


