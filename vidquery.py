import re
import pdb
import gdata.youtube
import gdata.youtube.service
import lastfm
from pprint import pprint 

def log(msg):
    print msg

def runJob(fileName):
    mVids = {}
    artists = open(fileName,'r').readlines()
    for artist in artists:
        entries = fetchVideos(artist)
        mVids['artist'] = entries

def fetchVideos(artistName, ip_addr):
    videos_relevance = _fetchVideos(artistName, ip_addr, orderby='relevance')

    log( "videos by relevance %s" % videos_relevance )
    videos_popularity = _fetchVideos(artistName, ip_addr, orderby='viewCount')
    log(  "videos by popularity %s" % videos_popularity )
    hits = lastfm.getHits(artistName)
    videos = videos_relevance + videos_popularity
    log( "before filterSimilar: %s" % [v['title'] for v in videos] )
    videos = filterSimilar(videos)
    log( "after filterSimilar: %s" % [v['title'] for v in videos] )
    videos = orderPopular(videos, hits)
    log( "after orderPopular: %s" % [v['title'] for v in videos] )
    return videos

def filterSimilar(allVideos):
    vidByTitle = {}
    junkWords = [
        'official',
        'hq',
        'music video',
        ]
    for video in allVideos:
        minTitle = _makeMinTitle(video['title'])
        vidByTitle[minTitle] = vidByTitle.get(minTitle,[]) + [video]
    for minTitle, videos in vidByTitle.iteritems():
        log( "mintitle=%s contains %s" % (minTitle, [v['title'] for v in videos]) )
        vidByTitle[minTitle] = sorted(videos, key = lambda v: v['view_count'])
    return sorted([ v[0] for v in vidByTitle.values() ],
                  key = lambda v: v['view_count'])

def _makeMinTitle(videoTitle):
    junkWords = [
        'official',
        'hq',
        'music video',
        ]
    minTitle = videoTitle.lower()
    for word in junkWords:
        minTitle = minTitle.replace(word,"")
    minTitle = re.sub("\(.*\)", "", minTitle, count=0)
    minTitle = re.sub("[^a-zA-Z]", "", minTitle, count=0)
    return minTitle

def orderPopular(videos, hitNames):
    ordered_videos = []
    minHits = [ _makeMinTitle(h) for h in hitNames ]
    log( "hit names are %s" % minHits )
    _m = []
    for h in minHits:
        if h not in _m:
            _m.append(h)
    minHits = _m

    for hitName in minHits:
        for video in list(videos):
            desc = video['description'].lower()
            minTitle = str(_makeMinTitle(video['title']))
            log( "min title is %s" % minTitle )
            if str(hitName) == minTitle and \
                    ('official' in desc or 'music video' in desc):
                log( "appending %s because it is a hit and seems official" % video['title'] )
                ordered_videos.append(video)
    for video in list(videos):
        if video not in ordered_videos:
            log( "appending %s because it has not been added" % video['title'] )
            ordered_videos.append(video)

    return ordered_videos

def _removeUmlaut(word):
    umMap = {252:u'u',
             220:u'u',
             246:u'o',
             214:u'o',
             228:u'a',
             196:u'a'}
    word = word.decode('utf-8')
    for k, v in umMap.items():
        word = word.replace(unichr(k), v)
    return word

def _fetchVideos(artistName,
                 ip_addr,
                 orderby='relevance'):
    musicEntries = []
    ytService = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = artistName.lower()
    query.orderby = orderby
    query.racy = 'include'
    query.max_results=50
    query.format = '5'
    #query.restriction = ip_addr
    feed = ytService.YouTubeQuery(query)
    _blockWords = ['unofficial','parody','anime']
    artistName = _removeUmlaut(artistName)
    for entry in feed.entry:
        vidTitle = _removeUmlaut(entry.media.title.text.lower())
        vidDescription = entry.media.description.text or ''
        
        if not vidTitle:
            continue

        _blockFound = False
        for _w in _blockWords:
            if _w in  vidTitle or _w in vidDescription.lower():
                _blockFound = True
                break
        if _blockFound:
            continue


        vidTitle = re.sub("^[Tt]he","",vidTitle).strip()
        if re.search("^"+artistName.lower()+"[ ]*\-", vidTitle):
            vidTitle = '-'.join(vidTitle.split('-')[1:]).lstrip()
        elif re.search("\-[ ]*"+artistName.lower()+"$", vidTitle):
            vidTitle = '-'.join(vidTitle.split('-')[:1]).lstrip()
        elif re.search("[^\"]*"+artistName.lower()+'[ ]*\"[^\"]+\"',vidTitle):
            vidTitle = vidTitle.split('"')[1]
        else:
            continue
        entryDict = {
            'artist':artistName,
            'title':vidTitle,
            'description':vidDescription,
            'page_url':entry.media.player.url,
            'flash_url':entry.GetSwfUrl(),
            'duration':entry.media.duration.seconds,
            'view_count':entry.statistics.view_count,
            'thumbnails':[t.url for t in entry.media.thumbnail]
            }
        if entryDict['flash_url']:
            musicEntries.append(entryDict)
        else:

            log( "--rejected %s" % vidTitle )
    return musicEntries

def levenshtein_distance(first, second):
    """Find the Levenshtein distance between two strings."""
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
       distance_matrix[i][0] = i
    for j in range(second_length):
       distance_matrix[0][j]=j
    for i in xrange(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]
