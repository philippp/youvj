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
    query.vq = artistName.lower()+"+music+video"
    query.orderby = 'viewCount'
    query.racy = 'include'
    query.max_results=50
    print query
    feed = ytService.YouTubeQuery(query)
    for entry in feed.entry:
        vidTitle = entry.media.title.text
        print vidTitle
        if not vidTitle:
            continue
        if re.search(artistName.lower()+"[ ]*\-", vidTitle.lower()):
            vidTitle = '-'.join(vidTitle.split('-')[1:]).lstrip()
        elif re.search("\-[ ]*"+artistName.lower(), vidTitle.lower()):
            vidTitle = '-'.join(vidTitle.split('-')[:1]).lstrip()
        elif re.search("[^\"]*"+artistName.lower()+'[ ]*\"[^\"]+\"',vidTitle.lower()):
            vidTitle = vidTitle.split('"')[1]
        else:
            #if artistName.lower() in vidTitle.lower():
            #    import pdb; pdb.set_trace()
            continue
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
