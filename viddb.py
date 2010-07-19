import config
import MySQLdb

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
    'user':[
        'id',
        'created_at',
        'subdomain',
        'nickname',
        'origin_network',
        'salt',
        'passwd_hash'
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
    query_str = "INSERT %s INTO %s (%s) VALUES (%s)" % \
        (ignore,
         table, 
         ",".join(kwargs.keys()),
         ",".join( [ "'%s'" % conn.escape_string(str(v)) for v in kwargs.values() ] )
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
    set_str = ','.join(['='.join(i) for i in set_dict.items()])
    query_str = "UPDATE %s SET %s WHERE %s" % \
        (table, set_str, where)
    query_str += " WHERE "+where
    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return rows
