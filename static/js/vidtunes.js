UVJ.log = function(logObj){
  jsonPost('/log',
           logObj,
           function(resp){}
          );

};

UVJ.searchInline = function(){
  var val = $("#inline-search")[0].value;
  if( val != $('#inline-search')[0].title ){
    UVJ.searchArtists([val]);
  }
  return false;

};

UVJ.searchArtists = function(artistNames){
  $('#footer').show();
  $("#popup-welcome-border").hide();
  UVJ.searchArtists.list = unique(artistNames.concat(UVJ.searchArtists.list));
  var searchHeader = $('<span id="artist-search-header"></span>').append(
    $("<span class='medium'>Browse and Find</span>")
  ).append($("<form class='inline-search-box'></form>").append(
             $("<input class='default-text' type='text' id='inline-search' title='Artist Search'/>")
           ).append(
             $("<input type='submit' value='Find'/>")
           ).submit(function(e){ UVJ.searchInline(); })
  ).append($("<a href='#'>Saved Videos</a>").click(function(){UVJ.loadSaved();}));

  $(".default-text", searchHeader).focus(function(srcc){
    if ($(this).val() == $(this)[0].title){
      $(this).removeClass("default-text-active");
      $(this).val("");
    }
  });
  $(".default-text", searchHeader).blur(function(){
    if ($(this).val() == ""){
      $(this).addClass("default-text-active");
      $(this).val($(this)[0].title);
    }
  });
  $(".default-text", searchHeader).blur();

  renderArtistsGrouping(UVJ.searchArtists.list, searchHeader, 'Search');
};
UVJ.searchArtists.list = [];

var renderArtistsGrouping = function(artistNames, headerElement, targetID){
  var aid = targetID;
  if( aid ) {
    $("#artistGrouping"+aid).remove();
  }else{
    renderArtistsGrouping.id++;
    aid = renderArtistsGrouping.id;
  }

  var artistGrouping = $('<div class="artist-grouping" id="artistGrouping'+aid+'"></div>');
  if( headerElement ){
    headerElement = $("<div class='menu-artist-title'></div>").append(
      $('<a href="#" title="hide list of artists" class="toggle toggle_off-'+aid+'"></a>').append(
        $('<span>[-]</span>')
      ).click(
        (function(i){return function(){
          $('.artistBatch'+i).hide();
          $('.toggle_off-'+i).hide();
          $('.toggle_on-'+i).show();
          return false;
        };})(aid)
      )
    ).append(
      $('<a href="#" title="show list of artists" class="toggle toggle_on-'+aid+'" style="display:none;"></a>').append(
        $('<span>[+]</span>')
      ).click(
        (function(i){return function(){
          $('.artistBatch'+i).show();
          $('.toggle_off-'+i).show();
          $('.toggle_on-'+i).hide();
          return false;
        };})(aid)
      )
    ).append(headerElement);
    artistGrouping.append(headerElement);
  }

  for( var i = 0; i < artistNames.length; i++ ){
	var artistName = artistNames[i];
	var artistEntry = makeArtistMenuItem(artistName);
        artistEntry.addClass('artistBatch'+aid);
	artistGrouping.append(artistEntry);
  }
  if( aid == "Search" ){
    $('#artistlisting').prepend(artistGrouping);
  }else{
    artistGrouping.insertAfter($('#artistGroupingSearch'));
  }

  $('#search').show();
  if($('a.artist-name', artistGrouping).length > 0){
    $($('a.artist-name', artistGrouping)[0]).click();
  }
};
renderArtistsGrouping.id = 0;

var parseArtistNames = function(textVal){
  var splitNames = textVal.split(",");
  for( var i = 0; i < splitNames.length; i++ ){
	splitNames[i] = splitNames[i].trim();
  }
  return splitNames;
};

var loadArtist = function(artistName){
  loadVideos(artistName);
  loadSimilar(artistName);
  renderArtistBox(artistName);
};

var makeArtistMenuItem = function(artistName){
    var artistDiv = $('<div class="menu-artist"></div>').append(
                      $('<div class="menu-artist-indicator">&#8594;</div>')).append(
                      $('<a class="artist-name" href="#">'+artistName+'</a>'));
    artistDiv.click(function(e){
      loadArtist(artistName);
      $(e.currentTarget).addClass('menu-artist-selected');
      $('.menu-artist-indicator', e.currentTarget).show();
    });
    return artistDiv;
};

var renderArtistBox = function(artistName){
  var artistBox = $("<div id='videoInfo-artist'></div>").append(
    $("<div id='videoInfo-artistName'>"+artistName+"</div>")
  ).append(
    $("<div id='videoInfo-artistFriends'></div>")
  ).append(
    $("<div id='videoInfo-similar'></div>")
  );
  artistBox.insertBefore($("#video-loader"));
  var shFriends = [];
  var friendLimit = 3;
  var found = 0;
  for( i = 0; FBC2.friends && i < FBC2.friends.friends.length; i++ ){
    var friend = FBC2.friends.friends[i];
    var regexp = new RegExp(artistName,'i');
    if( regexp.test(friend['music_str'])){
      found++;
      var extraCls = "";
      if(found > friendLimit){
        extraCls = "extra-content";
      }
      $("#videoInfo-artistFriends", artistBox).append(
          $("<a href='#' class='videoInfo-friend "+extraCls+"'>"+friend['name']+"</a>").click(

            (function(f){ return function(e){
              renderArtistsGrouping(f['bands'],
              FBC2.makeMenuArtistTitle(f),
              "_u"+f['id']
              );
              return false;
            }; })(friend)
          )
        );
    }
  }
  if( found > 0 ){
    $("#videoInfo-artistFriends", artistBox).prepend(
      $("<span class='videoInfo-friend'><img src='/images/heart.gif' alt='heart'/> by </span>")
    );

  }
  if( found > friendLimit ){
    $("#videoInfo-artistFriends", artistBox).append(
      $("<a class='videoInfo-friend show-more'> and "+(found-friendLimit)+" others.</a>").click(
        function(){
          $(".extra-content",artistBox).show();
          $(".show-more", artistBox).hide();
          artistBox.css({'height':'auto'});
        }
      )
    );
  }

};

var loadVideos = function(artistName){
  loadVideos.artistName = artistName;
  $('.menu-artist').removeClass('menu-artist-selected');
  $('.menu-artist-indicator').hide();
  $('#queryForm').dialog('close');
  $('.videoInfo, .message, #video-loader, #videoInfo-artist').remove();
  var loader = $("<div id='video-loader'></div>").append(
                 $("<img src='/images/spin_loader.gif'/>")
  ).append(
    $("<div id='video-loader-msg'>Please wait while we search for videos by "+artistName+"</div>")
    );
  loader.insertBefore($("#similar-artist-divider"));

  jsonPost('/findvideos',
           {'artist':artistName},
           function(resp){ loadVideosCallback(resp, artistName); }
          );
};
loadVideos.artistName = '';

var loadVideosCallback = function(resp, artistName){
  if( artistName != loadVideos.artistName ){
    return;
  }
  $("#video-loader").hide();
  $("#videoInfo-artist").show();
  for( var i=0; i < resp[0].length; i++){
    UVJ.renderVideo(resp[0][i]).insertBefore($("#similar-artist-divider"));
  }
  if( resp[0].length == 0 ){
    $("<div class='message'>Sorry, nothing found.</>").insertBefore($("#similar-artist-divider"));
  }
};

UVJ.renderVideos = function(videoInfoEntries){
  $('.videoInfo, .message, #video-loader, #videoInfo-artist').remove();
  for( var i=0; i < videoInfoEntries.length; i++){
    UVJ.renderVideo(videoInfoEntries[i]).insertBefore($("#similar-artist-divider"));
  }
};

UVJ.renderVideo = function(videoInfo){
  var vid = $('<div class="videoInfo"></div>').append(
    $('<div class="title"></div>').text(videoInfo['title'])
  ).append(
    $('<div class="description"></div>').text(videoInfo['description'])
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
  $(vid).mouseenter(function(e){flipImages.start(e);});
  $(vid).mouseleave(flipImages.stop);
  $('a',vid).click(function(){renderPlayer(videoInfo);});
  $('.screencaps',vid).click(function(){renderPlayer(videoInfo);});
  $('a',vid).button();
  return vid;
};

UVJ.unSaveVideo = function( youtube_id ){
  jsonPost('/unsavevideo',
           {'youtube_id':youtube_id},
           UVJ.unSaveVideoCallback);
};

UVJ.unSaveVideoCallback = function( resp ){

};

UVJ.saveVideo = function( videoInfo ){
  var toSend = {}, i = 0;
  var sameArgs = ['title',
                  'artist',
                  'description',
                  'view_count',
                  'duration',
                  'flash_url',
                  'youtube_id',
                  'thumbnail_1',
                  'thumbnail_2',
                  'thumbnail_3'];
  for( i=0; i < sameArgs.length; i++ ){
    toSend[sameArgs[i]] = videoInfo[sameArgs[i]];
  }



  jsonPost('/savevideo',
           toSend,
           UVJ.saveVideoCallback
          );
};

UVJ.saveVideoCallback = function( resp ){

};

UVJ.loadSaved = function(){
  jsonPost('/listsavedvideos',
           {},
           function(resp){UVJ.loadSavedCallback(resp);}
          );
};

UVJ.loadSavedCallback = function(resp){
  UVJ.renderVideos(resp);
};

var loadSimilar = function(artistName){
  loadSimilar.artistName = artistName;
  $('.similar-artist').remove();
  jsonPost('/findsimilar',
           {'artist':artistName},
           function(resp){loadSimilarCallback(resp, artistName);}
          );
};
loadSimilar.artistName = '';

var loadSimilarCallback = function(resp, artistName){
  if( artistName != loadSimilar.artistName ){
    return;
  }
  var similarLimit = 4;
  var extraCls = "";
  var similarDiv = $('#videoInfo-similar');
  for( var i=resp.length-1; i >= 0; i--){
    renderSimilar(resp[i]).insertAfter($("#similar-artist-divider"));
  }
  for( i=0; i < resp.length; i++){
    if( i > similarLimit ){
      extraCls = "extra-content";
    }
    var curArtist = resp[i][0];
    var shortArtist = curArtist;
    if( curArtist.length > 15 ){
      shortArtist = curArtist.substring(0,12)+'...';
    }
    similarDiv.append(
      $("<a href='#' class='videoInfo-similar "+extraCls+"' title='"+resp[i][0]+"'>"+shortArtist+"</a>").click(
        (function(f){return function(e){
                       UVJ.searchArtists([f]);
                       return false;
                     };})(curArtist)
      )
    );
  }

  if( resp.length > 0 ){
    similarDiv.prepend(
            $("<span class='videoInfo-similar'> ~ to </span>")
    );
  }

  if( resp.length > similarLimit ){
    var similarShow = $("<a class='videoInfo-similar show-more'> and "+(resp.length-similarLimit)+" others.</a>").click(
        function(){
          $("#videoInfo-similar .extra-content").show();
          $("#videoInfo-similar .show-more").hide();
          $("#videoInfo-artist").css({'height':'auto'});
        }
      );

    similarDiv.append(
      similarShow
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

var renderPlayer = function(videoInfo){
  UVJ.log({'data_1':2, 'text_info':videoInfo['flash_url']});
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
  flipImages.timer = setInterval(function(){flipImages(e);},500);
  return false;
};

flipImages.stop = function(){

  clearInterval(flipImages.timer);
  flipImages.timer = null;
  return false;
};

var jsonPost = function(path, params, success, fail){
    if( !fail ){
	fail = alert;
    }
    $.getJSON('http://notphil.com:8080'+path,
	   params,
	   success
	   );
};



FBC = {};

FBC.fbFriends = [];
FBC.session = {};



String.prototype.ltrim = function() {
    return this.replace(/^\s+/,"");
}

String.prototype.rtrim = function() {
    return this.replace(/\s+$/,"");
}

String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g,"");
}

var unique = function(a)
{
  var r = new Array();
  o:for(var i = 0, n = a.length; i < n; i++)
  {
    for(var x = 0, y = r.length; x < y; x++)
    {
      if(r[x]==a[i]) continue o;
    }
    r[r.length] = a[i];
  }
  return r;
};

  if(!Array.indexOf){
    Array.prototype.indexOf = function(obj){
      for(var i=0; i<this.length; i++){
      if(this[i]==obj){
        return i;
        }
      }
      return -1;
    };
  }
