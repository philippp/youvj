#!/usr/bin/env python

import cgi
import logging
import optparse
import sys
import os.path
import traceback
import urllib2

import gogreen.wsgi
import vidserv
import config
import magic
import daemon
from webob import Request, Response

handlers = {}

handlers = {
    '' : vidserv.FrontPage,
    'browse' : vidserv.Browse,
    'findvideos' : vidserv.FindVideos,
    'findsimilar' : vidserv.FindSimilar,
    'savevideo' : vidserv.SaveVideo,
    'unsavevideo' : vidserv.UnSaveVideo,
    'listsavedvideos' : vidserv.ListSavedVideos,
    'log' : vidserv.ClientLogger,
    'user/login' : vidserv.UserLogin,
    'user/logout' : vidserv.UserLogout,
    'user/create' : vidserv.UserCreate,
}

def wsgiapp(env, start_response):
    request = Request(env)
    request.args = getattr(request, request.method,{})
    request.user_id = 0

    # Try to hit actual responders
    for n, c in handlers.iteritems():
        if request.path_info == '/%s' % n:
            try:
                resp = c().render(request)
            except Exception, e:
                traceback.print_exc()
                e_msg = "Oh snaps, I messed up. SOWEE."
                start_response("500 SERVER ERROR",
                               [('content-type','text/html'),
                                ('content-length',len(e_msg))])
                return [e_msg]
            start_response(resp.status,
                           resp.headerlist)
            return [resp.body]

    # If that fails, look for a file at this location
    fpath = config.path + '/static' + request.path_info
    if os.path.isfile(fpath):
        mime = from_file(fpath)
        if fpath[-4:] == ".css":
            mime = "text/css"
        resp = file(fpath, 'r').read()
        start_response("200 OK",
                       [('content-type',mime),
                        ('content-length',len(resp))])
        return [resp]

    # Oh snaps! I guess the user is searching for an artist.
    artist_name = urllib2.unquote(request.path.split('/')[1])
    request.args['artist'] = artist_name
    try:
        resp = vidserv.Browse().render(request)
    except Exception, e:
        traceback.print_exc()
        e_msg = "Oh snaps, I messed up. SOWEE."
        start_response("500 SERVER ERROR",
                       [('content-type','text/html'),
                        ('content-length',len(e_msg))])
        return [e_msg]
    start_response(resp.status,
                   resp.headerlist)
    return [resp.body]

def from_file(fname):
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    type =  ms.file(fname)
    return type


class MyDaemon(daemon.Daemon):
    def run(self):
        gogreen.wsgi.serve((self.host, self.port), wsgiapp,
                           access_log='access.log')

if __name__ == "__main__":
    parser = optparse.OptionParser(add_help_option=False)
    parser.add_option("-p", "--port", type="int", default=config.port)
    parser.add_option("-h", "--host", default=config.hostname)
    parser.add_option("-d", "--daemon", default='')

    options, args = parser.parse_args()

    if not options.daemon:
        gogreen.wsgi.serve((options.host, options.port), wsgiapp,
                           access_log='access.log')
    else:
        d = MyDaemon('/tmp/youvj.pid',
                     port = options.port,
                     host = options.host)
        if options.daemon == 'start':
            d.start()
        elif options.daemon == 'stop':
            d.stop()
        elif options.daemon == 'restart':
            d.restart()
        else:
            print "Unknown command. Valid daemon values are start|stop|restart."
            sys.exit(2)
        sys.exit(0)

        
        
