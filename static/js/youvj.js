UVJ = {};

UVJ.renderTitleSection = function(title){
  return $('<div class="titleSection"><div class="title">'+
           title+'</div></div>');
};

UVJ.renderVideo = function(videoInfo){
  var vid = $('<div class="videoInfo"></div>').append(
    $('<div class="drag-handle">drag</div>')
  ).append(
    $('<div class="title"></div>').text(videoInfo['title'])
  ).append(
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
  $('a',vid).click(function(){renderPlayer(videoInfo);});
  $('.screencaps',vid).click(function(){renderPlayer(videoInfo);});
  $('a',vid).button();
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
