$(document).ready(function(){
  $('#queryForm').dialog({ autoOpen: false,
                           title : 'Search Artists',
                           buttons: { "OK": function() { UVJ.searchArtists(parseArtistNames( $('#artistnames').val() )); $(this).dialog("close"); } }});

  $('#friendForm').dialog({ autoOpen: false,
                            width: '560px',
                            title : "Browse your Friends' Favorites"});


  $('#search').click(function(){
                       $('#queryForm').show();
                       $('#queryForm').dialog('open');
                     });
  $('#search').hide();
  $('#welcome-search').button().click(
    function(){UVJ.searchArtists(parseArtistNames( $('#welcome-artistnames').val() ));}
  );

  $('#videos').css({'height':$(document).height()});
  if( UVJ.onLoadSearch ){
    UVJ.searchArtists(UVJ.onLoadSearch);
  }else{
    UVJ.searchArtists([]);
  };
  FBC2.init();
});


FBC2.user.pic = function(size){
  if( !size ){
    size = 'square';
  }
  return "http://graph.facebook.com/"+this.id+"/picture?type="+size;
};

FBC2.user.renderBands = function(){
  $("#artistGrouping_u"+FBC2.user.id).remove();
  renderArtistsGrouping(FBC2.user.bands,
                FBC2.makeMenuArtistTitle(FBC2.user),
                "_u"+FBC2.user.id);
};

FBC2.init = function(){
  if( FBC2.user.id ){
    FBC2.user['pic_square'] = FBC2.user.pic();
    var user_box = document.getElementById("fb-login");
    user_box.innerHTML = "<div id='fb-login-userpic' class='fb-login-pic''>" + "<img src='"+FBC2.user.pic()+"'/></div>" +
      "Logged in as: "+FBC2.user.name+"</span><br/><a href='#' onclick='FBCLogout();'>Logout</a>";
    $("#fb_logout_image").show();
    $('#fb-login-userpic').click(FBC2.user.renderBands);
    $("#friends-icon").show();
  }
};

FBC2.PostStream = function(vidEntry){

  var media = {
    "type":"flash",
    "swfsrc" : vidEntry['flash_url'],
    "imgsrc" : vidEntry['thumbnails'][0],
    "width" : "130",
    "height" : "97",
    "expanded_width" : "480",
    "expanded_height" : "385"

    };

  FB.ui(
    {
      method:'stream.publish',
      message:'Check out this video',
      action_links : [{'text':"Be the VJ", 'href':'http://youvj.com'}],
      user_prompt_message: 'Share this video on your wall',
      attachment : { 'name': vidEntry['title'],
                 'href': ' http://youvj.com',
                 'caption': '{*actor*} found this music video',
                 'description': vidEntry['description'],
                 'media': [ media ]
                 }
    }
  );
};

FBC2.browseFriends = function(){
  if( FBC2.friends ){
    FBC2._browseFriends(FBC2.friends);
  }else{
    jsonPost('/fb_friends',
             {},
             function(resp){ FBC2._browseFriends(resp); }
    );
  }
};

FBC2._browseFriends = function(friends){
  $('#friendForm').empty();
  FBC2.friends = friends;
  var friendsList = $("<div class='friends'></div>");
  for( var i = 0; i < friends.length; i++ ){
    var friend = friends[i];
    friendsList.append(
        $("<div class='friend'></div>").append(
          $("<span class='name'>"+friend+"</span><br/>")
        ).click(
          function(f){return function(){
            UVJ.searchArtists([f]);
            $('#friendForm').dialog('close');
          };}(friend)
        )
      );
  }
  $('#friendForm').append(
    friendsList
  ).append(
    $("<br class='clear'/>")
  );

  $('#friendForm').show();
  $('#friendForm').dialog('open');
};

UVJ.searchInline = function(){
  var val = $("#inline-search")[0].value;
  if( val != $('#inline-search')[0].title ){
    UVJ.searchArtists([val]);
  }
  return false;

};

UVJ.searchArtists = function(artistNames){
  $('#header').show();
  $("#popup-welcome-border").hide();
  UVJ.searchArtists.list = unique(artistNames.concat(UVJ.searchArtists.list));
  $('#artistGroupingSearch').remove();
  var searchHeader = $('<span id="artist-search-header"></span>').append(
    $("<span class='medium'>Browse and Find</span>")
  ).append($("<form class='inline-search-box'></form>").append(
             $("<input class='default-text' type='text' id='inline-search' title='Artist Search'/>")
           ).append(
             $("<input type='submit' value='Find'/>")
           ).submit(function(e){ UVJ.searchInline(); })
  );

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
  if( !aid ){
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
  $('#artistlisting').prepend(artistGrouping);
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
              renderArtistsGrouping(f['artists'],
              FBC2.makeMenuArtistTitle(f));
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
    $('<div class="player-title">'+videoInfo['title']+'</div>')
  ).append(
    $('<div class="player-description">'+videoInfo['description']+'</div>')
  ).append($(''));
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
    $.post(path,
	   params,
	   function(resp){
	       try{
		   resp = eval("("+resp+")");
	       }catch(e){
                 alert(e);
               }
	       success(resp);
	   },
	   fail,
	   'json'
	   );
};


var old_browseFriends = function(pageNum){
  var pageSize = 9;
  try{
    pageNum = parseInt(pageNum);
    if( !pageNum ) pageNum = 0;
  }catch(e){
    pageNum = 0;
  }

  var maxPages = Math.floor(FBC2.friends.length / pageSize);
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
  for( var i = startIdx; i < FBC2.friends.length && i < startIdx+9; i++ ){
    var friend = FBC2.friends[i];
      friendsList.append(
        $("<div class='friend'></div>").append(
          $("<img src='"+friend['pic_square']+"' align='left'/>")
        ).append(
          $("<span class='name'>"+friend['name']+"</span><br/>")
        ).append(
          $("<span class='info'>"+friend['artists'].length+"</span>")
        ).click(
          function(f){return function(){
            renderArtistsGrouping(f['artists'], FBC2.makeMenuArtistTitle(f));
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

FBC.fbFriends = [];
FBC.session = {};

FBC2.makeMenuArtistTitle = function(f){
  return $('<span></span>').append(
  $("<img class='menu-artist-title-pic' align='left' src='"+f['pic_square']+"' alt='profile pic'/>")
  ).append(
    $("<div class='medium menu-artist-title-name'>"+f['name']+"</div>")
  );
};

var FBCLogin = function(){
  window.location.reload();
};

var FBCLogout = function(){
  FB.logout(function(response){ window.location.reload(); });
};

FBCGetFriends = function(callback){
  var api = FB.Facebook.apiClient;

  // require user to login
  api.requireLogin(function(exception) {
    FBC.session = api.get_session();
    // Get friends list
    api.friends_get(null, function(result) {
      result[result.length] = FBC.session.uid;
      FB.Facebook.apiClient.users_getInfo(result,
        ['name','pic_square','music'],
	function(res){
          FBC.owner = FBCGetFriends_parseUser(res[res.length-1]);
          FBC.fbFriends = [];
          res.length--;
          for( var i=0; i < res.length; i++ ){
            var friend_user = FBCGetFriends_parseUser(res[i]);
            if( friend_user ){
              FBC.fbFriends[FBC.fbFriends.length] = friend_user;
            }
          }
          FBC.fbFriends = FBC.fbFriends.sort(function(a,b){
            return b['artists'].length - a['artists'].length;
          });
          callback();
        });
      });
    });
};

FBCGetFriends_parseUser = function( res ){
  if( !res['music'] || res['music'].length == 0 ){
    return false;
  }
  var mFriend = {};
  mFriend['music_str'] = res['music'];
  mFriend['artists'] = parseArtistNames(res['music']);
  if( mFriend['artists'].length < 4 ){
    return false;
  }
  mFriend['name'] = res['name'];
  mFriend['pic_square'] = res['pic_square'];
  return mFriend;
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
                     'href': ' http://youvj.com',
                     'caption': '{*actor*} found this music video',
                     'description': vidEntry['description'],
                     'media': [ media ]
                   };
  var action_links = [{'text':"Be the VJ",
                       'href':'http://youvj.com'}];
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

