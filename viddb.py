import config
from libs import MySQLdb

COLS = {
    'youtube_videos':[
        'youtube_id',
        'title',
        'artist',
        'description',
        'view_count',
        'duration',
        'thumbnail_1',
        'thumbnail_2',
        'thumbnail_3',
        'flash_url'
        ],
    'playlists':[
        'id',
        'user_id',
        'title',
        'subdomain',
        'created_at'
        ],
    'users':[
        'id',
        'created_at',
        'subdomain',
        'email',
        'origin_network',
        'salt',
        'passwd_hash'
        ],
    'tags':
        [
        'youtube_id',
        'tag_name',
        'user_id'
        ]
}

def get_cursor():
    conn = MySQLdb.connect( **config.db )
    return conn.cursor()

def get_conn():
    conn = MySQLdb.connect( **config.db )
    return conn

def insert(conn, table, **kwargs):
    ignore = ""
    cursor = conn.cursor()
    if '_ignore' in kwargs:
        ignore = "IGNORE"
        del kwargs['_ignore']

    vals = [ "'"+conn.escape_string(str(v))+"'" for v in kwargs.values() ]
    vals = ",".join( vals )
    query_str = "INSERT %s INTO %s (%s) VALUES (%s)" % \
        (ignore,
         table,
         ",".join(kwargs.keys()),
         vals
         )
    cursor.execute(query_str)
    last_id = cursor.lastrowid
    cursor.close()
    return last_id

def load(conn, table, col_list, where=''):
    cursor = conn.cursor()
    query_str = "SELECT %s FROM %s" % \
        (",".join(col_list),
         table)
    if where:
        query_str += " WHERE "+where

    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return [ dict( zip( col_list, r ) ) for r in rows ]

def delete(conn, table, where):
    cursor = conn.cursor()
    query_str = "DELETE FROM %s" % table
    query_str += " WHERE "+where
    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def update(conn, table, set_dict, where):
    cursor = conn.cursor()
    set_str = ','.join(['='.join(conn.escape_string(i)) for i in set_dict.items()])
    query_str = "UPDATE %s SET %s WHERE %s" % \
        (table, set_str, where)
    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return rows
