import viddb

def tset_fbid(fbid, uid=None):
    resp = viddb.load('user_foreign_map', ['user_id'], where="network=1 && foreign_id=%s" % fbid)
    if resp:
        return resp[0][0]

    if not uid:
        uid = viddb.insert('users', origin_network=1)
    
    viddb.insert('user_foreign_map',
                 **{'network':1,
                    'foreign_id':fbid,
                    'user_id':uid
                    })

    return uid
