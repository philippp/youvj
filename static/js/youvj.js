UVJ = {};

UVJ.renderTitleSection = function(title){
  return $('<div class="titleSection"><div class="title">'+
           title+'</div></div>');
};

UVJ.renderVideo = function(videoInfo){
  var vid = $('<div class="videoInfo" id="'+videoInfo['youtube_id']+'"></div>').append(
    $('<div class="videoInfo-top"></div>').append(
      $('<div class="drag-handle">[d]</div>')
    ).append(
      $('<div class="title"></div>').text(videoInfo['title'])
    )).append(
    $('<div class="screencaps"></div>').append(
      $('<img class="t0" src="'+videoInfo['thumbnail_1']+'"/>')
    ).append(
      $('<img class="t1" src="'+videoInfo['thumbnail_2']+'"/>')
    ).append(
      $('<img class="t2" src="'+videoInfo['thumbnail_3']+'"/>')
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
  $('img',e.currentTarget).hide();
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
  $("#featureVideo").empty();
  purl = videoInfo['flash_url'];
  purl += '&autoplay=1&fs=1';
  var pstr = '<object width="480" height="385">'
    + '<param name="movie" value="'+purl+'"></param>'
    + '<param name="fs" value="1"></param>'
    + '<param name="allowfullscreen" value="true"></param>'
    + '<param name="allowscriptaccess" value="always"></param>'
    + '<embed src="'+purl+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" fs="1" width="480" height="385"></embed>'
    + '</object>';
  var featVidObj = $('<div id="featureVideo-obj"></div>');
  featVidObj.html(pstr);
  $('#featureVideo').append(featVidObj);

  $('#featureVideo').append(
    $('<div class="player-fbpost"><a href="#"></a></div>').append(
      $('<img src="/images/facebook_share_button.png" alt="share on facebook"/>')
    ).click(
      function(){ FBC2.PostStream(videoInfo); }
    )
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

  $('#featureVideo').show();
};