import pdb
import viddb

def saveVideo(vidInfo, user_id):
    tail_node_id = 0
    conn = viddb.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_youtube_map WHERE user_id = %s and next_id IS NULL" % user_id)
    tail_nodes = cursor.fetchall()
    if tail_nodes:
        tail_node_id = tail_nodes[0][0]

    viddb.insert('youtube_videos', _ignore = True, **vidInfo)
    inserted_id = viddb.insert('user_youtube_map',
                               _ignore = True,
                               youtube_id = vidInfo['youtube_id'],
                               user_id = user_id)
    print "Inserted ID is %s" % inserted_id
    if tail_node_id:
        cursor.execute("UPDATE user_youtube_map SET next_id = %s WHERE id = %s" % \
                           (inserted_id, tail_node_id))

def unSaveVideo(youtube_id, user_id):
    conn = viddb.get_conn()
    cursor = conn.cursor()
    # Find the node to remove, identify the node it points to
    cursor.execute("SELECT id, next_id FROM user_youtube_map WHERE user_id = %s and youtube_id = \"%s\"" % \
                       (user_id, youtube_id))
    unsave_nodes = cursor.fetchall()
    if not unsave_nodes:
        return
    unsave_node_id, unsave_node_next_id = unsave_nodes[0]
    pdb.set_trace()

    # Find the node that points the node we will be removing
    cursor.execute("SELECT id FROM user_youtube_map WHERE next_id = %s" % \
                       unsave_node_id)
    unsave_pointers = cursor.fetchall()
    if unsave_pointers:
        unsave_pointer_id = unsave_pointers[0][0]
        cursor.execute("UPDATE user_youtube_map SET next_id = %s where id = %s" % \
                           (unsave_node_next_id or 'NULL', unsave_pointer_id))

    viddb.delete('user_youtube_map','id=%s' % unsave_node_id)

def listSavedVideos(user_id):
    keys = ['youtube_id',
            'next_id',
            'id']
    resp = viddb.load('user_youtube_map',
                      keys,
                      where='user_id=%s' % user_id)
    if not resp:
        return []

    resp = [ dict(zip(keys, r)) for r in resp ]
    print resp
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
