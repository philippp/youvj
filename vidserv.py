import base64
import hmac
import pdb
import hashlib
import json
import os.path
import time
import cgi
import urllib

#from twisted.web2 import server, http, resource, channel, stream
#from twisted.web2 import static, http_headers, responsecode
#from twisted.web2.http_headers import Cookie

import lastfm
import pylast
import vidquery
import vidmapper
import config
import vidlogger
import viddb
import genres
from lib import memcache, facebook, minifb

class Cookie(object):
    @staticmethod
    def generateDateTime(secSinceEpoch):
        """Convert seconds since epoch to HTTP datetime string."""
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(secSinceEpoch)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
        return s

class FBRequest(object):
    def __init__(self, ctx, mem=None):
        self._req = ctx
        self.args = ctx.args
        self.mem = mem

    def __getattr__(self, name):
        return getattr(self._req, name)
        
    def setCookie(self, response, name, value, domain=None, path="/", expires=None, signed=False):
        """Generates and signs a cookie for the give name/value"""
        if signed:
            timestamp = str(int(time.time()))
            value = base64.b64encode(value)
            signature = self._cookieSignature(value, timestamp)
            value = "|".join([value, timestamp, signature])
        cookie = Cookie(name, value, path=path, expires=expires, domain=domain)
        response.headers.setHeader('Set-Cookie', [cookie])

    def getCookie(self, name, default=''):
        cookies = self._req.headers.getHeader('cookie') or []
        value = default
        for c in cookies:
            if c.name == name:
                cparts = c.value.split('|')
                value = c.value
                if len(cparts) == 3:
                    value, tstamp, sig = cparts
                    realsig = self._cookieSignature(value, tstamp)
                    value = base64.b64decode(value)
                    assert sig == realsig
        return value

    def _cookieSignature(self, *parts):
        """Generates a cookie signature.

        We use the Facebook app secret since it is different for every app (so
        people using this example don't accidentally all use the same secret).
        """
        hash = hmac.new(config.FB_APP_SECRET, digestmod=hashlib.sha1)
        for part in parts: hash.update(part)
        return hash.hexdigest()
        

    def _getFBSession(self):
        self._req._fb_session = getattr(self._req,'_fb_session',None)
        if not self._req._fb_session:
            self._req._fb_session = self._getFBSessionFromCookie()
        return self._req._fb_session

    def getSession(self):
        fb_session = self._getFBSession()
        session = {}

        if not fb_session:
            self.setSession(0)
            return  {'fb':{}, 'uid':0}
            
        self._req._uvj_session = getattr(self._req, '_uvj_session', {})
        uvj_has_fb = self._req._uvj_session.get('fb',None)

        if not self._req._uvj_session or ( fb_session and not uvj_has_fb ):
            _sess_str = self.getCookie('uvj_session')
            _sess = _sess_str and cgi.parse_qs(_sess_str) or {}
            _sess = dict([ (k,len(v) == 1 and v[0] or v) for k, v in _sess.iteritems()])

            _sess['uid'] = int(_sess.get('uid','0'))
            self._req._uvj_session = _sess
            if fb_session and not self._req._uvj_session['uid']:
                self.setSession(vidmapper.tset_fbid(viddb.get_conn(),
                                                    fb_session["uid"]))
        session = self._req._uvj_session.copy()
        session['fb'] = fb_session
        return session

    def setSession(self, user_id):
        self._req._uvj_session = {'uid':user_id}
        session_str = urllib.urlencode(self._req._uvj_session)
        self.setCookie(self._req.response, 'uvj_session',session_str,signed=True)

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

    def getUser(self):
        sess = self.getSession()
        return {'id':sess['uid'], 'fb':self.getFBUser()}

    def getFBUser(self):
        fb_session = self.getSession()['fb']
        if not fb_session.get('uid',0):
            return {}

        if not getattr(self._req, '_fbUser', None):
            self._req._fbUser = self.mem.get('_fbUser_%s' % fb_session['uid'])
        if not self._req._fbUser:
            fbApi = facebook.GraphAPI(fb_session['access_token'])
            try:
                self._req._fbUser = fbApi.get_object(fb_session['uid'])
            except facebook.GraphAPIError, e:
                print e.code
                return None
            musicEntries = fbApi.request_old('users.getInfo',
                                             {'fields':'music',
                                              'uids':fb_session['uid'],
                                              'format':'json'
                                              })
            if type(musicEntries) == dict and musicEntries.get('error_code',0):
                musicList = ''
            else:
                musicList = musicEntries and musicEntries[0].get('music','') or ''
            self._req._fbUser['bands'] = [mE.strip() for mE in musicList.split(',')]
            self.mem.set('_fbUser_%s' % fb_session['uid'], self._req._fbUser)

        return self._req._fbUser

    def getFBFriends(self):
        fb_session = self.getSession()['fb']
        if getattr(self._req, '_fbFriends', None):
            return self._req._fbFriends
        self._req._fbFriends = self.mem.get('_fbFriends_%s' % fb_session['uid'])
        if not self._req._fbFriends:
            self._req._fbFriends = self._loadFBFriends()
            self.mem.set('_fbFriends_%s' % fb_session['uid'], self._req._fbFriends)
        return self._req._fbFriends
            

    def _filterFBBandNames(self, bandList):
        res = []
        for b in bandList:
            b = b.strip().lower()
            if b in genres.genres:
                continue
            if len(b.split(" ")) > 5:
                continue
            res.append(b)
        return res

    def _loadFBFriends(self):
        '''load the fb friends list for a user into memory, along with their
        music preferences'''
        fb_session = self.getSession()['fb']
        fbApi = facebook.GraphAPI(fb_session['access_token'])
        friends = fbApi.get_connections(fb_session['uid'], 'friends')['data']

        friends = dict([(int(f['id']),f) for f in friends])
        t1 = time.time()
        musicEntries = fbApi.request_old('users.getInfo',
                                         {'fields':'music',
                                          'uids':','.join([str(k) for k in friends.keys()]),
                                          'format':'json'
                                          })
        artistRanking = {}

        if type(musicEntries) == dict and musicEntries.get('error_code',0):
            musicEntries = []

        for mE in musicEntries:
            if not mE['music']:
                continue
            bands = mE['music'].split(',')
            bands = self._filterFBBandNames(bands)
            if len(bands) < 3:
                continue
            friends[mE['uid']]['bands'] = bands
            friends[mE['uid']]['music_str'] = mE['music']
            for band in bands:
                minBand = vidquery._makeMinTitle(band)
                if artistRanking.get(minBand,None):
                    artistRanking[minBand].append( [mE['uid'], band] )
                else:
                    artistRanking[minBand] = [ [mE['uid'], band] ]

        #Sort most popular artists in your social group
        ranked = sorted( artistRanking.items(),
                         key = lambda k: len(k[1]),
                         reverse = True )
        ranked = [(r[0], len(r[1]), self._mostCommon(r[1])) for r in ranked][:20]

        friends = sorted( friends.values(),
                          key = lambda f: len(f.get('bands',[])),
                          reverse = True)

        return {'ranked' : [r[2] for r in ranked], 'friends':friends}

    def _mostCommon(self, uid_artists):
        hits = {}
        for uid_artist in uid_artists:
            n = uid_artist[1].encode('ascii', 'xmlcharrefreplace').strip()

            if hits.get(n, None):
                hits[n] += 1
            else:
                hits[n] = 1
        hits = sorted( hits.items(), key = lambda k: k[1], reverse = True )
        return hits[0][0]


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
        resp = http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type})
        ctx.response = resp
        resp_str = json.dumps(self.respond(FBRequest(ctx, self.mem)))
        resp.stream = stream.IByteStream(resp_str)
        return resp

class HTMLController(Controller, resource.PostableResource):
    creation_time = time.time()
    content_type = http_headers.MimeType('text','html')

    def respond(self):
        pass

    def render(self, ctx):
        resp = http.Response(
            responsecode.OK,
            {'last-modified': self.creation_time,
            'content-type': self.content_type})
        ctx.response = resp
        resp_str = self.respond(FBRequest(ctx, self.mem))
        resp.stream = stream.IByteStream(resp_str)
        return resp

class FindVideos(JSONController):    
    def respond(self, ctx):
        artists = ctx.args.get('artist',[])
        artistVids = []
        ip_addr = ctx.remoteAddr.host
        for artist in artists:
            vidlogger.log(ctx=ctx,
                          data_1=vidlogger.EVENT_SEARCH,
                          text_info=artist)
            artistVids.append( self.fetchVideos(artist) )
        return artistVids

    def fetchVideos(self, artist):
        print "in fetchVideos"
        cacheKey = 'videos_%s' % vidquery._makeMinTitle(artist)
        cachedRes = self.mem.get(cacheKey)
        if not cachedRes:
            cachedRes = vidquery.fetchVideos(artist)
            self.mem.set(cacheKey, cachedRes)
        return cachedRes

class ClientLogger(JSONController):
    def respond(self, ctx):
        args = dict( [ (k, v[0]) for k, v in ctx.args.iteritems() ] )
        vidlogger.log(ctx=ctx, **args)
        return True

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

class SaveVideo(JSONController):    
    def respond(self, ctx):
        uid = ctx.getSession()['uid']
        if not uid:
            return False
        saveArgs = viddb.COLS['youtube_videos']
        vidData = {}
        for a in saveArgs:
            vidData[a] = ctx.args.get(a)[0]
        vidData['description'] = vidData['description'][:255]
        vidmapper.saveVideo(viddb.get_conn(), vidData, uid)
        
        return True


class ListSavedVideos(JSONController):    
    def respond(self, ctx):
        uid = ctx.getSession()['uid']
        if not uid:
            return []
        conn = viddb.get_conn()
        yids = vidmapper.listSavedVideos(conn, uid)
        vids = vidmapper.retrieveVideos(conn, yids)
        return vids

class UnSaveVideo(JSONController):    
    def respond(self, ctx):
        uid = ctx.getSession()['uid']
        youtube_id = ctx.args.get('youtube_id')[0]
        vidmapper.unSaveVideo(viddb.get_conn(), youtube_id, uid)
        return 1

class Toplevel(HTMLController):
    addSlash = True
    def respond(self, ctx):
        arguments = dict( (k,v[0]) for k,v in ctx.args.iteritems() )
        
        user = ctx.getUser()
        template_args = {
            'fbSession':ctx.getSession()['fb'],
            'fbUser':ctx.getUser()['fb'],
            'user':ctx.getSession()['uid']
            }

        if user.get('id',0):
            template_args['favorites'] = vidmapper.listSavedVideos(viddb.get_conn(), user['id'])
        else:
            template_args['favorites'] = []
        if self.init_args.get('problempath',None):
             template_args['onLoadSearch'] = self.init_args['problempath'].split(',')


        return self.template("index", **template_args)

class FBFriends(JSONController):    
    def respond(self, ctx):
        ctx.getSession()
        fbFriends = ctx.getFBFriends()
        return fbFriends


