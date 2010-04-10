import re
import gdata.youtube
import gdata.youtube.service
from pprint import pprint 

def runJob(fileName):
    mVids = {}
    artists = open(fileName,'r').readlines()
    for artist in artists:
        entries = fetchVideos(artist)
        mVids['artist'] = entries

def fetchVideos(artistName, ip_addr):
    videos_relevance = _fetchVideos(artistName, ip_addr, orderby='relevance')
    videos_popularity = _fetchVideos(artistName, ip_addr, orderby='viewCount')
    videos = videos_relevance + videos_popularity
    videos = filterSimilar(videos)
    pprint(videos)
    return videos

def filterSimilar(allVideos):
    vidByTitle = {}
    junkWords = [
        'official',
        'hq',
        'music video',
        ]
    for video in allVideos:
        minTitle = video['title']
        for word in junkWords:
            minTitle = minTitle.replace(word,"")
        minTitle = re.sub("\(.*\)", "", minTitle, count=0)
        minTitle = re.sub("[^a-zA-Z]", "", minTitle, count=0)
        
        vidByTitle[minTitle] = vidByTitle.get(minTitle,[]) + [video]
    for minTitle, videos in vidByTitle.iteritems():
        vidByTitle[minTitle] = sorted(videos, key = lambda v: v['view_count'])
    return sorted([ v[0] for v in vidByTitle.values() ],
                  key = lambda v: v['view_count'])

def _fetchVideos(artistName,
                 ip_addr,
                 orderby='relevance'):
    musicEntries = []
    ytService = gdata.youtube.service.YouTubeService()
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = artistName.lower()+"+music+video"
    query.orderby = orderby
    query.racy = 'include'
    query.max_results=50
    query.format = '5'
    query.restriction = ip_addr
    feed = ytService.YouTubeQuery(query)
    for entry in feed.entry:
        vidTitle = entry.media.title.text.lower()

        if not vidTitle:
            continue
        if "unofficial" in vidTitle or "parody" in vidTitle:
            continue

        if re.search("^"+artistName.lower()+"[ ]*\-", vidTitle):
            vidTitle = '-'.join(vidTitle.split('-')[1:]).lstrip()
        elif re.search("\-[ ]*"+artistName.lower()+"$", vidTitle):
            vidTitle = '-'.join(vidTitle.split('-')[:1]).lstrip()
        elif re.search("[^\"]*"+artistName.lower()+'[ ]*\"[^\"]+\"',vidTitle):
            vidTitle = vidTitle.split('"')[1]
        else:
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
        else:

            print "--rejected %s" % vidTitle
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
