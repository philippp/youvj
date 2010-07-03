import viddb

EVENT_SEARCH = 1
EVENT_VIEW_VIDEO = 2
EVENT_CLICK_FRIEND = 3
EVENT_CLICK_SHARE = 4
EVENT_URL_SHORTCUT = 5
EVENT_FB_LOGON = 6
EVENT_FB_LOGOFF = 7

def log(*args, **kwargs):
    if 'ctx' in kwargs:
        sess = kwargs['ctx'].getSession()
        if sess:
            kwargs['fbid'] = sess['uid']
        del kwargs['ctx']
    keylist = ['session_id','fbid','data_1','data_2','data_3','data_4','data_5','data_6','text_info']
    #[ assert (k in keylist) for k in kwargs.keys() ]
    conn = viddb.get_conn()
    viddb.insert(conn, 'log', **kwargs)
