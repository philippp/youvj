import config
import MySQLdb

EVENT_SEARCH = 1
EVENT_VIEW_VIDEO = 2
EVENT_CLICK_FRIEND = 3
EVENT_CLICK_SHARE = 4
EVENT_URL_SHORTCUT = 5
EVENT_FB_LOGON = 6
EVENT_FB_LOGOFF = 7

def get_conn():
    conn = MySQLdb.connect( **config.db )
    return conn

def insert(table, **kwargs):
    conn = get_conn()
    cursor = conn.cursor()
    query_str = "INSERT INTO %s (%s) VALUES (%s)" % \
        (table, 
         ",".join(kwargs.keys()),
         ",".join( [ "'%s'" % conn.escape_string(str(v)) for v in kwargs.values() ] )
         )
    cursor.execute(query_str)
    cursor.close()
    
def load(table, col_list):
    conn = get_conn()
    cursor = conn.cursor()
    query_str = "SELECT %s FROM %s" % \
        (",".join(col_list),
         table)
    
    cursor.execute(query_str)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def log(*args, **kwargs):
    if 'ctx' in kwargs:
        sess = kwargs['ctx'].getFBSession()
        if sess:
            kwargs['fbid'] = sess['uid']
        del kwargs['ctx']
    keylist = ['session_id','fbid','data_1','data_2','data_3','data_4','data_5','data_6','text_info']
    #[ assert (k in keylist) for k in kwargs.keys() ]
    insert('log', **kwargs)
