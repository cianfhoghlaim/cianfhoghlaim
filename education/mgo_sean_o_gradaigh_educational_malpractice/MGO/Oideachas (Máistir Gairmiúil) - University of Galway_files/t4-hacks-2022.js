//  Norbert @ RMG, 2015/01/21
//  Luca @ RMG, 2015/01/27
 
//  This files holds JS scripts that are:
//  1. specific to Terminal4
//  2. needed for old content to work under the new template (eventually to be removed as old content is replaced).
//  3. scripts brought from the old site (Evan's)
//  4. specific to the 2020 cookie manager 

	//=================================================
	//Cookie Manager Variables & Functions
	//Evan Ryder - Sep 2020
	//=================================================
	var consentExpiry = 182.5; // 6 months 
	var JSCC_CurrentPath = document.URL.replace(/^https?\:\/\/[^\/]*/i,"");

	function JSCC_GetCookie(name) {
		var nameEQ = name + "=";
		var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') {
				c = c.substring(1,c.length);
			}
			if (c.indexOf(nameEQ) == 0) {
				return c.substring(nameEQ.length,c.length);
			}
		}
		return null;
	}

	function JSCC_SetCookie(name, value, days) {
			if (days) {
			var date = new Date();
			date.setTime(date.getTime() + (days * 24 * 60 * 60 *1000));
			var expires = "; expires=" + date.toGMTString();
		} else {
			var expires = "";
		}
		document.cookie = name + "=" + value + expires + "; path=/";
	}

	function JSCC_DeleteCookie(name)
	{
	   var now = new Date();
	   var subdomain = document.location.host; //e.g. mri.nuigalway.ie
	   var host  = document.location.host.substring(document.location.host.indexOf('.')+1); //nuigalway.ie
	   var domain = "www." + host;
	   now.setTime(now.getTime()-(24*60*60*1000));
	   var exp = now.toGMTString();
           //subdomains could be in use so delete the domain in use, AND the normal domain, AND its short version
	   //e.g. mri.nuigalway.ie, www.nuigalway.ie, nuigalway.ie
	   //specify common paths ([blank], /, current path) to be sure all are deleted
	   //some cookies put a dot on front of the domain so delete both
	   document.cookie = name + "=;path=;expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + "; expires=" + exp;
	   document.cookie = name + "=;path=/;expires=" + exp;
	   //current subdomain name with a . on front of it
	   document.cookie = name + "=;path=;domain=."+subdomain+";expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + ";domain=."+subdomain+";expires=" + exp;
	   document.cookie = name + "=;path=/;domain=."+subdomain+";expires=" + exp;
           //.www.nuigalway.ie
	   document.cookie = name + "=;path=;domain=."+domain+";expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + ";domain=."+domain+";expires=" + exp;
	   document.cookie = name + "=;path=/;domain=."+domain+";expires=" + exp;
           //www.nuigalway.ie
	   document.cookie = name + "=;path=;domain="+domain+";expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + ";domain="+domain+";expires=" + exp;
	   document.cookie = name + "=;path=/;domain="+domain+";expires=" + exp;
           //.nuigalway.ie
	   document.cookie = name + "=;path=;domain=."+host+";expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + ";domain=."+host+";expires=" + exp;
	   document.cookie = name + "=;path=/;domain=."+host+";expires=" + exp;
           //nuigalway.ie
	   document.cookie = name + "=;path=;domain="+host+";expires=" + exp;
	   document.cookie = name + "=;path="+JSCC_CurrentPath + ";domain="+host+";expires=" + exp;
	   document.cookie = name + "=;path=/;domain="+host+";expires=" + exp;
	   return;
	}

	function JSCC_DeleteAllCookies(namestr)
	{
	   	var ca = document.cookie.split(';');
		for(var i=0;i < ca.length;i++) {
			var c = ca[i].split('=');
			if (namestr == null || namestr == '') {
				JSCC_DeleteCookie(c[0]);
			} else {
				if (c[0].indexOf(namestr) > -1) JSCC_DeleteCookie(c[0]);
			}
		}
		return;
	}

	function JSCC_Decode(text) {
	  var decodedText = decodeURI(text);
	  var doubleDecodedText = "";
	  try {
	    doubleDecodedText = decodeURIComponent(decodedText);
	  } catch(e) {
	    return(decodedText);
  	  }
	  return(doubleDecodedText);
	}

	function JSCC_ShowAllCookies(filter, note, targetID, overwrite) {
          overwrite = overwrite || false;
          var info = "";
          var label = "";
          if (note != '') label = "(" + note + ") ";
          if (targetID != null && targetID != '') {
                var ca = document.cookie.split(String.fromCharCode(59));
                for(var i=0;i < ca.length;i++) {
                        var c = ca[i].split('=');
                        if (filter == null || filter == '') {
                                info += '<em>' + c[0] + '</em> ' + label + '= ' + decodeURI(c[1]) + '<br>';
                        } else {
                                if (c[0].indexOf(filter) > -1) info += '<em>' + c[0] + '</em> ' + label + '= ' + JSCC_Decode(c[1]) + '<br>';
                        }
                }
                var target = document.getElementById(targetID);
                if (overwrite == true && target) { target.innerHTML = ""; }
                if (target && info != "") {
                        if (overwrite == true) { target.innerHTML = info; } else { target.innerHTML += info; }
                }
          }
          return;
        }

	function allowSelected() {
	  var cookieValue = "";
	  //Functionality
	  if ($('#func:checked').length > 0) {
		cookieValue="yes";
	  } else {
		cookieValue="no";
		JSCC_DeleteAllCookies('pubble');
		JSCC_DeleteAllCookies('watchedVids');
		JSCC_DeleteAllCookies('CMSdigitalBadge');
		JSCC_DeleteAllCookies('Recite.Persist');
		//JSCC_DeleteAllCookies('AWSALBCORS');
		//JSCC_DeleteAllCookies('AWSALB');
	  }
	  JSCC_SetCookie('func', cookieValue, consentExpiry);

	  //Analytics
	  if ($('#anal:checked').length > 0) {
		cookieValue="yes";
	  } else {
		cookieValue="no";
		JSCC_DeleteAllCookies('_ga');
		JSCC_DeleteAllCookies('_gid');
		JSCC_DeleteAllCookies('AMP_TOKEN');
		JSCC_DeleteAllCookies('_gtm');
		JSCC_DeleteAllCookies('__utm');
		JSCC_DeleteAllCookies('_hj');
		JSCC_DeleteAllCookies('ln_or');
	  } 
	  JSCC_SetCookie('anal', cookieValue, consentExpiry);

	  //Ads (Marketing)
	  if ($('#ads:checked').length > 0) {
		cookieValue="yes";
	  } else {
		cookieValue="no";
		JSCC_DeleteAllCookies('__ar_v4');
		JSCC_DeleteAllCookies('__adroll');
		JSCC_DeleteAllCookies('_gcl_au');
		JSCC_DeleteAllCookies('_scid');
		JSCC_DeleteAllCookies('_fbp');
		JSCC_DeleteAllCookies('sa-user-id');
		JSCC_DeleteAllCookies('_ttp');
		JSCC_DeleteAllCookies('_tt_enable_cookie');
	  }
	  JSCC_SetCookie('ads', cookieValue, consentExpiry);

	  //Preferences
	  if ($('#pref:checked').length > 0) {
		cookieValue="yes";
	  } else {
		cookieValue="no";
		JSCC_DeleteAllCookies('Recite.Preferences');
	  }
	  JSCC_SetCookie('pref', cookieValue, consentExpiry);

	  JSCC_SetCookie('consent', 'yes', consentExpiry);
	  location.reload(); //reload page so you'll see previously suppressed content
	}

	function allowAll() {
	  JSCC_SetCookie('pref', 'yes', consentExpiry);
	  $( "#pref" ).prop( "checked", true );
	  JSCC_SetCookie('anal', 'yes', consentExpiry);
	  $( "#anal" ).prop( "checked", true );
	  JSCC_SetCookie('ads', 'yes', consentExpiry);
	  $( "#ads" ).prop( "checked", true );
	  JSCC_SetCookie('func', 'yes', consentExpiry);
	  $( "#func" ).prop( "checked", true );
	  JSCC_SetCookie('consent', 'yes', consentExpiry);
	}

	function allowNone() {
	  JSCC_DeleteCookie('pref');
	  $( "#pref" ).prop( "checked", false );
	  JSCC_DeleteCookie('anal');
	  $( "#anal" ).prop( "checked", false );
	  JSCC_DeleteCookie('ads');
	  $( "#ads" ).prop( "checked", false );
	  JSCC_DeleteCookie('func');
	  $( "#func" ).prop( "checked", false );
	  JSCC_DeleteAllCookies();
	  JSCC_SetCookie('consent', 'yes', consentExpiry);
	  location.reload(); //reload page so you'll see the content is now suppressed
	}

	function checkCookieBoxes() {
	  // select any relevant checkboxes
	  if (consentPrefs) $( "#pref" ).prop( "checked", true );
	  if (consentAnalytics) $( "#anal" ).prop( "checked", true );
	  if (consentMarketing) $( "#ads" ).prop( "checked", true );
	  if (consentFunctionality) $( "#func" ).prop( "checked", true );
	}

	function toggleCookieInfo() {
console.log('toggling cookie banner');
	  // hide the global navigation (instead of moving it down) 
	  //$('#globalNavigation').toggle();
	  if ($('.cookie-info').css("display") == 'none') {
	    //banner is about to be made visible, so move the floated links down
	    let cookieMsgPos = $('.cookie-info').css("top").replace("px","");
	    let cookieMsgHeight = $('.cookie-info').height();
	    let newTop = 69 + cookieMsgHeight + parseInt(cookieMsgPos);
	    let newVal = newTop.toString() + "px";
	    $('#globalNavigation').css("top", newVal); 
	  } else {
	    $('#globalNavigation').css("top", "77px"); 
	  }
	  // Cookie banner appears below the utility nav: 33px down. If the Jump to Content links are visible, bring it down another 20 px 
	  if ($('#utilityNavigation').css("top") == "20px") { $('#cookie-info').css("top", "53px"); }
	  $('.cookie-info').slideToggle('slow');
	  checkCookieBoxes();				
	  if ($('.cookie-info').is(":visible")) $("#consentAll").focus();
	}

	var consentPrefs = (JSCC_GetCookie('pref') == 'yes');
	var consentAnalytics = (JSCC_GetCookie('anal') == 'yes');
	var consentMarketing = (JSCC_GetCookie('ads') == 'yes');
	var consentFunctionality = (JSCC_GetCookie('func') == 'yes');
	var consent = JSCC_GetCookie('consent');
	var consentGiven = (consent != null && consent != '');

function accessibilityFix() {
  //delayed - runs 2.5 secs after page load to catch js-created iframes
  console.log('Accessibility: Fixing 3rd-party JS-generated iframes');
  $('iframe[style*="display: none"').attr('aria-hidden', 'true');
	
	// Fix Home links on subsites
	var homeBCLink = document.querySelector("div.breadcrumb > a[href='/']");
	if (homeBCLink) { 
		homeBCLink.ariaLabel = "Home"; 
		console.log("Fixed breadcrumb home link"); 
	}
  return;
}

//functions to set tab order - used by accordions 
var tabIdx = -2; //global var. -2 means not set 
  
function getTabIdx() { 
  var tabIdxs = document.querySelectorAll('[tabindex]'); 
  if (tabIdxs) { 
    let max = -1; 
    for (i=0; i<tabIdxs.length; i++) { 
      if (tabIdxs[i].tabIndex > max) { 
        max = tabIdxs[i].tabIndex; 
        console.log(tabIdxs[i].tagName + ' ' + tabIdxs[i].tabIndex); 
      } 
    } 
    tabIdx = max + 1; 
  } 
} 
  
function setTabIndexes(selector, staticVal="auto") { 
  if (staticVal == "auto" && tabIdx == -2) getTabIdx(); 
  var attr = null; 
  let els = document.querySelectorAll(selector); 
  if (els.length > 0) { 
    for (i=0; i<els.length; i++) { 
      attr = els[i].getAttribute('tabindex'); 
      let styles = window.getComputedStyle(els[i]); 
      if (styles.display !== 'none' && styles.visibility !== 'hidden' && (attr == "" || attr == null)) { 
        if (staticVal == "auto") {  
          els[i].setAttribute('tabindex', tabIdx++);  
        } else { 
          els[i].setAttribute('tabindex', staticVal);  
        } 
      } 
    } 
  } 
} 
// end tab order functions 

String.prototype.replaceArrays = function(find, replace) {
  var replaceString = this;
  for (var i = 0; i < find.length; i++) {
    replaceString = replaceString.replace(find[i], replace[i]);
  }
  return replaceString;
};

function revealKBNav() {
 var utilityNav = document.getElementById('utilityNavigation');
 var globalNav = document.getElementById('globalNavigation');
 var keybNav = document.getElementById('keyboardNav');
 utilityNav.style.top="20px"; 
 globalNav.style.top="97px";
 keybNav.style.height = "20px";
 //make the links absolute
 j2c.src = document.location.href + j2c.src;
 bClass = document.body.className;
 if (bClass.indexOf('courseDetailPage') == -1 && bClass.indexOf('fullWidth') == -1 && bClass.indexOf('gatewayPage') == -1) {
  //page has a left-nav.  Nav Link goes to #side-nav and is hidden by default
  //find the label of hte sidenav and change the link if necessary
  var sideNav = document.getElementById('#side-nav');
  if (!sideNav || sideNav == null) {
    let nav = document.querySelector('div#secondaryNavigationWrapper > ul');
	if (nav && nav.id) {
 	  j2s.href = "#" + nav.id
    }
  }
  j2s.style.display="inline-block";
 }
}

$(document).ready(function() {
	
	//====================
	// Accessibility Fixes
	// ===================
	/* Enable Keyboard Navigation */
	var j2c = document.getElementById('j2c');
	var j2s = document.getElementById('j2s');
	if (j2c && j2c != null) j2c.addEventListener('focus', revealKBNav);
	if (j2s && j2s != null) j2s.addEventListener('focus', revealKBNav);
        //fix common errors
	$('p,h2').removeAttr('align');  
  	$("#fancybox-left").attr("aria-label","Left Arrow"); 
	$("#fancybox-right").attr("aria-label","Right Arrow"); 
	// add a title to iframes if not there already AND no aria-label defined
	var iframes = document.querySelectorAll("iframe");
	var newTitle = "";
	if (iframes.length > 0) {
	  let changeCnt = 0;
	  for (i=0; i<iframes.length; i++) {
	    	var title = iframes[i].title;
		var ssrc = iframes[i].src;
		if (ssrc != null && (title == null || title == "")) {
		  var ariaLabel = iframes[i].ariaLabel;
		  if (ariaLabel == null || ariaLabel == "") {
			//needs a title
			newTitle = "";
			if (ssrc.indexOf('facebook') > -1) {  newTitle = "Facebook Feed"; changeCnt++; }
			if (ssrc.indexOf('calendar') > -1 || ssrc.indexOf('dialann') > -1) {  newTitle = "Calendar of Events"; changeCnt++; }
			if (ssrc.indexOf('shorthand') > -1) { newTitle = "Article"; changeCnt++; }
			if (ssrc.indexOf('snapwidget') > -1) { newTitle = "Instagram photos"; changeCnt++; }
			if (ssrc.indexOf('youtube') > -1) { newTitle = "YouTube video"; changeCnt++; }
			if (ssrc.indexOf('kaltura') > -1) { newTitle = "Embedded video"; changeCnt++; }
	       		if (newTitle != "") {
			  iframes[i].title = newTitle;
			  changeCnt++;
			}
		  }
		}
	  }
	  if (changeCnt > 0) console.log('Accessibility: Added titles to ' + changeCnt + ' iframes');
	}
	// add an aria-label to links containing spans (if not there already)
	var linkSpans = document.querySelectorAll('a>span');
	if (linkSpans && linkSpans != null) {
		let changeCnt = 0;
		for (i=0; i<linkSpans.length; i++) {
			let parentLink = linkSpans[i].parentElement;
			if (parentLink.ariaLabel == null || parentLink.ariaLabel == "") {
				parentLink.ariaLabel = linkSpans[i].innerText.replace(/\&nbsp;/gi, " ");
				changeCnt++;
			}
		}
		console.log('Accessibility: Added aria-label to ' + changeCnt + ' links');
	}
	// Make links to new tabs say so in their title
	var newTabLinks = document.querySelectorAll("a[target='_blank']");
	for (i=0; i<newTabLinks.length; i++) { 
		newTabLinks[i].title += " (opens in a new tab)";	
	}
	// remove any links that contain only <br> and/or &nbsp;
	var unlabelledLinks = document.querySelectorAll('a:not(a [aria-label])');
	if ( unlabelledLinks && unlabelledLinks != null ) {
		var aSearch = [" ", "&nbsp;", "<br>"];
		var aReplace = ["", "", ""];
		let removeCnt = 0;
		for (i=0; i < unlabelledLinks.length; i++ ) {
			if (unlabelledLinks[i].innerHTML.replaceArrays(aSearch, aReplace) == "") {
				let sAnchorName = unlabelledLinks[i].name;
                                let sAnchorID = unlabelledLinks[i].id;
                                //if it has no name AND no ID, its not an anchor - it's just a text-less link, so remove it.
				if ((sAnchorName == '' || sAnchorName == null) && (sAnchorID == '' || sAnchorID == null)) {
					unlabelledLinks[i].remove();
					removeCnt++;
				}
			}
		}
		console.log('Accessibility: Removed ' + removeCnt + ' empty links ');
	}

	setTimeout('accessibilityFix()', 2500);

	//$('#search').hide();
        if (document.body.className.indexOf('noReplace') < 0) {	
	  replaceInContent("(National University of Ireland|NUI),? Galway", "University of Galway", false); 
	  replaceInContent("(Ollscoil na h.ireann|OE|O.),? Gaillimh", "Ollscoil na Gaillimhe", false);
	  //replaceInLinks('nuigalway.ie','universityofgalway.ie');
	  replaceInLinks('oegaillimh.ie','ollscoilnagaillimhe.ie');
	}

	// loop through all downloads - if the link's href contains a full link (this happens when a media item
	// is inserted), change it to just the URL
	var dls = document.querySelectorAll("ul.downloadList a");
	if (dls.length > 0) {
	  for (i=0; i<dls.length; i++) {
	    var linkHTML = dls[i].href;
 	    if (linkHTML.indexOf("%22") > -1) {
	        console.log("fixing download link: " + dls[i].href);
		var start = linkHTML.indexOf('%22')+3;
	      	var end = linkHTML.lastIndexOf('%22');
	      	var url = linkHTML.substr(start, end - start);
	      	dls[i].href=url;
	    }
	  }
	}
	 // Evan's code brought from the old site

	//=================================================
	//Enable local onLoad() functions in pages
	//Evan Ryder - Dec 2009
	//=================================================
	//If a function called onLoad() exists in the current page, run it automatically
	try {
	//if (window.onLoad())
	            onLoad();
	} catch (exception) {
	  //do nothing
	}


        //=========================================================
        //Toggle hidden spans inside anything with class rightclick
        //Evan Ryder - May 2020
        //=========================================================
        $(".rightclick").mousedown(function(event) {
    	  switch (event.which) {
            case 3:
              event.preventDefault();
              $(this).find(".hidden").toggle();
              break;
            default:
              break;
          }
        });

	//=================================================
	//Setup Cookie Manager
	//Evan Ryder - Sep 2020
	//=================================================
	  if (!consentGiven) toggleCookieInfo();
	  // event listeners for cookie form buttons
	  $( "#consentSome" ).click(function() { allowSelected(); });
	  $( "#consentNone" ).click(function() { allowNone(); });
	  $( "#consentAll" ).click(function() {  allowAll(); });
	  $( "#recommendedCookies" ).click(function(e) { e.preventDefault(); allowAll(); toggleCookieInfo(); });
	  // Create Ctrl-M / Cmd-M toggle for cookie manager
	  $(document).keydown(function(e) {
	    if((e.ctrlKey || e.metaKey) && e.which == 77) { e.preventDefault(); toggleCookieInfo(); }
	  });

	 // add missing span
	 
	$('#primaryNavigation div.dropdown a').wrapInner('<span></span>');
	$('#collegePageButtonNavigation ul a ').wrapInner('<span></span>');
	
	$('div.footerNews div.columnOne').last().removeClass('columnOne').addClass('columnThree');
	
	 // fixes to breadcrumb
	 
	if($('div.breadcrumb > a').length > 1) {
		var lastItem = $('div.breadcrumb > a').last(),
			lastItemLabel = lastItem.text();
		lastItem.remove();
		$('div.breadcrumb').append('<span class="last">' + lastItemLabel + '</span>');
		$('div.breadcrumb span.path_delimiter.last').html('<span class="chevron">▻</span>');
	}
	
	 // remove public-sites, staff-sites, student-sites, research-sites from breadcrumb
	 
	$('div.pageHeader div.breadcrumb a[href$="-sites/"]').each(function () {
		$(this).prev().remove(); //path_delimiter
		$(this).remove();
	});
	$('div.pageHeader div.breadcrumb a[href*="oegaillimh/suiomh"]').each(function () {
		$(this).prev().remove(); //path_delimiter
		$(this).remove();
	});

	 // remove the doubled home link in the breadcrumb
	var homeLinks = $('div.pageHeader div.breadcrumb a[href="/"]');
	if (homeLinks.length == 2) {
		homeLinks.each(function(index) {
			if (index == 0) {
				$(this).next().remove();
				$(this).remove();
			}
			if (index == 1) {
				$(this).wrapInner('<span/>');
			}
		});
	}
	// remove doubled chevron that occurs if something in, say, public-sites, is published to /something
	if ($('div.breadcrumb a').length < $('div.breadcrumb span.chevron').length) $('div.breadcrumb span.path_delimiter.last').remove();
	
	//$('#secondaryNavigation li span.currentbranch0').parent().addClass('active');

	// Fix margin on .Content-box elements
	$('.Content-box').each(function() {
	  $(this).parent().css('margin', 0);
	});

	// Wrap boxes in right column	
	$('#pageRightColumnWrapper > .section').each(function() {
	  $(this).addClass('box');
	});

	// Move #pageRightColumn content to the left column when .fullContentWidth is set
	// if ($(document.body).hasClass("fullContentWidth") && $('#pageRightColumnWrapper').children().length) {
	// 	$("#pageSideContentWrapper").append($('#pageRightColumnWrapper').contents().detach());
	// }
	
	// T4 horizontal tabs
	$('ul.tabbed-content').closest('#pageContentWrapper').easytabs({
	  'tabs': 'ul.tabbed-content > li',
	  'updateHash': true,
	  'animate': false
	});
	//make the tabs not scroll when you click on them
	var tabScrollPoint = null;
	$('ul.tabbed-content').closest('#pageContentWrapper').bind('easytabs:before', function() {
	    tabScrollPoint = $(document).scrollTop();
	  });
	$('ul.tabbed-content').closest('#pageContentWrapper').bind('easytabs:after', function() {
            $("body,html").animate({ scrollTop: tabScrollPoint }, 0);
	  });

	// Move boxes at the bottom of content to the #pageSideContentWrapper
	$('#pageContentWrapper > .boxes-bottom').appendTo('#pageRightColumnWrapper');

	// Make sure boxes are stacked beside each other on tablet
	$("#pageRightColumnWrapper div.box").filter(":odd").addClass("node-item_right");
	$("#pageRightColumnWrapper div.box").filter(":even").addClass("node-item_left");

	// Add open to secondary navigation
	$('#secondaryNavigation li span.currentbranch0, #secondaryNavigation li span.currentbranch1').parent("li").addClass("open");

	// Hide empty list items
	$('div.call-to-action li > div:not(:visible)').parent().hide();

	// Init Cycle2 gallery for Image Slider
	$('div#home-page-feature-pager > div#pager-wrapper').remove();
	$('div#home-page-feature-pager > div').addClass("slide");
	$('div#home-page-feature-pager').append('<div class="pager"></div>');
	$('div#home-page-feature-pager').cycle({
		slides: "> .slide",
		swipe: true,
		pager: "> .pager",
		pagerTemplate: '<a href=#> {{slideNum}} </a>',
		log: false
	});

	// News section hacks
	var newsItems = $(".newslist-item");
	if (newsItems.length > 0) {
		var parent = newsItems.parent();
		if (!parent.hasClass("newsList")) {
			parent.addClass("newsList");
			var body = $(document.body);
			if (body.hasClass("article")) body.removeClass("article newsPage");
		}
	}

	 // Centre image on content boxes
	$("#pageRightColumn div.section.box p img").closest('p').css("text-align", "center");

	 // Staff pages (such as /our-research/people/business-and-economics/tonydundon/)

	// remove empty titles
	$('#rms-centre h3').each(function() {
		var el = $(this);
		if (jQuery.trim(el.text()).length == 0) el.remove(); 
	});
	// remove whitespace from tabs
	$('#rms-centre > div > div').each(function() {
		var el = $(this);
		var content = el.html();
		el.html(jQuery.trim(content.replace(/&nbsp;/g, " ")));
	});
	// move staff picture into the contact details
	$('#rms-centre #va_contact_outer #va_contact_inner > table > tbody > tr > td').append($('#rms-centre #va_contact_outer #va_contact_inner + div').detach());
	// remove extra images for staff with more than one profile
	$('#rms-centre #va_contact_outer #va_contact_inner > table > tbody > tr > td img').not(':first').remove();
	// wrap all sections in divs
	$('#rms-centre h3').each(function() {
		var el = $(this);
		var content = el.nextUntil("h3");
		content.wrap('<div class="section"></div>');
	});
	// put tab names as h2
	$('#rms-centre > div > div').each(function() {
		var el = $(this);
		var title = el.attr("title");
		if (title && title.length > 0 && title != 'Home') el.prepend("<h2>" + title + "</h2>");
	});
	// init acordeon
	$('#rms-centre h3 ~ div.section').hide();
	$('#rms-centre #va_contact_inner h3').addClass("open");
	$('#rms-centre #va_contact_inner h3 ~ div.section').show();
	$('#rms-centre h3').on('click', function(e) {
		$(this).toggleClass('open').next('div.section').slideToggle();
	});

	//=================================================
//		Light box gallery
//		See details & options at http://fancybox.net/
//	=================================================
	
	if ($("a.gallery").length) {
		$("a.gallery").fancybox({ 
				transitionIn: "elastic", 
				transitionOut: "elastic"
    	});
		$("div.imageGallery a.gallery:not(.fancyImage)").fancybox({'type': 'image'});
	};

	 // Some videos to be run inside FancyBox
	try {
	  $(".fancyYoutube").fancybox({ type: 'iframe', width: 800, height: 460 });
	} catch(e){
          console.log("error: "+e);	
	}

	// convert youtube links into an embed type to allow iframing
	$(".fancyYoutube").each(function() {
		var framed = $(this).attr("href").replace("//www.youtube.com/watch?v=", "//www.youtube.com/embed/").replace("&feature=plcp", '');
		framed += "?autoplay=1&origin=" + window.location.hostname;
		$(this).attr("href", framed);
	});

	//=================================================
//		Image Carousel
//	=================================================

	if ($("#mycarousel").length) {
		$('#mycarousel').jcarousel({
			scroll: 7
		});
//console.log('configured jcarousel');
	};
//console.log('page setup completed');

	//===================================================
	//      Top Menu
	//===================================================
	const d8 = new Date();
	var d8mth = d8.getMonth()+1;
	var d8day = d8.getDate;
	var d8dayOfWeek = d8.getDay();
	//Move exams links to top of student dropdown list at exam time
	if (d8mth > 3 && d8mth < 7 ) {
	  $("div.dropdown a[href*='exam']").addClass('featured');
	}
	//Move registration links to top of student dropdown list in August
	if (d8mth == 8) {
	  $("div.dropdown a[href*='reg']").addClass('featured');
	}
	//move featured ones to top of list
	$("a.featured").parent().each(function() {
	  $(this).parent().prepend(this);
	});

        //====================================================
        //        IRIS PRofiles
        //====================================================
  	//if its an IRIS profile, change the IRIS image srcs so that the public can see them
  	if (document.location.href.indexOf('our-research/people/') > 0) {
  	  replaceInImages('iris.nuigalway.ie', 'irispublic.nuigalway.ie');
  	}

//==============================================
//	Forms & Validation
//	
//	The validate jQuery plugin is used here.
//	Find the relevant documentation here:
//	
//	Home Page with demos
//	http://docs.jquery.com/Plugins/Validation
//	
//	Plugin Options
//	http://docs.jquery.com/Plugins/Validation/validate#toptions
//	
//	Documentation
//	http://bassistance.de/jquery-plugins/jquery-plugin-validation/
//	Lots more demos
//	http://jquery.bassistance.de/validate/demo/
//	
//==============================================


if ($("#OrderProspectus").length) {
	
	$("#OrderProspectus").validate({

	//Normally and error class is added to the input element - I'm adding it to the parent div
	//so we can show our error cross
		highlight: function(element, errorClass) {
     	$(element).parent().parent().addClass(errorClass);
  		},
  		unhighlight: function(element, errorClass) {
     	$(element).parent().parent().removeClass(errorClass);
	  	},
		

	//Create an error container with an unordered list

		errorContainer: "#error-list",
		errorLabelContainer: $("#error-list ul"),
		wrapper: 'li',

	//The default will put focus on the first erroneous input. I wish to disable this function.
	//If there are errors, I wish to scroll to the error container instead

		focusInvalid: false,
		
		invalidHandler: function(form, validator) {
      var errors = validator.numberOfInvalids();
      if (errors) {
        window.location.hash = '#error-anchor';
      }
    },

	//Here are our field rules and their corresponding messages

		rules: {
			t4_content_element_ProspectusType: {required:true},
			t4_content_element_FirstName: "required",
			t4_content_element_LastName: "required",
			t4_content_element_Address1: "required",
			t4_content_element_Country: "required",
						
			t4_content_element_Email: {
				required: true,
				email: true
			},
			t4_content_element_ConfirmEmail: {
				required: true,
				email: true,
				equalTo: "#t4_content_element_Email"
			},
			t4_content_element_ContactPhoneNumber: {
				required: true
			},			
			
			t4_content_element_SchoolCollegeName: {
				required: true
			},						
			
			t4_content_element_SchoolAddress1: {
				required: true
			},				
			t4_content_element_SchoolCountry: {
				required: true
			},									
			t4_content_element_Agree: "required"
		},
		messages: {
			t4_content_element_ProspectusType: {
				required: "Please select the prospectus you would like sent"
			},
			t4_content_element_FirstName: "Please enter your First Name",
			t4_content_element_LastName: "Please enter your Last Name",			
			t4_content_element_Address1: "Please enter your Address",
			t4_content_element_Country: "Please enter your Country",
			t4_content_element_Email: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com"
			},
			t4_content_element_ConfirmEmail: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com",
				equalTo: "Confirm Email and Email should be the same"
			},
			t4_content_element_Country: "Please enter your Country",
			t4_content_element_ContactPhoneNumber: "Please provide a Contact Phone Number",						
			t4_content_element_SchoolCollegeName: "Please provide the name of your Current School or College",						
			t4_content_element_SchoolAddress1: "Please provide the address of your Current School or College",						
			t4_content_element_SchoolCountry: "Please provide the country of your Current School or College",						
			t4_content_element_Agree: "Please tick the box to indicate you agree with our 'Use of data statement'"
		}
	});
	}	
	
if ($("#PostgraduateOpenDayForm").length) {

	$("#PostgraduateOpenDayForm").validate({

	//Normally and error class is added to the input element - I'm adding it to the parent div
	//so we can show our error cross
		highlight: function(element, errorClass) {
     	$(element).parent().parent().addClass(errorClass);
  		},
  		unhighlight: function(element, errorClass) {
     	$(element).parent().parent().removeClass(errorClass);
	  	},
		

	//Create an error container with an unordered list

		errorContainer: "#error-list",
		errorLabelContainer: $("#error-list ul"),
		wrapper: 'li',

	//The default will put focus on the first erroneous input. I wish to disable this function.
	//If there are errors, I wish to scroll to the error container instead

		focusInvalid: false,
		
		invalidHandler: function(form, validator) {
      var errors = validator.numberOfInvalids();
      if (errors) {
        window.location.hash = '#error-anchor';
      }
    },

	//Here are our field rules and their corresponding messages

		rules: {
			t4_content_element_FirstName: "required",
			t4_content_element_LastName: "required",
			t4_content_element_Address1: "required",
			t4_content_element_Country: "required",	
			t4_content_element_Email: {
				required: true,
				email: true
			},
			t4_content_element_ConfirmEmail: {
				required: true,
				email: true,
				equalTo: "#Email"
			},
			t4_content_element_ContactPhoneNumber: {
				required: true
			},	
			t4_content_element_Agree: "required"
		},
		messages: {
			t4_content_element_FirstName: "Please enter your First Name",
			t4_content_element_LastName: "Please enter your Last Name",			
			t4_content_element_Address1: "Please enter your Address",
			t4_content_element_Country: "Please enter your Country",
			t4_content_element_Email: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com"
			},
			t4_content_element_ConfirmEmail: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com",
				equalTo: "Confirm Email and Email should be the same"
			},
			t4_content_element_ContactPhoneNumber: "Please provide a Contact Phone Number",	
			t4_content_element_Agree: "Please tick the box to indicate you agree with our 'Use of data statement'"					
		}
	});
	}	
	
	
if ($("#DonateForm").length) {

	$("#DonateForm").validate({

	//Normally and error class is added to the input element - I'm adding it to the parent div
	//so we can show our error cross
		highlight: function(element, errorClass) {
     	$(element).parent().parent().addClass(errorClass);
  		},
  		unhighlight: function(element, errorClass) {
     	$(element).parent().parent().removeClass(errorClass);
	  	},
		

	//Create an error container with an unordered list

		errorContainer: "#error-list",
		errorLabelContainer: $("#error-list ul"),
		wrapper: 'li',

	//The default will put focus on the first erroneous input. I wish to disable this function.
	//If there are errors, I wish to scroll to the error container instead

		focusInvalid: false,
		
		invalidHandler: function(form, validator) {
      var errors = validator.numberOfInvalids();
      if (errors) {
        window.location.hash = '#error-anchor';
      }
    },

	//Here are our field rules and their corresponding messages

		rules: {
			t4_content_element_FirstName: "required",
			t4_content_element_LastName: "required",
			t4_content_element_Address1: "required",
			t4_content_element_Country: "required",
						
			t4_content_element_Email: {
				required: true,
				email: true
			},

			t4_content_element_ContactPhoneNumber: {
				required: true
			},			
			t4_content_element_GiftAmount: "required"
		},
		messages: {
			t4_content_element_FirstName: "Please enter your First Name",
			t4_content_element_LastName: "Please enter your Last Name",			
			t4_content_element_Address1: "Please enter your Address",
			t4_content_element_Country: "Please enter your Country",
			t4_content_element_Email: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com"
			},
			t4_content_element_Country: "Please enter your Country",
			t4_content_element_ContactPhoneNumber: "Please provide a Contact Phone Number",						
			t4_content_element_GiftAmount: "Please enter the amount of your Gift"
		}
	});
	}	

	
// summer schools 




if ($('#summerschool').length) {

	
// email back code 

function setEmail(){
	var returnemail = $('#t4_content_element_EmailAddress').val();
	$('.mailaddress').val(returnemail);
	console.log('submitted');

}

// validation 
	$("#summerschool").validate({

	//Normally and error class is added to the input element - I'm adding it to the parent div
	//so we can show our error cross
		highlight: function(element, errorClass) {
     	$(element).parent().parent().addClass(errorClass);
  		},
  		unhighlight: function(element, errorClass) {
     	$(element).parent().parent().removeClass(errorClass);
	  	},
		

	//Create an error container with an unordered list

		errorContainer: "#error-list",
		errorLabelContainer: $("#error-list ul"),
		wrapper: 'li',

	//The default will put focus on the first erroneous input. I wish to disable this function.
	//If there are errors, I wish to scroll to the error container instead

		focusInvalid: false,
		
		invalidHandler: function(form, validator) {
      var errors = validator.numberOfInvalids();
      if (errors) {
        window.location.hash = '#error-anchor';
      }
    },

	//Here are our field rules and their corresponding messages

		rules: {
			t4_content_element_StudentName: "required",
			t4_content_element_Address: "required",
			t4_content_element_HomePhone: "required",
			t4_content_element_StudentMobile: "required",
			t4_content_element_DOBDay: "required",
			t4_content_element_DOBMonth: "required",
			t4_content_element_DOBYear: "required",
			t4_content_element_School: "required",
			t4_content_element_Sex: "required",
			t4_content_element_YearAtSchool: "required",
			t4_content_element_LeavingCertYear: "required",
			t4_content_element_AreaofInterest: "required",
			t4_content_element_WhereDidYouHear: "required",
			t4_content_element_Top5CAO: "required",
			t4_content_element_Rules: "required",
			t4_content_element_SignedStudentName: "required",
			t4_content_element_DateSignedStudentDay: "required",
			t4_content_element_DateSignedStudentMonth: "required",
			t4_content_element_DateSignedStudentYear: "required",
			t4_content_element_ParentSignedName: "required",
			t4_content_element_DateSignedParentDay: "required",
			t4_content_element_DateSignedParentMonth: "required",
			t4_content_element_DateSignedParentYear: "required",
			t4_content_element_WhyYouWishToAttend: "required",
			t4_content_element_MathsLevel: "required",
			t4_content_element_JuniorCertResults: "required",

						
			t4_content_element_EmailAddress: {
				required: true,
				email: true
			},

			t4_content_element_ContactPhoneNumber: {
				required: true,
				number:true
			},	

			t4_content_element_EmergencyContactHomePhone: {
				number:true
			},	

			t4_content_element_EmergencyContactMobile: {
				number:true
			},	

			t4_content_element_StudentMobile: {
				required: true,
				number:true
			},	
					
			t4_content_element_WhyYouWishToAttend: "required"
		},
		messages: {
			t4_content_element_StudentName: "Please enter the student's name",
			t4_content_element_Address: "Please enter your address",			
			t4_content_element_HomePhone: "Please enter your home phone number",
			t4_content_element_DOBYear: "Please enter your date a birth",
			t4_content_element_School: "Please enter your school",
			t4_content_element_Sex: "Please specify whether the student is male or female",
			t4_content_element_YearAtSchool: "Please enter your current year at school",
			t4_content_element_LeavingCertYear: "Please enter the year in which you intend sitting the Leaving Certificate",
			t4_content_element_AreaofInterest: "Please enter your areas of interest",
			t4_content_element_WhereDidYouHear: "Please tell us where you heard about this Summer School",
			t4_content_element_Top5CAO: "Please specify your top 5 CAO preferences",
			t4_content_element_Rules: "Please tick that you have carefully read the Rules and Procedures agree to observe them.",
			t4_content_element_SignedStudentName: "Please enter the student's name",
			t4_content_element_DateSignedStudentYear: "Please enter the date",
			t4_content_element_ParentSignedName: "Please enter the Parent/Guardian's name",
			t4_content_element_EmailAddress: {
				required: "Please enter your Email address",
				email: "Please enter the email address in the format name@domain.com"
			}
		}
	});
	}	



// end summer schools 

        //=========================================================
        //Make relative links, created by CMS Nav objects, absolute
        //Also, read in and react to any affiliate site settings
        //Evan Ryder - May 2016
        //=========================================================
        $(document).ajaxError(function(){
          //if siteSettings.js doesn't exist, or has an error in its syntax
          defaultMenuLinksTo("www.universityofgalway.ie");
        });

        $.getJSON("/siteSettings.js", function(result) {
          if (result.megaMenuDefaultDomain) {
            defaultMenuLinksTo(result.megaMenuDefaultDomain);
          } else {
            defaultMenuLinksTo("www.universityofgalway.ie");
          }
	  if (result.title) {
	    document.title = document.title.replace("University of Galway", result.title);
	  }
          if (result.favicon && result.favicon != "") {
	    var link = document.querySelector("link[rel~='icon']");
	    if (!link) {
	      link = document.createElement('link');
	      link.rel = 'icon';
	      document.getElementsByTagName('head')[0].appendChild(link);
	    }
	    link.href = result.favicon;
	  }
        });
	
	// Switch to .fullContentWidth template if #pageRightColumn is empty
	if ($('#pageRightColumnWrapper').children().length == 0 ) {
		if ($('body').is('.fullWidth, .landingPage, .gatewayPage')) return;
		$('#pageRightColumn').hide();
		$('body').addClass('fullContentWidth');
	}

});


//======================================
//  Simple Anti Spam Crawler Function
//  Evan Ryder - 21 May 2003
//======================================
var MAIL_SERVER = "@universityofgalway.ie";
 
function mail(name, subj) {
  subj = subj || "Online Contact";
  if (name == "webeditor") {
            NO_SPAM = "mailto:" + name + MAIL_SERVER + "?subject=University of Galway Web Site Enquiry";
  } else {
    if (name.match("@")) {
              NO_SPAM = "mailto:" + name + "?subject=" + subj;
    } else {
              if (name.indexOf("*") > 0) {
                NO_SPAM = "mailto:" + name.replace(/\*/g, "@").replace(/nuigalway/i, "universityofgalway") + "?subject=" + subj;
              } else {
                NO_SPAM = "mailto:" + name + MAIL_SERVER + "?subject=" + subj;
              }
    }
  }
  document.location.href = NO_SPAM;  
}

function defaultMenuLinksTo(domain) {
  //make mega menu links point at the supplied domain name if they don't already contain '//'
  $("div.menu").find("a").each(function() {
    var attr = this.getAttribute("href");
    if (attr.indexOf('//') < 0) this.href = "//" + domain + attr;
  })
}

function replaceInContent(from, to, caseSensitive=true, replaceAll=true) {
  let options="";
  if (replaceAll) options+="g";
  if (!caseSensitive) options+="i";
  let re = new RegExp(from, options);
  //document.body.innerHTML=document.body.innerHTML.replace(re, to);
  e2r=document.querySelectorAll("p, span, h1, h2, h3, h4, h5, h6");
  for (i=0; i<e2r.length; i++) {
    e2r[i].innerHTML=e2r[i].innerHTML.replace(re, to);
  }
}

function replaceInLinks(from, to) {
  $("div#pageContentWrapper").find("a").each(function() {
    var attr = this.getAttribute("href");
    if (attr && attr != null) {
      this.href = attr.replace(from, to);
    }
    this.innerHTML=this.innerHTML.replace(from, to);
  })
}
function replaceInImages(from, to, overwrite=false) {
  $("div#pageContentWrapper").find("img").each(function() {
    if (overwrite) {
      this.src = to;
    } else {
      this.src = this.src.replace(from, to);
    }
  })
}

function nuigSearch() {
  //link to http search tool without browsers complaining the page is insecure
  document.getElementById('srchfrm').action="https://" + document.location.host + "/search-results/";
  return(true);
}
