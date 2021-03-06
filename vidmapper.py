import pdb
import pprint
import viddb
import vidauth
import vidfail
import _mysql_exceptions

def createPlaylist(conn, user_id, title, subdomain=None):
    playlist = {'title':title,
                'user_id':uid
                }
    if subdomain:
        playlist['subdomain']

    viddb.insert(conn,
                 'playlists',
                 **playlist)

def listPlaylists(conn, user_id):
    return viddb.load(conn, 'playlists', 
                      viddb.COLS['playlists'], 
                      where='user_id=%s'%user_id)

def deletePlaylist(conn, playlist_id):
    pass

def renamePlaylist(conn, playlist_id, title):
    cursor = conn.cursor()
    cursor.execute("UPDATE playlists SET title = \"%s\" WHERE id = %s" % \
                           (conn.escape_string(title), playlist_id))


def getUser(conn, email):
    email = conn.escape_string(email)    
    user = viddb.load(conn,
                      'users',
                      viddb.COLS['users'],
                      where= "email = \"%s\"" % email)
    user = user and user[0] or None
    return user

def addUser(conn, email, password=None):
    email = conn.escape_string(email)
    if not password:
        # Make a temp pw and sent the user a session
        password = vidauth.generate_secret()
    salt = vidauth.generate_secret()
    user_data = {
        'salt' : salt,
        'email' : email,
        'passwd_hash' : vidauth.hash_pass( password, salt )
        }
    try:
        viddb.insert(conn,
                     'users',
                     **user_data)
    except _mysql_exceptions.IntegrityError:
        raise vidfail.UserExists()

def tagVideo(conn, youtubeID, userID, tagName):
    viddb.insert(conn,
                 'tags',
                 _ignore = True,
                 youtube_id = youtubeID,
                 tag_name = tagName,
                 user_id = userID)


def untagVideo(conn, userID, ytID, tagName):
    viddb.delete(conn,
                 'tags',
                 'user_id = %s AND youtube_id = "%s" AND tag_name = "%s"' %\
                     (userID, ytID, tagName))

def clearUserTags(conn, userID):
    viddb.delete(conn,
                 'tags',
                 'user_id = %s' %\
                     (userID))

def listUserTags(conn, userID):
    tagEntries = viddb.load( 
        conn,
        'tags',
        viddb.COLS['tags'],
        'user_id = %s' % userID )
    
    tagMap = {}
    for e in tagEntries:
        tagName = e['tag_name']
        tagMap[tagName] = tagMap.get(tagName,[])
        tagMap[tagName].append( e['youtube_id'] )
    tagList = tagMap.items()
    tagList = sorted( tagList, key = lambda i: len(i[1]), reverse = True )
    return tagList

def listUserTagsTagged(conn, userID):
    ret = {'tags':listUserTags(conn, userID),
           'tagged':{}}
    for k, v in dict(ret['tags']).iteritems():
        for yid in v:
            ret['tagged'][yid] = ret['tagged'].get(yid,[]) + [k];
    return ret

def saveVideo(conn, vidInfo):
    viddb.insert(conn, 'youtube_videos', _ignore = True, **vidInfo)

def unSaveVideo(conn, youtube_id, user_id):
    cursor = conn.cursor()
    # Find the node to remove, identify the node it points to
    cursor.execute("SELECT id, next_id FROM user_youtube_map WHERE user_id = %s and youtube_id = \"%s\"" % \
                       (user_id, youtube_id))
    unsave_nodes = cursor.fetchall()
    if not unsave_nodes:
        return
    unsave_node_id, unsave_node_next_id = unsave_nodes[0]

    # Find the node that points the node we will be removing
    cursor.execute("SELECT id FROM user_youtube_map WHERE next_id = %s" % \
                       unsave_node_id)
    unsave_pointers = cursor.fetchall()
    if unsave_pointers:
        unsave_pointer_id = unsave_pointers[0][0]
        cursor.execute("UPDATE user_youtube_map SET next_id = %s where id = %s" % \
                           (unsave_node_next_id or 'NULL', unsave_pointer_id))

    viddb.delete(conn, 'user_youtube_map','id=%s' % unsave_node_id)

def listSavedVideos(conn, playlist_id):
    cursor = conn.cursor()
    keys = ['youtube_id',
            'next_id',
            'id']
    resp = viddb.load(conn,
                      'playlist_youtube_map',
                      keys,
                      where='playlist_id=%s' % playlist_id)
    if not resp:
        return []

    tail = filter( lambda n: n['next_id'] is None, resp )
    assert tail, "TAIL node not found"
    tail = tail[0]
    resp_map = dict([ (n['next_id'], n) for n in resp ] )
    ordered_resp = [tail['youtube_id']]

    current_node = resp_map.get(tail['id'],None)
    while current_node:
        ordered_resp.append(current_node['youtube_id'])
        current_node = resp_map.get(current_node['id'])

    return ordered_resp

def retrieveVideos(conn, youtube_ids):
    cursor = conn.cursor()
    if not youtube_ids:
        return []

    where_str = 'youtube_id IN (%s)' % \
        ','.join(['"%s"'%y for y in youtube_ids])
    c = viddb.COLS['youtube_videos']
    resp = viddb.load(conn,
                      'youtube_videos',
                      viddb.COLS['youtube_videos'],
                      where = where_str)
    pprint.pprint( resp )
    return resp

def tset_fbid(conn, fbid, uid=None):
    cursor = conn.cursor()
    resp = viddb.load(conn,
                      'user_foreign_map',
                      ['user_id'],
                      where="network=1 && foreign_id=%s" % fbid)
    if resp:
        return resp[0]['user_id']

    if not uid:
        uid = create_user(cursor, subdomain='', origin_network = 1)
    
    viddb.insert(cursor,
                 'user_foreign_map',
                 **{'network':1,
                    'foreign_id':fbid,
                    'user_id':uid,
                    '_ignore':True
                    })

    return uid

def create_user(conn, subdomain='', origin_network=0):
    uid = viddb.insert(conn,
                       'users',
                       {'origin_network':origin_network,
                        'subdomain':subdomain})

    createPlaylist(conn, uid, 'default')
    return uid
    
