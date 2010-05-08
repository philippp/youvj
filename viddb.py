import config
import MySQLdb

def get_conn():
    conn = MySQLdb.connect( **config.db )
    return conn

def insert(table, **kwargs):
    conn = get_conn()
    cursor = conn.cursor()
    ignore = ""
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

def load(table, col_list, where=''):
    conn = get_conn()
    cursor = conn.cursor()
    query_str = "SELECT %s FROM %s" % \
        (",".join(col_list),
         table)
    if where:
        query_str += " WHERE "+where

    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return rows
