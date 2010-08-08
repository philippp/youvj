#!/usr/bin/env python
import random
import unittest
import viddb
import vidmapper

TEST_USER = 10000

class TestTagging(unittest.TestCase):


    def setUp(self):
        self.seq = range(10)
        self.conn = viddb.get_conn()
        vidmapper.clearUserTags( self.conn, TEST_USER )

    def test_multiVidSameTag(self):
        u1 = TEST_USER
        vidmapper.tagVideo(self.conn, VINFO[0], u1, 't1')
        vidmapper.tagVideo(self.conn, VINFO[1], u1, 't1')
        
        tags = dict(vidmapper.listUserTags(self.conn, u1))
        
        self.assertEqual( tags.keys(),
                          ['t1'] )
        self.assertEqual( set(tags.values()[0]),
                          set([VINFO[0]['youtube_id'],
                           VINFO[1]['youtube_id']]) )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[0]['youtube_id'],
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          ['t1'] )
        self.assertEqual( tags.values(),
                          [[VINFO[1]['youtube_id']]] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[1]['youtube_id'],
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )

    def test_sameVidMultiTag(self):
        u1 = TEST_USER
        vidmapper.tagVideo(self.conn, VINFO[0], u1, 't1')
        vidmapper.tagVideo(self.conn, VINFO[0], u1, 't2')
        
        tags = dict(vidmapper.listUserTags(self.conn, u1))
        
        self.assertEqual( set(tags.keys()),
                          set(['t1', 't2']) )
        self.assertEqual( tags.values(),
                          [[VINFO[0]['youtube_id']],
                           [VINFO[0]['youtube_id']]] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[0]['youtube_id'],
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          ['t2'] )
        self.assertEqual( tags.values(),
                          [[VINFO[0]['youtube_id']]] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[0]['youtube_id'],
                             't2')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )

    def test_orderVideoCount(self):
        u1 = TEST_USER
        vidmapper.tagVideo(self.conn, VINFO[0], u1, 't1')
        vidmapper.tagVideo(self.conn, VINFO[1], u1, 't2')
        vidmapper.tagVideo(self.conn, VINFO[2], u1, 't2')
        vidmapper.tagVideo(self.conn, VINFO[3], u1, 't3')
        vidmapper.tagVideo(self.conn, VINFO[4], u1, 't3')
        vidmapper.tagVideo(self.conn, VINFO[5], u1, 't3')
        
        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags ),
                          ['t3', 't2', 't1'] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[4]['youtube_id'],
                             't3')

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[3]['youtube_id'],
                             't3')

        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags )[0],
                          't2')

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[5]['youtube_id'],
                             't3')

        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags ),
                          ['t2','t1'] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[0]['youtube_id'],
                             't1')

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[1]['youtube_id'],
                             't2')

        vidmapper.untagVideo(self.conn,
                             u1,
                             VINFO[2]['youtube_id'],
                             't2')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )

 


VINFO = [
        {'artist': 'Percee P',
         'description': 'Percee P\'s "Put it on the Line" from the album Perseverance. Produced by Madlib. BX Version. Directed/Edited by Duey FM. www.stonesthrow.com',
         'duration': 202L,
         'flash_url': 'http://www.youtube.com/v/MxuHQPMD7AE?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/MxuHQPMD7AE/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/MxuHQPMD7AE/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/MxuHQPMD7AE/3.jpg',
         'title': 'put it on the line',
         'view_count': 148092L,
         'youtube_id': 'MxuHQPMD7AE'},
        {'artist': 'dj hell',
         'description': "Dj Hell's awsome Copa vid. Just enjoy !!!",
         'duration': 192L,
         'flash_url': 'http://www.youtube.com/v/_Cq4UZsm6Yk?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/_Cq4UZsm6Yk/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/_Cq4UZsm6Yk/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/_Cq4UZsm6Yk/3.jpg',
         'title': 'copacabana',
         'view_count': 103270L,
         'youtube_id': '_Cq4UZsm6Yk'},
        {'artist': 'dj hell',
         'description': 'No More rmx, pzdr mkrwlf',
         'duration': 213L,
         'flash_url': 'http://www.youtube.com/v/oeGgN2aVekg?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/oeGgN2aVekg/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/oeGgN2aVekg/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/oeGgN2aVekg/3.jpg',
         'title': 'suicide commando',
         'view_count': 164412L,
         'youtube_id': 'oeGgN2aVekg'},
        {'artist': 'Tiga',
         'description': 'Music video by Tiga performing Shoes. (C) 2009 Last Gang Records / Turbo Recordings',
         'duration': 230L,
         'flash_url': 'http://www.youtube.com/v/wGz3Neb9Ik8?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/wGz3Neb9Ik8/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/wGz3Neb9Ik8/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/wGz3Neb9Ik8/3.jpg',
         'title': 'shoes',
         'view_count': 150268L,
         'youtube_id': 'wGz3Neb9Ik8'},
        {'artist': 'Tiga',
         'description': 'Music video by Tiga performing What You Need. (C) 2009 Last Gang Records / Turbo Recordings',
         'duration': 248L,
         'flash_url': 'http://www.youtube.com/v/ydFPpuGAbmw?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/ydFPpuGAbmw/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/ydFPpuGAbmw/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/ydFPpuGAbmw/3.jpg',
         'title': 'what you need',
         'view_count': 26337L,
         'youtube_id': 'ydFPpuGAbmw'},
        {'artist': 'Hacker',
         'description': 'Music',
         'duration': 240L,
         'flash_url': 'http://www.youtube.com/v/BwALo2TpO-Y?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/BwALo2TpO-Y/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/BwALo2TpO-Y/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/BwALo2TpO-Y/3.jpg',
         'title': 'anthony rother ',
         'view_count': 174566L,
         'youtube_id': 'BwALo2TpO-Y'},
        {'artist': 'Washed Out',
         'description': 'Music Video for "Belong", off High Times (Mirror Universe; 2009) Director: Blake Salzman',
         'duration': 199L,
         'flash_url': 'http://www.youtube.com/v/pqP2-w6AWS4?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/pqP2-w6AWS4/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/pqP2-w6AWS4/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/pqP2-w6AWS4/3.jpg',
         'title': 'belong (music video)',
         'view_count': 55461L,
         'youtube_id': 'pqP2-w6AWS4'},
        {'artist': 'Memory Cassette',
         'description': "The official video for Memory Cassette's 'Surfin' and 'Body in the Water'. Directed by Pat Vamos....rad",
         'duration': 390L,
         'flash_url': 'http://www.youtube.com/v/xhIJGF85Pro?f=videos&app=youtube_gdata',
         'thumbnail_1': 'http://i.ytimg.com/vi/xhIJGF85Pro/2.jpg',
         'thumbnail_2': 'http://i.ytimg.com/vi/xhIJGF85Pro/1.jpg',
         'thumbnail_3': 'http://i.ytimg.com/vi/xhIJGF85Pro/3.jpg',
         'title': 'surfin/body in the water',
         'view_count': 5359L,
         'youtube_id': 'xhIJGF85Pro'},         
         ]

if __name__ == '__main__':
    unittest.main()
