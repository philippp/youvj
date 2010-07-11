UVJ = {};

UVJ.renderTitleSection = function(title){
  return $('<div class="titleSection"><div class="title">'+
           title+'</div></div>');
};

UVJ.renderVideo = function(videoInfo){
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
      $('<img class="rhumb t2" src="'+videoInfo['thumbnail_3']+'"/>')
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
  vid.mouseenter(function(e){UVJ.flipImages.start(e);});
  vid.mouseleave(UVJ.flipImages.stop);
  $('a',vid).click(function(){UVJ.renderPlayer(videoInfo);});
  $('.screencaps',vid).click(function(){UVJ.renderPlayer(videoInfo);});
  $('a',vid).button();
  vid[0].info = videoInfo;
  return vid;
};

UVJ.flipImages = function(e){
  UVJ.flipImages.counter++;
  var targetCls = '.t'+(UVJ.flipImages.counter % 3);
  $('.screencaps img',e.currentTarget).hide();
  $(targetCls, e.currentTarget).show();
};

UVJ.flipImages.counter = 0;
UVJ.flipImages.timer = null;

UVJ.flipImages.start = function(e){
  if(UVJ.flipImages.timer) return false;
  UVJ.flipImages(e);
  UVJ.flipImages.timer = setInterval(function(){UVJ.flipImages(e);},500);
  return false;
};

UVJ.flipImages.stop = function(){
  clearInterval(UVJ.flipImages.timer);
  UVJ.flipImages.timer = null;
  return false;
};

UVJ.renderPlayer = function(videoInfo){
  var fV = $("#player-container");
  fV.empty();
  fV[0].info = videoInfo;
  purl = videoInfo['flash_url'];
  purl += '&autoplay=1&fs=1&enablejsapi=1&version=3';
  var pstr = '<object width="480" height="385" id="yt-player-obj">'
    + '<param name="movie" value="'+purl+'"></param>'
    + '<param name="fs" value="1"></param>'
    + '<param name="allowfullscreen" value="true"></param>'
    + '<param name="allowscriptaccess" value="always"></param>'
    + '<embed src="'+purl+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" fs="1" width="480" height="385"></embed>'
    + '</object>';
  var featVidObj = $('<div id="featureVideo-obj"></div>');
  featVidObj.html(pstr);

  var featVidClose = $('<div id="featureVideo-close>[X]</div>');
  featVidClose.click(function(){fV.empty().hide();});
  fV.append(featVidClose);
  fV.append(featVidObj);

  fV.append(
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
  fV.show();
};

UVJ.playerStateChange = function(state){
  alert(state);
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
      }
    }
  }// for
  $('#player-next-info').replace('Last one! Queue up more')[0].info = null;
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


