#!/usr/bin/env python

import cgi
import logging
import optparse
import sys
import os.path

import feather.wsgi

import config
import magic
from webob import Request, Response

handlers = {}

'''
handlers = {
    'findvideos' : vidserv.FindVideos,
    'findsimilar' : vidserv.FindSimilar,
    'savevideo' : vidserv.SaveVideo,
    'unsavevideo' : vidserv.UnSaveVideo,
    'listsavedvideos' : vidserv.ListSavedVideos,
    'log' : vidserv.ClientLogger,
    'fb_friends' : vidserv.FBFriends,
}
'''

def wsgiapp(ctx, start_response):

    # Try to hit actual responders
    request = Request(ctx)
    for n, c in handlers.iteritems():
        if request.path_info == '/%s' % n:
            try:
                resp = c().render(ctx)
            except Exception, e:
                print e
                e_msg = "Oh snaps"
                start_response("500 SERVER ERROR",
                               [('content-type','text/html'),
                                ('content-length',len(e_msg))])
                return [e_msg]
            start_response("200 OK",
                           [('content-type','text/html'),
                            ('content-length',len(resp))])
            return [resp]

    # If that fails, look for a file at this location
    fpath = config.path + '/static' + ctx['PATH_INFO']
    if os.path.isfile(fpath):
        mime = magic.from_file(fpath, mime=True)
        resp = file(fpath, 'r').read()
        start_response("200 OK",
                       [('content-type',mime),
                        ('content-length',len(resp))])
        return [resp]
        
if __name__ == "__main__":
    parser = optparse.OptionParser(add_help_option=False)
    parser.add_option("-p", "--port", type="int", default=config.port)
    parser.add_option("-h", "--host", default=config.host)

    options, args = parser.parse_args()
    feather.wsgi.serve((options.host, options.port), wsgiapp,
            traceback_body=True)
