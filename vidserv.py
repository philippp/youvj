import base64
import cgi
import hashlib
import hmac
import json
import os.path
import pdb
import time
import urllib

import config
import genres
import lastfm
import pylast
import vidauth
import viddb
import vidfail
import vidlogger
import vidmapper
import vidquery
import webob

from lib import memcache

class Controller(object):

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


class JSONController(Controller):

    def respond(self, form):
        pass

    def render(self, req):
        res = webob.Response()
        self.res = res
        res.content_type = 'text/json'
        res.charset = 'utf8'
        res.body = json.dumps(self.respond(req))
        return res

class HTMLController(Controller):
    def respond(self):
        pass

    def render(self, req):
        res = webob.Response()
        self.res = res
        res.body = self.respond(req)
        return res

class FrontPage(HTMLController):
    def respond(self, req):
        return self.template("landing_page")

class Browse(HTMLController):
    def respond(self, req):
        artist = req.args.get('artist','')
        artistVids = []

        ip_addr = getattr(req.remote_addr,'host','67.207.139.31')
        artistVids = artist and self.fetchVideos(artist) or []
        return self.template("browse",
                             artistVids = artistVids,
                             artist = artist
                             )

    def fetchVideos(self, artist):
        cacheKey = 'videos_%s' % vidquery._makeMinTitle(artist)
        cachedRes = self.mem.get(cacheKey)
        if not cachedRes:
            cachedRes = vidquery.fetchVideos(artist)
            self.mem.set(cacheKey, cachedRes)
        return cachedRes

class UserLogin(JSONController):
    def respond( self, req ):
        email = req.args.get('email','')
        raw_password = req.args.get('password','')
        user_data = vidmapper.getUser( viddb.get_conn(),
                                       email )
        if not user_data:
            raise vidfail.InvalidEmail()
        
        if not vidauth.auth_user( user_data, raw_password ):
            raise vidfail.InvalidPassword()

        session_str = vidauth.encode_session_str( user_data )
        self.res.set_cookie('session',session_str,
                             max_age = 60*60*24*10,
                             path = '/',
                             domain = '.'+config.hostname)
        return True

class UserLogout(JSONController):
    def respond( self, req ):
        self.res.set_cookie('session','0',
                             max_age = 60*60*24*10,
                             path = '/',
                             domain = config.hostname)
        return True

class UserCreate(JSONController):
    def respond( self, req ):
        email = req.args.get('email','')
        raw_password = req.args.get('password','')
        user_data = vidmapper.getUser( viddb.get_conn(),
                                       email )
        if user_data:
            raise vidfail.UserExists()
        
        vidmapper.addUser( viddb.get_conn(),
                           email,
                           raw_password )

        user_data = vidmapper.getUser( viddb.get_conn(),
                                       email )

        session_str = vidauth.encode_session_str( user_data )
        self.res.set_cookie('session',session_str,
                             max_age = 60*60*24*10,
                             path = '/',
                             domain = config.hostname,
                             secure = True)
        return 
class FindVideos(JSONController):    
    def respond(self, req):
        artist = req.args.get('artist')
        ip_addr = getattr(req.remote_addr,'host','67.207.139.31')
        artistVids = self.fetchVideos(artist)
        return artistVids

    def fetchVideos(self, artist):
        cacheKey = 'videos_%s' % vidquery._makeMinTitle(artist)
        cachedRes = self.mem.get(cacheKey)
        if not cachedRes:
            cachedRes = vidquery.fetchVideos(artist)
            self.mem.set(cacheKey, cachedRes)
        return cachedRes

class ClientLogger(JSONController):
    def respond(self, req):
        args = dict( [ (k, v[0]) for k, v in req.args.iteritems() ] )
        vidlogger.log(req=req, **args)
        return True

class FindSimilar(JSONController):    
    def respond(self, req):
        artist = req.args.get('artist')
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
    def respond(self, req):
        uid = req.user_id
        if not uid:
            return False
        saveArgs = viddb.COLS['youtube_videos']
        vidData = {}
        for a in saveArgs:
            vidData[a] = req.args.get(a)[0]
        vidData['description'] = vidData['description'][:255]
        vidmapper.saveVideo(viddb.get_conn(), vidData, uid)
        
        return True


class ListSavedVideos(JSONController):    
    def respond(self, req):
        uid = req.user_id
        if not uid:
            return []
        conn = viddb.get_conn()
        yids = vidmapper.listSavedVideos(conn, uid)
        vids = vidmapper.retrieveVideos(conn, yids)
        return vids

class UnSaveVideo(JSONController):    
    def respond(self, req):
        uid = req.user_id
        youtube_id = req.args.get('youtube_id')[0]
        vidmapper.unSaveVideo(viddb.get_conn(), youtube_id, uid)
        return 1

class Toplevel(HTMLController):
    addSlash = True
    def respond(self, req):
        arguments = dict( (k,v[0]) for k,v in req.args.iteritems() )
        
        user_id = req.user_id
        template_args = {
            'fbSession':0,
            'fbUser':0,
            'user':user_id,
            }

        if user_id != 0:
            template_args['favorites'] = vidmapper.listSavedVideos(viddb.get_conn(), user_id)
        else:
            template_args['favorites'] = []
        if getattr(req,'problempath',None):
             template_args['onLoadSearch'] = req.problempath.split(',')


        return self.template("index", **template_args)
