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

class FBRequest(object):
    def __init__(self, ctx, mem=None):
        self._req = ctx
        self.args = ctx.args
        self.mem = mem

    def __getattr__(self, name):
        return getattr(self._req, name)
        
    def setCookie(self, response, name, value, domain=None, path="/", expires=None):
        """Generates and signs a cookie for the give name/value"""
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = self._cookieSignature(value, timestamp)
        value = "|".join([value, timestamp, signature])
        cookie = Cookie(name, value, path=path, expires=expires, domain=domain)
        response.headers.setHeader('Set-Cookie', [cookie])

    def getCookie(self, name, default=''):
        cookies = self._req.headers.getHeader('cookie') or []
        for c in cookies:
            if c.name == name:
                return c.value
        return default

    def _cookieSignature(self, *parts):
        """Generates a cookie signature.

        We use the Facebook app secret since it is different for every app (so
        people using this example don't accidentally all use the same secret).
        """
        hash = hmac.new(config.FB_APP_SECRET, digestmod=hashlib.sha1)
        for part in parts: hash.update(part)
        return hash.hexdigest()
        

    def getFBSession(self):
        if not getattr(self._req,'_fbSession',None):
                self._req._fbSession = self._getFBSessionFromCookie()
        return self._req._fbSession

    def getFBUser(self):
        if not getattr(self._req, '_fbUser', None):
            self._req._fbUser = self.mem.get('_fbUser_%s' % self._req._fbSession['uid'])
        if not self._req._fbUser:
            fbApi = facebook.GraphAPI(self._req._fbSession['access_token'])
            try:
                self._req._fbUser = fbApi.get_object(self._req._fbSession['uid'])
            except facebook.GraphAPIError, e:
                print e.code
                return None
            musicEntries = fbApi.request_old('users.getInfo',
                                             {'fields':'music',
                                              'uids':self._req._fbSession['uid'],
                                              'format':'json'
                                              })
            musicList = musicEntries[0].get('music','') or ''
            self._req._fbUser['bands'] = [mE.strip() for mE in musicList.split(',')]
            self.mem.set('_fbUser_%s' % self._req._fbSession['uid'], self._req._fbUser)

        return self._req._fbUser

    def getFBFriends(self):
        if getattr(self._req, '_fbFriends', None):
            return self._req._fbFriends
        self._req._fbFriends = self.mem.get('_fbFriends_%s' % self._req._fbSession['uid'])
        if not self._req._fbFriends:
            self._req._fbFriends = self._loadFBFriends()
            self.mem.set('_fbFriends_%s' % self._req._fbSession['uid'], self._req._fbFriends)
        return self._req._fbFriends
            

    def _loadFBFriends(self):
        '''load the fb friends list for a user into memory, along with their
        music preferences'''
        fbApi = facebook.GraphAPI(self._req._fbSession['access_token'])
        friends = fbApi.get_connections(self._req._fbSession['uid'], 'friends')['data']
        t1 = time.time()
        musicEntries = fbApi.request_old('users.getInfo',
                                         {'fields':'music',
                                          'uids':','.join([f['id'] for f in friends]),
                                          'format':'json'
                                          })
        t2 = time.time()
        print "%s seconds to fetch" % (t2 - t1)
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
        t3 = time.time()
        print "%s seconds to sort" % (t3 - t2)
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

class Controller(resource.Resource):

    def __init__(self, *args, **kwargs):
        directory = kwargs.get('directory',None)
        if not directory:
            directory = config.path+"/static"
        self.directory = directory
        self.init_args = kwargs
        self.mem = memcache.Client([config.memcache_host])

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


class JSONController(Controller, resource.PostableResource):
    creation_time = time.time()
    content_type = http_headers.MimeType('text','json')

    def respond(self):
        pass

    def render(self, ctx):
        return http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type},
            json.dumps(self.respond(FBRequest(ctx, self.mem))))

class HTMLController(Controller, resource.PostableResource):
    creation_time = time.time()
    content_type = http_headers.MimeType('text','html')

    def respond(self):
        pass

    def render(self, ctx):
        return http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type},
            self.respond(FBRequest(ctx, self.mem)))

class FindVideos(JSONController):    
    def respond(self, ctx):
        artists = ctx.args.get('artist',[])
        artistVids = []
        ip_addr = ctx.remoteAddr.host
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
    def respond(self, ctx):
        artist = ctx.args.get('artist')[0]
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
    def respond(self, ctx):
        arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )
        
        template_args = {}
        if self.init_args.get('problempath',None):
             template_args['initialSearch'] = self.init_args['problempath'].split(',')

        if ctx.getFBSession():
            profile = ctx.getFBUser()
            if profile:
                template_args['fbSession'] = ctx.getFBSession()
                template_args['fbUser'] = profile

        return self.template("index", **template_args)

class FBFriends(JSONController):    
    def respond(self, ctx):
        ctx.getFBSession()
        fbFriends = ctx.getFBFriends()
        return fbFriends


