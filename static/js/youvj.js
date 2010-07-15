UVJ = {};

UVJ.renderTitleSection = function(title){
  return $('<div class="titleSection"><div class="title">'+
           title+'</div></div>');
};

/**
 * Render a draggable video thumbnail and preview box
 * @return div.videInfo
 */
UVJ.makeThumb = function(videoInfo){
  var vid = $('<div class="videoInfo vid_'+videoInfo['youtube_id']+'"></div>').append(
    $('<div class="videoInfo-top"></div>').append(
      $('<div class="drag-handle"><img src="/images/drag_handle.png" alt="drag"/></div>')
    ).append(
      $('<div class="title"></div>').text(videoInfo['title'])
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
  vid.draggable({
                  'handle':'drag-handle',
                  'zIndex':9999,
                  'revert':'invalid',
                  'helper':'clone',
                  'scroll':false,
                  'connectToSortable':'ul#playlist'
                });
  vid.mouseenter(function(e){UVJ.makeThumb.flipImages.start(e);});
  vid.mouseleave(UVJ.makeThumb.flipImages.stop);
  $('a',vid).click(function(){UVJ.renderPlayer(videoInfo);});
  $('.screencaps',vid).click(function(){UVJ.renderPlayer(videoInfo);});
  $('a',vid).button();
  vid[0].info = videoInfo;
  return vid;
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

UVJ.renderPlayer = function(videoInfo){
  var fV = $("#player-container");
  fV.empty();
  fV[0].info = videoInfo;

  fV.append(
    $('<div id="featureVideo-close>[X]</div>').click(
      function(){fV.empty().hide();}
    )
  ).append(
    $('<div id="featureVideo-obj"></div>')
  ).append(
    $('<div id="player-next-info"></div>')
  ).append(
   $('<a href="#" class="player-save">Save video</a>').click(function(){
     UVJ.saveVideo(videoInfo);
     $('.player-save').hide();
     $('.player-unsave').show();
     UVJ.favorites[UVJ.favorites.length] = videoInfo['youtube_id'];
   })
  ).append(
   $('<a href="#" class="player-unsave">Unsave video</a>').click(function(){
     UVJ.unSaveVideo(videoInfo['youtube_id']);
     $('.player-unsave').hide();
     $('.player-save').show();
     UVJ.favorites.splice(UVJ.indexOf(videoInfo['youtube_id']), 1);
   })
  ).append(
    $('<div class="player-title">'+videoInfo['title']+'</div>')
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
  UVJ.updatePlayerPlaylist();
};

UVJ.playerStateChange = function(newState) {
  if( newState == 0 ){ // If the video stopped, play the next one in the queue
    var nextInfo = $('#player-next-info')[0].info;
    if( nextInfo ){
      UVJ.renderPlayer( nextInfo );
    }
  }

};

UVJ.updatePlayerPlaylist = function(){
  var curInfo = $('#player-container')[0].info;
  if( !curInfo )
    return;
  var pl = $('#playlist .videoInfo');
  for( var i = 0; i < pl.length; i++ ){
    if( pl[i].info['youtube_id'] == curInfo['youtube_id'] ){
      if( i + 1 < pl.length ){
        var nextSong = pl[i+1].info['artist'] + ' - ' + pl[i+1].info['title'];
        $('#player-next-info').empty().append(
          $("<span>Next Video: </span><span>"+nextSong+"</span>")
        )[0].info = pl[i+1].info;
        return;
      }else{
          $('#player-next-info').empty().append('Last video in playlist! Queue up more')[0].info = null;
          return;
      }
    }
  }// for
  $('#player-next-info').empty().append('This video is not in your playlist')[0].info = null;
};

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
      var i = 0;
      var classNames = ui.item.attr('class').split(' ');
      var className = '';
      for( i = 0; i < classNames.length; i++ ){
        if( classNames[i].indexOf('vid_') == 0 ){
          className = classNames[i];
        }
      }
      var orig = $('#middle .'+className);
      var all = $('.'+className);
      for( i = 0; i < all.length; i++ ){
        all[i].info = orig[0].info;
      }
    },
    'stop' : UVJ.updatePlayerPlaylist
  });
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
  for( var i = 0; i < resp.length; i++ ){
    jQuery('#middle').append( UVJ.makeThumb(resp[i]) );
  }
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
            $("<span class='browse-similar-legend'> similar to </span>")
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


