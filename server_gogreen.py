#!/usr/bin/env python

import cgi
import logging
import optparse
import sys
import os.path
import traceback

#import feather.wsgi
import gogreen.wsgi
import vidserv
import config
import magic
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
                print e
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
        mime = magic.from_file(fpath, mime=True)
        if fpath[-4:] == ".css":
            mime = "text/css"
        resp = file(fpath, 'r').read()
        start_response("200 OK",
                       [('content-type',mime),
                        ('content-length',len(resp))])
        return [resp]

    # Oh snaps! I guess the user is searching for an artist.
    

if __name__ == "__main__":
    parser = optparse.OptionParser(add_help_option=False)
    parser.add_option("-p", "--port", type="int", default=config.port)
    parser.add_option("-h", "--host", default=config.host)

    options, args = parser.parse_args()
    gogreen.wsgi.serve((options.host, options.port), wsgiapp,
            access_log='access.log')