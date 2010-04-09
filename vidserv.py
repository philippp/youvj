import pdb
import json
import os.path, time
from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode
import lastfm
import vidquery

class Controller(resource.Resource):

  def __init__(self, directory=""):
    if not directory:
      directory = '/home/philippp/vidtunes/static'    
    self.directory = directory

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

class FindVideos(Controller, resource.PostableResource):
  creation_time = time.time()
  content_type = http_headers.MimeType('text','json')
  
  def render(self, ctx):
    artists = ctx.args.get('artist',[])
    artistVids = []
    for artist in artists:
      artistVids.append( vidquery.fetchVideos(artist) )

    return http.Response(
      responsecode.OK,
      {'last-modified': self.creation_time,
      'content-type': self.content_type},
      json.dumps(artistVids))

class FindSimilar(Controller, resource.PostableResource):
  creation_time = time.time()
  content_type = http_headers.MimeType('text','json')
  
  def render(self, ctx):
    artist = ctx.args.get('artist')[0]
    similar_artists = lastfm.get_similar(artist)
    return http.Response(
      responsecode.OK,
      {'last-modified': self.creation_time,
      'content-type': self.content_type},
      json.dumps(similar_artists))
    
class Toplevel(Controller):
  addSlash = True

  def render(self, ctx):
    return http.Response(
      200, 
      {'content-type': http_headers.MimeType('text', 'html')},
      self.template("index")
      )

root = Toplevel()
root.putChild("findvideos", FindVideos())
root.putChild("findsimilar", FindSimilar())
site = server.Site(root)


# Standard twisted application Boilerplate
from twisted.application import service, strports
application = service.Application("demoserver")
s = strports.service('tcp:8080', channel.HTTPFactory(site))
s.setServiceParent(application)
