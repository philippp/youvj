import viddb

def saveVideo(vidInfo, user_id):
    viddb.insert('youtube_videos', _ignore = True, **vidInfo)
    viddb.insert('user_youtube_map',
                 _ignore = True,
                 youtube_id = vidInfo['youtube_id'],
                 user_id = user_id)

def unSaveVideo(youtube_id, user_id):
    viddb.delete('user_youtube_map',
                 where = 'youtube_id="%s" and user_id=%s' % \
                     (youtube_id, user_id)
                 )

def listSavedVideos(user_id):
    resp = viddb.load('user_youtube_map',
                      ['youtube_id'],
                      where='user_id=%s' % user_id)
    return [r[0] for r in resp]

def retrieveVideos(youtube_ids):
    if not youtube_ids:
        return []

    where_str = 'youtube_id IN (%s)' % \
        ','.join(['"%s"'%y for y in youtube_ids])
    c = viddb.COLS['youtube_videos']
    resp = viddb.load('youtube_videos',
                      viddb.COLS['youtube_videos'],
                      where = where_str)
    resp = [ dict( zip( c, r ) ) for r in resp ]
    return resp

def tset_fbid(fbid, uid=None):
    resp = viddb.load('user_foreign_map',
                      ['user_id'],
                      where="network=1 && foreign_id=%s" % fbid)
    if resp:
        return resp[0][0]

    if not uid:
        uid = viddb.insert('users', origin_network=1, _ignore=True)
    
    viddb.insert('user_foreign_map',
                 **{'network':1,
                    'foreign_id':fbid,
                    'user_id':uid,
                    '_ignore':True
                    })

    return uid
