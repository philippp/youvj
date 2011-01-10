#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A barebones AppEngine application that uses Facebook for login.

This application uses OAuth 2.0 directly rather than relying on Facebook's
JavaScript SDK for login. It also accesses the Facebook Graph API directly
rather than using the Python SDK. It is designed to illustrate how easy
it is to use the Facebook Platform without any third party code.

See the "appengine" directory for an example using the JavaScript SDK.
Using JavaScript is recommended if it is feasible for your application,
as it handles some complex authentication states that can only be detected
in client-side code.
"""

import base64
import cgi

import email.utils
import hashlib
import hmac
import logging
import os.path
import time
import urllib
import vidserv
from configs import config
import json
from twisted.web2 import http

#from django.utils import simplejson as json
#from google.appengine.ext import db
#from google.appengine.ext import webapp
#from google.appengine.ext.webapp import util
#from google.appengine.ext.webapp import template


class BaseHandler(vidserv.HTMLController):
    @property
    def current_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._current_user = User.get_by_key_name(user_id)
        return self._current_user


class LoginHandler(vidserv.HTMLController):

    def render(self, ctx):
        verification_code = ctx.args.get("code",[''])[0]
        args = dict(client_id=config.FB_APP_ID, callback='http://notphil.com:8080/fb_login')
        if verification_code:
            args["client_secret"] = config.FB_APP_SECRET
            args["code"] = verification_code
            args["scope"] = "user_music,friends_music,user_photos"
            response = cgi.parse_qs(urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read())
            access_token = response["access_token"][-1]

            # Download the user profile and cache a local instance of the
            # basic profile info
            profile = json.load(urllib.urlopen(
                "https://graph.facebook.com/me?" +
                urllib.urlencode(dict(access_token=access_token))))
            resp = http.Response(301,{'location': '/'},'')
            profile['access_token'] = access_token
            self.mem.set(str('fb_profile_'+profile['id']), profile)
            self.setCookie(resp, "fb_user", str(profile["id"]),
                       expires=time.time() + 30 * 86400)
            return resp

        else:
            oauth_url = "https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args)
            return http.Response( 301, {'location':oauth_url}, '' )



class LogoutHandler(vidserv.HTMLController):
    def get(self):
        self.setCookie(self.response, "fb_user", "", expires=time.time() - 86400)
        self.redirect("/")





