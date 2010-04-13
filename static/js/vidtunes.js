$(document).ready(function(){
  $('#queryForm').dialog({ autoOpen: false,
                           title : 'Search Artists',
                           buttons: { "OK": function() { renderArtists(parseArtistNames( $('#artistnames').val() )); $(this).dialog("close"); } }});

  $('#friendForm').dialog({ autoOpen: false,
                            width: '560px',
                            title : "Browse your Friends' Favorites"});


  $('#search').click(function(){
                       $('#queryForm').show();
                       $('#queryForm').dialog('open');
                     });
  $('#search').hide();
  $('#videos').css({'height':$(document).height()});
});

var renderSearch = function(){
  $('#queryForm').show();
  $('#queryForm').dialog('open');
};

var renderArtists = function(artistNames, headerElement){
  $('#artistlisting').empty();
  if( headerElement ){
    $('#artistlisting').append(headerElement);
  }
  for( var i = 0; i < artistNames.length; i++ ){
	var artistName = artistNames[i];
	var artistEntry = makeArtistMenuItem(artistName);
	$('#artistlisting').append(artistEntry);
  }
  $('#search').show();
  if($('#artistlisting a').length > 0){
    $($('#artistlisting a')[0]).click();
  }
};

var parseArtistNames = function(textVal){
  var splitNames = textVal.split(",");
  for( var i = 0; i < splitNames.length; i++ ){
	splitNames[i] = splitNames[i].trim();
  }
  return splitNames;
};

var makeArtistMenuItem = function(artistName){
    var artistDiv = $('<div class="menu-artist"></div>').append(
                      $('<div class="menu-artist-indicator">&#8594;</div>')).append(
                      $('<a href="#">'+artistName+'</a>'));
    artistDiv.click(function(e){
      loadVideos(artistName);
      loadSimilar(artistName);
      renderArtistBox(artistName);
      document.location.hash = artistName;
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
  for( i = 0; i < FBC.fbFriends.length; i++ ){
    var friend = FBC.fbFriends[i];
    var regexp = new RegExp(artistName,'i');
    if( regexp.test(friend['music_str'])){
      found++;
      var extraCls = "";
      if(found > friendLimit){
        extraCls = "extra-content";
      }
      $("#videoInfo-similar", artistBox).append(
          $("<a href='#' class='videoInfo-friend "+extraCls+"'>"+friend['name']+"</span>").click(

            (function(f){ return function(e){
              renderArtists(f['artists'],
              $('<div class="menu-artist-title">'+f['name']+'</div>'));
              return false;
            }; })(friend)
          )
        );
    }
  }
  if( found > 0 ){
    $("#videoInfo-similar", artistBox).prepend(
      $("<span class='videoInfo-friend'> &lt;3 by </span>")
    );

  }
  if( found > friendLimit ){
    $("#videoInfo-similar", artistBox).append(
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
           loadVideosCallback
          );
};

var loadVideosCallback = function(resp){
  $("#video-loader").hide();
  for( var i=0; i < resp[0].length; i++){
    renderVideo(resp[0][i]).insertBefore($("#similar-artist-divider"));
  }
  if( resp[0].length == 0 ){
    $("<div class='message'>Sorry, nothing found.</>").insertBefore($("#similar-artist-divider"));
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
  $('a',vid).click(function(){renderPlayer(videoInfo);});
  $('.screencaps',vid).click(function(){renderPlayer(videoInfo);});
  $('a',vid).button();
  return vid;
};

var loadSimilar = function(artistName){
  $('.similar-artist').remove();
  jsonPost('/findsimilar',
           {'artist':artistName},
           loadSimilarCallback
          );
};

var loadSimilarCallback = function(resp){
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
                               renderArtistBox(pairing[0]);
                               document.location.hash = pairing[0];
                             });
  return(similarArtist);
};

var renderPlayer = function(videoInfo){
  purl = videoInfo['flash_url'];
  purl += '&autoplay=1';
  var pstr = '<object width="480" height="385">'
    + '<param name="movie" value="'+purl+'"></param>'
    + '<param name="allowFullScreen" value="true"></param>'
    + '<param name="allowscriptaccess" value="always"></param>'
    + '<embed src="'+purl+'" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed>'
    + '</object>';
  $('#featureVideo').html(pstr);
  $('#featureVideo').show();
  $('#featureVideo').append(
    $('<div class="player-title">'+videoInfo['title']+'</div>')
  ).append(
    $('<div class="player-description">'+videoInfo['description']+'</div>')
  ).append(
    $('<a href="#">Post to Facebook</a>').click(
      function(){ FBCPostStream(videoInfo); }
    )
  ).append($(''));
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

var browseFriends = function(pageNum){
  var pageSize = 9;
  try{
    pageNum = parseInt(pageNum);
    if( !pageNum ) pageNum = 0;
  }catch(e){
    pageNum = 0;
  }

  var maxPages = Math.floor(FBC.fbFriends.length / pageSize);
  var navigationList = $('<div class="navigation"></div>');
  for( var page = 0; page < maxPages; page++ ){
    if( page != pageNum ){
      navigationList.append(
        $("<a href='#'>"+page+"</a>").click(
          function(p){ return function(){ browseFriends(p); }; }(page)
        )
      );
    }else{
      navigationList.append(
        $("<span>"+page+"</span>")
      );
    }
  }
  var startIdx = pageSize * pageNum;
  $('#friendForm').empty();
  var friendsList = $("<div class='friends'></div>");
  for( var i = startIdx; i < FBC.fbFriends.length && i < startIdx+9; i++ ){
    var friend = FBC.fbFriends[i];
      friendsList.append(
        $("<div class='friend'></div>").append(
          $("<img src='"+friend['pic_square']+"' align='left'/>")
        ).append(
          $("<span class='name'>"+friend['name']+"</span><br/>")
        ).append(
          $("<span class='info'>"+friend['artists'].length+"</span>")
        ).click(
          function(f){return function(){
            renderArtists(f['artists'], $('<div class="menu-artist-title">'+f['name']+'</div>'));
            $('#friendForm').dialog('close');
          };}(friend)
        )
      );
  }
  $('#friendForm').append(
    friendsList
  ).append(
    $("<br class='clear'/>")
  ).append(
    navigationList
  );

  $('#friendForm').show();
  $('#friendForm').dialog('open');
};

FBC = {};

FBCLogout = function(){
  FB.Connect.logout(function() { reload();  });
};

FBCLogin = function(){
  var user_box = document.getElementById("header");
  // add in some XFBML. note that we set useyou=false so it doesn't display "you"
  user_box.innerHTML = "<span>" + "<fb:profile-pic uid='loggedinuser' facebook-logo='true'></fb:profile-pic>" +
  "Welcome, <fb:name uid='loggedinuser' useyou='false'></fb:name>." +
  "</span>";
  FB.XFBML.Host.parseDomTree();
  $("#fb_logout_image").show();
  FBCGetFriends( function(){
		   $('.artists-menu-friends').css({'display':'inline-block'});
  });

};

FBCGetFriends = function(callback){
  var api = FB.Facebook.apiClient;

  // require user to login
  api.requireLogin(function(exception) {
    // Get friends list
    api.friends_get(null, function(result) {
      FB.Facebook.apiClient.users_getInfo(result,
        ['name','pic_square','music'],
	function(res){
          FBC.fbFriends = [];
          for( var i=0; i < res.length; i++ ){
            if( !res[i]['music'] || res[i]['music'].length == 0 ){
              continue;
            }
            var mFriend = {};
            mFriend['music_str'] = res[i]['music'];
            mFriend['artists'] = parseArtistNames(res[i]['music']);
            if( mFriend['artists'].length < 4 ){
              continue;
            }
            mFriend['name'] = res[i]['name'];
            mFriend['pic_square'] = res[i]['pic_square'];
            FBC.fbFriends[FBC.fbFriends.length] = mFriend;
          }
          FBC.fbFriends = FBC.fbFriends.sort(function(a,b){
            return b['artists'].length - a['artists'].length;
          });
          callback();
        });
      });
    });
};

FBCPostStream = function(vidEntry){

  var media = {
    "type":"flash",
    "swfsrc" : vidEntry['flash_url'],
    "imgsrc" : vidEntry['thumbnails'][0],
    "width" : "130",
    "height" : "97",
    "expanded_width" : "480",
    "expanded_height" : "385"

    };

  var message = 'Check out this video';
  var attachment = { 'name': vidEntry['title'],
                     'href': ' http://notphil.com:8080',
                     'caption': '{*actor*} found this video',
                     'description': vidEntry['description'],
                     'properties': {
                       'category': {
                         'text': vidEntry['artist'],
                         'href': 'http://notphil.com:8080#'+vidEntry['artist']}
                       },
                     'media': [ media ]
                   };
  var action_links = [{'text':'Find music videos',
                       'href':'http://notphil.com:8080'}];
  FB.Connect.streamPublish(message, attachment, action_links);
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
