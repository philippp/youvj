$(document).ready(function(){
  $('#queryForm').dialog({ autoOpen: false,
                           title : 'Search Artists',
                           buttons: { "Ok": function() { parseArtists(); $(this).dialog("close"); } }});
  $('#queryForm').dialog('open');
  $('#search').click(function(){
                       $('#queryForm').dialog('open');
                     });
  $('#search').hide();
  $('#videos').css({'height':$(document).height()});
});

var parseArtists = function(){
  $('#artistlisting').empty();
  splitNames = $('#artistnames').val().split(",");
  for( var i = 0; i < splitNames.length; i++ ){
	var artistName = splitNames[i].trim();
	var artistEntry = makeArtist(artistName);
	$('#artistlisting').append(artistEntry);
  }
  $('#search').show();
  if($('#artistlisting a').length > 0){
    $($('#artistlisting a')[0]).click();
  }
};

var makeArtist = function(artistName){
    var artistDiv = $('<div class="menu-artist"></div>').append(
                      $('<div class="menu-artist-indicator">&#8594;</div>')).append(
                      $('<a href="#">'+artistName+'</a>'));
    artistDiv.click(function(e){
      loadVideos(artistName);
      loadSimilar(artistName);
      document.location.hash = artistName;
      $('.menu-artist').removeClass('menu-artist-selected');
      $(e.currentTarget).addClass('menu-artist-selected');
      $('.menu-artist-indicator').hide();
      $('.menu-artist-indicator', e.currentTarget).show();
    });
    return artistDiv;
};


var loadVideos = function(artistName){
  $('#queryForm').dialog('close');
  jsonPost('/findvideos',
           {'artist':artistName},
           loadVideosCallback
          );
};

var loadVideosCallback = function(resp){
  $('.videoInfo, .message').remove();
  for( var i=0; i < resp[0].length; i++){
    renderVideo(resp[0][i]).insertBefore($("#similar-artist-divider"));
  }
  if( resp[0].length == 0 ){
    $('#media').append("<div class='message'>Sorry, nothing found.</>");
  }
};

var renderVideo = function(videoInfo){
  var vid = $('<div class="videoInfo"></div>').append(
    $('<div class="title"></div>').text(videoInfo['title'])
  ).append(
    $('<div class="description"></div>').text(videoInfo['description'])
  ).append(
    $('<div class="screencaps"></div>').append(
      $('<img class="t0" src="'+videoInfo['thumbnails'][0]+'"/>')
    ).append(
      $('<img class="t1" src="'+videoInfo['thumbnails'][1]+'"/>')
    ).append(
      $('<img class="t2" src="'+videoInfo['thumbnails'][2]+'"/>')
    ).append(
      $('<div class="screenspace">&nbsp;</div>')
    )
  ).append(
    $('<div class="video"></div>').append(
      $('<a href="#">View Video</a>')
    )
  );
  $('.screencaps img',vid).hide();
  $('.screencaps .t0',vid).show();
  $(vid).mouseenter(function(e){flipImages.start(e);});
  $(vid).mouseleave(flipImages.stop);
  $('a',vid).click(function(){renderPlayer(videoInfo['flash_url']);});
  $('.screencaps',vid).click(function(){renderPlayer(videoInfo['flash_url']);});
  $('a',vid).button();
  return vid;
};

var loadSimilar = function(artistName){
  jsonPost('/findsimilar',
           {'artist':artistName},
           loadSimilarCallback
          );
};

var loadSimilarCallback = function(resp){
  $('.similar-artist').remove();
  for( var i=resp.length-1; i >= 0; i--){
    renderSimilar(resp[i]).insertAfter($("#similar-artist-divider"));
  }
};

var renderSimilar = function(pairing){
  var similarArtist = $("<div class='similar-artist'></div>").append(
                        $("<a href='#'></a>").text(pairing[0])
                        );
  $('a',similarArtist).click(function(){
                               loadVideos(pairing[0]);
                               loadSimilar(pairing[0]);
                               document.location.hash = pairing[0];
                             });
  return(similarArtist);
};

var renderPlayer = function(purl){
  purl += '&autoplay=1';
  var pstr = '<object width="480" height="385">'
    + '<param name="movie" value="'+purl+'"></param>'
    + '<param name="allowFullScreen" value="true"></param>'
    + '<param name="allowscriptaccess" value="always"></param>'
    + '<embed src="'+purl+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed>'
    + '</object>';
  $('#featureVideo').html(pstr);
  $('#featureVideo').show();
};

var flipImages = function(e){
  flipImages.counter++;
  var targetCls = '.t'+(flipImages.counter % 3);
  $('img',e.currentTarget).hide();
  $(targetCls, e.currentTarget).show();
};
flipImages.counter = 0;
flipImages.timer = null;

flipImages.start = function(e){
  if(flipImages.timer) return false;
  flipImages(e);
  console.log('starting thumbnail image timer');
  flipImages.timer = setInterval(function(){flipImages(e);},500);
  return false;
};

flipImages.stop = function(){

  clearInterval(flipImages.timer);
  flipImages.timer = null;
  console.log('clearing thumbnail image timer');
  return false;
};

var jsonPost = function(path, params, success, fail){
    if( !fail ){
	fail = alert;
    }
    $.post(path,
	   params,
	   function(resp){
	       try{
		   resp = eval("("+resp+")");
	       }catch(e){}
	       success(resp);
	   },
	   fail,
	   'json'
	   );
};

String.prototype.ltrim = function() {
    return this.replace(/^\s+/,"");
}

String.prototype.rtrim = function() {
    return this.replace(/\s+$/,"");
}

String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g,"");
}
