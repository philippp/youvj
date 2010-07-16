UVJ = {};

UVJ.renderTitleSection = function(title){
  return $('<div class="titleSection"><div class="title">'+
           title+'</div></div>');
};

/**
 * Render a draggable video thumbnail and preview box
 * @return div.videInfo
 */
UVJ.makeThumb = function(videoInfo, options){
  if( !options ) options = {};
  if( options.draggable === undefined ){
    options.draggable = true;
  }
  var vid = $('<div class="videoInfo vid_'+videoInfo['youtube_id']+'"></div>').append(
    $('<div class="videoInfo-top"></div>').append(
      $('<div class="thumb-play-indicator">Playing Now</div>')
    ).append(
      $('<div class="drag-handle"><img src="/images/drag_handle.png" alt="drag"/><span class="title">'+videoInfo['title']+'</span></div>')
    )).append(
    $('<div class="screencaps"></div>').append(
      $('<img class="thumb t0" src="'+videoInfo['thumbnail_1']+'"/>')
    ).append(
      $('<img class="thumb t1" src="'+videoInfo['thumbnail_2']+'"/>')
    ).append(
      $('<img class="thumb t2" src="'+videoInfo['thumbnail_3']+'"/>')
    ).append(
      $('<div class="screenspace">&nbsp;</div>')
    )
  ).append(
    $('<div class="play-video"></div>').append(
      $('<a href="#">Play Video</a>')
    )
  );
  $('.screencaps img',vid).hide();
  $('.screencaps .t0',vid).show();
  if( options.draggable ){
    vid.draggable({
      'handle':'.drag-handle',
      'zIndex':9999,
      'revert':'invalid',
      'helper':'clone',
      'scroll':false,
      'connectToSortable':'ul#playlist'
    });
  }
  vid[0].info = videoInfo;
  UVJ.initThumb(vid);
  return vid;
};

UVJ.initThumb = function(thumbElem){
  thumbElem.mouseenter(
    function(v){
      return function(e){UVJ.makeThumb.flipImages.start(e);
                         $('.play-video',v).show();
                        };
    }(thumbElem)
  );
  thumbElem.mouseleave(
    function(v){
      return function(e){
       UVJ.makeThumb.flipImages.stop();
        $('.play-video',v).hide();
      };
    }(thumbElem)
  );
  $('a',thumbElem).click(function(){UVJ.renderPlayer(thumbElem[0].info);});
  $('.screencaps',thumbElem).click(function(){UVJ.renderPlayer(thumbElem[0].info);});
  $('a',thumbElem).button();
};

UVJ.makeThumb.flipImages = function(e){
  UVJ.makeThumb.flipImages.counter++;
  var targetCls = '.t'+(UVJ.makeThumb.flipImages.counter % 3);
  $('.screencaps img',e.currentTarget).hide();
  $(targetCls, e.currentTarget).show();
};

UVJ.makeThumb.flipImages.counter = 0;
UVJ.makeThumb.flipImages.timer = null;

UVJ.makeThumb.flipImages.start = function(e){
  var flip = UVJ.makeThumb.flipImages;
  if(flip.timer) return false;
  flip(e);
  flip.timer = setInterval(function(){UVJ.makeThumb.flipImages(e);},500);
  return false;
};

UVJ.makeThumb.flipImages.stop = function(){
  clearInterval(UVJ.makeThumb.flipImages.timer);
  UVJ.makeThumb.flipImages.timer = null;
  return false;
};


UVJ.player = {};
UVJ.renderPlayer = function(videoInfo){
  var fV = $("#player-container");
  fV.empty();
  fV[0].info = videoInfo;

  fV.append(
    $('<div id="player-close" title="close player">[X]</div>').click(
      function(){fV.empty().hide();}
    )
  ).append(
    $('<div class="player-title">'+videoInfo['artist']+' - '+videoInfo['title']+'</div>')
  ).append(
    $('<div id="featureVideo-obj"></div>')
  ).append(
    $('<div id="player-next-info"></div>')
  ).append(
    $('<div class="player-description">'+videoInfo['description']+'</div>')
  ).append($(''));

  if( UVJ.favorites && UVJ.favorites.indexOf && UVJ.favorites.indexOf(videoInfo['youtube_id']) >= 0 ){
    $('.player-save').hide();
    $('.player-unsave').show();
  }else{
    $('.player-unsave').hide();
    $('.player-save').show();
  }

  purl = videoInfo['flash_url'];
  purl += '&autoplay=1&fs=1&enablejsapi=1&version=3';
  swfobject.embedSWF(purl,
                     'featureVideo-obj', //replace ID
                     '480', //width
                     '385', //height
                     '9',
                     null,
                     {'movie':purl,
                      'fs':1,
                      'allowfullscreen':true,
                      'allowscriptaccess':'always'},
                     {'movie':purl,
                      'fs':1,
                      'allowfullscreen':true,
                      'allowScriptAccess':'always'},
                     {'id':'myytplayer'}
  );
  fV.show();
  UVJ.player.updatePlaylist();
};

UVJ.player.addToPlaylist = function(){
  var player = $('#player-container')[0];
  if( player.info ){
    var thumb = UVJ.makeThumb( player.info, {'draggable':false} );
    $('#playlist').append(thumb).sortable('refresh');
    UVJ.playlist.onAddItem( thumb );
  }
  return false;
};

UVJ.player.next = function(){
  var nextInfo = $('#player-next-info')[0].info;
  if( nextInfo ){
    UVJ.renderPlayer( nextInfo );
  }
};

UVJ.playerStateChange = function(newState) {
  if( newState == 0 ){ // If the video stopped, play the next one in the queue
    UVJ.player.next();
  }

};

UVJ.player.updatePlaylist = function(){
  var curInfo = $('#player-container')[0].info;
  if( !curInfo )
    return;
  var pl = $('#playlist .videoInfo');
  var videoIdx = -1;
  for( var i = 0; i < pl.length; i++ ){
    if( pl[i].info['youtube_id'] == curInfo['youtube_id'] ){
      if( i + 1 < pl.length ){
        var nextSong = pl[i+1].info['artist'] + ' - ' + pl[i+1].info['title'];

        // Render the next song indicator in the player
        $('#player-next-info').empty().append(
          $("<span>Next video:&nbsp;</span>")
        ).append(
          $("(<a href='#'>"+nextSong+"</a>").click(
            function(){ UVJ.player.next(); return false;}
          )
        )[0].info = pl[i+1].info;
        videoIdx = i;
        break;
      }else{
        $('#player-next-info').empty().append('Last video: Queue up more!')[0].info = null;
        videoIdx = i;
        break;
      }
    }
  }// for
  if( videoIdx != -1 ){
    // Update what is currently playing in the playlist
    $("#playlist .thumb-play-indicator").hide();
    var selector = "#playlist .vid_"+pl[videoIdx].info['youtube_id']+" .thumb-play-indicator";
    $(selector).show();
    return;
  }
  $('#player-next-info').empty().append('Not in this playlist:&nbsp;')[0].info = null;
  $('#player-next-info').append($('<a href="#">Add it!</a>').click(
                                  function(){ return UVJ.player.addToPlaylist(); }
                                  ));
};

UVJ.playlist = {};
UVJ.configurePlaylist = function(){
  jQuery('#playlist').sortable({
    'over':function(e, ui){
      e.target.style.border = '2px solid blue';
    },
    'out':function(e, ui){
      e.target.style.border = 'none';
    },
    'tolerance': 'pointer',
    'receive' : function(e, ui){
      UVJ.playlist.onAddItem( ui.item );
    },
    'stop' : UVJ.player.updatePlaylist
  });
};

UVJ.playlist.onAddItem = function(elem){
  var i = 0;
  var classNames = elem.attr('class').split(' ');
  var className = '';
  for( i = 0; i < classNames.length; i++ ){
    if( classNames[i].indexOf('vid_') == 0 ){
      className = classNames[i];
    }
  }

  var orig = $('#middle .'+className);
  var dst = $('#playlist .'+className);
  for( i = 0; i < dst.length; i++ ){
    dst[i].info = orig[0].info;
  }

  UVJ.initThumb(dst);
  $('.title',dst).width(90);
  $('.videoInfo-top',dst).append(
    $('<a class="playlist-del" href="#">[X]</a>').click(
      function(e){
        $(this.parentNode.parentNode).remove();
        $('#playlist').sortable('refresh');
        UVJ.player.updatePlaylist();
        return false;
      }
    )
  );
  dst.height(125);
};

UVJ.browse = function( artist ){
  jQuery.post('/findvideos',
              {'artist':artist},
              function(resp){
                UVJ.onBrowseCallback(resp, artist);
              },
              'json'
  );
  jQuery.post('/findsimilar',
              {'artist':artist},
              function(resp){
                UVJ.onLoadSimilar(resp, artist);
              },
              'json'
  );
  UVJ.artist = artist;
  $('#browseInput')[0].value = artist;
  return false;
};

UVJ.onBrowseCallback = function( resp, artist ){
  jQuery('#middle .videoInfo').remove();
  jQuery('#middle br').remove();
  UVJ.artistVids = resp;
  for( var i = 0; i < resp.length; i++ ){
    jQuery('#middle').append( UVJ.makeThumb(resp[i]) );
  }
  $('#middle').append($("<br style='clear: both'/>"));
};

UVJ.loadSimilar = function(artistName){
  UVJ.artist = artistName;
  $('.similar-artist').remove();
  jQuery.post('/findsimilar',
           {'artist':artistName},
           function(resp){UVJ.onLoadSimilar(resp, artistName);},
           'json'
          );
};

UVJ.onLoadSimilar = function(resp, artistName){
  if( artistName != UVJ.artist ){
    return;
  }
  var extraCls = "";
  var similarDiv = $('#browse-similar');
  similarDiv.empty();
  for( i=0; i < Math.min(10,resp.length); i++){
    var curArtist = resp[i][0];
    similarDiv.append(
      $("<a href='#' class='browse-similar-entry "+extraCls+"' title='"+resp[i][0]+"'>"+curArtist+"</a>").click(
        (function(f){return function(e){
                       UVJ.browse(f);
                       return false;
                     };})(curArtist)
      )
    );
  }

  if( resp.length > 0 ){
    similarDiv.prepend(
            $("<span class='browse-similar-legend'>Similar artists: </span>")
    );
  }

};

var renderSimilar = function(pairing){
  var similarArtist = $("<div class='similar-artist'></div>").append(
                        $("<a href='#'></a>").text(pairing[0])
                        );
  $('a',similarArtist).click(function(){
                               UVJ.searchArtists([pairing[0]]);
                             });
  return(similarArtist);
};

function onYouTubePlayerReady(playerId) {
  ytplayer = document.getElementById("myytplayer");
  ytplayer.addEventListener("onStateChange", "UVJ.playerStateChange");
}


