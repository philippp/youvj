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
	var artistEntry = makeArtist(artistName, "artist"+i);
	$('#artistlisting').append(artistEntry);
  }
  $('#search').show();
};

var makeArtist = function(artistName, artistID){
    var artistDiv = $('<div id="'+artistID+'"></div>').append(artistName);
    artistDiv.click(function(){loadVideos(artistName, artistID);});
    return artistDiv;
};


var loadVideos = function(artistName, artistID){
  $('#queryForm').dialog('close');
  jsonPost('/findvideos',
           {'artist':artistName},
           function(resp){loadVideosCallback(resp, artistID);}
          );
};

var loadVideosCallback = function(resp, artistID){
  $('#videos').empty();
  for( var i=0; i < resp[0].length; i++){
      $('#videos').append(renderVideo(resp[0][i]));
  }
  if( resp[0].length == 0 ){
    $('#videos').text("Sorry, nothing found.");
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
    )
  ).append(
    $('<div class="video"></div>').append(
      $('<a href="#">View Video</a>')
    )
  );
  $('.screencaps img',vid).hide();
  $('.screencaps .t0',vid).show();
  $('.screencaps',vid).mouseover(function(e){flipImages.start(e);});
  $('.screencaps',vid).mouseout(flipImages.stop);
  $('a',vid).click(function(){renderPlayer(videoInfo['flash_url']);});
  $('.screencaps',vid).click(function(){renderPlayer(videoInfo['flash_url']);});
  return vid;
};


var renderPlayer = function(purl){
  var pstr = '<object width="480" height="385">'
    + '<param name="movie" value="'+purl+'"></param>'
    + '<param name="allowFullScreen" value="true"></param>'
    + '<param name="allowscriptaccess" value="always"></param>'
    + '<embed src="'+purl+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed>'
    + '</object>';
  $('#featureVideo').html(pstr);
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
  if(flipImages.timer) return;
  flipImages.timer = setInterval(function(){flipImages(e);},500);
};

flipImages.stop = function(){
  clearInterval(flipImages.timer);
  flipImages.timer = null;
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
