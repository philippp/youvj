#!/usr/bin/env python




##################################################
## DEPENDENCIES
import sys
import os
import os.path
import __builtin__
from os.path import getmtime, exists
import time
import types
from Cheetah.Version import MinCompatibleVersion as RequiredCheetahVersion
from Cheetah.Version import MinCompatibleVersionTuple as RequiredCheetahVersionTuple
from Cheetah.Template import Template
from Cheetah.DummyTransaction import *
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers
from base import base

##################################################
## MODULE CONSTANTS
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time
__CHEETAH_version__ = '2.4.0'
__CHEETAH_versionTuple__ = (2, 4, 0, 'final', 0)
__CHEETAH_genTime__ = 1270449407.7765961
__CHEETAH_genTimestamp__ = 'Mon Apr  5 06:36:47 2010'
__CHEETAH_src__ = 'show.tmpl'
__CHEETAH_srcLastModified__ = 'Sun Apr  4 20:40:50 2010'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class show(base):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(show, self).__init__(*args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)
        

    def title(self, **KWS):



        ## CHEETAH: generated from #def title() at line 3, col 1.
        trans = KWS.get("trans")
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write(u'''Your choons
''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        

    def body(self, **KWS):



        ## CHEETAH: generated from #def body() at line 7, col 1.
        trans = KWS.get("trans")
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        idx = 0
        for artist,entries in VFN(VFFSL(SL,"artist_entries",True),"iteritems",False)(): # generated from line 9, col 3
            write(u'''
    <h2>''')
            _v = VFFSL(SL,"artist",True) # u'$artist' on line 11, col 9
            if _v is not None: write(_filter(_v, rawExpr=u'$artist')) # from line 11, col 9.
            write(u'''</h2>
''')
            for entry in VFFSL(SL,"entries",True): # generated from line 12, col 5
                idx = VFFSL(SL,"idx",True) + 1
                write(u'''        ''')
                _v = VFFSL(SL,"artist_entry",False)(VFFSL(SL,"entry",True), VFFSL(SL,"idx",True)) # u'$artist_entry($entry, $idx)' on line 14, col 9
                if _v is not None: write(_filter(_v, rawExpr=u'$artist_entry($entry, $idx)')) # from line 14, col 9.
                write(u'''
''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        

    def artist_entry(self, entry, id, **KWS):



        ## CHEETAH: generated from #def artist_entry($entry, $id): at line 19, col 1.
        trans = KWS.get("trans")
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write(u'''<div>
  <h3>''')
        _v = VFFSL(SL,"entry.title",True) # u'$entry.title' on line 21, col 7
        if _v is not None: write(_filter(_v, rawExpr=u'$entry.title')) # from line 21, col 7.
        write(u''' (''')
        _v = VFFSL(SL,"entry.view_count",True) # u'$entry.view_count' on line 21, col 21
        if _v is not None: write(_filter(_v, rawExpr=u'$entry.view_count')) # from line 21, col 21.
        write(u''' views)</h3>
  <h4>''')
        _v = VFFSL(SL,"entry.description",True) # u'$entry.description' on line 22, col 7
        if _v is not None: write(_filter(_v, rawExpr=u'$entry.description')) # from line 22, col 7.
        write(u'''</h4>
  <div>
''')
        for th in VFN(VFFSL(SL,"entry",True),"thumbnails",True)[:-1]: # generated from line 24, col 5
            write(u'''      <img src="''')
            _v = VFFSL(SL,"th",True) # u'$th' on line 25, col 17
            if _v is not None: write(_filter(_v, rawExpr=u'$th')) # from line 25, col 17.
            write(u'''" class="thumbnail"/>
''')
        write(u'''      <a name="mv''')
        _v = VFFSL(SL,"id",True) # u'$id' on line 27, col 18
        if _v is not None: write(_filter(_v, rawExpr=u'$id')) # from line 27, col 18.
        write(u'''"></a>
      <a href="#mv''')
        _v = VFFSL(SL,"id",True) # u'$id' on line 28, col 19
        if _v is not None: write(_filter(_v, rawExpr=u'$id')) # from line 28, col 19.
        write(u'''" onclick="$(\'.music-video\').hide();$(\'#mv''')
        _v = VFFSL(SL,"id",True) # u'$id' on line 28, col 66
        if _v is not None: write(_filter(_v, rawExpr=u'$id')) # from line 28, col 66.
        write(u'''\').show();return false;">Show video</a>
      <div class="music-video" id="mv''')
        _v = VFFSL(SL,"id",True) # u'$id' on line 29, col 38
        if _v is not None: write(_filter(_v, rawExpr=u'$id')) # from line 29, col 38.
        write(u'''" style="display:none;">
\t<object width="640" height="385">
\t  <param name="movie" value="''')
        _v = VFFSL(SL,"entry.flash_url",True) # u'$entry.flash_url' on line 31, col 31
        if _v is not None: write(_filter(_v, rawExpr=u'$entry.flash_url')) # from line 31, col 31.
        write(u'''"></param>
\t  <param name="allowFullScreen" value="true"></param>
\t  <param name="allowscriptaccess" value="always"></param>
\t  <embed src="''')
        _v = VFFSL(SL,"entry.flash_url",True) # u'$entry.flash_url' on line 34, col 16
        if _v is not None: write(_filter(_v, rawExpr=u'$entry.flash_url')) # from line 34, col 16.
        write(u'''"
\t\t type="application/x-shockwave-flash"
\t\t allowscriptaccess="always" 
\t\t allowfullscreen="true" 
\t\t width="640" 
\t\t height="385">
\t  </embed>
\t</object>
      </div>
  </div>
</div>
''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        

    def writeBody(self, **KWS):



        ## CHEETAH: main method generated for this template
        trans = KWS.get("trans")
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write(u'''


''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        
    ##################################################
    ## CHEETAH GENERATED ATTRIBUTES


    _CHEETAH__instanceInitialized = False

    _CHEETAH_version = __CHEETAH_version__

    _CHEETAH_versionTuple = __CHEETAH_versionTuple__

    _CHEETAH_genTime = __CHEETAH_genTime__

    _CHEETAH_genTimestamp = __CHEETAH_genTimestamp__

    _CHEETAH_src = __CHEETAH_src__

    _CHEETAH_srcLastModified = __CHEETAH_srcLastModified__

    _mainCheetahMethod_for_show= 'writeBody'

## END CLASS DEFINITION

if not hasattr(show, '_initCheetahAttributes'):
    templateAPIClass = getattr(show, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(show)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=show()).run()


