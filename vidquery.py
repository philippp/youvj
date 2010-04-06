import re
import gdata.youtube
import gdata.youtube.service

def runJob(fileName):
    mVids = {}
    artists = open(fileName,'r').readlines()
    for artist in artists:
        entries = fetchVideos(artist)
        mVids['artist'] = entries

def fetchVideos(artistName):
    musicEntries = []
    ytService = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = artistName+"+music+video"
    query.orderby = 'viewCount'
    query.racy = 'include'
    query.max_results=50
    feed = ytService.YouTubeQuery(query)
    for entry in feed.entry:
        vidTitle = entry.media.title.text
        if not vidTitle:
            continue
        if re.match("^"+artistName.lower()+"[ ]*\-", vidTitle.lower()):
            entryDict = {
                'title':vidTitle,
                'description':entry.media.description.text,
                'page_url':entry.media.player.url,
                'flash_url':entry.GetSwfUrl(),
                'duration':entry.media.duration.seconds,
                'view_count':entry.statistics.view_count,
                'thumbnails':[t.url for t in entry.media.thumbnail]
                }
            if entryDict['flash_url']:
                musicEntries.append(entryDict)
    return musicEntries
