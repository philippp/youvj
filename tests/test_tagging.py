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
        vidmapper.tagVideo(self.conn, 0, u1, 't1')
        vidmapper.tagVideo(self.conn, 1, u1, 't1')
        
        tags = dict(vidmapper.listUserTags(self.conn, u1))
        
        self.assertEqual( tags.keys(),
                          ['t1'] )
        self.assertEqual( set(tags.values()[0]),
                          set(['0','1']) )

        vidmapper.untagVideo(self.conn,
                             u1,
                             0,
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          ['t1'] )
        self.assertEqual( tags.values(),
                          [['1']] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             1,
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )

    def test_sameVidMultiTag(self):
        u1 = TEST_USER
        vidmapper.tagVideo(self.conn, '0', u1, 't1')
        vidmapper.tagVideo(self.conn, '0', u1, 't2')
        
        tags = dict(vidmapper.listUserTags(self.conn, u1))
        
        self.assertEqual( set(tags.keys()),
                          set(['t1', 't2']) )
        self.assertEqual( tags.values(),
                          [['0'],
                           ['0']] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             '0',
                             't1')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          ['t2'] )
        self.assertEqual( tags.values(),
                          [['0']] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             '0',
                             't2')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )

    def test_orderVideoCount(self):
        u1 = TEST_USER
        vidmapper.tagVideo(self.conn, '0', u1, 't1')
        vidmapper.tagVideo(self.conn, '1', u1, 't2')
        vidmapper.tagVideo(self.conn, '2', u1, 't2')
        vidmapper.tagVideo(self.conn, '3', u1, 't3')
        vidmapper.tagVideo(self.conn, '4', u1, 't3')
        vidmapper.tagVideo(self.conn, '5', u1, 't3')
        
        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags ),
                          ['t3', 't2', 't1'] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             '4',
                             't3')

        vidmapper.untagVideo(self.conn,
                             u1,
                             '3',
                             't3')

        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags )[0],
                          't2')

        vidmapper.untagVideo(self.conn,
                             u1,
                             '5',
                             't3')

        tags = vidmapper.listUserTags(self.conn, u1)
        self.assertEqual( map( lambda t: t[0], tags ),
                          ['t2','t1'] )

        vidmapper.untagVideo(self.conn,
                             u1,
                             '0',
                             't1')

        vidmapper.untagVideo(self.conn,
                             u1,
                             '1',
                             't2')

        vidmapper.untagVideo(self.conn,
                             u1,
                             '2',
                             't2')

        tags = dict(vidmapper.listUserTags(self.conn, u1))

        self.assertEqual( tags.keys(),
                          [] )
        self.assertEqual( tags.values(),
                          [] )


if __name__ == '__main__':
    unittest.main()
