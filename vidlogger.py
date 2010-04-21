import config
try:
    import MySQLdb
except DeprecationWarning:
    pass

import MySQLdb


def get_cursor():
    conn = MySQLdb.connect( **config.db )
    return conn.cursor()

def execute(to_exec):
    cursor = get_cursor()
    cursor.execute(to_exec)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def insert(table, **kwargs):
    query_str = "INSERT INTO %s (%s) VALUES (%s)" % \
        (table, 
         ",".join(kwargs.keys()),
         ",".join( [ "'%s'" % v for v in kwargs.values() ] )
         )
    execute(query_str)
    
def load(table, col_list):
    query_str = "SELECT %s FROM %s" % \
        (",".join(col_list),
         table)
    
    return execute(query_str)




def log(*args, **kwargs):
    get_cursor()
    keylist = ['data_1','data_2','data_3','data_4','data_5','data_6','text_info']
    [ assert k in keylist for k in kwargs.keys() ]
    cursor.insert('log', name=name, email=email)
