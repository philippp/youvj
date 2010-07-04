from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode
from twisted.application import service, strports

import vidfbc
import vidserv
import config

root = vidserv.Toplevel()
root.putChild("findvideos", vidserv.FindVideos())
root.putChild("findsimilar", vidserv.FindSimilar())
root.putChild("savevideo", vidserv.SaveVideo())
root.putChild("unsavevideo", vidserv.UnSaveVideo())
root.putChild("listsavedvideos", vidserv.ListSavedVideos())
root.putChild("log", vidserv.ClientLogger())
root.putChild("fb_friends", vidserv.FBFriends())
site = server.Site(root)

# Standard twisted application Boilerplate
application = service.Application("demoserver")
s = strports.service('tcp:%s' % config.port, channel.HTTPFactory(site))
s.setServiceParent(application)

