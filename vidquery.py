#!/usr/bin/env python
import re
import pdb
import gdata.youtube
import gdata.youtube.service
import lastfm
from pprint import pprint 
from optparse import OptionParser

track_code = None

def log(msg):
    print msg

def runJob(fileName):
    mVids = {}
    artists = open(fileName,'r').readlines()
    for artist in artists:
        entries = fetchVideos(artist)
        mVids['artist'] = entries

def fetchVideos(artistName):
    artistName = re.sub("^[Tt]he","",artistName).strip()
    videos_relevance = _fetchVideos(artistName,  orderby='relevance')
    #videos_popularity = _fetchVideos(artistName, orderby='viewCount')
    hits = lastfm.getHits(artistName)
    videos = videos_relevance# + videos_popularity
    log( "before filterSimilar: %s" % [v['title'] for v in videos] )
    videos = filterSimilar(videos)
    log( "after filterSimilar: %s" % [v['title'] for v in videos] )
    videos = orderPopular(videos, hits)
    log( "after orderPopular: %s" % [v['title'] for v in videos] )
    return videos

def filterSimilar(allVideos):
    vidByTitle = {}

    for video in allVideos:
        minTitle = _makeMinTitle(video['title'])
        vidByTitle[minTitle] = vidByTitle.get(minTitle,[]) + [video]
    for minTitle, videos in vidByTitle.iteritems():
        log( "mintitle=%s contains %s" % (minTitle, [v['title']+" "+v['flash_url'] for v in videos]) )
        videosNoRmx = filter( lambda v: (('remix' not in v['title']) and ('rmx' not in v['title'])), videos )
        if videosNoRmx:
            videos = videosNoRmx
        vidByTitle[minTitle] = sorted(videos, key = lambda v: int(v['view_count']))[0]
        officialVid = filter( lambda v: 'vevo.com' in v['description'], videos )
        if officialVid:
            vidByTitle[minTitle] = officialVid[0]

    return sorted(vidByTitle.values(),
                  key = lambda v: v['view_count'])

def _makeMinTitle(videoTitle):
    junkWords = [
        'official',
        'hq',
        'music video',
        ]
    minTitle = videoTitle.lower() #videoTitle.decode('utf-8')
    '''
    try:
        minTitle = _replaceUmlauts(minTitle)
    except UnicodeDecodeError:
        pass
        '''
    for word in junkWords:
        minTitle = minTitle.replace(word,"")
    minTitle = re.sub("^[Tt]he","",minTitle).strip()
    minTitle = re.sub("\(.*\)", "", minTitle, count=0)
    minTitle = re.sub("[^a-zA-Z\-\"]", "", minTitle, count=0)

    # replace umlauts, as people often do
    return str(minTitle)

def _replaceUmlauts(minTitle):
    minTitle = minTitle.decode('utf-8')
    umMap = {252:u'u',
             220:u'u',
             246:u'o',
             214:u'o',
             228:u'a',
             196:u'a'}
    for k, v in umMap.items():
            minTitle = minTitle.replace(unichr(k), v)
    minTitle = minTitle.encode('latin-1').lower()
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
            if str(hitName) == video['match_title'] and \
                    ('official' in desc or 'music video' in desc):
                log( "appending %s because it is a hit and seems official" % video['title'] )
                ordered_videos.append(video)
    for video in list(videos):
        if video not in ordered_videos:
            log( "appending %s because it has not been added" % video['title'] )
            ordered_videos.append(video)

    return ordered_videos

def _fetchVideos(artistName,
                 orderby='relevance'):
    musicEntries = []
    ytService = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = artistName.lower()
    query.orderby = orderby
    query.racy = 'include'
    query.max_results=50
    query.format = '5'
    feed = ytService.YouTubeQuery(query)
    _blockWords = ['unofficial','parody','anime']
    artistName = _makeMinTitle(artistName)

    for entry in feed.entry:
        origTitle = str(entry.media.title.text.lower())
        vidTitle = _makeMinTitle(origTitle)
        pageURL = entry.media.player.url
        vidDescription = entry.media.description.text or ''
        
        if track_code and track_code in pageURL:
            log("TRACKER: Found %s in %s search" %
                (vidTitle, orderby))
            

        if not vidTitle:
            continue

        _blockFound = False
        for _w in _blockWords:
            if _w in  vidTitle or _w in vidDescription.lower():
                _blockFound = True
                break
        if _blockFound:
            continue
        artistNameL = artistName.lower()
        if re.search("^"+artistNameL+"[ ]*\-", vidTitle):
            prettyTitle = '-'.join(origTitle.split('-')[1:]).lstrip()
        elif re.search("\-[ ]*"+artistNameL+"$", vidTitle):
            prettyTitle = '-'.join(origTitle.split('-')[:1]).lstrip()
        elif re.search("[^\"]*"+artistNameL+'[ ]*\"[^\"]+\"',vidTitle):
            prettyTitle = origTitle.split('"')[1]
        else:
            if (track_code and pageURL) and track_code in pageURL:
                log("Eliminated %s because it did not match %s" % 
                    (vidTitle, artistNameL) )
            continue
        vidTitle = _makeMinTitle(prettyTitle)

        entryDict = {
            'artist':artistName,
            'title':prettyTitle,
            'match_title':vidTitle,
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
            if track_code and track_code in pageURL:
                log("TRACKER: Eliminated %s because it did not have a flash_url" % 
                    (vidTitle) )
    if track_code:
        for mE in musicEntries:
            if track_code in mE['page_url']:
                log("TRACKER: Found %s in %s search" %
                    (mE['title'], orderby))
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

if __name__ == "__main__":
    usage = "usage: %prog [options] ARTIST_NAME"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--follow", dest="follow", default=track_code,
                      help="follow the VIDEO_ID", metavar="VIDEO_ID")
    (options, args) = parser.parse_args()
    track_code = options.follow
    print args
    if len(args) != 1:
        print parser.print_help()
    else:
        fetchVideos(args[0])
