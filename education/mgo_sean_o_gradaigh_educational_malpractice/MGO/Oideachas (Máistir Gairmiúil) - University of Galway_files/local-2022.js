/**
 * Norbert @ RMG, 2014/12/11
 * Hugo @ RMG, 2014/12/11
 * Luca @ RMG, 2015/01/07
 *
 * This files holds JS sctipts that are exclusively related to the new template/layouts.
 * Any T4 specific scripts or fixes for old content are kept in t4_hacks.js
 *
 */
 
/*
 * jQuery hashchange event, v1.4, 2013-11-29
 * https://github.com/georgekosmidis/jquery-hashchange
 */
(function(e,t,n){"$:nomunge";function f(e){e=e||location.href;return"#"+e.replace(/^[^#]*#?(.*)$/,"$1")}var r="hashchange",i=document,s,o=e.event.special,u=i.documentMode,a="on"+r in t&&(u===n||u>7);e.fn[r]=function(e){return e?this.bind(r,e):this.trigger(r)};e.fn[r].delay=50;o[r]=e.extend(o[r],{setup:function(){if(a){return false}e(s.start)},teardown:function(){if(a){return false}e(s.stop)}});s=function(){function p(){var n=f(),i=h(u);if(n!==u){c(u=n,i);e(t).trigger(r)}else if(i!==u){location.href=location.href.replace(/#.*/,"")+i}o=setTimeout(p,e.fn[r].delay)}var s={},o,u=f(),l=function(e){return e},c=l,h=l;s.start=function(){o||p()};s.stop=function(){o&&clearTimeout(o);o=n};var d=function(){var e,t=3,n=document.createElement("div"),r=n.getElementsByTagName("i");while(n.innerHTML="<!--[if gt IE "+ ++t+"]><i></i><![endif]-->",r[0]);return t>4?t:e}();d&&!a&&function(){var t,n;s.start=function(){if(!t){n=e.fn[r].src;n=n&&n+f();t=e('<iframe tabindex="-1" title="empty"/>').hide().one("load",function(){n||c(f());p()}).attr("src",n||"javascript:0").insertAfter("body")[0].contentWindow;i.onpropertychange=function(){try{if(event.propertyName==="title"){t.document.title=i.title}}catch(e){}}}};s.stop=l;h=function(){return f(t.location.href)};c=function(n,s){var o=t.document,u=e.fn[r].domain;if(n!==s){o.title=i.title;o.open();u&&o.write('<script>document.domain="'+u+'"</script>');o.close();t.location.hash=n}}}();return s}()})(jQuery,this);

/* 
 * jQuery EasyTabs plugin,  v3.2.0, 2013-05-09
 * https://github.com/JangoSteve/jQuery-EasyTabs
 */
(function(a){a.easytabs=function(j,e){var f=this,q=a(j),i={animate:true,panelActiveClass:"active",tabActiveClass:"active",defaultTab:"li:first-child",animationSpeed:"normal",tabs:"> ul > li",updateHash:true,cycle:false,collapsible:false,collapsedClass:"collapsed",collapsedByDefault:true,uiTabs:false,transitionIn:"fadeIn",transitionOut:"fadeOut",transitionInEasing:"swing",transitionOutEasing:"swing",transitionCollapse:"slideUp",transitionUncollapse:"slideDown",transitionCollapseEasing:"swing",transitionUncollapseEasing:"swing",containerClass:"",tabsClass:"",tabClass:"",panelClass:"",cache:true,event:"click",panelContext:q},h,l,v,m,d,t={fast:200,normal:400,slow:600},r;f.init=function(){f.settings=r=a.extend({},i,e);r.bind_str=r.event+".easytabs";if(r.uiTabs){r.tabActiveClass="ui-tabs-selected";r.containerClass="ui-tabs ui-widget ui-widget-content ui-corner-all";r.tabsClass="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all";r.tabClass="ui-state-default ui-corner-top";r.panelClass="ui-tabs-panel ui-widget-content ui-corner-bottom"}if(r.collapsible&&e.defaultTab!==undefined&&e.collpasedByDefault===undefined){r.collapsedByDefault=false}if(typeof(r.animationSpeed)==="string"){r.animationSpeed=t[r.animationSpeed]}a("a.anchor").remove().prependTo("body");q.data("easytabs",{});f.setTransitions();f.getTabs();b();g();w();n();c();q.attr("data-easytabs",true)};f.setTransitions=function(){v=(r.animate)?{show:r.transitionIn,hide:r.transitionOut,speed:r.animationSpeed,collapse:r.transitionCollapse,uncollapse:r.transitionUncollapse,halfSpeed:r.animationSpeed/2}:{show:"show",hide:"hide",speed:0,collapse:"hide",uncollapse:"show",halfSpeed:0}};f.getTabs=function(){var x;f.tabs=q.find(r.tabs),f.panels=a(),f.tabs.each(function(){var A=a(this),z=A.children("a"),y=A.children("a").data("target");A.data("easytabs",{});if(y!==undefined&&y!==null){A.data("easytabs").ajax=z.attr("href")}else{y=z.attr("href")}y=y.match(/#([^\?]+)/)[1];x=r.panelContext.find("#"+y);if(x.length){x.data("easytabs",{position:x.css("position"),visibility:x.css("visibility")});x.not(r.panelActiveClass).hide();f.panels=f.panels.add(x);A.data("easytabs").panel=x}else{f.tabs=f.tabs.not(A);if("console" in window){console.warn("Warning: tab without matching panel for selector '#"+y+"' removed from set")}}})};f.selectTab=function(x,C){var y=window.location,B=y.hash.match(/^[^\?]*/)[0],z=x.parent().data("easytabs").panel,A=x.parent().data("easytabs").ajax;if(r.collapsible&&!d&&(x.hasClass(r.tabActiveClass)||x.hasClass(r.collapsedClass))){f.toggleTabCollapse(x,z,A,C)}else{if(!x.hasClass(r.tabActiveClass)||!z.hasClass(r.panelActiveClass)){o(x,z,A,C)}else{if(!r.cache){o(x,z,A,C)}}}};f.toggleTabCollapse=function(x,y,z,A){f.panels.stop(true,true);if(u(q,"easytabs:before",[x,y,r])){f.tabs.filter("."+r.tabActiveClass).removeClass(r.tabActiveClass).children().removeClass(r.tabActiveClass);if(x.hasClass(r.collapsedClass)){if(z&&(!r.cache||!x.parent().data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[x,y]);y.load(z,function(C,B,D){x.parent().data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[x,y,C,B,D])})}x.parent().removeClass(r.collapsedClass).addClass(r.tabActiveClass).children().removeClass(r.collapsedClass).addClass(r.tabActiveClass);y.addClass(r.panelActiveClass)[v.uncollapse](v.speed,r.transitionUncollapseEasing,function(){q.trigger("easytabs:midTransition",[x,y,r]);if(typeof A=="function"){A()}})}else{x.addClass(r.collapsedClass).parent().addClass(r.collapsedClass);y.removeClass(r.panelActiveClass)[v.collapse](v.speed,r.transitionCollapseEasing,function(){q.trigger("easytabs:midTransition",[x,y,r]);if(typeof A=="function"){A()}})}}};f.matchTab=function(x){return f.tabs.find("[href='"+x+"'],[data-target='"+x+"']").first()};f.matchInPanel=function(x){return(x&&f.validId(x)?f.panels.filter(":has("+x+")").first():[])};f.validId=function(x){return x.substr(1).match(/^[A-Za-z]+[A-Za-z0-9\-_:\.].$/)};f.selectTabFromHashChange=function(){var y=window.location.hash.match(/^[^\?]*/)[0],x=f.matchTab(y),z;if(r.updateHash){if(x.length){d=true;f.selectTab(x)}else{z=f.matchInPanel(y);if(z.length){y="#"+z.attr("id");x=f.matchTab(y);d=true;f.selectTab(x)}else{if(!h.hasClass(r.tabActiveClass)&&!r.cycle){if(y===""||f.matchTab(m).length||q.closest(y).length){d=true;f.selectTab(l)}}}}}};f.cycleTabs=function(x){if(r.cycle){x=x%f.tabs.length;$tab=a(f.tabs[x]).children("a").first();d=true;f.selectTab($tab,function(){setTimeout(function(){f.cycleTabs(x+1)},r.cycle)})}};f.publicMethods={select:function(x){var y;if((y=f.tabs.filter(x)).length===0){if((y=f.tabs.find("a[href='"+x+"']")).length===0){if((y=f.tabs.find("a"+x)).length===0){if((y=f.tabs.find("[data-target='"+x+"']")).length===0){if((y=f.tabs.find("a[href$='"+x+"']")).length===0){a.error("Tab '"+x+"' does not exist in tab set")}}}}}else{y=y.children("a").first()}f.selectTab(y)}};var u=function(A,x,z){var y=a.Event(x);A.trigger(y,z);return y.result!==false};var b=function(){q.addClass(r.containerClass);f.tabs.parent().addClass(r.tabsClass);f.tabs.addClass(r.tabClass);f.panels.addClass(r.panelClass)};var g=function(){var y=window.location.hash.match(/^[^\?]*/)[0],x=f.matchTab(y).parent(),z;if(x.length===1){h=x;r.cycle=false}else{z=f.matchInPanel(y);if(z.length){y="#"+z.attr("id");h=f.matchTab(y).parent()}else{h=f.tabs.parent().find(r.defaultTab);if(h.length===0){a.error("The specified default tab ('"+r.defaultTab+"') could not be found in the tab set ('"+r.tabs+"') out of "+f.tabs.length+" tabs.")}}}l=h.children("a").first();p(x)};var p=function(z){var y,x;if(r.collapsible&&z.length===0&&r.collapsedByDefault){h.addClass(r.collapsedClass).children().addClass(r.collapsedClass)}else{y=a(h.data("easytabs").panel);x=h.data("easytabs").ajax;if(x&&(!r.cache||!h.data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[l,y]);y.load(x,function(B,A,C){h.data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[l,y,B,A,C])})}h.data("easytabs").panel.show().addClass(r.panelActiveClass);h.addClass(r.tabActiveClass).children().addClass(r.tabActiveClass)}q.trigger("easytabs:initialised",[l,y])};var w=function(){f.tabs.children("a").bind(r.bind_str,function(x){r.cycle=false;d=false;f.selectTab(a(this));x.preventDefault?x.preventDefault():x.returnValue=false})};var o=function(z,D,E,H){f.panels.stop(true,true);if(u(q,"easytabs:before",[z,D,r])){var A=f.panels.filter(":visible"),y=D.parent(),F,x,C,G,B=window.location.hash.match(/^[^\?]*/)[0];if(r.animate){F=s(D);x=A.length?k(A):0;C=F-x}m=B;G=function(){q.trigger("easytabs:midTransition",[z,D,r]);if(r.animate&&r.transitionIn=="fadeIn"){if(C<0){y.animate({height:y.height()+C},v.halfSpeed).css({"min-height":""})}}if(r.updateHash&&!d){window.location.hash="#"+D.attr("id")}else{d=false}D[v.show](v.speed,r.transitionInEasing,function(){y.css({height:"","min-height":""});q.trigger("easytabs:after",[z,D,r]);if(typeof H=="function"){H()}})};if(E&&(!r.cache||!z.parent().data("easytabs").cached)){q.trigger("easytabs:ajax:beforeSend",[z,D]);D.load(E,function(J,I,K){z.parent().data("easytabs").cached=true;q.trigger("easytabs:ajax:complete",[z,D,J,I,K])})}if(r.animate&&r.transitionOut=="fadeOut"){if(C>0){y.animate({height:(y.height()+C)},v.halfSpeed)}else{y.css({"min-height":y.height()})}}f.tabs.filter("."+r.tabActiveClass).removeClass(r.tabActiveClass).children().removeClass(r.tabActiveClass);f.tabs.filter("."+r.collapsedClass).removeClass(r.collapsedClass).children().removeClass(r.collapsedClass);z.parent().addClass(r.tabActiveClass).children().addClass(r.tabActiveClass);f.panels.filter("."+r.panelActiveClass).removeClass(r.panelActiveClass);D.addClass(r.panelActiveClass);if(A.length){A[v.hide](v.speed,r.transitionOutEasing,G)}else{D[v.uncollapse](v.speed,r.transitionUncollapseEasing,G)}}};var s=function(z){if(z.data("easytabs")&&z.data("easytabs").lastHeight){return z.data("easytabs").lastHeight}var B=z.css("display"),y,x;try{y=a("<div></div>",{position:"absolute",visibility:"hidden",overflow:"hidden"})}catch(A){y=a("<div></div>",{visibility:"hidden",overflow:"hidden"})}x=z.wrap(y).css({position:"relative",visibility:"hidden",display:"block"}).outerHeight();z.unwrap();z.css({position:z.data("easytabs").position,visibility:z.data("easytabs").visibility,display:B});z.data("easytabs").lastHeight=x;return x};var k=function(y){var x=y.outerHeight();if(y.data("easytabs")){y.data("easytabs").lastHeight=x}else{y.data("easytabs",{lastHeight:x})}return x};var n=function(){if(typeof a(window).hashchange==="function"){a(window).hashchange(function(){f.selectTabFromHashChange()})}else{if(a.address&&typeof a.address.change==="function"){a.address.change(function(){f.selectTabFromHashChange()})}}};var c=function(){var x;if(r.cycle){x=f.tabs.index(h);setTimeout(function(){f.cycleTabs(x+1)},r.cycle)}};f.init()};a.fn.easytabs=function(c){var b=arguments;return this.each(function(){var e=a(this),d=e.data("easytabs");if(undefined===d){d=new a.easytabs(this,c);e.data("easytabs",d)}if(d.publicMethods[c]){return d.publicMethods[c](Array.prototype.slice.call(b,1))}})}})(jQuery);

// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
// http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
// requestAnimationFrame polyfill by Erik Möller. fixes from Paul Irish and Tino Zijdel
// MIT license
(function() {var lastTime = 0; var vendors = ['ms', 'moz', 'webkit', 'o']; for(var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame']; window.cancelAnimationFrame = window[vendors[x]+'CancelAnimationFrame'] || window[vendors[x]+'CancelRequestAnimationFrame']; } if (!window.requestAnimationFrame) window.requestAnimationFrame = function(callback, element) {var currTime = new Date().getTime(); var timeToCall = Math.max(0, 16 - (currTime - lastTime)); var id = window.setTimeout(function() { callback(currTime + timeToCall); }, timeToCall); lastTime = currTime + timeToCall; return id; }; if (!window.cancelAnimationFrame) window.cancelAnimationFrame = function(id) {clearTimeout(id); }; }());

/* Calculate the viewport's width, excluding the browser scrollbar on PCs. Needed for matching media queries perfectly. */
$.fn.viewport = function(){ 
	var e = window, a = 'inner';
	if (!('innerWidth' in window )) {
		a = 'client';
		e = document.documentElement || document.body;
	}
	return { width : e[ a+'Width' ] , height : e[ a+'Height' ] };
}

/* Equalise height of elements collection */
$.fn.equalHeights = function() {
	var maxHeight = 0,
		$this = $(this);
	$this.each( function() {
		var height = $(this).innerHeight();
		if ( height > maxHeight ) { maxHeight = height; }
	});
	return $this.css('height', maxHeight);
};

/**
 * Screen size detection
 */
function isDesktop() {
	return ($.fn.viewport().width >= 1000);
}

function isTablet() {
	return ($.fn.viewport().width < 1000 && $.fn.viewport().width > 767);
}

function isMobile() {
	return ($.fn.viewport().width <= 767);
}

function isHandheld() {
	return (/Android|iPhone|iPad|iPod|BlackBerry/i).test(navigator.userAgent || navigator.vendor || window.opera);
}

/**
 * Pagination
 *
 * Example usage: $(".search_results .item").paginate(10);
 */
jQuery.fn.extend({
	paginate: function(limit) {

		var items = this;
		var itemCount = this.length;
		var pageCount = Math.ceil(itemCount / limit);
		var parent = this.parent();
		var currentPage = 0;

		function updateStatus() {
			var from = currentPage * limit + 1;
			var to = Math.min(itemCount, (currentPage + 1) * limit);
			var status = "Showing " + from + " to " + to + " of " + itemCount;
			parent.find("p.status span").html(status);
			if (from > 0) items.slice(0, from - 1).hide();
			items.slice(from - 1, to).show();
			items.slice(to).hide();
			parent.find(".pagination li a").removeClass("active");
			parent.find(".pagination li").removeClass("active");
			parent.find(".pagination li").eq(currentPage).addClass("active").find("a").addClass("active");
		}

		if (itemCount > limit) {
			var status = '<p class="status"><span></span></p>';
			var list = '<ul>';
			for (var i = 0; i < pageCount; i++) {
				list += '<li><a href="#" aria-label="Item ' + (i+1) + '">' + (i + 1) +'</a></li>';
			}
			list += '</ul>';
			var html = '<div class="pagination"><hr/>' + status + list + '</div>';
			parent.append(html);
			$(window).on("hashchange", function(event) {
				var page = window.location.hash.replace("#page", "") * 1 - 1;
				if (page <= 0 || page == undefined || isNaN(page)) page = 0;
				if (page != currentPage) {
					currentPage = page;
					updateStatus();
					var targetOffset = parent.offset().top;
					$('html,body').animate({scrollTop: targetOffset}, 300);
				}
			});
			parent.find(".pagination li a").click(function(e) {
				currentPage = $(this).parent().index();
				window.location.hash = "page" + (currentPage + 1);
				updateStatus();
				var targetOffset = parent.offset().top;
				$('html,body').animate({scrollTop: targetOffset}, 300);
				e.preventDefault();
				return false;
			});
			updateStatus();
		}

	}
});

/**
 * Other utilities
 */

/**
 * Trim text to specified length, but do not split words.
 */
function trimText(text, maxLength, includeEllipsis) {
	if (text.length <= maxLength) return text;
	var result = text.substr(0, maxLength);
	result = result.substr(0, Math.min(result.length, result.lastIndexOf(" ")))
	if (includeEllipsis == true && result.length < text.length) result += "&hellip;";
	return result;
}

jQuery.fn.extend({
	trimText: function(maxLength, includeEllipsis) {
		return this.each(function() {
			var el = $(this);
			var text = el.text();
			el.html(trimText(text, maxLength, includeEllipsis));
		});
	}
});

$(document).ready(function() {

	/**
	 * Navigation Properties
	 */

	var desktopDropdownEffectsOn = false;
	var mobileDropdownEffectsOn = false;
	var activeDropdown = false;
	var activeMenuItem = false;
	var intentTimer = false;
	var intentDelay = 200;
	var showOutDuration = 400;
	var showInDuration = 400;
	var swapOutDuration = 200;
	var swapInDuration = 400;

	/**
	 * Mobile Navigation - Primary/Global/Utility Combined into single dropdown
	 */

	$('#revealNavigationButton').click(function(e) {
		e.preventDefault();

		$(this).toggleClass("open");
		$("#navigation, #search").toggleClass("open");
		
		$('html').toggleClass("mobileMenuActive");

		return false;
	});

	function showMobileDropdown(e) {
		var el = $(this).closest("li");

		if (el.hasClass("open")) {
			el.find("div.dropdown").slideUp(300);
			el.removeClass("open");
		} else {
			el.find("div.dropdown").slideDown(300);
			el.addClass("open");
		}

		if (el.hasClass("has_child")) e.preventDefault();
	}

	/**
	 * Desktop Primary Navigation Dropdown (hide/unhide animations, hover effects)
	 */

	function getDropdownForMenuItem(li) {
		var className = li.prop("className");
		var matches = className.match(/node_id_(\d+)/);
		if (matches && matches.length > 0) return $("div.dropdown.for_node_id_" + matches[1]);
		return false;
	}

	function highlightMenuItem(li) {
		if (activeMenuItem && !activeMenuItem.is(li)) activeMenuItem.removeClass("active");
		li.addClass("active");
		activeMenuItem = li;
	}

	function resetTimer() {
		if (intentTimer) clearTimeout(intentTimer);
	}

	/**
	 * Convert Image roundels
	 */
	$("img.roundel").each(function() {
		var img = $(this);
		var caption = img.attr("alt");
		var align = img.hasClass("left") ? "left" : "right";
		img.attr("align", null);
		img.attr("style", null);
		img.wrap('<figure class="' + align + '"/>').wrap('<span class="image roundel"/>').wrap('<span class="imageWrapper"/>')
		var figure = img.parent().parent().parent();
		figure.append('<figcaption>' + caption + '</figcaption>');
	});

	$("img.polaroid").each(function() {
		var img = $(this);
		var caption = img.attr("alt");
		var align = "big";
     		if (img.hasClass("left")) align="left";
     		if (img.hasClass("right")) align="right";
		img.attr("align", null);
		img.attr("style", null);
		img.wrap('<figure class="polaroid ' + align + '"/>').wrap('<span class="image"/>').wrap('<span class="imageWrapper"/>')
		var figure = img.parent().parent().parent();
		figure.append('<figcaption>' + caption + '</figcaption>');
	});

	/**
	 * Events calendar - connect category checkboxes with label
	 */
	$("body.newsPage.events #categories .mainCategory input").each(function(i) {
		$(this).attr("id", "eventCategoriesChecbox" + i).next().attr("for", "eventCategoriesChecbox" + i);
	});
	$("body.newsPage.events #categories .mainCategory br").remove();
	// overlay calendar on tablet and mobile
	$("body.newsPage.events #calendar tr:first-child").click(function() {
		$("body.newsPage.events #calendar").toggleClass("open");
	});
	// hide categories in dropdown on tablet and mobile
	$("body.newsPage.events #categories fieldset").prepend('<span class="placeholder">Select Event Types</span>');
	$("body.newsPage.events #categories fieldset legend").click(function() {
		$("body.newsPage.events #categories").toggleClass("open");
	});

	function showPrimaryNavDropdownIntent() {
		highlightMenuItem($(this));
		resetTimer();

		intentTimer = setTimeout(function() {
			if (activeMenuItem) {
				var dropdown = getDropdownForMenuItem(activeMenuItem);
				if (dropdown) {
					if (activeDropdown) {
						activeDropdown.hide();
						dropdown.show();
					}
					else {
						dropdown.show();
					}
				}
				activeDropdown = dropdown;
			}
		}, activeDropdown ? 10 : intentDelay);
	}

	function hidePrimaryNavDropdown() {
		if (activeDropdown) {
			activeDropdown.hide();
			activeDropdown = false;
		}
		if (activeMenuItem) {
			activeMenuItem.removeClass("active");
			activeMenuItem = false;
		}
	}

	function initDesktopDropdownEffects() {
		if (!desktopDropdownEffectsOn) {
			desktopDropdownEffectsOn = true;
			//storeDropdownHeights();
			$("#primaryNavigation").on("mouseleave.dropdown", hidePrimaryNavDropdown);
			$("#primaryNavigation div.content > ul > li").on("mouseenter.dropdown", showPrimaryNavDropdownIntent);
			$("#primaryNavigation div.content > ul > li").on("mouseleave.dropdown", resetTimer);
		}
	}

	function initMobileDropdownEffects() {
		if (!mobileDropdownEffectsOn) {
			mobileDropdownEffectsOn = true;
			$("#primaryNavigation div.content > ul > li.has_child > a").after('<span class="arrow-dropdown" />');
			$("#primaryNavigation div.content > ul > li.has_child span.arrow-dropdown").on("click.dropdown", showMobileDropdown);
		}
	}

	function removeDesktopDropdownEffects() {
		if (desktopDropdownEffectsOn) {
			desktopDropdownEffectsOn = false;
			$("#primaryNavigation").off("mouseleave.dropdown", hidePrimaryNavDropdown);
			$("#primaryNavigation div.content > ul > li").off("mouseenter.dropdown", showPrimaryNavDropdownIntent);
			$("#primaryNavigation div.content > ul > li").off("mouseleave.dropdown", resetTimer);
			$("#primaryNavigation div.dropdown, #primaryNavigation div.dropdown .menu, #primaryNavigation div.dropdown .info").attr("style", "");
		}
	}

	function removeMobileDropdownEffects() {
		if (mobileDropdownEffectsOn) {
			mobileDropdownEffectsOn = false;
			$("#primaryNavigation div.content > ul > li.has_child span.arrow-dropdown").remove();
			$("#search.open, #revealNavigationButton.open, #navigation.open").removeClass("open");
		}
	}
	
	/**
	 * Primary navigation current link
	 */
	$('#primaryNavigationWrapper > div.content > ul > li > a').each(function() {
		var a = $(this);
		var path = location.pathname;
		var link = a.attr('href').replace(location.protocol + "//", "").replace(location.host, "");
		if (path == '') path = "/";
		if (link == '') link = "/";
		if (link == '/') {
			if (path == '' || path == '/curam/') a.parent().addClass('current');
		} else {
			if (path.match('^' + link)) a.parent().addClass('current');
		}
	});
	
    /**
     * Language check
     */
     if (document.location.href.indexOf('gaillimh') > 0 || document.location.href.indexOf('acadamh') > 0 || document.location.href.indexOf('ong.ie') > 0 || document.location.href.indexOf('onag.ie') > 0) { $('body').addClass('IE'); }

    /**
     * Secondary navigation for mobile/tablet
     */

    var secondaryMenu = $('#secondaryNavigationWrapper > ul');
    if (secondaryMenu.length) {

	    var overviewLink;
	    overviewLink = ($('body').hasClass('IE')) ? "Baile" : "Overview";
	    var rootMenuLink = $('#secondaryNavigationWrapper > ul > li:first a').attr("href").replace(/\/[^\/]+\/?$/, '') + '/';
	    var active = window.location.pathname == rootMenuLink ? ' class="active"' : '';
	    secondaryMenu.prepend('<li' + active + '><a href="' + rootMenuLink + '"><span>' + overviewLink + '</span></a></li>');
	    secondaryMenu.find('a[href="' + location.pathname + '"]').closest('li').addClass('active');
	    $('#secondaryNavigationWrapper #rootMenuItem a').click(function(e) {
	        if(!isDesktop() ) {
	            e.preventDefault();
	            $(this).toggleClass('open');
	            $('#secondaryNavigation ul').toggleClass('open');
	            if( $(this).hasClass('open') ) {
	                    var closeText = ($(this).data('close-text')) ? $(this).data('close-text') : "Close";
	                    $(this).find('span').text(closeText);
	            } else {
	                    $(this).find('span').text($(this).data('original-text'));
	            }
	        }
	    });
	}
	
	function closeMobileSecondaryMenu(that) {
		that.find('span').text(that.data('original-text'));
		that.removeClass('open');
		$('#secondaryNavigation ul').removeClass('open');
	}
	
	/**
	 * Sticky Page Buttons for mobile/tablet
	 */
	
	function checkBottomMarginForPageButtons() {
		if( !$('div.pageButtons').length ) return;
		
		pageButtons.css('height', 'auto');
		if ( isDesktop() )
			$('body').css('margin-bottom', 0);
		else {
			$('body').css('margin-bottom', $('div.pageButtons').height());
			pageButtons.equalHeights();
		}
	}
	
	function addPageButtonsHandlers() {
		$('div.pageButtons a.sharePage')
			.prop('target', '_blank')
			.prop('href', 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(location.href));
		$('div.pageButtons a.printPage')
			.on('click', function(e) {
				e.preventDefault();
				window.print();
			});
	}
	var pageButtons = $('div.pageButtons a');
	addPageButtonsHandlers();
	
	/**
	 * YouTube iFrame z-index issue fix (Win7/IE11/Flash 11?)
	 */
	$('iframe').each(function(){
             try {
		var url = $(this).attr('src');
		if( url.indexOf('youtube.com') !== -1 || url.indexOf('youtu.be') !== -1 ) {
		  if( url.indexOf('?') !== -1 )
			$(this).attr('src', url + '&amp;wmode=opaque');
		  else
		    $(this).attr('src', url + '?wmode=opaque');
		}
             }
             catch(err) {
              // do nothing
             }
	});

	/**
	 * Initialize all responsive handlers
	 */

	if (isDesktop()) initDesktopDropdownEffects();
	else initMobileDropdownEffects();
	checkBottomMarginForPageButtons();

	$(window).resize(function() {

		if (isDesktop()) {
			initDesktopDropdownEffects();
			removeMobileDropdownEffects();
			closeMobileSecondaryMenu($('#secondaryNavigationWrapper #rootMenuItem a'));
		} else {
			initMobileDropdownEffects();
			removeDesktopDropdownEffects();
		}
		checkBottomMarginForPageButtons();

	});
	
	/**
	 * collegePage
	 */
	
	if ($('body').hasClass('collegePage')) {
		
		/**
		 * collegeIconNavigation
		 */
		 
		$("#collegeIconNavigation span.disciplines").click(function() {
			var parentItem = $(this).closest("li.item");
			if(!parentItem.hasClass("open")) { //closed
				$(this).prev().slideDown(400);
				parentItem.addClass("open");
			} else { //opened
				$(this).prev().slideUp(400, function() {
					parentItem.removeClass("open");
				});
			}
		});

	}

	/**
	 * Collapsible navigation for mobile
	 */
	 
	$('.mobileCollapsibleNavigation a.nav_root').click(function(e) {
		if(isMobile()) {
			e.preventDefault();
			$(this).toggleClass('open');
			$('.mobileCollapsibleNavigation ul').toggleClass('open');
			if($(this).hasClass('open')) {
				var closeText = ($('body').hasClass('IE')) ? "D&uacute;n" : "Close";
				$(this).find('span').text(closeText);
			} else {
				$(this).find('span').text($(this).data('original-text'));
			}
		}
	});
	
	function closeCollapsibleMenu(that) {
		that.find('span').text(that.data('original-text'));
		that.removeClass('open');
		$('.mobileCollapsibleNavigation ul').removeClass('open');
	}
	
	$(window).resize(function() {
		if (!isMobile()) closeCollapsibleMenu($('.mobileCollapsibleNavigation a.nav_root'));
	});

	/**
	 * Limit footer news heading to two lines
	 */
	$(".footerNews").find("h4").trimText(60, true);

	/**
	 * Curam - Team Profiles
	 */
	$(".staffListItem .full").each(function() {
		var t = $(this);
		if (t.text().length > 0) {
			t.after('<a class="more" href="#">READ MORE</a>');
			t.parent().find("a.more").toggle(function() {
				$(this).html("CLOSE").prev().slideDown(600);
			}, function() {
				$(this).html("READ MORE").prev().slideUp(600);
			});
		}
	});
	$(".staffListItem").each(function() {
		var p = $(this).find(".position");
		p.html(p.text().toLocaleUpperCase().replace("PHD", " PhD"));
	});

    // Course Overview accordion
	$('.accordion').find('h4').each(function() {
		var h4 = $(this);
		var div = h4.nextUntil("h4").wrapAll("<div></div>").parent();
		if (jQuery.trim(div.text()).length == 0) {
			div.prev('h4').remove();
			div.remove(); // remove empty tabs
		}
	});
	$('.accordion')
		.find('> div').hide().end()
		.find('> h4').on('click', function(e) {
			$(this).toggleClass('open').next('div').slideToggle();
		});

	/**
	 * Library website - accordion
	 */
	$("#accordianplace .expander-link a").toggle(function(e) {
		e.preventDefault();
		$(this).closest(".expander").addClass("open").find(".expander-content").slideDown();
		return false;
	}, function(e) {
		e.preventDefault();
		$(this).closest(".expander").removeClass("open").find(".expander-content").slideUp();
		return false;
	});

	/**
	 * Download List Footer Carousel
	 */
	function updateDownloadsPagination() {

		$("div.downloadPagination").remove();
		$("div.downloads div.downloadListWrapper").css("margin-left", 0);

		var itemWidth = $("div.downloads ul li img").width() + 30;
		var numItems = $("div.downloads ul li").length;
		var listWidth = itemWidth * numItems;
		var pageWidth = $(window).width();
		var index = 0;

		function scrollToIndex() {
			$("div.downloadPagination a.page").removeClass("active");
			$("div.downloadPagination a.page").eq(index).addClass("active");
			$("div.downloads div.downloadListWrapper").animate({
				"margin-left": itemWidth * perPage * -1 * index
			}, 600);
		}

		if (listWidth > pageWidth) {

			$("div.downloads div.downloadListWrapper").css("width", "10000px").css("margin", "0");
			$("div.downloads").addClass("with_pagination");

			var perPage = Math.floor(pageWidth / itemWidth);
			var numPages = Math.ceil(numItems / perPage);

			var html = '<div class="downloadPagination">';
			html += '<a href="#" class="prev" aria-label="Show previous page of downloads">&#x25c5;</a>';
			for (var i = 0; i < numPages; i++) {
				html += '<a aria-label="Show Page ';
				html += i+1;
				html += ' of downloads" class="page';
				if (i == 0) html += ' active';
				html += '" href="#"><span>•</span></a>';
			}
			html += '<a href="#" class="next" aria-label="Show next page of downloads">&#x25bb;</a>';
			html += '</div>';

			$("div.downloadsWrapper").append(html);

			$("div.downloadPagination a.page").click(function() {
				index = $(this).addClass("active").index() - 1;
				scrollToIndex();
				return false;
			});

			$("div.downloadPagination a.prev").click(function() {
				if (index > 0) index--;
				scrollToIndex();
				return false;
			});

			$("div.downloadPagination a.next").click(function() {
				if (index < numPages - 1) index++;
				scrollToIndex();
				return false;
			});

		} else {

			$("div.downloads div.downloadListWrapper").css("width", listWidth + "px").css("margin", "0 auto");
			$("div.downloads").removeClass("with_pagination");

		}
	}
	setTimeout(updateDownloadsPagination, 500);
	$(window).resize(updateDownloadsPagination);

	function initKeyFactsTouchEvents() {
		var touchStartX = 0;
		var touchDiffX = 0;

		$("div.keyFactsRoundels").on("touchstart", function(e) { 
			touchStartX = e.originalEvent.touches[0].clientX;
		});
		$("div.keyFactsRoundels").on("touchmove", function(e) { 
			touchDiffX = e.originalEvent.touches[0].clientX - touchStartX;
		});
		$("div.keyFactsRoundels").on("touchend", function(e) { 
			if (Math.abs(touchDiffX) > 50) {
				if (touchDiffX > 0) $(this).find("a.prev").click();
				else $(this).find("a.next").click();
			}
		});
	}

	function updateKeyFactsPagination() {

		$("div.keyFactsRoundels").each(function() {

			var c = $(this);			

			c.find("div.keyFactsRoundelsPagination").remove();
			c.find("div.keyFactsRoundelsScroller").css("margin-left", 0);

			var pageWidth = c.width();
			var perPage = 3;
			var itemWidth = pageWidth / 3;
			if (pageWidth < 735) {
				perPage = 1;
				itemWidth = 240;
			}
			var numItems = c.find("div.roundel:not(.hidden)").length;
			var listWidth = itemWidth * numItems;
			var index = 0;

			function scrollToIndex() {
				c.find("div.keyFactsRoundelsPagination a.page").removeClass("active");
				c.find("div.keyFactsRoundelsPagination a.page").eq(index).addClass("active");
				c.find("div.keyFactsRoundelsScroller").animate({
					"margin-left": itemWidth * perPage * -1 * index
				}, 600);
			}

			if (listWidth > pageWidth) {

				c.find("div.keyFactsRoundels").addClass("with_pagination");

				var numPages = Math.ceil(numItems / perPage);

				var html = '<div class="keyFactsRoundelsPagination">';
				html += '<a href="#" class="prev" aria-label="Previous Key Fact">&#x25c5;</a>';
				for (var i = 0; i < numPages; i++) {
					html += '<a aria-label="Key Fact ';
					html += i+1;
					html += '" class="page';
					if (i == 0) html += ' active';
					html += '" href="#"><span>•</span></a>';
				}
				html += '<a href="#" class="next" aria-label="Next Key Fact">&#x25bb;</a>';
				html += '</div>';

				c.append(html);

				c.find("div.keyFactsRoundelsPagination a.page").click(function() {
					index = $(this).addClass("active").index() - 1;
					scrollToIndex();
					return false;
				});

				c.find("div.keyFactsRoundelsPagination a.prev").click(function() {
					if (index > 0) index--;
					scrollToIndex();
					return false;
				});

				c.find("div.keyFactsRoundelsPagination a.next").click(function() {
					if (index < numPages - 1) index++;
					scrollToIndex();
					return false;
				});

			} else {
				c.find("div.keyFactsRoundels").removeClass("with_pagination");
			}

		});
	}
	setTimeout(updateKeyFactsPagination, 500);
	setTimeout(initKeyFactsTouchEvents, 500);
	$(window).resize(updateKeyFactsPagination);

});
