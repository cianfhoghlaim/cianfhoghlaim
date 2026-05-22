(function(){'use strict';var p;function aa(a){var b=0;return function(){return b<a.length?{done:!1,value:a[b++]}:{done:!0}}}
var ba=typeof Object.defineProperties=="function"?Object.defineProperty:function(a,b,c){if(a==Array.prototype||a==Object.prototype)return a;a[b]=c.value;return a};
function da(a){a=["object"==typeof globalThis&&globalThis,a,"object"==typeof window&&window,"object"==typeof self&&self,"object"==typeof global&&global];for(var b=0;b<a.length;++b){var c=a[b];if(c&&c.Math==Math)return c}throw Error("Cannot find global object");}
var ea=da(this);function u(a,b){if(b)a:{var c=ea;a=a.split(".");for(var d=0;d<a.length-1;d++){var e=a[d];if(!(e in c))break a;c=c[e]}a=a[a.length-1];d=c[a];b=b(d);b!=d&&b!=null&&ba(c,a,{configurable:!0,writable:!0,value:b})}}
u("Symbol",function(a){function b(f){if(this instanceof b)throw new TypeError("Symbol is not a constructor");return new c(d+(f||"")+"_"+e++,f)}
function c(f,g){this.h=f;ba(this,"description",{configurable:!0,writable:!0,value:g})}
if(a)return a;c.prototype.toString=function(){return this.h};
var d="jscomp_symbol_"+(Math.random()*1E9>>>0)+"_",e=0;return b});
u("Symbol.iterator",function(a){if(a)return a;a=Symbol("Symbol.iterator");for(var b="Array Int8Array Uint8Array Uint8ClampedArray Int16Array Uint16Array Int32Array Uint32Array Float32Array Float64Array".split(" "),c=0;c<b.length;c++){var d=ea[b[c]];typeof d==="function"&&typeof d.prototype[a]!="function"&&ba(d.prototype,a,{configurable:!0,writable:!0,value:function(){return fa(aa(this))}})}return a});
function fa(a){a={next:a};a[Symbol.iterator]=function(){return this};
return a}
var ha=typeof Object.create=="function"?Object.create:function(a){function b(){}
b.prototype=a;return new b},ja=function(){function a(){function c(){}
new c;Reflect.construct(c,[],function(){});
return new c instanceof c}
if(typeof Reflect!="undefined"&&Reflect.construct){if(a())return Reflect.construct;var b=Reflect.construct;return function(c,d,e){c=b(c,d);e&&Reflect.setPrototypeOf(c,e.prototype);return c}}return function(c,d,e){e===void 0&&(e=c);
e=ha(e.prototype||Object.prototype);return Function.prototype.apply.call(c,e,d)||e}}(),ka;
if(typeof Object.setPrototypeOf=="function")ka=Object.setPrototypeOf;else{var la;a:{var ma={a:!0},na={};try{na.__proto__=ma;la=na.a;break a}catch(a){}la=!1}ka=la?function(a,b){a.__proto__=b;if(a.__proto__!==b)throw new TypeError(a+" is not extensible");return a}:null}var oa=ka;
function v(a,b){a.prototype=ha(b.prototype);a.prototype.constructor=a;if(oa)oa(a,b);else for(var c in b)if(c!="prototype")if(Object.defineProperties){var d=Object.getOwnPropertyDescriptor(b,c);d&&Object.defineProperty(a,c,d)}else a[c]=b[c];a.Aa=b.prototype}
function y(a){var b=typeof Symbol!="undefined"&&Symbol.iterator&&a[Symbol.iterator];if(b)return b.call(a);if(typeof a.length=="number")return{next:aa(a)};throw Error(String(a)+" is not an iterable or ArrayLike");}
function A(a){if(!(a instanceof Array)){a=y(a);for(var b,c=[];!(b=a.next()).done;)c.push(b.value);a=c}return a}
function pa(a){return qa(a,a)}
function qa(a,b){a.raw=b;Object.freeze&&(Object.freeze(a),Object.freeze(b));return a}
function ra(a,b){return Object.prototype.hasOwnProperty.call(a,b)}
var sa=typeof Object.assign=="function"?Object.assign:function(a,b){for(var c=1;c<arguments.length;c++){var d=arguments[c];if(d)for(var e in d)ra(d,e)&&(a[e]=d[e])}return a};
u("Object.assign",function(a){return a||sa});
function ta(){this.A=!1;this.u=null;this.i=void 0;this.h=1;this.o=this.H=0;this.M=this.j=null}
function ua(a){if(a.A)throw new TypeError("Generator is already running");a.A=!0}
ta.prototype.G=function(a){this.i=a};
function va(a,b){a.j={exception:b,Bd:!0};a.h=a.H||a.o}
ta.prototype.return=function(a){this.j={return:a};this.h=this.o};
ta.prototype.yield=function(a,b){this.h=b;return{value:a}};
ta.prototype.B=function(a){this.h=a};
function wa(a,b,c){a.H=b;c!=void 0&&(a.o=c)}
function xa(a,b){a.h=b;a.H=0}
function ya(a){a.H=0;var b=a.j.exception;a.j=null;return b}
function za(a){var b=a.M.splice(0)[0];(b=a.j=a.j||b)?b.Bd?a.h=a.H||a.o:b.B!=void 0&&a.o<b.B?(a.h=b.B,a.j=null):a.h=a.o:a.h=0}
function Aa(a){this.h=new ta;this.i=a}
function Ba(a,b){ua(a.h);var c=a.h.u;if(c)return Ca(a,"return"in c?c["return"]:function(d){return{value:d,done:!0}},b,a.h.return);
a.h.return(b);return Da(a)}
function Ca(a,b,c,d){try{var e=b.call(a.h.u,c);if(!(e instanceof Object))throw new TypeError("Iterator result "+e+" is not an object");if(!e.done)return a.h.A=!1,e;var f=e.value}catch(g){return a.h.u=null,va(a.h,g),Da(a)}a.h.u=null;d.call(a.h,f);return Da(a)}
function Da(a){for(;a.h.h;)try{var b=a.i(a.h);if(b)return a.h.A=!1,{value:b.value,done:!1}}catch(c){a.h.i=void 0,va(a.h,c)}a.h.A=!1;if(a.h.j){b=a.h.j;a.h.j=null;if(b.Bd)throw b.exception;return{value:b.return,done:!0}}return{value:void 0,done:!0}}
function Ea(a){this.next=function(b){ua(a.h);a.h.u?b=Ca(a,a.h.u.next,b,a.h.G):(a.h.G(b),b=Da(a));return b};
this.throw=function(b){ua(a.h);a.h.u?b=Ca(a,a.h.u["throw"],b,a.h.G):(va(a.h,b),b=Da(a));return b};
this.return=function(b){return Ba(a,b)};
this[Symbol.iterator]=function(){return this}}
function Fa(a){function b(d){return a.next(d)}
function c(d){return a.throw(d)}
return new Promise(function(d,e){function f(g){g.done?d(g.value):Promise.resolve(g.value).then(b,c).then(f,e)}
f(a.next())})}
function B(a){return Fa(new Ea(new Aa(a)))}
function C(){for(var a=Number(this),b=[],c=a;c<arguments.length;c++)b[c-a]=arguments[c];return b}
u("globalThis",function(a){return a||ea});
u("Reflect",function(a){return a?a:{}});
u("Reflect.construct",function(){return ja});
u("Reflect.setPrototypeOf",function(a){return a?a:oa?function(b,c){try{return oa(b,c),!0}catch(d){return!1}}:null});
u("Promise",function(a){function b(g){this.X=0;this.bb=void 0;this.h=[];this.u=!1;var h=this.i();try{g(h.resolve,h.reject)}catch(k){h.reject(k)}}
function c(){this.h=null}
function d(g){return g instanceof b?g:new b(function(h){h(g)})}
if(a)return a;c.prototype.i=function(g){if(this.h==null){this.h=[];var h=this;this.j(function(){h.u()})}this.h.push(g)};
var e=ea.setTimeout;c.prototype.j=function(g){e(g,0)};
c.prototype.u=function(){for(;this.h&&this.h.length;){var g=this.h;this.h=[];for(var h=0;h<g.length;++h){var k=g[h];g[h]=null;try{k()}catch(l){this.o(l)}}}this.h=null};
c.prototype.o=function(g){this.j(function(){throw g;})};
b.prototype.i=function(){function g(l){return function(m){k||(k=!0,l.call(h,m))}}
var h=this,k=!1;return{resolve:g(this.U),reject:g(this.j)}};
b.prototype.U=function(g){if(g===this)this.j(new TypeError("A Promise cannot resolve to itself"));else if(g instanceof b)this.Z(g);else{a:switch(typeof g){case "object":var h=g!=null;break a;case "function":h=!0;break a;default:h=!1}h?this.M(g):this.o(g)}};
b.prototype.M=function(g){var h=void 0;try{h=g.then}catch(k){this.j(k);return}typeof h=="function"?this.ha(h,g):this.o(g)};
b.prototype.j=function(g){this.H(2,g)};
b.prototype.o=function(g){this.H(1,g)};
b.prototype.H=function(g,h){if(this.X!=0)throw Error("Cannot settle("+g+", "+h+"): Promise already settled in state"+this.X);this.X=g;this.bb=h;this.X===2&&this.Y();this.A()};
b.prototype.Y=function(){var g=this;e(function(){if(g.G()){var h=ea.console;typeof h!=="undefined"&&h.error(g.bb)}},1)};
b.prototype.G=function(){if(this.u)return!1;var g=ea.CustomEvent,h=ea.Event,k=ea.dispatchEvent;if(typeof k==="undefined")return!0;typeof g==="function"?g=new g("unhandledrejection",{cancelable:!0}):typeof h==="function"?g=new h("unhandledrejection",{cancelable:!0}):(g=ea.document.createEvent("CustomEvent"),g.initCustomEvent("unhandledrejection",!1,!0,g));g.promise=this;g.reason=this.bb;return k(g)};
b.prototype.A=function(){if(this.h!=null){for(var g=0;g<this.h.length;++g)f.i(this.h[g]);this.h=null}};
var f=new c;b.prototype.Z=function(g){var h=this.i();g.lc(h.resolve,h.reject)};
b.prototype.ha=function(g,h){var k=this.i();try{g.call(h,k.resolve,k.reject)}catch(l){k.reject(l)}};
b.prototype.then=function(g,h){function k(r,t){return typeof r=="function"?function(w){try{l(r(w))}catch(x){m(x)}}:t}
var l,m,n=new b(function(r,t){l=r;m=t});
this.lc(k(g,l),k(h,m));return n};
b.prototype.catch=function(g){return this.then(void 0,g)};
b.prototype.lc=function(g,h){function k(){switch(l.X){case 1:g(l.bb);break;case 2:h(l.bb);break;default:throw Error("Unexpected state: "+l.X);}}
var l=this;this.h==null?f.i(k):this.h.push(k);this.u=!0};
b.resolve=d;b.reject=function(g){return new b(function(h,k){k(g)})};
b.race=function(g){return new b(function(h,k){for(var l=y(g),m=l.next();!m.done;m=l.next())d(m.value).lc(h,k)})};
b.all=function(g){var h=y(g),k=h.next();return k.done?d([]):new b(function(l,m){function n(w){return function(x){r[w]=x;t--;t==0&&l(r)}}
var r=[],t=0;do r.push(void 0),t++,d(k.value).lc(n(r.length-1),m),k=h.next();while(!k.done)})};
return b});
u("Object.setPrototypeOf",function(a){return a||oa});
u("Symbol.dispose",function(a){return a?a:Symbol("Symbol.dispose")});
u("WeakMap",function(a){function b(k){this.h=(h+=Math.random()+1).toString();if(k){k=y(k);for(var l;!(l=k.next()).done;)l=l.value,this.set(l[0],l[1])}}
function c(){}
function d(k){var l=typeof k;return l==="object"&&k!==null||l==="function"}
function e(k){if(!ra(k,g)){var l=new c;ba(k,g,{value:l})}}
function f(k){var l=Object[k];l&&(Object[k]=function(m){if(m instanceof c)return m;Object.isExtensible(m)&&e(m);return l(m)})}
if(function(){if(!a||!Object.seal)return!1;try{var k=Object.seal({}),l=Object.seal({}),m=new a([[k,2],[l,3]]);if(m.get(k)!=2||m.get(l)!=3)return!1;m.delete(k);m.set(l,4);return!m.has(k)&&m.get(l)==4}catch(n){return!1}}())return a;
var g="$jscomp_hidden_"+Math.random();f("freeze");f("preventExtensions");f("seal");var h=0;b.prototype.set=function(k,l){if(!d(k))throw Error("Invalid WeakMap key");e(k);if(!ra(k,g))throw Error("WeakMap key fail: "+k);k[g][this.h]=l;return this};
b.prototype.get=function(k){return d(k)&&ra(k,g)?k[g][this.h]:void 0};
b.prototype.has=function(k){return d(k)&&ra(k,g)&&ra(k[g],this.h)};
b.prototype.delete=function(k){return d(k)&&ra(k,g)&&ra(k[g],this.h)?delete k[g][this.h]:!1};
return b});
u("Map",function(a){function b(){var h={};return h.previous=h.next=h.head=h}
function c(h,k){var l=h[1];return fa(function(){if(l){for(;l.head!=h[1];)l=l.previous;for(;l.next!=l.head;)return l=l.next,{done:!1,value:k(l)};l=null}return{done:!0,value:void 0}})}
function d(h,k){var l=k&&typeof k;l=="object"||l=="function"?f.has(k)?l=f.get(k):(l=""+ ++g,f.set(k,l)):l="p_"+k;var m=h[0][l];if(m&&ra(h[0],l))for(h=0;h<m.length;h++){var n=m[h];if(k!==k&&n.key!==n.key||k===n.key)return{id:l,list:m,index:h,entry:n}}return{id:l,list:m,index:-1,entry:void 0}}
function e(h){this[0]={};this[1]=b();this.size=0;if(h){h=y(h);for(var k;!(k=h.next()).done;)k=k.value,this.set(k[0],k[1])}}
if(function(){if(!a||typeof a!="function"||!a.prototype.entries||typeof Object.seal!="function")return!1;try{var h=Object.seal({x:4}),k=new a(y([[h,"s"]]));if(k.get(h)!="s"||k.size!=1||k.get({x:4})||k.set({x:4},"t")!=k||k.size!=2)return!1;var l=k.entries(),m=l.next();if(m.done||m.value[0]!=h||m.value[1]!="s")return!1;m=l.next();return m.done||m.value[0].x!=4||m.value[1]!="t"||!l.next().done?!1:!0}catch(n){return!1}}())return a;
var f=new WeakMap;e.prototype.set=function(h,k){h=h===0?0:h;var l=d(this,h);l.list||(l.list=this[0][l.id]=[]);l.entry?l.entry.value=k:(l.entry={next:this[1],previous:this[1].previous,head:this[1],key:h,value:k},l.list.push(l.entry),this[1].previous.next=l.entry,this[1].previous=l.entry,this.size++);return this};
e.prototype.delete=function(h){h=d(this,h);return h.entry&&h.list?(h.list.splice(h.index,1),h.list.length||delete this[0][h.id],h.entry.previous.next=h.entry.next,h.entry.next.previous=h.entry.previous,h.entry.head=null,this.size--,!0):!1};
e.prototype.clear=function(){this[0]={};this[1]=this[1].previous=b();this.size=0};
e.prototype.has=function(h){return!!d(this,h).entry};
e.prototype.get=function(h){return(h=d(this,h).entry)&&h.value};
e.prototype.entries=function(){return c(this,function(h){return[h.key,h.value]})};
e.prototype.keys=function(){return c(this,function(h){return h.key})};
e.prototype.values=function(){return c(this,function(h){return h.value})};
e.prototype.forEach=function(h,k){for(var l=this.entries(),m;!(m=l.next()).done;)m=m.value,h.call(k,m[1],m[0],this)};
e.prototype[Symbol.iterator]=e.prototype.entries;var g=0;return e});
u("Set",function(a){function b(c){this.h=new Map;if(c){c=y(c);for(var d;!(d=c.next()).done;)this.add(d.value)}this.size=this.h.size}
if(function(){if(!a||typeof a!="function"||!a.prototype.entries||typeof Object.seal!="function")return!1;try{var c=Object.seal({x:4}),d=new a(y([c]));if(!d.has(c)||d.size!=1||d.add(c)!=d||d.size!=1||d.add({x:4})!=d||d.size!=2)return!1;var e=d.entries(),f=e.next();if(f.done||f.value[0]!=c||f.value[1]!=c)return!1;f=e.next();return f.done||f.value[0]==c||f.value[0].x!=4||f.value[1]!=f.value[0]?!1:e.next().done}catch(g){return!1}}())return a;
b.prototype.add=function(c){c=c===0?0:c;this.h.set(c,c);this.size=this.h.size;return this};
b.prototype.delete=function(c){c=this.h.delete(c);this.size=this.h.size;return c};
b.prototype.clear=function(){this.h.clear();this.size=0};
b.prototype.has=function(c){return this.h.has(c)};
b.prototype.entries=function(){return this.h.entries()};
b.prototype.values=function(){return this.h.values()};
b.prototype.keys=b.prototype.values;b.prototype[Symbol.iterator]=b.prototype.values;b.prototype.forEach=function(c,d){var e=this;this.h.forEach(function(f){return c.call(d,f,f,e)})};
return b});
function Ga(a,b){a instanceof String&&(a+="");var c=0,d=!1,e={next:function(){if(!d&&c<a.length){var f=c++;return{value:b(f,a[f]),done:!1}}d=!0;return{done:!0,value:void 0}}};
e[Symbol.iterator]=function(){return e};
return e}
u("Array.prototype.entries",function(a){return a?a:function(){return Ga(this,function(b,c){return[b,c]})}});
u("Array.prototype.keys",function(a){return a?a:function(){return Ga(this,function(b){return b})}});
function Ha(a,b,c){if(a==null)throw new TypeError("The 'this' value for String.prototype."+c+" must not be null or undefined");if(b instanceof RegExp)throw new TypeError("First argument to String.prototype."+c+" must not be a regular expression");return a+""}
u("String.prototype.startsWith",function(a){return a?a:function(b,c){var d=Ha(this,b,"startsWith");b+="";var e=d.length,f=b.length;c=Math.max(0,Math.min(c|0,d.length));for(var g=0;g<f&&c<e;)if(d[c++]!=b[g++])return!1;return g>=f}});
u("String.prototype.endsWith",function(a){return a?a:function(b,c){var d=Ha(this,b,"endsWith");b+="";c===void 0&&(c=d.length);c=Math.max(0,Math.min(c|0,d.length));for(var e=b.length;e>0&&c>0;)if(d[--c]!=b[--e])return!1;return e<=0}});
u("Number.isFinite",function(a){return a?a:function(b){return typeof b!=="number"?!1:!isNaN(b)&&b!==Infinity&&b!==-Infinity}});
u("Array.prototype.find",function(a){return a?a:function(b,c){a:{var d=this;d instanceof String&&(d=String(d));for(var e=d.length,f=0;f<e;f++){var g=d[f];if(b.call(c,g,f,d)){b=g;break a}}b=void 0}return b}});
u("Object.values",function(a){return a?a:function(b){var c=[],d;for(d in b)ra(b,d)&&c.push(b[d]);return c}});
u("Object.is",function(a){return a?a:function(b,c){return b===c?b!==0||1/b===1/c:b!==b&&c!==c}});
u("Array.prototype.includes",function(a){return a?a:function(b,c){var d=this;d instanceof String&&(d=String(d));var e=d.length;c=c||0;for(c<0&&(c=Math.max(c+e,0));c<e;c++){var f=d[c];if(f===b||Object.is(f,b))return!0}return!1}});
u("String.prototype.includes",function(a){return a?a:function(b,c){return Ha(this,b,"includes").indexOf(b,c||0)!==-1}});
u("Array.from",function(a){return a?a:function(b,c,d){c=c!=null?c:function(h){return h};
var e=[],f=typeof Symbol!="undefined"&&Symbol.iterator&&b[Symbol.iterator];if(typeof f=="function"){b=f.call(b);for(var g=0;!(f=b.next()).done;)e.push(c.call(d,f.value,g++))}else for(f=b.length,g=0;g<f;g++)e.push(c.call(d,b[g],g));return e}});
u("Object.entries",function(a){return a?a:function(b){var c=[],d;for(d in b)ra(b,d)&&c.push([d,b[d]]);return c}});
u("Number.MAX_SAFE_INTEGER",function(){return 9007199254740991});
u("Number.MIN_SAFE_INTEGER",function(){return-9007199254740991});
u("Number.isInteger",function(a){return a?a:function(b){return Number.isFinite(b)?b===Math.floor(b):!1}});
u("Number.isSafeInteger",function(a){return a?a:function(b){return Number.isInteger(b)&&Math.abs(b)<=Number.MAX_SAFE_INTEGER}});
u("Math.trunc",function(a){return a?a:function(b){b=Number(b);if(isNaN(b)||b===Infinity||b===-Infinity||b===0)return b;var c=Math.floor(Math.abs(b));return b<0?-c:c}});
u("Number.isNaN",function(a){return a?a:function(b){return typeof b==="number"&&isNaN(b)}});
u("Array.prototype.values",function(a){return a?a:function(){return Ga(this,function(b,c){return c})}});/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
var Ia=Ia||{},D=this||self;function E(a,b,c){a=a.split(".");c=c||D;for(var d;a.length&&(d=a.shift());)a.length||b===void 0?c[d]&&c[d]!==Object.prototype[d]?c=c[d]:c=c[d]={}:c[d]=b}
function Ja(a,b){var c=F("CLOSURE_FLAGS");a=c&&c[a];return a!=null?a:b}
function F(a,b){a=a.split(".");b=b||D;for(var c=0;c<a.length;c++)if(b=b[a[c]],b==null)return null;return b}
function Ka(a){var b=typeof a;return b!="object"?b:a?Array.isArray(a)?"array":b:"null"}
function La(a){var b=Ka(a);return b=="array"||b=="object"&&typeof a.length=="number"}
function Ma(a){var b=typeof a;return b=="object"&&a!=null||b=="function"}
function Na(a){return Object.prototype.hasOwnProperty.call(a,Ra)&&a[Ra]||(a[Ra]=++Sa)}
var Ra="closure_uid_"+(Math.random()*1E9>>>0),Sa=0;function Ta(a,b,c){return a.call.apply(a.bind,arguments)}
function Ua(a,b,c){if(!a)throw Error();if(arguments.length>2){var d=Array.prototype.slice.call(arguments,2);return function(){var e=Array.prototype.slice.call(arguments);Array.prototype.unshift.apply(e,d);return a.apply(b,e)}}return function(){return a.apply(b,arguments)}}
function Va(a,b,c){Va=Function.prototype.bind&&Function.prototype.bind.toString().indexOf("native code")!=-1?Ta:Ua;return Va.apply(null,arguments)}
function Wa(a,b){var c=Array.prototype.slice.call(arguments,1);return function(){var d=c.slice();d.push.apply(d,arguments);return a.apply(this,d)}}
function Xa(){return Date.now()}
function Ya(a){return a}
function Za(a,b){function c(){}
c.prototype=b.prototype;a.Aa=b.prototype;a.prototype=new c;a.prototype.constructor=a;a.base=function(d,e,f){for(var g=Array(arguments.length-2),h=2;h<arguments.length;h++)g[h-2]=arguments[h];return b.prototype[e].apply(d,g)}}
;function ab(a){var b=C.apply(1,arguments).filter(Boolean).join("&");if(!b)return a;var c=a.match(/[?&]adurl=/);return c?a.slice(0,c.index+1)+b+"&"+a.slice(c.index+1):a+(a.indexOf("?")<0?"?":"&")+b}
function bb(a,b){return b?"&"+a+"="+encodeURIComponent(b):""}
function cb(a){var b=a.url;a=a.ji;this.i=b;this.o=a;this.j=(new Date).getTime()-17040672E5;this.h={};for(var c=/[?&]([^&=]+)=([^&]*)/g;a=c.exec(b);)this.h[a[1]]=a[2]}
function db(a){a=a.o;if(!a)return"";var b=bb("uap",a.platform)+bb("uapv",a.platformVersion)+bb("uafv",a.uaFullVersion)+bb("uaa",a.architecture)+bb("uam",a.model)+bb("uab",a.bitness);a.fullVersionList&&(b+="&uafvl="+encodeURIComponent(a.fullVersionList.map(function(c){return encodeURIComponent(c.brand)+";"+encodeURIComponent(c.version)}).join("|")));
a.wow64!=null&&(b+="&uaw="+Number(a.wow64));return b.slice(1)}
;function eb(a,b){if(Error.captureStackTrace)Error.captureStackTrace(this,eb);else{var c=Error().stack;c&&(this.stack=c)}a&&(this.message=String(a));b!==void 0&&(this.cause=b)}
Za(eb,Error);eb.prototype.name="CustomError";var fb=String.prototype.trim?function(a){return a.trim()}:function(a){return/^[\s\xa0]*([\s\S]*?)[\s\xa0]*$/.exec(a)[1]};/*

 Copyright Google LLC
 SPDX-License-Identifier: Apache-2.0
*/
var gb=globalThis.trustedTypes,hb;function ib(){var a=null;if(!gb)return a;try{var b=function(c){return c};
a=gb.createPolicy("goog#html",{createHTML:b,createScript:b,createScriptURL:b})}catch(c){}return a}
function jb(){hb===void 0&&(hb=ib());return hb}
;function kb(a){this.h=a}
kb.prototype.toString=function(){return this.h+""};
function lb(a){var b=jb();a=b?b.createScriptURL(a):a;return new kb(a)}
function nb(a){if(a instanceof kb)return a.h;throw Error("");}
;var ob=pa([""]),pb=qa(["\x00"],["\\0"]),qb=qa(["\n"],["\\n"]),rb=qa(["\x00"],["\\u0000"]);function sb(a){return a.toString().indexOf("`")===-1}
sb(function(a){return a(ob)})||sb(function(a){return a(pb)})||sb(function(a){return a(qb)})||sb(function(a){return a(rb)});function tb(a){this.h=a}
tb.prototype.toString=function(){return this.h};
var ub=new tb("about:invalid#zClosurez");function vb(a){this.Je=a}
function wb(a){return new vb(function(b){return b.substr(0,a.length+1).toLowerCase()===a+":"})}
var xb=[wb("data"),wb("http"),wb("https"),wb("mailto"),wb("ftp"),new vb(function(a){return/^[^:]*([/?#]|$)/.test(a)})],yb=/^\s*(?!javascript:)(?:[\w+.-]+:|[^:/?#]*(?:[/?#]|$))/i;
function zb(a){if(a instanceof tb)if(a instanceof tb)a=a.h;else throw Error("");else a=yb.test(a)?a:void 0;return a}
;function Ab(a,b){b=zb(b);b!==void 0&&(a.href=b)}
;function Bb(a,b){throw Error(b===void 0?"unexpected value "+a+"!":b);}
;function Cb(a){this.h=a}
Cb.prototype.toString=function(){return this.h+""};function Db(a){a=a===void 0?document:a;var b,c;a=(c=(b=a).querySelector)==null?void 0:c.call(b,"script[nonce]");return a==null?"":a.nonce||a.getAttribute("nonce")||""}
;function Eb(a){this.h=a}
Eb.prototype.toString=function(){return this.h+""};
function Fb(a){var b=jb();a=b?b.createScript(a):a;return new Eb(a)}
function Gb(a){if(a instanceof Eb)return a.h;throw Error("");}
;function Hb(a){var b=Db(a.ownerDocument);b&&a.setAttribute("nonce",b)}
function Ib(a,b){a.src=nb(b);Hb(a)}
;function Jb(){this.h=Kb[0].toLowerCase()}
Jb.prototype.toString=function(){return this.h};function Lb(a){var b="true".toString(),c=[new Jb];if(c.length===0)throw Error("");if(c.map(function(d){if(d instanceof Jb)d=d.h;else throw Error("");return d}).every(function(d){return"data-loaded".indexOf(d)!==0}))throw Error('Attribute "data-loaded" does not match any of the allowed prefixes.');
a.setAttribute("data-loaded",b)}
;var Mb="alternate author bookmark canonical cite help icon license modulepreload next prefetch dns-prefetch prerender preconnect preload prev search subresource".split(" ");function Nb(a,b){if(b instanceof kb)a.href=nb(b).toString(),a.rel="stylesheet";else{if(Mb.indexOf("stylesheet")===-1)throw Error('TrustedResourceUrl href attribute required with rel="stylesheet"');b=zb(b);b!==void 0&&(a.href=b,a.rel="stylesheet")}}
;var Ob=Array.prototype.indexOf?function(a,b){return Array.prototype.indexOf.call(a,b,void 0)}:function(a,b){if(typeof a==="string")return typeof b!=="string"||b.length!=1?-1:a.indexOf(b,0);
for(var c=0;c<a.length;c++)if(c in a&&a[c]===b)return c;return-1},Pb=Array.prototype.forEach?function(a,b){Array.prototype.forEach.call(a,b,void 0)}:function(a,b){for(var c=a.length,d=typeof a==="string"?a.split(""):a,e=0;e<c;e++)e in d&&b.call(void 0,d[e],e,a)},Rb=Array.prototype.filter?function(a,b){return Array.prototype.filter.call(a,b,void 0)}:function(a,b){for(var c=a.length,d=[],e=0,f=typeof a==="string"?a.split(""):a,g=0;g<c;g++)if(g in f){var h=f[g];
b.call(void 0,h,g,a)&&(d[e++]=h)}return d},Sb=Array.prototype.map?function(a,b){return Array.prototype.map.call(a,b,void 0)}:function(a,b){for(var c=a.length,d=Array(c),e=typeof a==="string"?a.split(""):a,f=0;f<c;f++)f in e&&(d[f]=b.call(void 0,e[f],f,a));
return d},Tb=Array.prototype.reduce?function(a,b,c){return Array.prototype.reduce.call(a,b,c)}:function(a,b,c){var d=c;
Pb(a,function(e,f){d=b.call(void 0,d,e,f,a)});
return d};
function Ub(a,b){a:{for(var c=a.length,d=typeof a==="string"?a.split(""):a,e=0;e<c;e++)if(e in d&&b.call(void 0,d[e],e,a)){b=e;break a}b=-1}return b<0?null:typeof a==="string"?a.charAt(b):a[b]}
function Vb(a,b){b=Ob(a,b);var c;(c=b>=0)&&Array.prototype.splice.call(a,b,1);return c}
function Wb(a){var b=a.length;if(b>0){for(var c=Array(b),d=0;d<b;d++)c[d]=a[d];return c}return[]}
function Xb(a,b){for(var c=1;c<arguments.length;c++){var d=arguments[c];if(La(d)){var e=a.length||0,f=d.length||0;a.length=e+f;for(var g=0;g<f;g++)a[e+g]=d[g]}else a.push(d)}}
function Yb(a,b){return a>b?1:a<b?-1:0}
;function Zb(a,b){a.__closure__error__context__984382||(a.__closure__error__context__984382={});a.__closure__error__context__984382.severity=b}
;function $b(a){var b=F("window.location.href");a==null&&(a='Unknown Error of type "null/undefined"');if(typeof a==="string")return{message:a,name:"Unknown error",lineNumber:"Not available",fileName:b,stack:"Not available"};var c=!1;try{var d=a.lineNumber||a.line||"Not available"}catch(g){d="Not available",c=!0}try{var e=a.fileName||a.filename||a.sourceURL||D.$googDebugFname||b}catch(g){e="Not available",c=!0}b=ac(a);if(!(!c&&a.lineNumber&&a.fileName&&a.stack&&a.message&&a.name)){c=a.message;if(c==
null){if(a.constructor&&a.constructor instanceof Function){if(a.constructor.name)c=a.constructor.name;else if(c=a.constructor,bc[c])c=bc[c];else{c=String(c);if(!bc[c]){var f=/function\s+([^\(]+)/m.exec(c);bc[c]=f?f[1]:"[Anonymous]"}c=bc[c]}c='Unknown Error of type "'+c+'"'}else c="Unknown Error of unknown type";typeof a.toString==="function"&&Object.prototype.toString!==a.toString&&(c+=": "+a.toString())}return{message:c,name:a.name||"UnknownError",lineNumber:d,fileName:e,stack:b||"Not available"}}return{message:a.message,
name:a.name,lineNumber:a.lineNumber,fileName:a.fileName,stack:b}}
function ac(a,b){b||(b={});b[cc(a)]=!0;var c=a.stack||"",d=a.cause;d&&!b[cc(d)]&&(c+="\nCaused by: ",d.stack&&d.stack.indexOf(d.toString())==0||(c+=typeof d==="string"?d:d.message+"\n"),c+=ac(d,b));a=a.errors;if(Array.isArray(a)){d=1;var e;for(e=0;e<a.length&&!(d>4);e++)b[cc(a[e])]||(c+="\nInner error "+d++ +": ",a[e].stack&&a[e].stack.indexOf(a[e].toString())==0||(c+=typeof a[e]==="string"?a[e]:a[e].message+"\n"),c+=ac(a[e],b));e<a.length&&(c+="\n... "+(a.length-e)+" more inner errors")}return c}
function cc(a){var b="";typeof a.toString==="function"&&(b=""+a);return b+a.stack}
var bc={};function dc(a){return decodeURIComponent(a.replace(/\+/g," "))}
function ec(a){for(var b=0,c=0;c<a.length;++c)b=31*b+a.charCodeAt(c)>>>0;return b}
;var fc=RegExp("^(?:([^:/?#.]+):)?(?://(?:([^\\\\/?#]*)@)?([^\\\\/?#]*?)(?::([0-9]+))?(?=[\\\\/?#]|$))?([^?#]+)?(?:\\?([^#]*))?(?:#([\\s\\S]*))?$");function hc(a){return a?decodeURI(a):a}
function ic(a){return hc(a.match(fc)[3]||null)}
function jc(a){return hc(a.match(fc)[5]||null)}
function kc(a){var b=a.match(fc);a=b[5];var c=b[6];b=b[7];var d="";a&&(d+=a);c&&(d+="?"+c);b&&(d+="#"+b);return d}
function lc(a){var b=a.indexOf("#");return b<0?a:a.slice(0,b)}
function mc(a,b){if(a){a=a.split("&");for(var c=0;c<a.length;c++){var d=a[c].indexOf("="),e=null;if(d>=0){var f=a[c].substring(0,d);e=a[c].substring(d+1)}else f=a[c];b(f,e?dc(e):"")}}}
function nc(a,b,c){if(Array.isArray(b))for(var d=0;d<b.length;d++)nc(a,String(b[d]),c);else b!=null&&c.push(a+(b===""?"":"="+encodeURIComponent(String(b))))}
function oc(a){var b=[],c;for(c in a)nc(c,a[c],b);return b.join("&")}
function pc(a,b){b=oc(b);if(b){var c=a.indexOf("#");c<0&&(c=a.length);var d=a.indexOf("?");if(d<0||d>c){d=c;var e=""}else e=a.substring(d+1,c);a=[a.slice(0,d),e,a.slice(c)];c=a[1];a[1]=b?c?c+"&"+b:b:c;b=a[0]+(a[1]?"?"+a[1]:"")+a[2]}else b=a;return b}
function qc(a,b,c,d){for(var e=c.length;(b=a.indexOf(c,b))>=0&&b<d;){var f=a.charCodeAt(b-1);if(f==38||f==63)if(f=a.charCodeAt(b+e),!f||f==61||f==38||f==35)return b;b+=e+1}return-1}
var rc=/#|$/,sc=/[?&]($|#)/;function tc(a,b){for(var c=a.search(rc),d=0,e,f=[];(e=qc(a,d,b,c))>=0;)f.push(a.substring(d,e)),d=Math.min(a.indexOf("&",e)+1||c,c);f.push(a.slice(d));return f.join("").replace(sc,"$1")}
;function uc(){try{var a,b;return!!((a=window)==null?0:(b=a.top)==null?0:b.location.href)&&!1}catch(c){return!0}}
;function vc(a){a&&typeof a.dispose=="function"&&a.dispose()}
;function wc(a){for(var b=0,c=arguments.length;b<c;++b){var d=arguments[b];La(d)?wc.apply(null,d):vc(d)}}
;function I(){this.ea=this.ea;this.H=this.H}
I.prototype.ea=!1;I.prototype.dispose=function(){this.ea||(this.ea=!0,this.ba())};
I.prototype[Symbol.dispose]=function(){this.dispose()};
function xc(a,b){a.addOnDisposeCallback(Wa(vc,b))}
I.prototype.addOnDisposeCallback=function(a,b){this.ea?b!==void 0?a.call(b):a():(this.H||(this.H=[]),b&&(a=a.bind(b)),this.H.push(a))};
I.prototype.ba=function(){if(this.H)for(;this.H.length;)this.H.shift()()};function yc(){var a=zc();a=a===void 0?"bevasrsg":a;return new Promise(function(b){var c=window===window.top?window:uc()?window:window.top,d=c[a],e;((e=d)==null?0:e.bevasrs)?b(new Ac(d.bevasrs)):(d||(d={},d=(d.nqfbel=[],d),c[a]=d),d.nqfbel.push(function(f){b(new Ac(f))}))})}
function Ac(a){I.call(this);var b=this;this.vm=a;this.i="keydown keypress keyup input focusin focusout select copy cut paste change click dblclick auxclick pointerover pointerdown pointerup pointermove pointerout dragenter dragleave drag dragend mouseover mousedown mouseup mousemove mouseout touchstart touchend touchmove wheel".split(" ");this.h=void 0;this.hd=this.vm.p;this.j=this.o.bind(this);this.addOnDisposeCallback(function(){return void Bc(b)})}
v(Ac,I);Ac.prototype.snapshot=function(a){return this.vm.s(Object.assign({},a.Pb&&{c:a.Pb},a.kd&&{s:a.kd},a.ld!==void 0&&{p:a.ld}))};
Ac.prototype.o=function(a){this.vm.e(a)};
function Bc(a){a.h!==void 0&&(a.i.forEach(function(b){var c;(c=a.h)==null||c.removeEventListener(b,a.j)}),a.h=void 0)}
;function Cc(a){var b=b===void 0?50:b;var c=[];Dc(a,Ec,6).forEach(function(d){Fc(d,2)<=b&&c.push(Fc(d,1))});
return c}
function Gc(a){var b=b===void 0?50:b;var c=[];Dc(a,Ec,6).forEach(function(d){Fc(d,2)>b&&c.push(Fc(d,1))});
return c}
;function Hc(){I.apply(this,arguments);this.i=1}
v(Hc,I);Hc.prototype.share=function(){if(this.ea)throw Error("E:AD");this.i++;return this};
Hc.prototype.dispose=function(){--this.i||I.prototype.dispose.call(this)};function Ic(a){return{fieldType:2,fieldName:a}}
function Jc(a){return{fieldType:3,fieldName:a}}
;function Kc(a){this.h=a;a.Kc("/client_streamz/bg/frs",Jc("mk"))}
Kc.prototype.record=function(a,b){this.h.record("/client_streamz/bg/frs",a,b)};
function Lc(a){this.h=a;a.Kc("/client_streamz/bg/wrl",Jc("mn"),Ic("ac"),Ic("sc"),Jc("rk"),Jc("mk"))}
Lc.prototype.record=function(a,b,c,d,e,f){this.h.record("/client_streamz/bg/wrl",a,b,c,d,e,f)};
function Mc(a){this.h=a;a.Mb("/client_streamz/bg/ec",Jc("en"),Jc("mk"))}
Mc.prototype.kb=function(a,b){this.h.Jb("/client_streamz/bg/ec",a,b)};
function Nc(a){this.h=a;a.Kc("/client_streamz/bg/el",Jc("en"),Jc("mk"))}
Nc.prototype.record=function(a,b,c){this.h.record("/client_streamz/bg/el",a,b,c)};
function Oc(a){this.h=a;a.Mb("/client_streamz/bg/cec",Ic("ec"),Jc("mk"))}
Oc.prototype.kb=function(a,b){this.h.Jb("/client_streamz/bg/cec",a,b)};
function Pc(a){this.h=a;a.Mb("/client_streamz/bg/po/csc",Ic("cs"),Jc("mk"))}
Pc.prototype.kb=function(a,b){this.h.Jb("/client_streamz/bg/po/csc",a,b)};
function Qc(a){this.h=a;a.Mb("/client_streamz/bg/po/ctav",Jc("av"),Jc("mk"))}
Qc.prototype.kb=function(a,b){this.h.Jb("/client_streamz/bg/po/ctav",a,b)};
function Rc(a){this.h=a;a.Mb("/client_streamz/bg/po/cwsc",Jc("su"),Jc("mk"))}
Rc.prototype.kb=function(a,b){this.h.Jb("/client_streamz/bg/po/cwsc",a,b)};function Sc(a){D.setTimeout(function(){throw a;},0)}
;var Tc=Ja(610401301,!1),Uc=Ja(748402147,Ja(1,!0));function Vc(){var a=D.navigator;return a&&(a=a.userAgent)?a:""}
var Wc,Xc=D.navigator;Wc=Xc?Xc.userAgentData||null:null;function Yc(a){if(!Tc||!Wc)return!1;for(var b=0;b<Wc.brands.length;b++){var c=Wc.brands[b].brand;if(c&&c.indexOf(a)!=-1)return!0}return!1}
function J(a){return Vc().indexOf(a)!=-1}
;function Zc(){return Tc?!!Wc&&Wc.brands.length>0:!1}
function $c(){return Zc()?!1:J("Opera")}
function ad(){return J("Firefox")||J("FxiOS")}
function bd(){return Zc()?Yc("Chromium"):(J("Chrome")||J("CriOS"))&&!(Zc()?0:J("Edge"))||J("Silk")}
;function cd(){return Tc?!!Wc&&!!Wc.platform:!1}
function dd(){return J("iPhone")&&!J("iPod")&&!J("iPad")}
;function ed(a){ed[" "](a);return a}
ed[" "]=function(){};var fd=$c(),gd=Zc()?!1:J("Trident")||J("MSIE"),hd=J("Edge"),id=J("Gecko")&&!(Vc().toLowerCase().indexOf("webkit")!=-1&&!J("Edge"))&&!(J("Trident")||J("MSIE"))&&!J("Edge"),jd=Vc().toLowerCase().indexOf("webkit")!=-1&&!J("Edge");jd&&J("Mobile");cd()||J("Macintosh");cd()||J("Windows");(cd()?Wc.platform==="Linux":J("Linux"))||cd()||J("CrOS");var kd=cd()?Wc.platform==="Android":J("Android");dd();J("iPad");J("iPod");dd()||J("iPad")||J("iPod");Vc().toLowerCase().indexOf("kaios");ad();var ld=dd()||J("iPod"),md=J("iPad");!J("Android")||bd()||ad()||$c()||J("Silk");bd();var nd=J("Safari")&&!(bd()||(Zc()?0:J("Coast"))||$c()||(Zc()?0:J("Edge"))||(Zc()?Yc("Microsoft Edge"):J("Edg/"))||(Zc()?Yc("Opera"):J("OPR"))||ad()||J("Silk")||J("Android"))&&!(dd()||J("iPad")||J("iPod"));var od={},pd=null;function qd(a,b){La(a);b===void 0&&(b=0);rd();b=od[b];for(var c=Array(Math.floor(a.length/3)),d=b[64]||"",e=0,f=0;e<a.length-2;e+=3){var g=a[e],h=a[e+1],k=a[e+2],l=b[g>>2];g=b[(g&3)<<4|h>>4];h=b[(h&15)<<2|k>>6];k=b[k&63];c[f++]=""+l+g+h+k}l=0;k=d;switch(a.length-e){case 2:l=a[e+1],k=b[(l&15)<<2]||d;case 1:a=a[e],c[f]=""+b[a>>2]+b[(a&3)<<4|l>>4]+k+d}return c.join("")}
function sd(a){var b=a.length,c=b*3/4;c%3?c=Math.floor(c):"=.".indexOf(a[b-1])!=-1&&(c="=.".indexOf(a[b-2])!=-1?c-2:c-1);var d=new Uint8Array(c),e=0;td(a,function(f){d[e++]=f});
return e!==c?d.subarray(0,e):d}
function td(a,b){function c(k){for(;d<a.length;){var l=a.charAt(d++),m=pd[l];if(m!=null)return m;if(!/^[\s\xa0]*$/.test(l))throw Error("Unknown base64 encoding at char: "+l);}return k}
rd();for(var d=0;;){var e=c(-1),f=c(0),g=c(64),h=c(64);if(h===64&&e===-1)break;b(e<<2|f>>4);g!=64&&(b(f<<4&240|g>>2),h!=64&&b(g<<6&192|h))}}
function rd(){if(!pd){pd={};for(var a="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789".split(""),b=["+/=","+/","-_=","-_.","-_"],c=0;c<5;c++){var d=a.concat(b[c].split(""));od[c]=d;for(var e=0;e<d.length;e++){var f=d[e];pd[f]===void 0&&(pd[f]=e)}}}}
;var ud=typeof Uint8Array!=="undefined",vd=!gd&&typeof btoa==="function",wd=/[-_.]/g,xd={"-":"+",_:"/",".":"="};function yd(a){return xd[a]||""}
var zd={};function Ad(a,b){Bd(b);this.h=a;if(a!=null&&a.length===0)throw Error("ByteString should be constructed with non-empty values");}
Ad.prototype.sizeBytes=function(){Bd(zd);var a=this.h;if(!(a==null||ud&&a!=null&&a instanceof Uint8Array))if(typeof a==="string")if(vd){a=wd.test(a)?a.replace(wd,yd):a;a=atob(a);for(var b=new Uint8Array(a.length),c=0;c<a.length;c++)b[c]=a.charCodeAt(c);a=b}else a=sd(a);else Ka(a),a=null;return(a=a==null?a:this.h=a)?a.length:0};
var Cd;function Bd(a){if(a!==zd)throw Error("illegal external caller");}
;var Dd=void 0;function Ed(a){a=Error(a);Zb(a,"warning");return a}
function Fd(a,b){if(a!=null){var c;var d=(c=Dd)!=null?c:Dd={};c=d[a]||0;c>=b||(d[a]=c+1,a=Error(),Zb(a,"incident"),Sc(a))}}
;var Gd=typeof Symbol==="function"&&typeof Symbol()==="symbol";function Hd(a,b,c){return typeof Symbol==="function"&&typeof Symbol()==="symbol"?(c===void 0?0:c)&&Symbol.for&&a?Symbol.for(a):a!=null?Symbol(a):Symbol():b}
var Id=Hd("jas",void 0,!0),Jd=Hd(void 0,"1oa"),Kd=Hd(void 0,Symbol()),Ld=Hd(void 0,"0ub"),Md=Hd(void 0,"0ubs"),Nd=Hd(void 0,"0actk"),Od=Hd("m_m","Sh",!0),Pd=Hd(void 0,"vps"),Qd=Hd();Math.max.apply(Math,A(Object.values({sh:1,rh:2,qh:4,wh:8,yh:16,th:32,Sf:64,oh:128,Xf:256,xh:512,Yf:1024,ph:2048,uh:4096})));var Rd={Ie:{value:0,configurable:!0,writable:!0,enumerable:!1}},Sd=Object.defineProperties,K=Gd?Id:"Ie",Td,Ud=[];Vd(Ud,7);Td=Object.freeze(Ud);function Wd(a,b){Gd||K in a||Sd(a,Rd);a[K]|=b}
function Vd(a,b){Gd||K in a||Sd(a,Rd);a[K]=b}
;function Xd(){return typeof BigInt==="function"}
;var Yd={};function Zd(a,b){if(b===void 0){if(b=a.h!==$d)b=!!(2&(a.F[K]|0));return b}return!!(2&b)&&a.h!==$d}
var $d={},ae=Object.freeze({}),be={};function ce(a){a.Nh=!0;return a}
;var de=ce(function(a){return typeof a==="number"}),ee=ce(function(a){return typeof a==="string"}),fe=ce(function(a){return typeof a==="boolean"});
function ge(){var a=he;return ce(function(b){for(var c in a)if(b===a[c]&&!/^[0-9]+$/.test(c))return!0;return!1})}
var ie=ce(function(a){return a!=null&&typeof a==="object"&&typeof a.then==="function"});var je=typeof D.BigInt==="function"&&typeof D.BigInt(0)==="bigint";function ke(a){var b=a;if(ee(b)){if(!/^\s*(?:-?[1-9]\d*|0)?\s*$/.test(b))throw Error(String(b));}else if(de(b)&&!Number.isSafeInteger(b))throw Error(String(b));return je?BigInt(a):a=fe(a)?a?"1":"0":ee(a)?a.trim()||"0":String(a)}
var qe=ce(function(a){return je?a>=le&&a<=me:a[0]==="-"?ne(a,oe):ne(a,pe)}),oe=Number.MIN_SAFE_INTEGER.toString(),le=je?BigInt(Number.MIN_SAFE_INTEGER):void 0,pe=Number.MAX_SAFE_INTEGER.toString(),me=je?BigInt(Number.MAX_SAFE_INTEGER):void 0;
function ne(a,b){if(a.length>b.length)return!1;if(a.length<b.length||a===b)return!0;for(var c=0;c<a.length;c++){var d=a[c],e=b[c];if(d>e)return!1;if(d<e)return!0}}
;var re=0,se=0;function te(a){var b=a>>>0;re=b;se=(a-b)/4294967296>>>0}
function ue(a){if(a<0){te(0-a);var b=y(ve(re,se));a=b.next().value;b=b.next().value;re=a>>>0;se=b>>>0}else te(a)}
function we(a,b){b>>>=0;a>>>=0;if(b<=2097151)var c=""+(4294967296*b+a);else Xd()?c=""+(BigInt(b)<<BigInt(32)|BigInt(a)):(c=(a>>>24|b<<8)&16777215,b=b>>16&65535,a=(a&16777215)+c*6777216+b*6710656,c+=b*8147497,b*=2,a>=1E7&&(c+=a/1E7>>>0,a%=1E7),c>=1E7&&(b+=c/1E7>>>0,c%=1E7),c=b+xe(c)+xe(a));return c}
function xe(a){a=String(a);return"0000000".slice(a.length)+a}
function ye(){var a=re,b=se;b&2147483648?Xd()?a=""+(BigInt(b|0)<<BigInt(32)|BigInt(a>>>0)):(b=y(ve(a,b)),a=b.next().value,b=b.next().value,a="-"+we(a,b)):a=we(a,b);return a}
function ve(a,b){b=~b;a?a=~a+1:b+=1;return[a,b]}
;function ze(a){return Array.prototype.slice.call(a)}
;var Ae=typeof BigInt==="function"?BigInt.asIntN:void 0,Be=Number.isSafeInteger,Ce=Number.isFinite,De=Math.trunc;function Ee(a){return a.displayName||a.name||"unknown type name"}
function Fe(a){if(a!=null&&typeof a!=="boolean")throw Error("Expected boolean but got "+Ka(a)+": "+a);return a}
var Ge=/^-?([1-9][0-9]*|0)(\.[0-9]+)?$/;function He(a){switch(typeof a){case "bigint":return!0;case "number":return Ce(a);case "string":return Ge.test(a);default:return!1}}
function Ie(a){if(typeof a!=="number")throw Ed("int32");if(!Ce(a))throw Ed("int32");return a|0}
function Je(a){return a==null?a:Ie(a)}
function Ke(a){if(a==null)return a;if(typeof a==="string"&&a)a=+a;else if(typeof a!=="number")return;return Ce(a)?a|0:void 0}
function Le(a){var b=0;b=b===void 0?0:b;if(!He(a))throw Ed("int64");var c=typeof a;switch(b){case 512:switch(c){case "string":return Me(a);case "bigint":return String(Ae(64,a));default:return Ne(a)}case 1024:switch(c){case "string":return Oe(a);case "bigint":return ke(Ae(64,a));default:return Pe(a)}case 0:switch(c){case "string":return Me(a);case "bigint":return ke(Ae(64,a));default:return Qe(a)}default:return Bb(b,"Unknown format requested type for int64")}}
function Re(a){return a==null?a:Le(a)}
function Se(a){var b=a.length;return a[0]==="-"?b<20?!0:b===20&&Number(a.substring(0,7))>-922337:b<19?!0:b===19&&Number(a.substring(0,6))<922337}
function Te(a){a.indexOf(".");if(Se(a))return a;if(a.length<16)ue(Number(a));else if(Xd())a=BigInt(a),re=Number(a&BigInt(4294967295))>>>0,se=Number(a>>BigInt(32)&BigInt(4294967295));else{var b=+(a[0]==="-");se=re=0;for(var c=a.length,d=0+b,e=(c-b)%6+b;e<=c;d=e,e+=6)d=Number(a.slice(d,e)),se*=1E6,re=re*1E6+d,re>=4294967296&&(se+=Math.trunc(re/4294967296),se>>>=0,re>>>=0);b&&(b=y(ve(re,se)),a=b.next().value,b=b.next().value,re=a,se=b)}return ye()}
function Qe(a){He(a);a=De(a);if(!Be(a)){ue(a);var b=re,c=se;if(a=c&2147483648)b=~b+1>>>0,c=~c>>>0,b==0&&(c=c+1>>>0);var d=c*4294967296+(b>>>0);b=Number.isSafeInteger(d)?d:we(b,c);a=typeof b==="number"?a?-b:b:a?"-"+b:b}return a}
function Ne(a){He(a);a=De(a);if(Be(a))a=String(a);else{var b=String(a);Se(b)?a=b:(ue(a),a=ye())}return a}
function Me(a){He(a);var b=De(Number(a));if(Be(b))return String(b);b=a.indexOf(".");b!==-1&&(a=a.substring(0,b));return Te(a)}
function Oe(a){var b=De(Number(a));if(Be(b))return ke(b);b=a.indexOf(".");b!==-1&&(a=a.substring(0,b));return Xd()?ke(Ae(64,BigInt(a))):ke(Te(a))}
function Pe(a){return Be(a)?ke(Qe(a)):ke(Ne(a))}
function Ue(a){if(typeof a!=="string")throw Error();return a}
function Ve(a){if(a!=null&&typeof a!=="string")throw Error();return a}
function We(a){return a==null||typeof a==="string"?a:void 0}
function Xe(a,b){if(!(a instanceof b))throw Error("Expected instanceof "+Ee(b)+" but got "+(a&&Ee(a.constructor)));}
function Ye(a,b,c){if(a!=null&&a[Od]===Yd)return a;if(Array.isArray(a)){var d=a[K]|0;c=d|c&32|c&2;c!==d&&Vd(a,c);return new b(a)}}
;var Ze={};function $e(a){return a}
;var af={bi:!0};function bf(a,b){b<100||Fd(Md,1)}
;function cf(a,b,c,d){var e=d!==void 0;d=!!d;var f=Ya(Kd),g;!e&&Gd&&f&&(g=a[f])&&g.Kh(bf);f=[];var h=a.length;g=4294967295;var k=!1,l=!!(b&64),m=l?b&128?0:-1:void 0;if(!(b&1)){var n=h&&a[h-1];n!=null&&typeof n==="object"&&n.constructor===Object?(h--,g=h):n=void 0;if(l&&!(b&128)&&!e){k=!0;var r;g=((r=df)!=null?r:$e)(g-m,m,a,n,void 0)+m}}b=void 0;for(e=0;e<h;e++)if(r=a[e],r!=null&&(r=c(r,d))!=null)if(l&&e>=g){var t=e-m,w=void 0;((w=b)!=null?w:b={})[t]=r}else f[e]=r;if(n)for(var x in n)a=n[x],a!=null&&
(a=c(a,d))!=null&&(h=+x,e=void 0,l&&!Number.isNaN(h)&&(e=h+m)<g?f[e]=a:(h=void 0,((h=b)!=null?h:b={})[x]=a));b&&(k?f.push(b):f[g]=b);return f}
function ef(a){switch(typeof a){case "number":return Number.isFinite(a)?a:""+a;case "bigint":return qe(a)?Number(a):""+a;case "boolean":return a?1:0;case "object":if(Array.isArray(a)){var b=a[K]|0;return a.length===0&&b&1?void 0:cf(a,b,ef)}if(a!=null&&a[Od]===Yd)return ff(a);if(a instanceof Ad){b=a.h;if(b==null)a="";else if(typeof b==="string")a=b;else{if(vd){for(var c="",d=0,e=b.length-10240;d<e;)c+=String.fromCharCode.apply(null,b.subarray(d,d+=10240));c+=String.fromCharCode.apply(null,d?b.subarray(d):
b);b=btoa(c)}else b=qd(b);a=a.h=b}return a}return}return a}
var df;function gf(a,b){if(b){df=b==null||b===$e||b[Pd]!==Ze?$e:b;try{return ff(a)}finally{df=void 0}}return ff(a)}
function ff(a){a=a.F;return cf(a,a[K]|0,ef)}
;function L(a,b,c){var d=d===void 0?0:d;if(a==null){var e=32;c?(a=[c],e|=128):a=[];b&&(e=e&-8380417|(b&1023)<<13)}else{if(!Array.isArray(a))throw Error("narr");e=a[K]|0;if(Uc&&1&e)throw Error("rfarr");2048&e&&!(2&e)&&hf();if(e&256)throw Error("farr");if(e&64)return d!==0||e&2048||Vd(a,e|2048),a;if(c&&(e|=128,c!==a[0]))throw Error("mid");a:{c=a;e|=64;var f=c.length;if(f){var g=f-1,h=c[g];if(h!=null&&typeof h==="object"&&h.constructor===Object){b=e&128?0:-1;g-=b;if(g>=1024)throw Error("pvtlmt");for(var k in h)f=
+k,f<g&&(c[f+b]=h[k],delete h[k]);e=e&-8380417|(g&1023)<<13;break a}}if(b){k=Math.max(b,f-(e&128?0:-1));if(k>1024)throw Error("spvt");e=e&-8380417|(k&1023)<<13}}}e|=64;d===0&&(e|=2048);Vd(a,e);return a}
function hf(){if(Uc)throw Error("carr");Fd(Nd,5)}
;function jf(a,b){if(typeof a!=="object")return a;if(Array.isArray(a)){var c=a[K]|0;a.length===0&&c&1?a=void 0:c&2||(!b||4096&c||16&c?a=kf(a,c,!1,b&&!(c&16)):(Wd(a,34),c&4&&Object.freeze(a)));return a}if(a!=null&&a[Od]===Yd)return b=a.F,c=b[K]|0,Zd(a,c)?a:lf(a,b,c)?mf(a,b):kf(b,c);if(a instanceof Ad)return a}
function mf(a,b,c){a=new a.constructor(b);c&&(a.h=$d);a.i=$d;return a}
function kf(a,b,c,d){d!=null||(d=!!(34&b));a=cf(a,b,jf,d);d=32;c&&(d|=2);b=b&8380609|d;Vd(a,b);return a}
function nf(a){var b=a.F,c=b[K]|0;return Zd(a,c)?lf(a,b,c)?mf(a,b,!0):new a.constructor(kf(b,c,!1)):a}
function of(a){if(a.h!==$d)return!1;var b=a.F;b=kf(b,b[K]|0);Wd(b,2048);a.F=b;a.h=void 0;a.i=void 0;return!0}
function pf(a){if(!of(a)&&Zd(a,a.F[K]|0))throw Error();}
function qf(a,b){b===void 0&&(b=a[K]|0);b&32&&!(b&4096)&&Vd(a,b|4096)}
function lf(a,b,c){return c&2?!0:c&32&&!(c&4096)?(Vd(b,c|2),a.h=$d,!0):!1}
;var rf=ke(0),sf={};function tf(a,b,c,d){Object.isExtensible(a);b=uf(a.F,b,c);if(b!==null||d&&a.i!==$d)return b}
function uf(a,b,c,d){if(b===-1)return null;var e=b+(c?0:-1),f=a.length-1;if(!(f<1+(c?0:-1))){if(e>=f){var g=a[f];if(g!=null&&typeof g==="object"&&g.constructor===Object){c=g[b];var h=!0}else if(e===f)c=g;else return}else c=a[e];if(d&&c!=null){d=d(c);if(d==null)return d;if(!Object.is(d,c))return h?g[b]=d:a[e]=d,d}return c}}
function vf(a,b,c,d){pf(a);var e=a.F;wf(e,e[K]|0,b,c,d);return a}
function wf(a,b,c,d,e){var f=c+(e?0:-1),g=a.length-1;if(g>=1+(e?0:-1)&&f>=g){var h=a[g];if(h!=null&&typeof h==="object"&&h.constructor===Object)return h[c]=d,b}if(f<=g)return a[f]=d,b;if(d!==void 0){var k;g=((k=b)!=null?k:b=a[K]|0)>>13&1023||536870912;c>=g?d!=null&&(f={},a[g+(e?0:-1)]=(f[c]=d,f)):a[f]=d}return b}
function xf(a){return!!(2&a)&&!!(4&a)||!!(256&a)}
function yf(a,b,c){pf(a);var d=a.F,e=d[K]|0;if(b==null)return wf(d,e,3),a;if(!Array.isArray(b))throw Ed();var f=b===Td?7:b[K]|0,g=f,h=xf(f),k=h||Object.isFrozen(b);h||(f=0);k||(b=ze(b),g=0,f=zf(f,e),k=!1);f|=5;h=4&f?512&f?512:1024&f?1024:0:void 0;h=h!=null?h:0;for(var l=0;l<b.length;l++){var m=b[l],n=c(m,h);Object.is(m,n)||(k&&(b=ze(b),g=0,f=zf(f,e),k=!1),b[l]=n)}f!==g&&(k&&(b=ze(b),f=zf(f,e)),Vd(b,f));wf(d,e,3,b);return a}
function Af(a,b,c,d){pf(a);a=a.F;var e=a[K]|0;if(d==null){var f=Bf(a);if(Cf(f,a,e,c)===b)f.set(c,0);else return}else{b===0||c.includes(b);f=Bf(a);var g=Cf(f,a,e,c);g!==b&&(g&&(e=wf(a,e,g)),f.set(c,b))}wf(a,e,b,d)}
function Bf(a){if(Gd){var b;return(b=a[Jd])!=null?b:a[Jd]=new Map}if(Jd in a)return a[Jd];b=new Map;Object.defineProperty(a,Jd,{value:b});return b}
function Cf(a,b,c,d){var e=a.get(d);if(e!=null)return e;for(var f=e=0;f<d.length;f++){var g=d[f];uf(b,g)!=null&&(e!==0&&(c=wf(b,c,e)),e=g)}a.set(d,e);return e}
function Df(a,b,c,d,e){var f=!1;d=uf(a,d,e,function(g){var h=Ye(g,c,b);f=h!==g&&h!=null;return h});
if(d!=null)return f&&!Zd(d)&&qf(a,b),d}
function Ef(a,b,c,d){var e=a.F,f=e[K]|0;b=Df(e,f,b,c,d);if(b==null)return b;f=e[K]|0;if(!Zd(a,f)){var g=nf(b);g!==b&&(of(a)&&(e=a.F,f=e[K]|0),b=g,f=wf(e,f,c,b,d),qf(e,f))}return b}
function Dc(a,b,c){var d=void 0===ae?2:4;var e=a.F,f=e,g=e[K]|0;e=!1;var h=Zd(a,g);d=h?1:d;e=!!e||d===3;var k=!h;(d===2||k)&&of(a)&&(f=a.F,g=f[K]|0);a=uf(f,c);h=Array.isArray(a)?a:Td;var l=h===Td?7:h[K]|0;a=l;2&g&&(a|=2);var m=a|1;if(a=!(4&m)){var n=h,r=g,t=!!(2&m);t&&(r|=2);for(var w=!t,x=!0,z=0,G=0;z<n.length;z++){var H=Ye(n[z],b,r);if(H instanceof b){if(!t){var U=Zd(H);w&&(w=!U);x&&(x=U)}n[G++]=H}}G<z&&(n.length=G);m|=4;m=x?m&-4097:m|4096;m=w?m|8:m&-9}m!==l&&(Vd(h,m),2&m&&Object.freeze(h));if(k&&
!(8&m||!h.length&&(d===1||(d!==4?0:2&m||!(16&m)&&32&g)))){xf(m)&&(h=ze(h),m=zf(m,g),g=wf(f,g,c,h));b=h;k=m;for(l=0;l<b.length;l++)n=b[l],m=nf(n),n!==m&&(b[l]=m);k|=8;m=k=b.length?k|4096:k&-4097;Vd(h,m)}b=h;k=h=m;d===1||(d!==4?0:2&h||!(16&h)&&32&g)?xf(h)||(h|=!b.length||a&&!(4096&h)||32&g&&!(4096&h||16&h)?2:256,h!==k&&Vd(b,h),Object.freeze(b)):(d===2&&xf(h)&&(b=ze(b),k=0,h=zf(h,g),g=wf(f,g,c,b)),xf(h)||(e||(h|=16),h!==k&&Vd(b,h)));2&h||!(4096&h||16&h)||qf(f,g);return b}
function Ff(a,b,c,d,e){d!=null?Xe(d,b):d=void 0;vf(a,c,d,e);d&&!Zd(d)&&qf(a.F);return a}
function Gf(a,b,c,d){pf(a);var e=a.F,f=e[K]|0;if(d==null)return wf(e,f,c),a;if(!Array.isArray(d))throw Ed();for(var g=d===Td?7:d[K]|0,h=g,k=xf(g),l=k||Object.isFrozen(d),m=!0,n=!0,r=0;r<d.length;r++){var t=d[r];Xe(t,b);k||(t=Zd(t),m&&(m=!t),n&&(n=t))}k||(g=m?13:5,g=n?g&-4097:g|4096);l&&g===h||(d=ze(d),h=0,g=zf(g,f));g!==h&&Vd(d,g);f=wf(e,f,c,d);2&g||!(4096&g||16&g)||qf(e,f);return a}
function zf(a,b){return a=(2&b?a|2:a&-3)&-273}
function Fc(a,b,c){c=c===void 0?0:c;a=Ke(tf(a,b));return a!=null?a:c}
function Hf(a,b,c){c=c===void 0?rf:c;a=tf(a,b);b=typeof a;a=a==null?a:b==="bigint"?ke(Ae(64,a)):He(a)?b==="string"?Oe(a):Pe(a):void 0;return a!=null?a:c}
function If(a,b,c,d){c=c===void 0?"":c;var e;return(e=We(tf(a,b,d)))!=null?e:c}
function Jf(a){var b=b===void 0?0:b;a=tf(a,1);a=a==null?a:Ce(a)?a|0:void 0;return a!=null?a:b}
function Kf(a,b,c){return vf(a,b,Ve(c))}
function Lf(a,b,c){c=Ve(c);pf(a);a=a.F;wf(a,a[K]|0,b,c===""?void 0:c,be)}
function Mf(a,b,c){if(c!=null){if(!Ce(c))throw Ed("enum");c|=0}return vf(a,b,c)}
;function M(a,b,c){this.F=L(a,b,c)}
M.prototype.toJSON=function(){return gf(this)};
M.prototype.serialize=function(a){return JSON.stringify(gf(this,a))};
function Nf(a,b){if(b==null||b=="")return new a;b=JSON.parse(b);if(!Array.isArray(b))throw Error("dnarr");Wd(b,32);return new a(b)}
M.prototype.clone=function(){var a=this.F,b=a[K]|0;return lf(this,a,b)?mf(this,a,!0):new this.constructor(kf(a,b,!1))};
M.prototype[Od]=Yd;M.prototype.toString=function(){return this.F.toString()};function Of(){var a=Pf;this.ctor=Qf;this.isRepeated=0;this.h=Ef;this.defaultValue=void 0;this.i=a.Pe!=null?be:void 0}
Of.prototype.register=function(){ed(this)};function Rf(a){return function(b){return Nf(a,b)}}
;function Sf(a){this.F=L(a)}
v(Sf,M);function Tf(a,b){return yf(a,b,Ie)}
;function Uf(a){this.F=L(a)}
v(Uf,M);var Vf=[1,2,3];function Wf(a){this.F=L(a)}
v(Wf,M);var Xf=[1,2,3];function Yf(a){this.F=L(a)}
v(Yf,M);function Zf(a){this.F=L(a)}
v(Zf,M);function $f(a){this.F=L(a)}
v($f,M);function ag(a){if(!a)return"";if(/^about:(?:blank|srcdoc)$/.test(a))return window.origin||"";a.indexOf("blob:")===0&&(a=a.substring(5));a=a.split("#")[0].split("?")[0];a=a.toLowerCase();a.indexOf("//")==0&&(a=window.location.protocol+a);/^[\w\-]*:\/\//.test(a)||(a=window.location.href);var b=a.substring(a.indexOf("://")+3),c=b.indexOf("/");c!=-1&&(b=b.substring(0,c));c=a.substring(0,a.indexOf("://"));if(!c)throw Error("URI is missing protocol: "+a);if(c!=="http"&&c!=="https"&&c!=="chrome-extension"&&
c!=="moz-extension"&&c!=="file"&&c!=="android-app"&&c!=="chrome-search"&&c!=="chrome-untrusted"&&c!=="chrome"&&c!=="app"&&c!=="devtools")throw Error("Invalid URI scheme in origin: "+c);a="";var d=b.indexOf(":");if(d!=-1){var e=b.substring(d+1);b=b.substring(0,d);if(c==="http"&&e!=="80"||c==="https"&&e!=="443")a=":"+e}return c+"://"+b+a}
;function bg(){function a(){e[0]=1732584193;e[1]=4023233417;e[2]=2562383102;e[3]=271733878;e[4]=3285377520;m=l=0}
function b(n){for(var r=g,t=0;t<64;t+=4)r[t/4]=n[t]<<24|n[t+1]<<16|n[t+2]<<8|n[t+3];for(t=16;t<80;t++)n=r[t-3]^r[t-8]^r[t-14]^r[t-16],r[t]=(n<<1|n>>>31)&4294967295;n=e[0];var w=e[1],x=e[2],z=e[3],G=e[4];for(t=0;t<80;t++){if(t<40)if(t<20){var H=z^w&(x^z);var U=1518500249}else H=w^x^z,U=1859775393;else t<60?(H=w&x|z&(w|x),U=2400959708):(H=w^x^z,U=3395469782);H=((n<<5|n>>>27)&4294967295)+H+G+U+r[t]&4294967295;G=z;z=x;x=(w<<30|w>>>2)&4294967295;w=n;n=H}e[0]=e[0]+n&4294967295;e[1]=e[1]+w&4294967295;e[2]=
e[2]+x&4294967295;e[3]=e[3]+z&4294967295;e[4]=e[4]+G&4294967295}
function c(n,r){if(typeof n==="string"){n=unescape(encodeURIComponent(n));for(var t=[],w=0,x=n.length;w<x;++w)t.push(n.charCodeAt(w));n=t}r||(r=n.length);t=0;if(l==0)for(;t+64<r;)b(n.slice(t,t+64)),t+=64,m+=64;for(;t<r;)if(f[l++]=n[t++],m++,l==64)for(l=0,b(f);t+64<r;)b(n.slice(t,t+64)),t+=64,m+=64}
function d(){var n=[],r=m*8;l<56?c(h,56-l):c(h,64-(l-56));for(var t=63;t>=56;t--)f[t]=r&255,r>>>=8;b(f);for(t=r=0;t<5;t++)for(var w=24;w>=0;w-=8)n[r++]=e[t]>>w&255;return n}
for(var e=[],f=[],g=[],h=[128],k=1;k<64;++k)h[k]=0;var l,m;a();return{reset:a,update:c,digest:d,ne:function(){for(var n=d(),r="",t=0;t<n.length;t++)r+="0123456789ABCDEF".charAt(Math.floor(n[t]/16))+"0123456789ABCDEF".charAt(n[t]%16);return r}}}
;function cg(a,b,c){var d=String(D.location.href);return d&&a&&b?[b,dg(ag(d),a,c||null)].join(" "):null}
function dg(a,b,c){var d=[],e=[];if((Array.isArray(c)?2:1)==1)return e=[b,a],Pb(d,function(h){e.push(h)}),eg(e.join(" "));
var f=[],g=[];Pb(c,function(h){g.push(h.key);f.push(h.value)});
c=Math.floor((new Date).getTime()/1E3);e=f.length==0?[c,b,a]:[f.join(":"),c,b,a];Pb(d,function(h){e.push(h)});
a=eg(e.join(" "));a=[c,a];g.length==0||a.push(g.join(""));return a.join("_")}
function eg(a){var b=bg();b.update(a);return b.ne().toLowerCase()}
;function fg(a){this.h=a||{cookie:""}}
p=fg.prototype;p.isEnabled=function(){if(!D.navigator.cookieEnabled)return!1;if(this.h.cookie)return!0;this.set("TESTCOOKIESENABLED","1",{Xb:60});if(this.get("TESTCOOKIESENABLED")!=="1")return!1;this.remove("TESTCOOKIESENABLED");return!0};
p.set=function(a,b,c){var d=!1;if(typeof c==="object"){var e=c.ff;d=c.secure||!1;var f=c.domain||void 0;var g=c.path||void 0;var h=c.Xb}if(/[;=\s]/.test(a))throw Error('Invalid cookie name "'+a+'"');if(/[;\r\n]/.test(b))throw Error('Invalid cookie value "'+b+'"');h===void 0&&(h=-1);c=f?";domain="+f:"";g=g?";path="+g:"";d=d?";secure":"";h=h<0?"":h==0?";expires="+(new Date(1970,1,1)).toUTCString():";expires="+(new Date(Date.now()+h*1E3)).toUTCString();this.h.cookie=a+"="+b+c+g+h+d+(e!=null?";samesite="+
e:"")};
p.get=function(a,b){for(var c=a+"=",d=(this.h.cookie||"").split(";"),e=0,f;e<d.length;e++){f=fb(d[e]);if(f.lastIndexOf(c,0)==0)return f.slice(c.length);if(f==a)return""}return b};
p.remove=function(a,b,c){var d=this.get(a)!==void 0;this.set(a,"",{Xb:0,path:b,domain:c});return d};
p.Tb=function(){return gg(this).keys};
p.Wa=function(){return gg(this).values};
p.clear=function(){for(var a=gg(this).keys,b=a.length-1;b>=0;b--)this.remove(a[b])};
function gg(a){a=(a.h.cookie||"").split(";");for(var b=[],c=[],d,e,f=0;f<a.length;f++)e=fb(a[f]),d=e.indexOf("="),d==-1?(b.push(""),c.push(e)):(b.push(e.substring(0,d)),c.push(e.substring(d+1)));return{keys:b,values:c}}
var hg=new fg(typeof document=="undefined"?null:document);function ig(){var a=D.__SAPISID||D.__APISID||D.__3PSAPISID||D.__1PSAPISID||D.__OVERRIDE_SID;if(a)return!0;typeof document!=="undefined"&&(a=new fg(document),a=a.get("SAPISID")||a.get("APISID")||a.get("__Secure-3PAPISID")||a.get("__Secure-1PAPISID"));return!!a}
function jg(a,b,c,d){(a=D[a])||typeof document==="undefined"||(a=(new fg(document)).get(b));return a?cg(a,c,d):null}
function kg(a){var b=ag(D==null?void 0:D.location.href),c=[];if(ig()){b=b.indexOf("https:")==0||b.indexOf("chrome-extension:")==0||b.indexOf("chrome-untrusted://new-tab-page")==0||b.indexOf("moz-extension:")==0;var d=b?D.__SAPISID:D.__APISID;d||typeof document==="undefined"||(d=new fg(document),d=d.get(b?"SAPISID":"APISID")||d.get("__Secure-3PAPISID"));(d=d?cg(d,b?"SAPISIDHASH":"APISIDHASH",a):null)&&c.push(d);b&&((b=jg("__1PSAPISID","__Secure-1PAPISID","SAPISID1PHASH",a))&&c.push(b),(a=jg("__3PSAPISID",
"__Secure-3PAPISID","SAPISID3PHASH",a))&&c.push(a))}return c.length==0?null:c.join(" ")}
;function lg(){}
lg.prototype.compress=function(a){var b,c,d,e;return B(function(f){switch(f.h){case 1:return b=new CompressionStream("gzip"),c=(new Response(b.readable)).arrayBuffer(),d=b.writable.getWriter(),f.yield(d.write((new TextEncoder).encode(a)),2);case 2:return f.yield(d.close(),3);case 3:return e=Uint8Array,f.yield(c,4);case 4:return f.return(new e(f.i))}})};
lg.prototype.isSupported=function(a){return a<1024?!1:typeof CompressionStream!=="undefined"};function mg(a){this.F=L(a)}
v(mg,M);function ng(a,b){this.intervalMs=a;this.callback=b;this.enabled=!1;this.h=function(){return Xa()};
this.i=this.h()}
ng.prototype.setInterval=function(a){this.intervalMs=a;this.timer&&this.enabled?(this.stop(),this.start()):this.timer&&this.stop()};
ng.prototype.start=function(){var a=this;this.enabled=!0;this.timer||(this.timer=setTimeout(function(){a.tick()},this.intervalMs),this.i=this.h())};
ng.prototype.stop=function(){this.enabled=!1;this.timer&&(clearTimeout(this.timer),this.timer=void 0)};
ng.prototype.tick=function(){var a=this;if(this.enabled){var b=Math.max(this.h()-this.i,0);b<this.intervalMs*.8?this.timer=setTimeout(function(){a.tick()},this.intervalMs-b):(this.timer&&(clearTimeout(this.timer),this.timer=void 0),this.callback(),this.enabled&&(this.stop(),this.start()))}else this.timer=void 0};function og(a){this.F=L(a)}
v(og,M);function pg(a){this.F=L(a)}
v(pg,M);function qg(a,b){this.x=a!==void 0?a:0;this.y=b!==void 0?b:0}
p=qg.prototype;p.clone=function(){return new qg(this.x,this.y)};
p.equals=function(a){return a instanceof qg&&(this==a?!0:this&&a?this.x==a.x&&this.y==a.y:!1)};
p.ceil=function(){this.x=Math.ceil(this.x);this.y=Math.ceil(this.y);return this};
p.floor=function(){this.x=Math.floor(this.x);this.y=Math.floor(this.y);return this};
p.round=function(){this.x=Math.round(this.x);this.y=Math.round(this.y);return this};
p.scale=function(a,b){this.x*=a;this.y*=typeof b==="number"?b:a;return this};function rg(a,b){this.width=a;this.height=b}
p=rg.prototype;p.clone=function(){return new rg(this.width,this.height)};
p.aspectRatio=function(){return this.width/this.height};
p.ceil=function(){this.width=Math.ceil(this.width);this.height=Math.ceil(this.height);return this};
p.floor=function(){this.width=Math.floor(this.width);this.height=Math.floor(this.height);return this};
p.round=function(){this.width=Math.round(this.width);this.height=Math.round(this.height);return this};
p.scale=function(a,b){this.width*=a;this.height*=typeof b==="number"?b:a;return this};function sg(a,b){for(var c in a)b.call(void 0,a[c],c,a)}
function tg(a){var b=[],c=0,d;for(d in a)b[c++]=a[d];return b}
function ug(a){var b=vg,c;for(c in b)if(a.call(void 0,b[c],c,b))return c}
function wg(a){for(var b in a)return!1;return!0}
function xg(a,b){if(a!==null&&b in a)throw Error('The object already contains the key "'+b+'"');a[b]=!0}
function yg(a){return a!==null&&"privembed"in a?a.privembed:!1}
function zg(a,b){for(var c in a)if(!(c in b)||a[c]!==b[c])return!1;for(var d in b)if(!(d in a))return!1;return!0}
function Ag(a){var b={},c;for(c in a)b[c]=a[c];return b}
function Bg(a){if(!a||typeof a!=="object")return a;if(typeof a.clone==="function")return a.clone();if(typeof Map!=="undefined"&&a instanceof Map)return new Map(a);if(typeof Set!=="undefined"&&a instanceof Set)return new Set(a);if(a instanceof Date)return new Date(a.getTime());var b=Array.isArray(a)?[]:typeof ArrayBuffer!=="function"||typeof ArrayBuffer.isView!=="function"||!ArrayBuffer.isView(a)||a instanceof DataView?{}:new a.constructor(a.length),c;for(c in a)b[c]=Bg(a[c]);return b}
var Cg="constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");function Dg(a,b){for(var c,d,e=1;e<arguments.length;e++){d=arguments[e];for(c in d)a[c]=d[c];for(var f=0;f<Cg.length;f++)c=Cg[f],Object.prototype.hasOwnProperty.call(d,c)&&(a[c]=d[c])}}
;function Eg(a,b){this.h=a===Fg&&b||""}
Eg.prototype.toString=function(){return this.h};
var Fg={};new Eg(Fg,"");"ARTICLE SECTION NAV ASIDE H1 H2 H3 H4 H5 H6 HEADER FOOTER ADDRESS P HR PRE BLOCKQUOTE OL UL LH LI DL DT DD FIGURE FIGCAPTION MAIN DIV EM STRONG SMALL S CITE Q DFN ABBR RUBY RB RT RTC RP DATA TIME CODE VAR SAMP KBD SUB SUP I B U MARK BDI BDO SPAN BR WBR NOBR INS DEL PICTURE PARAM TRACK MAP TABLE CAPTION COLGROUP COL TBODY THEAD TFOOT TR TD TH SELECT DATALIST OPTGROUP OPTION OUTPUT PROGRESS METER FIELDSET LEGEND DETAILS SUMMARY MENU DIALOG SLOT CANVAS FONT CENTER ACRONYM BASEFONT BIG DIR HGROUP STRIKE TT".split(" ").concat(["BUTTON",
"INPUT"]);function Gg(a){var b=document;return typeof a==="string"?b.getElementById(a):a}
function Hg(a){var b=document;a=String(a);b.contentType==="application/xhtml+xml"&&(a=a.toLowerCase());return b.createElement(a)}
function Ig(a){a&&a.parentNode&&a.parentNode.removeChild(a)}
function Jg(a,b){for(var c=0;a;){if(b(a))return a;a=a.parentNode;c++}return null}
;function Kg(a){this.F=L(a)}
v(Kg,M);Kg.prototype.sc=function(){return Jf(this)};function Lg(a){this.F=L(a)}
v(Lg,M);function Mg(a){this.F=L(a)}
v(Mg,M);function Ng(a){Gf(Og,Lg,1,a)}
var Pg=Rf(Mg);function Qg(a){this.F=L(a)}
v(Qg,M);var Rg=["platform","platformVersion","architecture","model","uaFullVersion"],Og=new Mg,Sg=null;function Tg(a,b){b=b===void 0?Rg:b;if(!Sg){var c;a=(c=a.navigator)==null?void 0:c.userAgentData;if(!a||typeof a.getHighEntropyValues!=="function"||a.brands&&typeof a.brands.map!=="function")return Promise.reject(Error("UACH unavailable"));Ng((a.brands||[]).map(function(e){var f=new Lg;f=Kf(f,1,e.brand);return Kf(f,2,e.version)}));
typeof a.mobile==="boolean"&&vf(Og,2,Fe(a.mobile));Sg=a.getHighEntropyValues(b)}var d=new Set(b);return Sg.then(function(e){var f=Og.clone();d.has("platform")&&Kf(f,3,e.platform);d.has("platformVersion")&&Kf(f,4,e.platformVersion);d.has("architecture")&&Kf(f,5,e.architecture);d.has("model")&&Kf(f,6,e.model);d.has("uaFullVersion")&&Kf(f,7,e.uaFullVersion);return f.serialize()}).catch(function(){return Og.serialize()})}
;function Ug(a){this.F=L(a)}
v(Ug,M);function Vg(a){return Mf(a,1,1)}
;function Wg(a){this.F=L(a,4)}
v(Wg,M);function Xg(a){this.F=L(a,36)}
v(Xg,M);function Yg(a){this.F=L(a,19)}
v(Yg,M);Yg.prototype.ac=function(a){return Mf(this,2,a)};function Zg(a,b){this.Oa=b=b===void 0?!1:b;this.j=this.locale=null;this.i=0;this.isFinal=!1;this.h=new Yg;Number.isInteger(a)&&this.h.ac(a);b||(this.locale=document.documentElement.getAttribute("lang"));$g(this,new Ug)}
Zg.prototype.ac=function(a){this.h.ac(a);return this};
function $g(a,b){Ff(a.h,Ug,1,b);Jf(b)||Vg(b);a.Oa||(b=ah(a),If(b,5)||Kf(b,5,a.locale));a.j&&(b=ah(a),Ef(b,Mg,9)||Ff(b,Mg,9,a.j))}
function bh(a,b){a.i=b}
function ch(a){var b=b===void 0?Rg:b;var c=a.Oa?void 0:window;c?Tg(c,b).then(function(d){a.j=Pg(d!=null?d:"[]");d=ah(a);Ff(d,Mg,9,a.j);return!0}).catch(function(){return!1}):Promise.resolve(!1)}
function ah(a){var b=Ef(a.h,Ug,1);b||(b=new Ug,$g(a,b));a=b;b=Ef(a,Qg,11);b||(b=new Qg,Ff(a,Qg,11,b));return b}
function dh(a,b,c,d,e,f,g){c=c===void 0?0:c;d=d===void 0?0:d;e=e===void 0?null:e;f=f===void 0?0:f;g=g===void 0?0:g;if(!a.Oa){var h=ah(a);var k=new Kg;k=Mf(k,1,a.i);k=vf(k,2,Fe(a.isFinal));d=vf(k,3,Je(d>0?d:void 0));d=vf(d,4,Je(f>0?f:void 0));d=vf(d,5,Je(g>0?g:void 0));f=d.F;g=f[K]|0;d=Zd(d,g)?d:lf(d,f,g)?mf(d,f):new d.constructor(kf(f,g,!0));Ff(h,Kg,10,d)}a=a.h.clone();h=Date.now().toString();a=vf(a,4,Re(h));b=b.slice();b=Gf(a,Xg,3,b);e&&(a=new og,e=vf(a,13,Je(e)),a=new pg,e=Ff(a,og,2,e),a=new Wg,
e=Ff(a,pg,1,e),e=Mf(e,2,9),Ff(b,Wg,18,e));c&&vf(b,14,Re(c));return b}
;var eh=function(){if(!D.addEventListener||!Object.defineProperty)return!1;var a=!1,b=Object.defineProperty({},"passive",{get:function(){a=!0}});
try{var c=function(){};
D.addEventListener("test",c,b);D.removeEventListener("test",c,b)}catch(d){}return a}();function fh(a){this.h=this.i=this.j=a}
fh.prototype.reset=function(){this.h=this.i=this.j};
fh.prototype.getValue=function(){return this.i};function Pf(a){this.F=L(a,8)}
v(Pf,M);var gh=Rf(Pf);function Qf(a){this.F=L(a)}
v(Qf,M);var hh;hh=new Of;function ih(a){I.call(this);var b=this;this.componentId="";this.h=[];this.Ra="";this.pageId=null;this.fb=this.ma=-1;this.G=this.experimentIds=null;this.A=this.o=0;this.U=null;this.Z=this.ha=0;this.Kb=1;this.timeoutMillis=0;this.xa=!1;this.logSource=a.logSource;this.yb=a.yb||function(){};
this.j=new Zg(a.logSource,a.Oa);this.network=a.network||null;this.ob=a.ob||null;this.bufferSize=1E3;this.M=a.Df||null;this.sessionIndex=a.sessionIndex||null;this.Rb=a.Rb||!1;this.logger=null;this.withCredentials=!a.Nc;this.Oa=a.Oa||!1;this.Y=!this.Oa&&!!window&&!!window.navigator&&window.navigator.sendBeacon!==void 0;this.Qa=typeof URLSearchParams!=="undefined"&&!!(new URL(jh())).searchParams&&!!(new URL(jh())).searchParams.set;var c=Vg(new Ug);$g(this.j,c);this.u=new fh(1E4);a=kh(this,a.rd);this.i=
new ng(this.u.getValue(),a);this.Fa=new ng(6E5,a);this.Rb||this.Fa.start();this.Oa||(document.addEventListener("visibilitychange",function(){if(document.visibilityState==="hidden"){lh(b);var d;(d=b.U)==null||d.flush()}}),document.addEventListener("pagehide",function(){lh(b);
var d;(d=b.U)==null||d.flush()}))}
v(ih,I);function kh(a,b){return a.Qa?b?function(){b().then(function(){a.flush()})}:function(){a.flush()}:function(){}}
ih.prototype.ba=function(){lh(this);this.i.stop();this.Fa.stop();I.prototype.ba.call(this)};
function mh(a){a.M||(a.M=jh());try{return(new URL(a.M)).toString()}catch(b){return(new URL(a.M,window.location.origin)).toString()}}
function nh(a,b,c){a.U&&a.U.kb(b,c)}
ih.prototype.log=function(a){nh(this,2,1);if(this.Qa){a=a.clone();var b=this.Kb++;a=vf(a,21,Re(b));this.componentId&&Kf(a,26,this.componentId);b=a;var c=tf(b,1);var d=d===void 0?!1:d;var e=typeof c;d=c==null?c:e==="bigint"?String(Ae(64,c)):He(c)?e==="string"?Me(c):d?Ne(c):Qe(c):void 0;d==null&&(d=Date.now(),d=Number.isFinite(d)?d.toString():"0",vf(b,1,Re(d)));d=tf(b,15);d!=null&&(typeof d==="bigint"?qe(d)?d=Number(d):(d=Ae(64,d),d=qe(d)?Number(d):String(d)):d=He(d)?typeof d==="number"?Qe(d):Me(d):
void 0);d==null&&vf(b,15,Re((new Date).getTimezoneOffset()*60));this.experimentIds&&(d=this.experimentIds.clone(),Ff(b,mg,16,d));nh(this,1,1);b=this.h.length-this.bufferSize+1;b>0&&(this.h.splice(0,b),this.o+=b,nh(this,3,b));this.h.push(a);this.Rb||this.i.enabled||this.i.start()}};
ih.prototype.flush=function(a,b){var c=this;if(this.h.length===0)a&&a();else if(this.xa&&this.Y)this.j.i=3,oh(this);else{var d=Date.now();if(this.fb>d&&this.ma<d)b&&b("throttled");else{this.network&&(typeof this.network.sc==="function"?bh(this.j,this.network.sc()):this.j.i=0);var e=this.h.length,f=dh(this.j,this.h,this.o,this.A,this.ob,this.ha,this.Z),g=this.yb();if(g&&this.Ra===g)b&&b("stale-auth-token");else{this.h=[];this.i.enabled&&this.i.stop();this.o=0;d=f.serialize();var h;this.G&&this.G.isSupported(d.length)&&
(h=this.G.compress(d));var k=ph(this,d,g),l=function(r){c.u.reset();c.i.setInterval(c.u.getValue());if(r){var t=null;try{var w=JSON.stringify(JSON.parse(r.replace(")]}'\n","")));t=gh(w)}catch(G){}if(t){r=Number(Hf(t,1,ke("-1")));r>0&&(c.ma=Date.now(),c.fb=c.ma+r);r=Ya(Kd);var x;Gd&&r&&((x=t.F[r])==null?void 0:x[175237375])!=null&&Fd(Ld,3);a:{var z=z===void 0?!1:z;if(Ya(Qd)&&Ya(Kd)&&void 0===Qd){x=t.F;r=x[Kd];if(!r)break a;if(r=r.ci)try{r(x,175237375,af);break a}catch(G){Sc(G)}}z&&(z=t.F,(x=Ya(Kd))&&
x in z&&(z=z[x])&&delete z[175237375])}z=hh.ctor?hh.h(t,hh.ctor,175237375,hh.i):hh.h(t,175237375,null,hh.i);if(z=z===null?void 0:z)z=Fc(z,1,-1),z!==-1&&(c.u=new fh(z<1?1:z),c.i.setInterval(c.u.getValue()))}}a&&a();c.A=0},m=function(r,t){var w=Dc(f,Xg,3);
var x=Number(Hf(f,14)),z=c.u;z.h=Math.min(3E5,z.h*2);z.i=Math.min(3E5,z.h+Math.round(.1*(Math.random()-.5)*2*z.h));c.i.setInterval(c.u.getValue());r===401&&g&&(c.Ra=g);x&&(c.o+=x);t===void 0&&(t=c.isRetryable(r));t&&(c.h=w.concat(c.h),c.Rb||c.i.enabled||c.i.start());nh(c,7,1);b&&b("net-send-failed",r);++c.A},n=function(){c.network&&c.network.send(k,l,m)};
h?h.then(function(r){nh(c,5,e);k.Ec["Content-Encoding"]="gzip";k.Ec["Content-Type"]="application/binary";k.body=r;k.ge=2;n()},function(){nh(c,6,e);
n()}):n()}}}};
function ph(a,b,c){c=c===void 0?null:c;var d=d===void 0?a.withCredentials:d;var e={},f=new URL(mh(a));c&&(e.Authorization=c);a.sessionIndex&&(e["X-Goog-AuthUser"]=a.sessionIndex,f.searchParams.set("authuser",a.sessionIndex));a.pageId&&(Object.defineProperty(e,"X-Goog-PageId",{value:a.pageId}),f.searchParams.set("pageId",a.pageId));return{url:f.toString(),body:b,ge:1,Ec:e,requestType:"POST",withCredentials:d,timeoutMillis:a.timeoutMillis}}
function lh(a){a.j.isFinal=!0;a.flush();a.j.isFinal=!1}
function oh(a){qh(a,function(b,c){b=new URL(b);b.searchParams.set("format","json");var d=!1;try{d=window.navigator.sendBeacon(b.toString(),c.serialize())}catch(e){}d||(a.Y=!1);return d})}
function qh(a,b){if(a.h.length!==0){var c=new URL(mh(a));c.searchParams.delete("format");var d=a.yb();d&&c.searchParams.set("auth",d);c.searchParams.set("authuser",a.sessionIndex||"0");for(d=0;d<10&&a.h.length;++d){var e=a.h.slice(0,32),f=dh(a.j,e,a.o,a.A,a.ob,a.ha,a.Z);if(!b(c.toString(),f)){++a.A;break}a.o=0;a.A=0;a.ha=0;a.Z=0;a.h=a.h.slice(e.length)}a.i.enabled&&a.i.stop()}}
ih.prototype.isRetryable=function(a){return 500<=a&&a<600||a===401||a===0};
function jh(){return"https://play.google.com/log?format=json&hasfast=true"}
;function rh(){this.Yd=typeof AbortController!=="undefined"}
rh.prototype.send=function(a,b,c){var d=this,e,f,g,h,k,l,m,n,r,t;return B(function(w){switch(w.h){case 1:return f=(e=d.Yd?new AbortController:void 0)?setTimeout(function(){e.abort()},a.timeoutMillis):void 0,wa(w,2,3),g=Object.assign({},{method:a.requestType,
headers:Object.assign({},a.Ec)},a.body&&{body:a.body},a.withCredentials&&{credentials:"include"},{signal:a.timeoutMillis&&e?e.signal:null}),w.yield(fetch(a.url,g),5);case 5:h=w.i;if(h.status!==200){(k=c)==null||k(h.status);w.B(3);break}if((l=b)==null){w.B(7);break}return w.yield(h.text(),8);case 8:l(w.i);case 7:case 3:w.M=[w.j];w.H=0;w.o=0;clearTimeout(f);za(w);break;case 2:m=ya(w);switch((n=m)==null?void 0:n.name){case "AbortError":(r=c)==null||r(408);break;default:(t=c)==null||t(400)}w.B(3)}})};
rh.prototype.sc=function(){return 4};function sh(a,b){b=b===void 0?"0":b;I.call(this);this.logSource=a;this.sessionIndex=b;this.Va="https://play.google.com/log?format=json&hasfast=true";this.i=null;this.o=!1;this.network=null;this.componentId="";this.h=this.ob=null;this.j=!1;this.pageId=null;this.bufferSize=void 0}
v(sh,I);function th(a,b){a.i=b;return a}
function uh(a,b){a.network=b;return a}
function xh(a,b){a.h=b}
function yh(a){a.j=!0;return a}
sh.prototype.Nc=function(){this.u=!0;return this};
function zh(a){a.network||(a.network=new rh);var b=new ih({logSource:a.logSource,yb:a.yb?a.yb:kg,sessionIndex:a.sessionIndex,Df:a.Va,Oa:a.o,Rb:!1,Nc:a.u,rd:a.rd,network:a.network});xc(a,b);if(a.i){var c=a.i,d=ah(b.j);Kf(d,7,c)}b.G=new lg;a.componentId&&(b.componentId=a.componentId);a.ob&&(b.ob=a.ob);a.pageId&&(b.pageId=a.pageId);a.h&&((d=a.h)?(b.experimentIds||(b.experimentIds=new mg),c=b.experimentIds,d=d.serialize(),Kf(c,4,d)):b.experimentIds&&vf(b.experimentIds,4));a.j&&(b.xa=b.Y);ch(b.j);a.bufferSize&&
(b.bufferSize=a.bufferSize);a.network.ac&&a.network.ac(a.logSource);a.network.sf&&a.network.sf(b);return b}
;function Ah(a,b,c,d,e,f,g){a=a===void 0?-1:a;b=b===void 0?"":b;c=c===void 0?"":c;d=d===void 0?!1:d;e=e===void 0?"":e;I.call(this);this.logSource=a;this.componentId=b;f?b=f:(a=new sh(a,"0"),a.componentId=b,xc(this,a),c!==""&&(a.Va=c),d&&(a.o=!0),e&&th(a,e),g&&uh(a,g),b=zh(a));this.h=b}
v(Ah,I);
Ah.prototype.flush=function(a){var b=a||[];if(b.length){a=new $f;for(var c=[],d=0;d<b.length;d++){var e=b[d],f=new Zf;f=Kf(f,1,e.i);var g=Bh(e);f=yf(f,g,Ue);g=[];var h=[];for(var k=y(e.h.keys()),l=k.next();!l.done;l=k.next())h.push(l.value.split(","));for(k=0;k<h.length;k++){l=h[k];var m=e.o;for(var n=e.Qc(l)||[],r=[],t=0;t<n.length;t++){var w=n[t],x=w&&w.h;w=new Wf;switch(m){case 3:x=Number(x);Number.isFinite(x)&&Af(w,1,Xf,Re(x));break;case 2:x=Number(x);if(x!=null&&typeof x!=="number")throw Error("Value of float/double field must be a number, found "+typeof x+
": "+x);Af(w,2,Xf,x)}r.push(w)}m=r;for(n=0;n<m.length;n++){r=m[n];t=new Yf;r=Ff(t,Wf,2,r);t=l;w=[];x=Ch(e);for(var z=0;z<x.length;z++){var G=x[z],H=t[z],U=new Uf;switch(G){case 3:Af(U,1,Vf,Ve(String(H)));break;case 2:G=Number(H);Number.isFinite(G)&&Af(U,2,Vf,Je(G));break;case 1:Af(U,3,Vf,Fe(H==="true"))}w.push(U)}Gf(r,Uf,1,w);g.push(r)}}Gf(f,Yf,4,g);c.push(f);e.clear()}Gf(a,Zf,1,c);b=this.h;if(a instanceof Xg)b.log(a);else try{var Z=new Xg,mb=a.serialize();var Qb=Kf(Z,8,mb);b.log(Qb)}catch(ca){nh(b,
4,1)}this.h.flush()}};function Dh(a){this.h=a}
;function Eh(a,b,c){this.i=a;this.o=b;this.fields=c||[];this.h=new Map}
function Ch(a){return a.fields.map(function(b){return b.fieldType})}
function Bh(a){return a.fields.map(function(b){return b.fieldName})}
p=Eh.prototype;p.Zd=function(a){var b=C.apply(1,arguments),c=this.Qc(b);c?c.push(new Dh(a)):this.Md(a,b)};
p.Md=function(a){var b=this.qd(C.apply(1,arguments));this.h.set(b,[new Dh(a)])};
p.Qc=function(){var a=this.qd(C.apply(0,arguments));return this.h.has(a)?this.h.get(a):void 0};
p.ze=function(){var a=this.Qc(C.apply(0,arguments));return a&&a.length?a[0]:void 0};
p.clear=function(){this.h.clear()};
p.qd=function(){var a=C.apply(0,arguments);return a?a.join(","):"key"};function Fh(a,b){Eh.call(this,a,3,b)}
v(Fh,Eh);Fh.prototype.j=function(a){var b=C.apply(1,arguments),c=0,d=this.ze(b);d&&(c=d.h);this.Md(c+a,b)};function Gh(a,b){Eh.call(this,a,2,b)}
v(Gh,Eh);Gh.prototype.record=function(a){this.Zd(a,C.apply(1,arguments))};function Hh(a,b){this.type=a;this.h=this.target=b;this.defaultPrevented=this.j=!1}
Hh.prototype.stopPropagation=function(){this.j=!0};
Hh.prototype.preventDefault=function(){this.defaultPrevented=!0};function Ih(a,b){Hh.call(this,a?a.type:"");this.relatedTarget=this.h=this.target=null;this.button=this.screenY=this.screenX=this.clientY=this.clientX=0;this.key="";this.charCode=this.keyCode=0;this.metaKey=this.shiftKey=this.altKey=this.ctrlKey=!1;this.state=null;this.pointerId=0;this.pointerType="";this.i=null;a&&this.init(a,b)}
Za(Ih,Hh);
Ih.prototype.init=function(a,b){var c=this.type=a.type,d=a.changedTouches&&a.changedTouches.length?a.changedTouches[0]:null;this.target=a.target||a.srcElement;this.h=b;b=a.relatedTarget;b||(c=="mouseover"?b=a.fromElement:c=="mouseout"&&(b=a.toElement));this.relatedTarget=b;d?(this.clientX=d.clientX!==void 0?d.clientX:d.pageX,this.clientY=d.clientY!==void 0?d.clientY:d.pageY,this.screenX=d.screenX||0,this.screenY=d.screenY||0):(this.clientX=a.clientX!==void 0?a.clientX:a.pageX,this.clientY=a.clientY!==
void 0?a.clientY:a.pageY,this.screenX=a.screenX||0,this.screenY=a.screenY||0);this.button=a.button;this.keyCode=a.keyCode||0;this.key=a.key||"";this.charCode=a.charCode||(c=="keypress"?a.keyCode:0);this.ctrlKey=a.ctrlKey;this.altKey=a.altKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey;this.pointerId=a.pointerId||0;this.pointerType=a.pointerType;this.state=a.state;this.i=a;a.defaultPrevented&&Ih.Aa.preventDefault.call(this)};
Ih.prototype.stopPropagation=function(){Ih.Aa.stopPropagation.call(this);this.i.stopPropagation?this.i.stopPropagation():this.i.cancelBubble=!0};
Ih.prototype.preventDefault=function(){Ih.Aa.preventDefault.call(this);var a=this.i;a.preventDefault?a.preventDefault():a.returnValue=!1};var Jh="closure_listenable_"+(Math.random()*1E6|0);var Kh=0;function Lh(a,b,c,d,e){this.listener=a;this.proxy=null;this.src=b;this.type=c;this.capture=!!d;this.vc=e;this.key=++Kh;this.Zb=this.kc=!1}
function Mh(a){a.Zb=!0;a.listener=null;a.proxy=null;a.src=null;a.vc=null}
;function Nh(a){this.src=a;this.listeners={};this.h=0}
Nh.prototype.add=function(a,b,c,d,e){var f=a.toString();a=this.listeners[f];a||(a=this.listeners[f]=[],this.h++);var g=Oh(a,b,d,e);g>-1?(b=a[g],c||(b.kc=!1)):(b=new Lh(b,this.src,f,!!d,e),b.kc=c,a.push(b));return b};
Nh.prototype.remove=function(a,b,c,d){a=a.toString();if(!(a in this.listeners))return!1;var e=this.listeners[a];b=Oh(e,b,c,d);return b>-1?(Mh(e[b]),Array.prototype.splice.call(e,b,1),e.length==0&&(delete this.listeners[a],this.h--),!0):!1};
function Ph(a,b){var c=b.type;c in a.listeners&&Vb(a.listeners[c],b)&&(Mh(b),a.listeners[c].length==0&&(delete a.listeners[c],a.h--))}
function Oh(a,b,c,d){for(var e=0;e<a.length;++e){var f=a[e];if(!f.Zb&&f.listener==b&&f.capture==!!c&&f.vc==d)return e}return-1}
;var Qh="closure_lm_"+(Math.random()*1E6|0),Rh={},Sh=0;function Th(a,b,c,d,e){if(d&&d.once)Uh(a,b,c,d,e);else if(Array.isArray(b))for(var f=0;f<b.length;f++)Th(a,b[f],c,d,e);else c=Vh(c),a&&a[Jh]?a.listen(b,c,Ma(d)?!!d.capture:!!d,e):Wh(a,b,c,!1,d,e)}
function Wh(a,b,c,d,e,f){if(!b)throw Error("Invalid event type");var g=Ma(e)?!!e.capture:!!e,h=Xh(a);h||(a[Qh]=h=new Nh(a));c=h.add(b,c,d,g,f);if(!c.proxy){d=Yh();c.proxy=d;d.src=a;d.listener=c;if(a.addEventListener)eh||(e=g),e===void 0&&(e=!1),a.addEventListener(b.toString(),d,e);else if(a.attachEvent)a.attachEvent(Zh(b.toString()),d);else if(a.addListener&&a.removeListener)a.addListener(d);else throw Error("addEventListener and attachEvent are unavailable.");Sh++}}
function Yh(){function a(c){return b.call(a.src,a.listener,c)}
var b=$h;return a}
function Uh(a,b,c,d,e){if(Array.isArray(b))for(var f=0;f<b.length;f++)Uh(a,b[f],c,d,e);else c=Vh(c),a&&a[Jh]?ai(a,b,c,Ma(d)?!!d.capture:!!d,e):Wh(a,b,c,!0,d,e)}
function bi(a,b,c,d,e){if(Array.isArray(b))for(var f=0;f<b.length;f++)bi(a,b[f],c,d,e);else(d=Ma(d)?!!d.capture:!!d,c=Vh(c),a&&a[Jh])?a.i.remove(String(b),c,d,e):a&&(a=Xh(a))&&(b=a.listeners[b.toString()],a=-1,b&&(a=Oh(b,c,d,e)),(c=a>-1?b[a]:null)&&ci(c))}
function ci(a){if(typeof a!=="number"&&a&&!a.Zb){var b=a.src;if(b&&b[Jh])Ph(b.i,a);else{var c=a.type,d=a.proxy;b.removeEventListener?b.removeEventListener(c,d,a.capture):b.detachEvent?b.detachEvent(Zh(c),d):b.addListener&&b.removeListener&&b.removeListener(d);Sh--;(c=Xh(b))?(Ph(c,a),c.h==0&&(c.src=null,b[Qh]=null)):Mh(a)}}}
function Zh(a){return a in Rh?Rh[a]:Rh[a]="on"+a}
function $h(a,b){if(a.Zb)a=!0;else{b=new Ih(b,this);var c=a.listener,d=a.vc||a.src;a.kc&&ci(a);a=c.call(d,b)}return a}
function Xh(a){a=a[Qh];return a instanceof Nh?a:null}
var di="__closure_events_fn_"+(Math.random()*1E9>>>0);function Vh(a){if(typeof a==="function")return a;a[di]||(a[di]=function(b){return a.handleEvent(b)});
return a[di]}
;function ei(){I.call(this);this.i=new Nh(this);this.xa=this;this.Z=null}
Za(ei,I);ei.prototype[Jh]=!0;p=ei.prototype;p.addEventListener=function(a,b,c,d){Th(this,a,b,c,d)};
p.removeEventListener=function(a,b,c,d){bi(this,a,b,c,d)};
function fi(a,b){var c=a.Z;if(c){var d=[];for(var e=1;c;c=c.Z)d.push(c),++e}a=a.xa;c=b.type||b;typeof b==="string"?b=new Hh(b,a):b instanceof Hh?b.target=b.target||a:(e=b,b=new Hh(c,a),Dg(b,e));e=!0;var f;if(d)for(f=d.length-1;!b.j&&f>=0;f--){var g=b.h=d[f];e=gi(g,c,!0,b)&&e}b.j||(g=b.h=a,e=gi(g,c,!0,b)&&e,b.j||(e=gi(g,c,!1,b)&&e));if(d)for(f=0;!b.j&&f<d.length;f++)g=b.h=d[f],e=gi(g,c,!1,b)&&e}
p.ba=function(){ei.Aa.ba.call(this);this.removeAllListeners();this.Z=null};
p.listen=function(a,b,c,d){return this.i.add(String(a),b,!1,c,d)};
function ai(a,b,c,d,e){a.i.add(String(b),c,!0,d,e)}
p.removeAllListeners=function(a){if(this.i){var b=this.i;a=a&&a.toString();var c=0,d;for(d in b.listeners)if(!a||d==a){for(var e=b.listeners[d],f=0;f<e.length;f++)++c,Mh(e[f]);delete b.listeners[d];b.h--}b=c}else b=0;return b};
function gi(a,b,c,d){b=a.i.listeners[String(b)];if(!b)return!0;b=b.concat();for(var e=!0,f=0;f<b.length;++f){var g=b[f];if(g&&!g.Zb&&g.capture==c){var h=g.listener,k=g.vc||g.src;g.kc&&Ph(a.i,g);e=h.call(k,d)!==!1&&e}}return e&&!d.defaultPrevented}
;var hi=typeof AsyncContext!=="undefined"&&typeof AsyncContext.Snapshot==="function"?function(a){return a&&AsyncContext.Snapshot.wrap(a)}:function(a){return a};function ii(a,b){this.j=a;this.o=b;this.i=0;this.h=null}
ii.prototype.get=function(){if(this.i>0){this.i--;var a=this.h;this.h=a.next;a.next=null}else a=this.j();return a};
function ji(a,b){a.o(b);a.i<100&&(a.i++,b.next=a.h,a.h=b)}
;function ki(){this.i=this.h=null}
ki.prototype.add=function(a,b){var c=li.get();c.set(a,b);this.i?this.i.next=c:this.h=c;this.i=c};
ki.prototype.remove=function(){var a=null;this.h&&(a=this.h,this.h=this.h.next,this.h||(this.i=null),a.next=null);return a};
var li=new ii(function(){return new mi},function(a){return a.reset()});
function mi(){this.next=this.scope=this.h=null}
mi.prototype.set=function(a,b){this.h=a;this.scope=b;this.next=null};
mi.prototype.reset=function(){this.next=this.scope=this.h=null};var ni,oi=!1,pi=new ki;function qi(a,b){ni||ri();oi||(ni(),oi=!0);pi.add(a,b)}
function ri(){var a=Promise.resolve(void 0);ni=function(){a.then(si)}}
function si(){for(var a;a=pi.remove();){try{a.h.call(a.scope)}catch(b){Sc(b)}ji(li,a)}oi=!1}
;function ti(){}
function ui(a){var b=!1,c;return function(){b||(c=a(),b=!0);return c}}
;function vi(a){this.X=0;this.bb=void 0;this.wb=this.Ta=this.parent_=null;this.uc=this.Oc=!1;if(a!=ti)try{var b=this;a.call(void 0,function(c){wi(b,2,c)},function(c){wi(b,3,c)})}catch(c){wi(this,3,c)}}
function xi(){this.next=this.context=this.h=this.i=this.child=null;this.j=!1}
xi.prototype.reset=function(){this.context=this.h=this.i=this.child=null;this.j=!1};
var yi=new ii(function(){return new xi},function(a){a.reset()});
function zi(a,b,c){var d=yi.get();d.i=a;d.h=b;d.context=c;return d}
function Ai(a){return new vi(function(b,c){c(a)})}
vi.prototype.then=function(a,b,c){return Bi(this,hi(typeof a==="function"?a:null),hi(typeof b==="function"?b:null),c)};
vi.prototype.$goog_Thenable=!0;function Ci(a,b,c,d){Di(a,zi(b||ti,c||null,d))}
p=vi.prototype;p.finally=function(a){var b=this;a=hi(a);return new Promise(function(c,d){Ci(b,function(e){a();c(e)},function(e){a();
d(e)})})};
p.Hc=function(a,b){return Bi(this,null,hi(a),b)};
p.catch=vi.prototype.Hc;p.cancel=function(a){if(this.X==0){var b=new Ei(a);qi(function(){Fi(this,b)},this)}};
function Fi(a,b){if(a.X==0)if(a.parent_){var c=a.parent_;if(c.Ta){for(var d=0,e=null,f=null,g=c.Ta;g&&(g.j||(d++,g.child==a&&(e=g),!(e&&d>1)));g=g.next)e||(f=g);e&&(c.X==0&&d==1?Fi(c,b):(f?(d=f,d.next==c.wb&&(c.wb=d),d.next=d.next.next):Gi(c),Hi(c,e,3,b)))}a.parent_=null}else wi(a,3,b)}
function Di(a,b){a.Ta||a.X!=2&&a.X!=3||Ii(a);a.wb?a.wb.next=b:a.Ta=b;a.wb=b}
function Bi(a,b,c,d){var e=zi(null,null,null);e.child=new vi(function(f,g){e.i=b?function(h){try{var k=b.call(d,h);f(k)}catch(l){g(l)}}:f;
e.h=c?function(h){try{var k=c.call(d,h);k===void 0&&h instanceof Ei?g(h):f(k)}catch(l){g(l)}}:g});
e.child.parent_=a;Di(a,e);return e.child}
p.Bf=function(a){this.X=0;wi(this,2,a)};
p.Cf=function(a){this.X=0;wi(this,3,a)};
function wi(a,b,c){if(a.X==0){a===c&&(b=3,c=new TypeError("Promise cannot resolve to itself"));a.X=1;a:{var d=c,e=a.Bf,f=a.Cf;if(d instanceof vi){Ci(d,e,f,a);var g=!0}else{if(d)try{var h=!!d.$goog_Thenable}catch(l){h=!1}else h=!1;if(h)d.then(e,f,a),g=!0;else{if(Ma(d))try{var k=d.then;if(typeof k==="function"){Ji(d,k,e,f,a);g=!0;break a}}catch(l){f.call(a,l);g=!0;break a}g=!1}}}g||(a.bb=c,a.X=b,a.parent_=null,Ii(a),b!=3||c instanceof Ei||Ki(a,c))}}
function Ji(a,b,c,d,e){function f(k){h||(h=!0,d.call(e,k))}
function g(k){h||(h=!0,c.call(e,k))}
var h=!1;try{b.call(a,g,f)}catch(k){f(k)}}
function Ii(a){a.Oc||(a.Oc=!0,qi(a.te,a))}
function Gi(a){var b=null;a.Ta&&(b=a.Ta,a.Ta=b.next,b.next=null);a.Ta||(a.wb=null);return b}
p.te=function(){for(var a;a=Gi(this);)Hi(this,a,this.X,this.bb);this.Oc=!1};
function Hi(a,b,c,d){if(c==3&&b.h&&!b.j)for(;a&&a.uc;a=a.parent_)a.uc=!1;if(b.child)b.child.parent_=null,Li(b,c,d);else try{b.j?b.i.call(b.context):Li(b,c,d)}catch(e){Mi.call(null,e)}ji(yi,b)}
function Li(a,b,c){b==2?a.i.call(a.context,c):a.h&&a.h.call(a.context,c)}
function Ki(a,b){a.uc=!0;qi(function(){a.uc&&Mi.call(null,b)})}
var Mi=Sc;function Ei(a){eb.call(this,a)}
Za(Ei,eb);Ei.prototype.name="cancel";function Ni(a,b){ei.call(this);this.j=a||1;this.h=b||D;this.o=Va(this.yf,this);this.u=Xa()}
Za(Ni,ei);p=Ni.prototype;p.enabled=!1;p.Ea=null;p.setInterval=function(a){this.j=a;this.Ea&&this.enabled?(this.stop(),this.start()):this.Ea&&this.stop()};
p.yf=function(){if(this.enabled){var a=Xa()-this.u;a>0&&a<this.j*.8?this.Ea=this.h.setTimeout(this.o,this.j-a):(this.Ea&&(this.h.clearTimeout(this.Ea),this.Ea=null),fi(this,"tick"),this.enabled&&(this.stop(),this.start()))}};
p.start=function(){this.enabled=!0;this.Ea||(this.Ea=this.h.setTimeout(this.o,this.j),this.u=Xa())};
p.stop=function(){this.enabled=!1;this.Ea&&(this.h.clearTimeout(this.Ea),this.Ea=null)};
p.ba=function(){Ni.Aa.ba.call(this);this.stop();delete this.h};function Oi(a){I.call(this);this.G=a;this.j=0;this.o=100;this.u=!1;this.i=new Map;this.A=new Set;this.flushInterval=3E4;this.h=new Ni(this.flushInterval);this.h.listen("tick",this.Gc,!1,this);xc(this,this.h)}
v(Oi,I);p=Oi.prototype;p.sendIsolatedPayload=function(a){this.u=a;this.o=1};
function Pi(a){a.h.enabled||a.h.start();a.j++;a.j>=a.o&&a.Gc()}
p.Gc=function(){var a=this.i.values();a=[].concat(A(a)).filter(function(b){return b.h.size});
a.length&&this.G.flush(a,this.u);Qi(a);this.j=0;this.h.enabled&&this.h.stop()};
p.Mb=function(a){var b=C.apply(1,arguments);this.i.has(a)||this.i.set(a,new Fh(a,b))};
p.Kc=function(a){var b=C.apply(1,arguments);this.i.has(a)||this.i.set(a,new Gh(a,b))};
function Ri(a,b){return a.A.has(b)?void 0:a.i.get(b)}
p.Jb=function(a){this.Xd(a,1,C.apply(1,arguments))};
p.Xd=function(a,b){var c=C.apply(2,arguments),d=Ri(this,a);d&&d instanceof Fh&&(d.j(b,c),Pi(this))};
p.record=function(a,b){var c=C.apply(2,arguments),d=Ri(this,a);d&&d instanceof Gh&&(d.record(b,c),Pi(this))};
function Qi(a){for(var b=0;b<a.length;b++)a[b].clear()}
;function Si(){}
Si.prototype.serialize=function(a){var b=[];Ti(this,a,b);return b.join("")};
function Ti(a,b,c){if(b==null)c.push("null");else{if(typeof b=="object"){if(Array.isArray(b)){var d=b;b=d.length;c.push("[");for(var e="",f=0;f<b;f++)c.push(e),Ti(a,d[f],c),e=",";c.push("]");return}if(b instanceof String||b instanceof Number||b instanceof Boolean)b=b.valueOf();else{c.push("{");e="";for(d in b)Object.prototype.hasOwnProperty.call(b,d)&&(f=b[d],typeof f!="function"&&(c.push(e),Ui(d,c),c.push(":"),Ti(a,f,c),e=","));c.push("}");return}}switch(typeof b){case "string":Ui(b,c);break;case "number":c.push(isFinite(b)&&
!isNaN(b)?String(b):"null");break;case "boolean":c.push(String(b));break;case "function":c.push("null");break;default:throw Error("Unknown type: "+typeof b);}}}
var Vi={'"':'\\"',"\\":"\\\\","/":"\\/","\b":"\\b","\f":"\\f","\n":"\\n","\r":"\\r","\t":"\\t","\v":"\\u000b"},Wi=/\uffff/.test("\uffff")?/[\\"\x00-\x1f\x7f-\uffff]/g:/[\\"\x00-\x1f\x7f-\xff]/g;function Ui(a,b){b.push('"',a.replace(Wi,function(c){var d=Vi[c];d||(d="\\u"+(c.charCodeAt(0)|65536).toString(16).slice(1),Vi[c]=d);return d}),'"')}
;function Xi(){ei.call(this);this.headers=new Map;this.h=!1;this.K=null;this.o=this.Y="";this.j=this.U=this.A=this.M=!1;this.G=0;this.u=null;this.ma="";this.ha=!1}
Za(Xi,ei);var Yi=/^https?$/i,Zi=["POST","PUT"],$i=[];function aj(a,b,c,d,e,f,g){var h=new Xi;$i.push(h);b&&h.listen("complete",b);ai(h,"ready",h.je);f&&(h.G=Math.max(0,f));g&&(h.ha=g);h.send(a,c,d,e)}
p=Xi.prototype;p.je=function(){this.dispose();Vb($i,this)};
p.send=function(a,b,c,d){if(this.K)throw Error("[goog.net.XhrIo] Object is active with another request="+this.Y+"; newUri="+a);b=b?b.toUpperCase():"GET";this.Y=a;this.o="";this.M=!1;this.h=!0;this.K=new XMLHttpRequest;this.K.onreadystatechange=hi(Va(this.Fd,this));try{this.getStatus(),this.U=!0,this.K.open(b,String(a),!0),this.U=!1}catch(g){this.getStatus();bj(this,g);return}a=c||"";c=new Map(this.headers);if(d)if(Object.getPrototypeOf(d)===Object.prototype)for(var e in d)c.set(e,d[e]);else if(typeof d.keys===
"function"&&typeof d.get==="function"){e=y(d.keys());for(var f=e.next();!f.done;f=e.next())f=f.value,c.set(f,d.get(f))}else throw Error("Unknown input type for opt_headers: "+String(d));d=Array.from(c.keys()).find(function(g){return"content-type"==g.toLowerCase()});
e=D.FormData&&a instanceof D.FormData;!(Ob(Zi,b)>=0)||d||e||c.set("Content-Type","application/x-www-form-urlencoded;charset=utf-8");b=y(c);for(d=b.next();!d.done;d=b.next())c=y(d.value),d=c.next().value,c=c.next().value,this.K.setRequestHeader(d,c);this.ma&&(this.K.responseType=this.ma);"withCredentials"in this.K&&this.K.withCredentials!==this.ha&&(this.K.withCredentials=this.ha);try{this.u&&(clearTimeout(this.u),this.u=null),this.G>0&&(this.getStatus(),this.u=setTimeout(this.Af.bind(this),this.G)),
this.getStatus(),this.A=!0,this.K.send(a),this.A=!1}catch(g){this.getStatus(),bj(this,g)}};
p.Af=function(){typeof Ia!="undefined"&&this.K&&(this.o="Timed out after "+this.G+"ms, aborting",this.getStatus(),fi(this,"timeout"),this.abort(8))};
function bj(a,b){a.h=!1;a.K&&(a.j=!0,a.K.abort(),a.j=!1);a.o=b;cj(a);dj(a)}
function cj(a){a.M||(a.M=!0,fi(a,"complete"),fi(a,"error"))}
p.abort=function(){this.K&&this.h&&(this.getStatus(),this.h=!1,this.j=!0,this.K.abort(),this.j=!1,fi(this,"complete"),fi(this,"abort"),dj(this))};
p.ba=function(){this.K&&(this.h&&(this.h=!1,this.j=!0,this.K.abort(),this.j=!1),dj(this,!0));Xi.Aa.ba.call(this)};
p.Fd=function(){this.ea||(this.U||this.A||this.j?ej(this):this.Re())};
p.Re=function(){ej(this)};
function ej(a){if(a.h&&typeof Ia!="undefined")if(a.A&&(a.K?a.K.readyState:0)==4)setTimeout(a.Fd.bind(a),0);else if(fi(a,"readystatechange"),a.isComplete()){a.getStatus();a.h=!1;try{if(fj(a))fi(a,"complete"),fi(a,"success");else{try{var b=(a.K?a.K.readyState:0)>2?a.K.statusText:""}catch(c){b=""}a.o=b+" ["+a.getStatus()+"]";cj(a)}}finally{dj(a)}}}
function dj(a,b){if(a.K){a.u&&(clearTimeout(a.u),a.u=null);var c=a.K;a.K=null;b||fi(a,"ready");try{c.onreadystatechange=null}catch(d){}}}
p.isActive=function(){return!!this.K};
p.isComplete=function(){return(this.K?this.K.readyState:0)==4};
function fj(a){var b=a.getStatus();a:switch(b){case 200:case 201:case 202:case 204:case 206:case 304:case 1223:var c=!0;break a;default:c=!1}if(!c){if(b=b===0)a=String(a.Y).match(fc)[1]||null,!a&&D.self&&D.self.location&&(a=D.self.location.protocol.slice(0,-1)),b=!Yi.test(a?a.toLowerCase():"");c=b}return c}
p.getStatus=function(){try{return(this.K?this.K.readyState:0)>2?this.K.status:-1}catch(a){return-1}};
p.getLastError=function(){return typeof this.o==="string"?this.o:String(this.o)};function gj(){}
gj.prototype.send=function(a,b,c){b=b===void 0?function(){}:b;
c=c===void 0?function(){}:c;
aj(a.url,function(d){d=d.target;if(fj(d)){try{var e=d.K?d.K.responseText:""}catch(f){e=""}b(e)}else c(d.getStatus())},a.requestType,a.body,a.Ec,a.timeoutMillis,a.withCredentials)};
gj.prototype.sc=function(){return 1};function hj(a,b){this.logger=a;this.event=b;this.startTime=ij()}
hj.prototype.done=function(){this.logger.Wb(this.event,ij()-this.startTime)};
function jj(){Hc.apply(this,arguments)}
v(jj,Hc);function kj(a,b){var c=ij();b=b();a.Wb("n",ij()-c);return b}
function lj(){jj.apply(this,arguments)}
v(lj,jj);p=lj.prototype;p.Vc=function(){};
p.Db=function(){};
p.Wb=function(){};
p.Ha=function(){};
p.Dc=function(){};
function mj(a,b,c,d,e){a=yh(uh(th(new sh(1828,"0"),a),new gj));b.length&&xh(a,Tf(new Sf,b));d!==void 0&&(a.Va=d);e&&a.Nc();var f=new Ah(1828,"","",!1,"",zh(a));xc(f,a);var g=new Oi({flush:function(h){try{f.flush(h)}catch(k){c(k)}}});
g.addOnDisposeCallback(function(){setTimeout(function(){try{g.Gc()}finally{f.dispose()}})});
g.o=1E5;g.flushInterval=3E4;g.h.setInterval(3E4);return g}
function nj(a,b){I.call(this);var c=this;this.callback=a;this.i=b;this.h=-b;this.addOnDisposeCallback(function(){return void clearTimeout(c.timer)})}
v(nj,I);function oj(a){if(a.timer===void 0){var b=Math.max(0,a.h+a.i-ij());a.timer=setTimeout(function(){try{a.callback()}finally{a.h=ij(),a.timer=void 0}},b)}}
function pj(a,b){jj.call(this);this.metrics=a;this.Da=b}
v(pj,jj);pj.prototype.Vc=function(a){this.metrics.wf.record(a,this.Da)};
pj.prototype.Db=function(a){this.metrics.eventCount.kb(a,this.Da)};
pj.prototype.Wb=function(a,b){this.metrics.se.record(b,a,this.Da)};
pj.prototype.Ha=function(a){this.metrics.errorCount.kb(a,this.Da)};
function qj(a,b){b=b===void 0?[]:b;var c={Da:a.Da||"_",Pc:a.Pc||[],Uc:a.Uc|0,Va:a.Va,disableClearcutCredentialBinding:a.disableClearcutCredentialBinding,yc:a.yc||function(){},
dc:a.dc||function(f,g){return mj(f,g,c.yc,c.Va,c.disableClearcutCredentialBinding)}},d=c.dc("50",c.Pc.concat(b));
pj.call(this,{wf:new Kc(d),errorCount:new Oc(d),eventCount:new Mc(d),se:new Nc(d),li:new Lc(d),ni:new Pc(d),Ch:new Qc(d),mi:new Rc(d)},c.Da);var e=this;this.options=c;this.service=d;this.j=!a.dc;this.h=new nj(function(){return void e.service.Gc()},c.Uc);
this.addOnDisposeCallback(function(){e.h.dispose();e.j&&e.service.dispose()});
b.slice().sort(Yb)}
v(qj,pj);qj.prototype.Dc=function(){oj(this.h)};
function ij(){var a,b,c;return(c=(a=globalThis.performance)==null?void 0:(b=a.now)==null?void 0:b.call(a))!=null?c:Date.now()}
;function rj(a){this.F=L(a)}
v(rj,M);function sj(a){this.F=L(a)}
v(sj,M);function tj(a){this.F=L(a,0,"bfkj")}
v(tj,M);var uj=function(a){return ce(function(b){return b instanceof a&&!Zd(b)})}(tj);
tj.Pe="bfkj";function vj(a){this.F=L(a)}
v(vj,M);function Ec(a){this.F=L(a)}
v(Ec,M);function wj(a){this.F=L(a)}
v(wj,M);var xj=Rf(wj);function yj(){var a=this;this.promise=new Promise(function(b,c){a.resolve=b;a.reject=c})}
;function zj(a,b){if(a.disable)return new lj;var c=b?Cc(b):[],d=a.Da,e=a.Ih,f=a.Uh,g=a.Va,h=a.yc;a=a.dc;b=b==null?void 0:Ef(b,vj,11);var k=k===void 0?50:k;b=(b==null?void 0:Fc(b,1))||0;d={Da:d,Pc:e,Uc:f,Va:g,yc:h,dc:a,disableClearcutCredentialBinding:b>0&&k>=b};c=c===void 0?[]:c;return new qj(d,c)}
function Aj(a){function b(w,x,z,G){Promise.resolve().then(function(){k.done();h.Dc();h.dispose();g.resolve({ce:w,uf:x,Ve:z,Eh:G})})}
function c(w,x,z,G){if(!d.logger.ea){var H="k";x?H="h":z&&(H="u");H!=="k"?G!==0&&(d.logger.Db(H),d.logger.Wb(H,w)):d.i<=0?(d.logger.Db(H),d.logger.Wb(H,w),d.i=Math.floor(Math.random()*200)):d.i--}}
I.call(this);var d=this;this.i=Math.floor(Math.random()*200);this.h=new wj;if("challenge"in a&&uj(a.challenge)){var e=If(a.challenge,4,void 0,be);var f=If(a.challenge,5,void 0,be);If(a.challenge,7,void 0,be)&&(this.h=xj(If(a.challenge,7,void 0,be)))}else e=a.program,f=a.globalName;this.addOnDisposeCallback(function(){var w,x,z;return B(function(G){if(G.h==1)return G.yield(d.j,2);w=G.i;x=w.uf;(z=x)==null||z();G.h=0})});
this.logger=zj(a.Dd||{},this.h);xc(this,this.logger);var g=new yj;this.j=g.promise;this.logger.Db("t");var h=this.logger.share(),k=new hj(h,"t");if(!D[f])throw this.logger.Ha(25),Error("EGOU");if(!D[f].a)throw this.logger.Ha(26),Error("ELIU");try{var l=D[f].a;f=[];for(var m=[],n=Cc(this.h),r=0;r<n.length;r++)f.push(n[r]),m.push(1);var t=Gc(this.h);for(n=0;n<t.length;n++)f.push(t[n]),m.push(2);this.u=y(l(e,b,!0,a.ki,c,[f,m],If(this.h,5))).next().value;this.hd=g.promise.then(function(){})}catch(w){throw this.logger.Ha(28),
w;
}}
v(Aj,I);Aj.prototype.snapshot=function(a){if(this.ea)throw Error("Already disposed");this.logger.Db("n");var b=this.logger.share();return this.j.then(function(c){var d=c.ce;return new Promise(function(e){var f=new hj(b,"n");d(function(g){f.done();b.Vc(g.length);b.Dc();b.dispose();e(g)},[a.Pb,
a.kd,a.Gf,a.ld])})})};
Aj.prototype.Od=function(a){var b=this;if(this.ea)throw Error("Already disposed");this.logger.Db("n");var c=kj(this.logger,function(){return b.u([a.Pb,a.kd,a.Gf,a.ld])});
this.logger.Vc(c.length);this.logger.Dc();return c};
Aj.prototype.o=function(a){this.j.then(function(b){var c;(c=b.Ve)==null||c(a)})};function Bj(a){if(!a)return null;a=We(tf(a,4,void 0,sf));return a===null||a===void 0?null:lb(a)}
;function Cj(){this.promises={};this.h=null}
function Dj(){Cj.instance||(Cj.instance=new Cj);return Cj.instance}
function Ej(a,b){return Fj(a,Ef(b,rj,1,be),Ef(b,sj,2,be),If(b,3,void 0,be))}
function Fj(a,b,c,d){if(!b&&!c)return Promise.resolve();if(!d)return Gj(b,c);var e;(e=a.promises)[d]||(e[d]=new Promise(function(f,g){Gj(b,c).then(function(){a.h=d;f()},function(h){delete a.promises[d];
g(h)})}));
return a.promises[d]}
function Gj(a,b){return b?Hj(b):a?Ij(a):Promise.resolve()}
function Hj(a){return new Promise(function(b,c){var d=Hg("SCRIPT"),e=Bj(a);Ib(d,e);d.onload=function(){Ig(d);b()};
d.onerror=function(){Ig(d);c(Error("EWLS"))};
(document.getElementsByTagName("HEAD")[0]||document.documentElement).appendChild(d)})}
function Ij(a){return new Promise(function(b){var c=Hg("SCRIPT");if(a){var d=We(tf(a,6,void 0,sf));d=d===null||d===void 0?null:Fb(d)}else d=null;c.textContent=Gb(d);Hb(c);(document.getElementsByTagName("HEAD")[0]||document.documentElement).appendChild(c);Ig(c);b()})}
;var Jj=window;function Kj(a){var b=Lj;if(b)for(var c in b)Object.prototype.hasOwnProperty.call(b,c)&&a(b[c],c,b)}
function Mj(){var a=[];Kj(function(b){a.push(b)});
return a}
var Lj={Hf:"allow-forms",If:"allow-modals",Jf:"allow-orientation-lock",Kf:"allow-pointer-lock",Lf:"allow-popups",Mf:"allow-popups-to-escape-sandbox",Nf:"allow-presentation",Of:"allow-same-origin",Pf:"allow-scripts",Qf:"allow-top-navigation",Rf:"allow-top-navigation-by-user-activation"},Nj=ui(function(){return Mj()});
function Oj(){var a=Pj(),b={};Pb(Nj(),function(c){a.sandbox&&a.sandbox.supports&&a.sandbox.supports(c)&&(b[c]=!0)});
return b}
function Pj(){var a=a===void 0?document:a;return a.createElement("iframe")}
;function Qj(a){typeof a=="number"&&(a=Math.round(a)+"px");return a}
;var Rj=(new Date).getTime();function Sj(a){ei.call(this);var b=this;this.A=this.j=0;this.Ca=a!=null?a:{pa:function(e,f){return setTimeout(e,f)},
qa:function(e){clearTimeout(e)}};
var c,d;this.h=(d=(c=window.navigator)==null?void 0:c.onLine)!=null?d:!0;this.o=function(){return B(function(e){return e.yield(Tj(b),0)})};
window.addEventListener("offline",this.o);window.addEventListener("online",this.o);this.A||Uj(this)}
v(Sj,ei);function Vj(){var a=Wj;Sj.instance||(Sj.instance=new Sj(a));return Sj.instance}
Sj.prototype.dispose=function(){window.removeEventListener("offline",this.o);window.removeEventListener("online",this.o);this.Ca.qa(this.A);delete Sj.instance};
Sj.prototype.ta=function(){return this.h};
function Uj(a){a.A=a.Ca.pa(function(){var b;return B(function(c){if(c.h==1)return a.h?((b=window.navigator)==null?0:b.onLine)?c.B(3):c.yield(Tj(a),3):c.yield(Tj(a),3);Uj(a);c.h=0})},3E4)}
function Tj(a,b){return a.u?a.u:a.u=new Promise(function(c){var d,e,f,g;return B(function(h){switch(h.h){case 1:return d=window.AbortController?new window.AbortController:void 0,f=(e=d)==null?void 0:e.signal,g=!1,wa(h,2,3),d&&(a.j=a.Ca.pa(function(){d.abort()},b||2E4)),h.yield(fetch("/generate_204",{method:"HEAD",
signal:f}),5);case 5:g=!0;case 3:h.M=[h.j];h.H=0;h.o=0;a.u=void 0;a.j&&(a.Ca.qa(a.j),a.j=0);g!==a.h&&(a.h=g,a.h?fi(a,"networkstatus-online"):fi(a,"networkstatus-offline"));c(g);za(h);break;case 2:ya(h),g=!1,h.B(3)}})})}
;function Xj(){this.data=[];this.h=-1}
Xj.prototype.set=function(a,b){b=b===void 0?!0:b;0<=a&&a<52&&Number.isInteger(a)&&this.data[a]!==b&&(this.data[a]=b,this.h=-1)};
Xj.prototype.get=function(a){return!!this.data[a]};
function Yj(a){a.h===-1&&(a.h=a.data.reduce(function(b,c,d){return b+(c?Math.pow(2,d):0)},0));
return a.h}
;function Zj(){this.blockSize=-1}
;function ak(){this.blockSize=-1;this.blockSize=64;this.h=[];this.u=[];this.H=[];this.j=[];this.j[0]=128;for(var a=1;a<this.blockSize;++a)this.j[a]=0;this.o=this.i=0;this.reset()}
Za(ak,Zj);ak.prototype.reset=function(){this.h[0]=1732584193;this.h[1]=4023233417;this.h[2]=2562383102;this.h[3]=271733878;this.h[4]=3285377520;this.o=this.i=0};
function bk(a,b,c){c||(c=0);var d=a.H;if(typeof b==="string")for(var e=0;e<16;e++)d[e]=b.charCodeAt(c)<<24|b.charCodeAt(c+1)<<16|b.charCodeAt(c+2)<<8|b.charCodeAt(c+3),c+=4;else for(e=0;e<16;e++)d[e]=b[c]<<24|b[c+1]<<16|b[c+2]<<8|b[c+3],c+=4;for(b=16;b<80;b++)c=d[b-3]^d[b-8]^d[b-14]^d[b-16],d[b]=(c<<1|c>>>31)&4294967295;b=a.h[0];c=a.h[1];e=a.h[2];for(var f=a.h[3],g=a.h[4],h,k,l=0;l<80;l++)l<40?l<20?(h=f^c&(e^f),k=1518500249):(h=c^e^f,k=1859775393):l<60?(h=c&e|f&(c|e),k=2400959708):(h=c^e^f,k=3395469782),
h=(b<<5|b>>>27)+h+g+k+d[l]&4294967295,g=f,f=e,e=(c<<30|c>>>2)&4294967295,c=b,b=h;a.h[0]=a.h[0]+b&4294967295;a.h[1]=a.h[1]+c&4294967295;a.h[2]=a.h[2]+e&4294967295;a.h[3]=a.h[3]+f&4294967295;a.h[4]=a.h[4]+g&4294967295}
ak.prototype.update=function(a,b){if(a!=null){b===void 0&&(b=a.length);for(var c=b-this.blockSize,d=0,e=this.u,f=this.i;d<b;){if(f==0)for(;d<=c;)bk(this,a,d),d+=this.blockSize;if(typeof a==="string")for(;d<b;){if(e[f]=a.charCodeAt(d),++f,++d,f==this.blockSize){bk(this,e);f=0;break}}else for(;d<b;)if(e[f]=a[d],++f,++d,f==this.blockSize){bk(this,e);f=0;break}}this.i=f;this.o+=b}};
ak.prototype.digest=function(){var a=[],b=this.o*8;this.i<56?this.update(this.j,56-this.i):this.update(this.j,this.blockSize-(this.i-56));for(var c=this.blockSize-1;c>=56;c--)this.u[c]=b&255,b/=256;bk(this,this.u);for(c=b=0;c<5;c++)for(var d=24;d>=0;d-=8)a[b]=this.h[c]>>d&255,++b;return a};function ck(a){return typeof a.className=="string"?a.className:a.getAttribute&&a.getAttribute("class")||""}
function dk(a,b){typeof a.className=="string"?a.className=b:a.setAttribute&&a.setAttribute("class",b)}
function ek(a,b){a.classList?b=a.classList.contains(b):(a=a.classList?a.classList:ck(a).match(/\S+/g)||[],b=Ob(a,b)>=0);return b}
function fk(){var a=document.body;a.classList?a.classList.remove("inverted-hdpi"):ek(a,"inverted-hdpi")&&dk(a,Array.prototype.filter.call(a.classList?a.classList:ck(a).match(/\S+/g)||[],function(b){return b!="inverted-hdpi"}).join(" "))}
;function gk(){}
gk.prototype.next=function(){return hk};
var hk={done:!0,value:void 0};gk.prototype.tb=function(){return this};function ik(a){if(a instanceof jk||a instanceof kk||a instanceof lk)return a;if(typeof a.next=="function")return new jk(function(){return a});
if(typeof a[Symbol.iterator]=="function")return new jk(function(){return a[Symbol.iterator]()});
if(typeof a.tb=="function")return new jk(function(){return a.tb()});
throw Error("Not an iterator or iterable.");}
function jk(a){this.h=a}
jk.prototype.tb=function(){return new kk(this.h())};
jk.prototype[Symbol.iterator]=function(){return new lk(this.h())};
jk.prototype.i=function(){return new lk(this.h())};
function kk(a){this.h=a}
v(kk,gk);kk.prototype.next=function(){return this.h.next()};
kk.prototype[Symbol.iterator]=function(){return new lk(this.h)};
kk.prototype.i=function(){return new lk(this.h)};
function lk(a){jk.call(this,function(){return a});
this.j=a}
v(lk,jk);lk.prototype.next=function(){return this.j.next()};function N(a){I.call(this);this.u=1;this.j=[];this.o=0;this.h=[];this.i={};this.A=!!a}
Za(N,I);p=N.prototype;p.subscribe=function(a,b,c){var d=this.i[a];d||(d=this.i[a]=[]);var e=this.u;this.h[e]=a;this.h[e+1]=b;this.h[e+2]=c;this.u=e+3;d.push(e);return e};
p.unsubscribe=function(a,b,c){if(a=this.i[a]){var d=this.h;if(a=a.find(function(e){return d[e+1]==b&&d[e+2]==c}))return this.fc(a)}return!1};
p.fc=function(a){var b=this.h[a];if(b){var c=this.i[b];this.o!=0?(this.j.push(a),this.h[a+1]=function(){}):(c&&Vb(c,a),delete this.h[a],delete this.h[a+1],delete this.h[a+2])}return!!b};
p.sb=function(a,b){var c=this.i[a];if(c){var d=Array(arguments.length-1),e=arguments.length,f;for(f=1;f<e;f++)d[f-1]=arguments[f];if(this.A)for(f=0;f<c.length;f++)e=c[f],mk(this.h[e+1],this.h[e+2],d);else{this.o++;try{for(f=0,e=c.length;f<e&&!this.ea;f++){var g=c[f];this.h[g+1].apply(this.h[g+2],d)}}finally{if(this.o--,this.j.length>0&&this.o==0)for(;c=this.j.pop();)this.fc(c)}}return f!=0}return!1};
function mk(a,b,c){qi(function(){a.apply(b,c)})}
p.clear=function(a){if(a){var b=this.i[a];b&&(b.forEach(this.fc,this),delete this.i[a])}else this.h.length=0,this.i={}};
p.ba=function(){N.Aa.ba.call(this);this.clear();this.j.length=0};function nk(a){this.h=a}
nk.prototype.set=function(a,b){b===void 0?this.h.remove(a):this.h.set(a,(new Si).serialize(b))};
nk.prototype.get=function(a){try{var b=this.h.get(a)}catch(c){return}if(b!==null)try{return JSON.parse(b)}catch(c){throw"Storage: Invalid value was encountered";}};
nk.prototype.remove=function(a){this.h.remove(a)};function ok(a){this.h=a}
Za(ok,nk);function pk(a){this.data=a}
function qk(a){return a===void 0||a instanceof pk?a:new pk(a)}
ok.prototype.set=function(a,b){ok.Aa.set.call(this,a,qk(b))};
ok.prototype.i=function(a){a=ok.Aa.get.call(this,a);if(a===void 0||a instanceof Object)return a;throw"Storage: Invalid value was encountered";};
ok.prototype.get=function(a){if(a=this.i(a)){if(a=a.data,a===void 0)throw"Storage: Invalid value was encountered";}else a=void 0;return a};function rk(a){this.h=a}
Za(rk,ok);rk.prototype.set=function(a,b,c){if(b=qk(b)){if(c){if(c<Xa()){rk.prototype.remove.call(this,a);return}b.expiration=c}b.creation=Xa()}rk.Aa.set.call(this,a,b)};
rk.prototype.i=function(a){var b=rk.Aa.i.call(this,a);if(b){var c=b.creation,d=b.expiration;if(d&&d<Xa()||c&&c>Xa())rk.prototype.remove.call(this,a);else return b}};function sk(){}
;function tk(){}
Za(tk,sk);tk.prototype[Symbol.iterator]=function(){return ik(this.tb(!0)).i()};
tk.prototype.clear=function(){var a=Array.from(this);a=y(a);for(var b=a.next();!b.done;b=a.next())this.remove(b.value)};function uk(a){this.h=a;this.i=null}
Za(uk,tk);p=uk.prototype;p.isAvailable=function(){if(this.i===null){var a=this.h;if(a)try{a.setItem("__sak","1");a.removeItem("__sak");var b=!0}catch(c){b=c instanceof DOMException&&(c.name==="QuotaExceededError"||c.code===22||c.code===1014||c.name==="NS_ERROR_DOM_QUOTA_REACHED")&&a&&a.length!==0}else b=!1;this.i=b}return this.i};
p.set=function(a,b){vk(this);try{this.h.setItem(a,b)}catch(c){if(this.h.length==0)throw"Storage mechanism: Storage disabled";throw"Storage mechanism: Quota exceeded";}};
p.get=function(a){vk(this);a=this.h.getItem(a);if(typeof a!=="string"&&a!==null)throw"Storage mechanism: Invalid value was encountered";return a};
p.remove=function(a){vk(this);this.h.removeItem(a)};
p.tb=function(a){vk(this);var b=0,c=this.h,d=new gk;d.next=function(){if(b>=c.length)return hk;var e=c.key(b++);if(a)return{value:e,done:!1};e=c.getItem(e);if(typeof e!=="string")throw"Storage mechanism: Invalid value was encountered";return{value:e,done:!1}};
return d};
p.clear=function(){vk(this);this.h.clear()};
p.key=function(a){vk(this);return this.h.key(a)};
function vk(a){if(a.h==null)throw Error("Storage mechanism: Storage unavailable");a.isAvailable()||Sc(Error("Storage mechanism: Storage unavailable"))}
;function wk(){var a=null;try{a=D.localStorage||null}catch(b){}uk.call(this,a)}
Za(wk,uk);function xk(a,b){this.i=a;this.h=b+"::"}
Za(xk,tk);xk.prototype.set=function(a,b){this.i.set(this.h+a,b)};
xk.prototype.get=function(a){return this.i.get(this.h+a)};
xk.prototype.remove=function(a){this.i.remove(this.h+a)};
xk.prototype.tb=function(a){var b=this.i[Symbol.iterator](),c=this,d=new gk;d.next=function(){var e=b.next();if(e.done)return e;for(e=e.value;e.slice(0,c.h.length)!=c.h;){e=b.next();if(e.done)return e;e=e.value}return{value:a?e.slice(c.h.length):c.i.get(e),done:!1}};
return d};function yk(a){if(a.Wa&&typeof a.Wa=="function")return a.Wa();if(typeof Map!=="undefined"&&a instanceof Map||typeof Set!=="undefined"&&a instanceof Set)return Array.from(a.values());if(typeof a==="string")return a.split("");if(La(a)){for(var b=[],c=a.length,d=0;d<c;d++)b.push(a[d]);return b}return tg(a)}
function zk(a){if(a.Tb&&typeof a.Tb=="function")return a.Tb();if(!a.Wa||typeof a.Wa!="function"){if(typeof Map!=="undefined"&&a instanceof Map)return Array.from(a.keys());if(!(typeof Set!=="undefined"&&a instanceof Set)){if(La(a)||typeof a==="string"){var b=[];a=a.length;for(var c=0;c<a;c++)b.push(c);return b}b=[];c=0;for(var d in a)b[c++]=d;return b}}}
function Ak(a,b,c){if(a.forEach&&typeof a.forEach=="function")a.forEach(b,c);else if(La(a)||typeof a==="string")Array.prototype.forEach.call(a,b,c);else for(var d=zk(a),e=yk(a),f=e.length,g=0;g<f;g++)b.call(c,e[g],d&&d[g],a)}
;function Bk(a){this.i=this.A=this.j="";this.G=null;this.u=this.h="";this.o=!1;var b;a instanceof Bk?(this.o=a.o,Ck(this,a.j),this.A=a.A,this.i=a.i,Dk(this,a.G),this.h=a.h,Ek(this,a.H.clone()),this.u=a.u):a&&(b=String(a).match(fc))?(this.o=!1,Ck(this,b[1]||"",!0),this.A=Fk(b[2]||""),this.i=Fk(b[3]||"",!0),Dk(this,b[4]),this.h=Fk(b[5]||"",!0),Ek(this,b[6]||"",!0),this.u=Fk(b[7]||"")):(this.o=!1,this.H=new Gk(null,this.o))}
Bk.prototype.toString=function(){var a=[],b=this.j;b&&a.push(Hk(b,Ik,!0),":");var c=this.i;if(c||b=="file")a.push("//"),(b=this.A)&&a.push(Hk(b,Ik,!0),"@"),a.push(encodeURIComponent(String(c)).replace(/%25([0-9a-fA-F]{2})/g,"%$1")),c=this.G,c!=null&&a.push(":",String(c));if(c=this.h)this.i&&c.charAt(0)!="/"&&a.push("/"),a.push(Hk(c,c.charAt(0)=="/"?Jk:Kk,!0));(c=this.H.toString())&&a.push("?",c);(c=this.u)&&a.push("#",Hk(c,Lk));return a.join("")};
Bk.prototype.resolve=function(a){var b=this.clone(),c=!!a.j;c?Ck(b,a.j):c=!!a.A;c?b.A=a.A:c=!!a.i;c?b.i=a.i:c=a.G!=null;var d=a.h;if(c)Dk(b,a.G);else if(c=!!a.h){if(d.charAt(0)!="/")if(this.i&&!this.h)d="/"+d;else{var e=b.h.lastIndexOf("/");e!=-1&&(d=b.h.slice(0,e+1)+d)}e=d;if(e==".."||e==".")d="";else if(e.indexOf("./")!=-1||e.indexOf("/.")!=-1){d=e.lastIndexOf("/",0)==0;e=e.split("/");for(var f=[],g=0;g<e.length;){var h=e[g++];h=="."?d&&g==e.length&&f.push(""):h==".."?((f.length>1||f.length==1&&
f[0]!="")&&f.pop(),d&&g==e.length&&f.push("")):(f.push(h),d=!0)}d=f.join("/")}else d=e}c?b.h=d:c=a.H.toString()!=="";c?Ek(b,a.H.clone()):c=!!a.u;c&&(b.u=a.u);return b};
Bk.prototype.clone=function(){return new Bk(this)};
function Ck(a,b,c){a.j=c?Fk(b,!0):b;a.j&&(a.j=a.j.replace(/:$/,""))}
function Dk(a,b){if(b){b=Number(b);if(isNaN(b)||b<0)throw Error("Bad port number "+b);a.G=b}else a.G=null}
function Ek(a,b,c){b instanceof Gk?(a.H=b,Mk(a.H,a.o)):(c||(b=Hk(b,Nk)),a.H=new Gk(b,a.o))}
function Fk(a,b){return a?b?decodeURI(a.replace(/%25/g,"%2525")):decodeURIComponent(a):""}
function Hk(a,b,c){return typeof a==="string"?(a=encodeURI(a).replace(b,Ok),c&&(a=a.replace(/%25([0-9a-fA-F]{2})/g,"%$1")),a):null}
function Ok(a){a=a.charCodeAt(0);return"%"+(a>>4&15).toString(16)+(a&15).toString(16)}
var Ik=/[#\/\?@]/g,Kk=/[#\?:]/g,Jk=/[#\?]/g,Nk=/[#\?@]/g,Lk=/#/g;function Gk(a,b){this.i=this.h=null;this.j=a||null;this.o=!!b}
function Pk(a){a.h||(a.h=new Map,a.i=0,a.j&&mc(a.j,function(b,c){a.add(dc(b),c)}))}
p=Gk.prototype;p.add=function(a,b){Pk(this);this.j=null;a=Qk(this,a);var c=this.h.get(a);c||this.h.set(a,c=[]);c.push(b);this.i=this.i+1;return this};
p.remove=function(a){Pk(this);a=Qk(this,a);return this.h.has(a)?(this.j=null,this.i=this.i-this.h.get(a).length,this.h.delete(a)):!1};
p.clear=function(){this.h=this.j=null;this.i=0};
function Rk(a,b){Pk(a);b=Qk(a,b);return a.h.has(b)}
p.forEach=function(a,b){Pk(this);this.h.forEach(function(c,d){c.forEach(function(e){a.call(b,e,d,this)},this)},this)};
p.Tb=function(){Pk(this);for(var a=Array.from(this.h.values()),b=Array.from(this.h.keys()),c=[],d=0;d<b.length;d++)for(var e=a[d],f=0;f<e.length;f++)c.push(b[d]);return c};
p.Wa=function(a){Pk(this);var b=[];if(typeof a==="string")Rk(this,a)&&(b=b.concat(this.h.get(Qk(this,a))));else{a=Array.from(this.h.values());for(var c=0;c<a.length;c++)b=b.concat(a[c])}return b};
p.set=function(a,b){Pk(this);this.j=null;a=Qk(this,a);Rk(this,a)&&(this.i=this.i-this.h.get(a).length);this.h.set(a,[b]);this.i=this.i+1;return this};
p.get=function(a,b){if(!a)return b;a=this.Wa(a);return a.length>0?String(a[0]):b};
p.toString=function(){if(this.j)return this.j;if(!this.h)return"";for(var a=[],b=Array.from(this.h.keys()),c=0;c<b.length;c++){var d=b[c],e=encodeURIComponent(String(d));d=this.Wa(d);for(var f=0;f<d.length;f++){var g=e;d[f]!==""&&(g+="="+encodeURIComponent(String(d[f])));a.push(g)}}return this.j=a.join("&")};
p.clone=function(){var a=new Gk;a.j=this.j;this.h&&(a.h=new Map(this.h),a.i=this.i);return a};
function Qk(a,b){b=String(b);a.o&&(b=b.toLowerCase());return b}
function Mk(a,b){b&&!a.o&&(Pk(a),a.j=null,a.h.forEach(function(c,d){var e=d.toLowerCase();d!=e&&(this.remove(d),this.remove(e),c.length>0&&(this.j=null,this.h.set(Qk(this,e),Wb(c)),this.i=this.i+c.length))},a));
a.o=b}
p.extend=function(a){for(var b=0;b<arguments.length;b++)Ak(arguments[b],function(c,d){this.add(d,c)},this)};/*

 (The MIT License)

 Copyright (C) 2014 by Vitaly Puzrin

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.

 -----------------------------------------------------------------------------
 Ported from zlib, which is under the following license
 https://github.com/madler/zlib/blob/master/zlib.h

 zlib.h -- interface of the 'zlib' general purpose compression library
   version 1.2.8, April 28th, 2013
   Copyright (C) 1995-2013 Jean-loup Gailly and Mark Adler
   This software is provided 'as-is', without any express or implied
   warranty.  In no event will the authors be held liable for any damages
   arising from the use of this software.
   Permission is granted to anyone to use this software for any purpose,
   including commercial applications, and to alter it and redistribute it
   freely, subject to the following restrictions:
   1. The origin of this software must not be misrepresented; you must not
      claim that you wrote the original software. If you use this software
      in a product, an acknowledgment in the product documentation would be
      appreciated but is not required.
   2. Altered source versions must be plainly marked as such, and must not be
      misrepresented as being the original software.
   3. This notice may not be removed or altered from any source distribution.
   Jean-loup Gailly        Mark Adler
   jloup@gzip.org          madler@alumni.caltech.edu
   The data format used by the zlib library is described by RFCs (Request for
   Comments) 1950 to 1952 in the files http://tools.ietf.org/html/rfc1950
   (zlib format), rfc1951 (deflate format) and rfc1952 (gzip format).
*/
var O={},Sk=typeof Uint8Array!=="undefined"&&typeof Uint16Array!=="undefined"&&typeof Int32Array!=="undefined";O.assign=function(a){for(var b=Array.prototype.slice.call(arguments,1);b.length;){var c=b.shift();if(c){if(typeof c!=="object")throw new TypeError(c+"must be non-object");for(var d in c)Object.prototype.hasOwnProperty.call(c,d)&&(a[d]=c[d])}}return a};
O.jd=function(a,b){if(a.length===b)return a;if(a.subarray)return a.subarray(0,b);a.length=b;return a};
var Tk={ub:function(a,b,c,d,e){if(b.subarray&&a.subarray)a.set(b.subarray(c,c+d),e);else for(var f=0;f<d;f++)a[e+f]=b[c+f]},
wd:function(a){var b,c;var d=c=0;for(b=a.length;d<b;d++)c+=a[d].length;var e=new Uint8Array(c);d=c=0;for(b=a.length;d<b;d++){var f=a[d];e.set(f,c);c+=f.length}return e}},Uk={ub:function(a,b,c,d,e){for(var f=0;f<d;f++)a[e+f]=b[c+f]},
wd:function(a){return[].concat.apply([],a)}};
O.tf=function(){Sk?(O.rb=Uint8Array,O.Ja=Uint16Array,O.Wd=Int32Array,O.assign(O,Tk)):(O.rb=Array,O.Ja=Array,O.Wd=Array,O.assign(O,Uk))};
O.tf();var Vk=!0;try{new Uint8Array(1)}catch(a){Vk=!1}
function Wk(a){var b,c,d=a.length,e=0;for(b=0;b<d;b++){var f=a.charCodeAt(b);if((f&64512)===55296&&b+1<d){var g=a.charCodeAt(b+1);(g&64512)===56320&&(f=65536+(f-55296<<10)+(g-56320),b++)}e+=f<128?1:f<2048?2:f<65536?3:4}var h=new O.rb(e);for(b=c=0;c<e;b++)f=a.charCodeAt(b),(f&64512)===55296&&b+1<d&&(g=a.charCodeAt(b+1),(g&64512)===56320&&(f=65536+(f-55296<<10)+(g-56320),b++)),f<128?h[c++]=f:(f<2048?h[c++]=192|f>>>6:(f<65536?h[c++]=224|f>>>12:(h[c++]=240|f>>>18,h[c++]=128|f>>>12&63),h[c++]=128|f>>>
6&63),h[c++]=128|f&63);return h}
;var Xk={};Xk=function(a,b,c,d){var e=a&65535|0;a=a>>>16&65535|0;for(var f;c!==0;){f=c>2E3?2E3:c;c-=f;do e=e+b[d++]|0,a=a+e|0;while(--f);e%=65521;a%=65521}return e|a<<16|0};for(var Yk={},Zk,$k=[],al=0;al<256;al++){Zk=al;for(var bl=0;bl<8;bl++)Zk=Zk&1?3988292384^Zk>>>1:Zk>>>1;$k[al]=Zk}Yk=function(a,b,c,d){c=d+c;for(a^=-1;d<c;d++)a=a>>>8^$k[(a^b[d])&255];return a^-1};var cl={};cl={2:"need dictionary",1:"stream end",0:"","-1":"file error","-2":"stream error","-3":"data error","-4":"insufficient memory","-5":"buffer error","-6":"incompatible version"};function dl(a){for(var b=a.length;--b>=0;)a[b]=0}
var el=[0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0],fl=[0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13],gl=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7],hl=[16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15],il=Array(576);dl(il);var jl=Array(60);dl(jl);var kl=Array(512);dl(kl);var ll=Array(256);dl(ll);var ml=Array(29);dl(ml);var nl=Array(30);dl(nl);function ol(a,b,c,d,e){this.Pd=a;this.xe=b;this.we=c;this.pe=d;this.Oe=e;this.zd=a&&a.length}
var pl,ql,rl;function sl(a,b){this.vd=a;this.Fb=0;this.cb=b}
function tl(a,b){a.aa[a.pending++]=b&255;a.aa[a.pending++]=b>>>8&255}
function ul(a,b,c){a.ia>16-c?(a.oa|=b<<a.ia&65535,tl(a,a.oa),a.oa=b>>16-a.ia,a.ia+=c-16):(a.oa|=b<<a.ia&65535,a.ia+=c)}
function vl(a,b,c){ul(a,c[b*2],c[b*2+1])}
function wl(a,b){var c=0;do c|=a&1,a>>>=1,c<<=1;while(--b>0);return c>>>1}
function xl(a,b,c){var d=Array(16),e=0,f;for(f=1;f<=15;f++)d[f]=e=e+c[f-1]<<1;for(c=0;c<=b;c++)e=a[c*2+1],e!==0&&(a[c*2]=wl(d[e]++,e))}
function yl(a){var b;for(b=0;b<286;b++)a.ra[b*2]=0;for(b=0;b<30;b++)a.hb[b*2]=0;for(b=0;b<19;b++)a.ja[b*2]=0;a.ra[512]=1;a.Pa=a.Ib=0;a.ya=a.matches=0}
function zl(a){a.ia>8?tl(a,a.oa):a.ia>0&&(a.aa[a.pending++]=a.oa);a.oa=0;a.ia=0}
function Al(a,b,c){zl(a);tl(a,c);tl(a,~c);O.ub(a.aa,a.window,b,c,a.pending);a.pending+=c}
function Bl(a,b,c,d){var e=b*2,f=c*2;return a[e]<a[f]||a[e]===a[f]&&d[b]<=d[c]}
function Cl(a,b,c){for(var d=a.da[c],e=c<<1;e<=a.Na;){e<a.Na&&Bl(b,a.da[e+1],a.da[e],a.depth)&&e++;if(Bl(b,d,a.da[e],a.depth))break;a.da[c]=a.da[e];c=e;e<<=1}a.da[c]=d}
function Dl(a,b,c){var d=0;if(a.ya!==0){do{var e=a.aa[a.Qb+d*2]<<8|a.aa[a.Qb+d*2+1];var f=a.aa[a.Tc+d];d++;if(e===0)vl(a,f,b);else{var g=ll[f];vl(a,g+256+1,b);var h=el[g];h!==0&&(f-=ml[g],ul(a,f,h));e--;g=e<256?kl[e]:kl[256+(e>>>7)];vl(a,g,c);h=fl[g];h!==0&&(e-=nl[g],ul(a,e,h))}}while(d<a.ya)}vl(a,256,b)}
function El(a,b){var c=b.vd,d=b.cb.Pd,e=b.cb.zd,f=b.cb.pe,g,h=-1;a.Na=0;a.Ab=573;for(g=0;g<f;g++)c[g*2]!==0?(a.da[++a.Na]=h=g,a.depth[g]=0):c[g*2+1]=0;for(;a.Na<2;){var k=a.da[++a.Na]=h<2?++h:0;c[k*2]=1;a.depth[k]=0;a.Pa--;e&&(a.Ib-=d[k*2+1])}b.Fb=h;for(g=a.Na>>1;g>=1;g--)Cl(a,c,g);k=f;do g=a.da[1],a.da[1]=a.da[a.Na--],Cl(a,c,1),d=a.da[1],a.da[--a.Ab]=g,a.da[--a.Ab]=d,c[k*2]=c[g*2]+c[d*2],a.depth[k]=(a.depth[g]>=a.depth[d]?a.depth[g]:a.depth[d])+1,c[g*2+1]=c[d*2+1]=k,a.da[1]=k++,Cl(a,c,1);while(a.Na>=
2);a.da[--a.Ab]=a.da[1];g=b.vd;k=b.Fb;d=b.cb.Pd;e=b.cb.zd;f=b.cb.xe;var l=b.cb.we,m=b.cb.Oe,n,r=0;for(n=0;n<=15;n++)a.Ka[n]=0;g[a.da[a.Ab]*2+1]=0;for(b=a.Ab+1;b<573;b++){var t=a.da[b];n=g[g[t*2+1]*2+1]+1;n>m&&(n=m,r++);g[t*2+1]=n;if(!(t>k)){a.Ka[n]++;var w=0;t>=l&&(w=f[t-l]);var x=g[t*2];a.Pa+=x*(n+w);e&&(a.Ib+=x*(d[t*2+1]+w))}}if(r!==0){do{for(n=m-1;a.Ka[n]===0;)n--;a.Ka[n]--;a.Ka[n+1]+=2;a.Ka[m]--;r-=2}while(r>0);for(n=m;n!==0;n--)for(t=a.Ka[n];t!==0;)d=a.da[--b],d>k||(g[d*2+1]!==n&&(a.Pa+=(n-g[d*
2+1])*g[d*2],g[d*2+1]=n),t--)}xl(c,h,a.Ka)}
function Fl(a,b,c){var d,e=-1,f=b[1],g=0,h=7,k=4;f===0&&(h=138,k=3);b[(c+1)*2+1]=65535;for(d=0;d<=c;d++){var l=f;f=b[(d+1)*2+1];++g<h&&l===f||(g<k?a.ja[l*2]+=g:l!==0?(l!==e&&a.ja[l*2]++,a.ja[32]++):g<=10?a.ja[34]++:a.ja[36]++,g=0,e=l,f===0?(h=138,k=3):l===f?(h=6,k=3):(h=7,k=4))}}
function Gl(a,b,c){var d,e=-1,f=b[1],g=0,h=7,k=4;f===0&&(h=138,k=3);for(d=0;d<=c;d++){var l=f;f=b[(d+1)*2+1];if(!(++g<h&&l===f)){if(g<k){do vl(a,l,a.ja);while(--g!==0)}else l!==0?(l!==e&&(vl(a,l,a.ja),g--),vl(a,16,a.ja),ul(a,g-3,2)):g<=10?(vl(a,17,a.ja),ul(a,g-3,3)):(vl(a,18,a.ja),ul(a,g-11,7));g=0;e=l;f===0?(h=138,k=3):l===f?(h=6,k=3):(h=7,k=4)}}}
function Hl(a){var b=4093624447,c;for(c=0;c<=31;c++,b>>>=1)if(b&1&&a.ra[c*2]!==0)return 0;if(a.ra[18]!==0||a.ra[20]!==0||a.ra[26]!==0)return 1;for(c=32;c<256;c++)if(a.ra[c*2]!==0)return 1;return 0}
var Il=!1;function Jl(a,b,c){a.aa[a.Qb+a.ya*2]=b>>>8&255;a.aa[a.Qb+a.ya*2+1]=b&255;a.aa[a.Tc+a.ya]=c&255;a.ya++;b===0?a.ra[c*2]++:(a.matches++,b--,a.ra[(ll[c]+256+1)*2]++,a.hb[(b<256?kl[b]:kl[256+(b>>>7)])*2]++);return a.ya===a.Vb-1}
;function Kl(a,b){a.msg=cl[b];return b}
function Ll(a){for(var b=a.length;--b>=0;)a[b]=0}
function Ml(a){var b=a.state,c=b.pending;c>a.S&&(c=a.S);c!==0&&(O.ub(a.output,b.aa,b.Yb,c,a.Gb),a.Gb+=c,b.Yb+=c,a.md+=c,a.S-=c,b.pending-=c,b.pending===0&&(b.Yb=0))}
function Nl(a,b){var c=a.va>=0?a.va:-1,d=a.v-a.va,e=0;if(a.level>0){a.P.Mc===2&&(a.P.Mc=Hl(a));El(a,a.xc);El(a,a.oc);Fl(a,a.ra,a.xc.Fb);Fl(a,a.hb,a.oc.Fb);El(a,a.td);for(e=18;e>=3&&a.ja[hl[e]*2+1]===0;e--);a.Pa+=3*(e+1)+5+5+4;var f=a.Pa+3+7>>>3;var g=a.Ib+3+7>>>3;g<=f&&(f=g)}else f=g=d+5;if(d+4<=f&&c!==-1)ul(a,b?1:0,3),Al(a,c,d);else if(a.strategy===4||g===f)ul(a,2+(b?1:0),3),Dl(a,il,jl);else{ul(a,4+(b?1:0),3);c=a.xc.Fb+1;d=a.oc.Fb+1;e+=1;ul(a,c-257,5);ul(a,d-1,5);ul(a,e-4,4);for(f=0;f<e;f++)ul(a,
a.ja[hl[f]*2+1],3);Gl(a,a.ra,c-1);Gl(a,a.hb,d-1);Dl(a,a.ra,a.hb)}yl(a);b&&zl(a);a.va=a.v;Ml(a.P)}
function P(a,b){a.aa[a.pending++]=b}
function Ol(a,b){a.aa[a.pending++]=b>>>8&255;a.aa[a.pending++]=b&255}
function Pl(a,b){var c=a.Cd,d=a.v,e=a.wa,f=a.Ed,g=a.v>a.la-262?a.v-(a.la-262):0,h=a.window,k=a.eb,l=a.Ia,m=a.v+258,n=h[d+e-1],r=h[d+e];a.wa>=a.yd&&(c>>=2);f>a.D&&(f=a.D);do{var t=b;if(h[t+e]===r&&h[t+e-1]===n&&h[t]===h[d]&&h[++t]===h[d+1]){d+=2;for(t++;h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&h[++d]===h[++t]&&d<m;);t=258-(m-d);d=m-258;if(t>e){a.Eb=b;e=t;if(t>=f)break;n=h[d+e-1];r=h[d+e]}}}while((b=l[b&k])>g&&--c!==0);return e<=
a.D?e:a.D}
function Ql(a){var b=a.la,c;do{var d=a.Ud-a.D-a.v;if(a.v>=b+(b-262)){O.ub(a.window,a.window,b,b,0);a.Eb-=b;a.v-=b;a.va-=b;var e=c=a.wc;do{var f=a.head[--e];a.head[e]=f>=b?f-b:0}while(--c);e=c=b;do f=a.Ia[--e],a.Ia[e]=f>=b?f-b:0;while(--c);d+=b}if(a.P.na===0)break;e=a.P;c=a.window;f=a.v+a.D;var g=e.na;g>d&&(g=d);g===0?c=0:(e.na-=g,O.ub(c,e.input,e.nb,g,f),e.state.wrap===1?e.J=Xk(e.J,c,g,f):e.state.wrap===2&&(e.J=Yk(e.J,c,g,f)),e.nb+=g,e.qb+=g,c=g);a.D+=c;if(a.D+a.sa>=3)for(d=a.v-a.sa,a.R=a.window[d],
a.R=(a.R<<a.Ma^a.window[d+1])&a.La;a.sa&&!(a.R=(a.R<<a.Ma^a.window[d+3-1])&a.La,a.Ia[d&a.eb]=a.head[a.R],a.head[a.R]=d,d++,a.sa--,a.D+a.sa<3););}while(a.D<262&&a.P.na!==0)}
function Rl(a,b){for(var c;;){if(a.D<262){Ql(a);if(a.D<262&&b===0)return 1;if(a.D===0)break}c=0;a.D>=3&&(a.R=(a.R<<a.Ma^a.window[a.v+3-1])&a.La,c=a.Ia[a.v&a.eb]=a.head[a.R],a.head[a.R]=a.v);c!==0&&a.v-c<=a.la-262&&(a.T=Pl(a,c));if(a.T>=3)if(c=Jl(a,a.v-a.Eb,a.T-3),a.D-=a.T,a.T<=a.Wc&&a.D>=3){a.T--;do a.v++,a.R=(a.R<<a.Ma^a.window[a.v+3-1])&a.La,a.Ia[a.v&a.eb]=a.head[a.R],a.head[a.R]=a.v;while(--a.T!==0);a.v++}else a.v+=a.T,a.T=0,a.R=a.window[a.v],a.R=(a.R<<a.Ma^a.window[a.v+1])&a.La;else c=Jl(a,0,
a.window[a.v]),a.D--,a.v++;if(c&&(Nl(a,!1),a.P.S===0))return 1}a.sa=a.v<2?a.v:2;return b===4?(Nl(a,!0),a.P.S===0?3:4):a.ya&&(Nl(a,!1),a.P.S===0)?1:2}
function Sl(a,b){for(var c,d;;){if(a.D<262){Ql(a);if(a.D<262&&b===0)return 1;if(a.D===0)break}c=0;a.D>=3&&(a.R=(a.R<<a.Ma^a.window[a.v+3-1])&a.La,c=a.Ia[a.v&a.eb]=a.head[a.R],a.head[a.R]=a.v);a.wa=a.T;a.Hd=a.Eb;a.T=2;c!==0&&a.wa<a.Wc&&a.v-c<=a.la-262&&(a.T=Pl(a,c),a.T<=5&&(a.strategy===1||a.T===3&&a.v-a.Eb>4096)&&(a.T=2));if(a.wa>=3&&a.T<=a.wa){d=a.v+a.D-3;c=Jl(a,a.v-1-a.Hd,a.wa-3);a.D-=a.wa-1;a.wa-=2;do++a.v<=d&&(a.R=(a.R<<a.Ma^a.window[a.v+3-1])&a.La,a.Ia[a.v&a.eb]=a.head[a.R],a.head[a.R]=a.v);
while(--a.wa!==0);a.lb=0;a.T=2;a.v++;if(c&&(Nl(a,!1),a.P.S===0))return 1}else if(a.lb){if((c=Jl(a,0,a.window[a.v-1]))&&Nl(a,!1),a.v++,a.D--,a.P.S===0)return 1}else a.lb=1,a.v++,a.D--}a.lb&&(Jl(a,0,a.window[a.v-1]),a.lb=0);a.sa=a.v<2?a.v:2;return b===4?(Nl(a,!0),a.P.S===0?3:4):a.ya&&(Nl(a,!1),a.P.S===0)?1:2}
function Tl(a,b){for(var c,d,e,f=a.window;;){if(a.D<=258){Ql(a);if(a.D<=258&&b===0)return 1;if(a.D===0)break}a.T=0;if(a.D>=3&&a.v>0&&(d=a.v-1,c=f[d],c===f[++d]&&c===f[++d]&&c===f[++d])){for(e=a.v+258;c===f[++d]&&c===f[++d]&&c===f[++d]&&c===f[++d]&&c===f[++d]&&c===f[++d]&&c===f[++d]&&c===f[++d]&&d<e;);a.T=258-(e-d);a.T>a.D&&(a.T=a.D)}a.T>=3?(c=Jl(a,1,a.T-3),a.D-=a.T,a.v+=a.T,a.T=0):(c=Jl(a,0,a.window[a.v]),a.D--,a.v++);if(c&&(Nl(a,!1),a.P.S===0))return 1}a.sa=0;return b===4?(Nl(a,!0),a.P.S===0?3:4):
a.ya&&(Nl(a,!1),a.P.S===0)?1:2}
function Ul(a,b){for(var c;;){if(a.D===0&&(Ql(a),a.D===0)){if(b===0)return 1;break}a.T=0;c=Jl(a,0,a.window[a.v]);a.D--;a.v++;if(c&&(Nl(a,!1),a.P.S===0))return 1}a.sa=0;return b===4?(Nl(a,!0),a.P.S===0?3:4):a.ya&&(Nl(a,!1),a.P.S===0)?1:2}
function Vl(a,b,c,d,e){this.Be=a;this.Ne=b;this.Qe=c;this.Me=d;this.ye=e}
var Wl;Wl=[new Vl(0,0,0,0,function(a,b){var c=65535;for(c>a.za-5&&(c=a.za-5);;){if(a.D<=1){Ql(a);if(a.D===0&&b===0)return 1;if(a.D===0)break}a.v+=a.D;a.D=0;var d=a.va+c;if(a.v===0||a.v>=d)if(a.D=a.v-d,a.v=d,Nl(a,!1),a.P.S===0)return 1;if(a.v-a.va>=a.la-262&&(Nl(a,!1),a.P.S===0))return 1}a.sa=0;if(b===4)return Nl(a,!0),a.P.S===0?3:4;a.v>a.va&&Nl(a,!1);return 1}),
new Vl(4,4,8,4,Rl),new Vl(4,5,16,8,Rl),new Vl(4,6,32,32,Rl),new Vl(4,4,16,16,Sl),new Vl(8,16,32,32,Sl),new Vl(8,16,128,128,Sl),new Vl(8,32,128,256,Sl),new Vl(32,128,258,1024,Sl),new Vl(32,258,258,4096,Sl)];
function Xl(){this.P=null;this.status=0;this.aa=null;this.wrap=this.pending=this.Yb=this.za=0;this.I=null;this.Ba=0;this.method=8;this.Cb=-1;this.eb=this.pd=this.la=0;this.window=null;this.Ud=0;this.head=this.Ia=null;this.Ed=this.yd=this.strategy=this.level=this.Wc=this.Cd=this.wa=this.D=this.Eb=this.v=this.lb=this.Hd=this.T=this.va=this.Ma=this.La=this.Rc=this.wc=this.R=0;this.ra=new O.Ja(1146);this.hb=new O.Ja(122);this.ja=new O.Ja(78);Ll(this.ra);Ll(this.hb);Ll(this.ja);this.td=this.oc=this.xc=
null;this.Ka=new O.Ja(16);this.da=new O.Ja(573);Ll(this.da);this.Ab=this.Na=0;this.depth=new O.Ja(573);Ll(this.depth);this.ia=this.oa=this.sa=this.matches=this.Ib=this.Pa=this.Qb=this.ya=this.Vb=this.Tc=0}
function Yl(a,b){if(!a||!a.state||b>5||b<0)return a?Kl(a,-2):-2;var c=a.state;if(!a.output||!a.input&&a.na!==0||c.status===666&&b!==4)return Kl(a,a.S===0?-5:-2);c.P=a;var d=c.Cb;c.Cb=b;if(c.status===42)if(c.wrap===2)a.J=0,P(c,31),P(c,139),P(c,8),c.I?(P(c,(c.I.text?1:0)+(c.I.Xa?2:0)+(c.I.extra?4:0)+(c.I.name?8:0)+(c.I.comment?16:0)),P(c,c.I.time&255),P(c,c.I.time>>8&255),P(c,c.I.time>>16&255),P(c,c.I.time>>24&255),P(c,c.level===9?2:c.strategy>=2||c.level<2?4:0),P(c,c.I.os&255),c.I.extra&&c.I.extra.length&&
(P(c,c.I.extra.length&255),P(c,c.I.extra.length>>8&255)),c.I.Xa&&(a.J=Yk(a.J,c.aa,c.pending,0)),c.Ba=0,c.status=69):(P(c,0),P(c,0),P(c,0),P(c,0),P(c,0),P(c,c.level===9?2:c.strategy>=2||c.level<2?4:0),P(c,3),c.status=113);else{var e=8+(c.pd-8<<4)<<8;e|=(c.strategy>=2||c.level<2?0:c.level<6?1:c.level===6?2:3)<<6;c.v!==0&&(e|=32);c.status=113;Ol(c,e+(31-e%31));c.v!==0&&(Ol(c,a.J>>>16),Ol(c,a.J&65535));a.J=1}if(c.status===69)if(c.I.extra){for(e=c.pending;c.Ba<(c.I.extra.length&65535)&&(c.pending!==c.za||
(c.I.Xa&&c.pending>e&&(a.J=Yk(a.J,c.aa,c.pending-e,e)),Ml(a),e=c.pending,c.pending!==c.za));)P(c,c.I.extra[c.Ba]&255),c.Ba++;c.I.Xa&&c.pending>e&&(a.J=Yk(a.J,c.aa,c.pending-e,e));c.Ba===c.I.extra.length&&(c.Ba=0,c.status=73)}else c.status=73;if(c.status===73)if(c.I.name){e=c.pending;do{if(c.pending===c.za&&(c.I.Xa&&c.pending>e&&(a.J=Yk(a.J,c.aa,c.pending-e,e)),Ml(a),e=c.pending,c.pending===c.za)){var f=1;break}f=c.Ba<c.I.name.length?c.I.name.charCodeAt(c.Ba++)&255:0;P(c,f)}while(f!==0);c.I.Xa&&c.pending>
e&&(a.J=Yk(a.J,c.aa,c.pending-e,e));f===0&&(c.Ba=0,c.status=91)}else c.status=91;if(c.status===91)if(c.I.comment){e=c.pending;do{if(c.pending===c.za&&(c.I.Xa&&c.pending>e&&(a.J=Yk(a.J,c.aa,c.pending-e,e)),Ml(a),e=c.pending,c.pending===c.za)){f=1;break}f=c.Ba<c.I.comment.length?c.I.comment.charCodeAt(c.Ba++)&255:0;P(c,f)}while(f!==0);c.I.Xa&&c.pending>e&&(a.J=Yk(a.J,c.aa,c.pending-e,e));f===0&&(c.status=103)}else c.status=103;c.status===103&&(c.I.Xa?(c.pending+2>c.za&&Ml(a),c.pending+2<=c.za&&(P(c,
a.J&255),P(c,a.J>>8&255),a.J=0,c.status=113)):c.status=113);if(c.pending!==0){if(Ml(a),a.S===0)return c.Cb=-1,0}else if(a.na===0&&(b<<1)-(b>4?9:0)<=(d<<1)-(d>4?9:0)&&b!==4)return Kl(a,-5);if(c.status===666&&a.na!==0)return Kl(a,-5);if(a.na!==0||c.D!==0||b!==0&&c.status!==666){d=c.strategy===2?Ul(c,b):c.strategy===3?Tl(c,b):Wl[c.level].ye(c,b);if(d===3||d===4)c.status=666;if(d===1||d===3)return a.S===0&&(c.Cb=-1),0;if(d===2&&(b===1?(ul(c,2,3),vl(c,256,il),c.ia===16?(tl(c,c.oa),c.oa=0,c.ia=0):c.ia>=
8&&(c.aa[c.pending++]=c.oa&255,c.oa>>=8,c.ia-=8)):b!==5&&(ul(c,0,3),Al(c,0,0),b===3&&(Ll(c.head),c.D===0&&(c.v=0,c.va=0,c.sa=0))),Ml(a),a.S===0))return c.Cb=-1,0}if(b!==4)return 0;if(c.wrap<=0)return 1;c.wrap===2?(P(c,a.J&255),P(c,a.J>>8&255),P(c,a.J>>16&255),P(c,a.J>>24&255),P(c,a.qb&255),P(c,a.qb>>8&255),P(c,a.qb>>16&255),P(c,a.qb>>24&255)):(Ol(c,a.J>>>16),Ol(c,a.J&65535));Ml(a);c.wrap>0&&(c.wrap=-c.wrap);return c.pending!==0?0:1}
;var Zl={};Zl=function(){this.input=null;this.qb=this.na=this.nb=0;this.output=null;this.md=this.S=this.Gb=0;this.msg="";this.state=null;this.Mc=2;this.J=0};var $l=Object.prototype.toString;
function am(a){if(!(this instanceof am))return new am(a);a=this.options=O.assign({level:-1,method:8,chunkSize:16384,windowBits:15,memLevel:8,strategy:0,to:""},a||{});a.raw&&a.windowBits>0?a.windowBits=-a.windowBits:a.gzip&&a.windowBits>0&&a.windowBits<16&&(a.windowBits+=16);this.err=0;this.msg="";this.ended=!1;this.chunks=[];this.P=new Zl;this.P.S=0;var b=this.P;var c=a.level,d=a.method,e=a.windowBits,f=a.memLevel,g=a.strategy;if(b){var h=1;c===-1&&(c=6);e<0?(h=0,e=-e):e>15&&(h=2,e-=16);if(f<1||f>
9||d!==8||e<8||e>15||c<0||c>9||g<0||g>4)b=Kl(b,-2);else{e===8&&(e=9);var k=new Xl;b.state=k;k.P=b;k.wrap=h;k.I=null;k.pd=e;k.la=1<<k.pd;k.eb=k.la-1;k.Rc=f+7;k.wc=1<<k.Rc;k.La=k.wc-1;k.Ma=~~((k.Rc+3-1)/3);k.window=new O.rb(k.la*2);k.head=new O.Ja(k.wc);k.Ia=new O.Ja(k.la);k.Vb=1<<f+6;k.za=k.Vb*4;k.aa=new O.rb(k.za);k.Qb=1*k.Vb;k.Tc=3*k.Vb;k.level=c;k.strategy=g;k.method=d;if(b&&b.state){b.qb=b.md=0;b.Mc=2;c=b.state;c.pending=0;c.Yb=0;c.wrap<0&&(c.wrap=-c.wrap);c.status=c.wrap?42:113;b.J=c.wrap===2?
0:1;c.Cb=0;if(!Il){d=Array(16);for(f=g=0;f<28;f++)for(ml[f]=g,e=0;e<1<<el[f];e++)ll[g++]=f;ll[g-1]=f;for(f=g=0;f<16;f++)for(nl[f]=g,e=0;e<1<<fl[f];e++)kl[g++]=f;for(g>>=7;f<30;f++)for(nl[f]=g<<7,e=0;e<1<<fl[f]-7;e++)kl[256+g++]=f;for(e=0;e<=15;e++)d[e]=0;for(e=0;e<=143;)il[e*2+1]=8,e++,d[8]++;for(;e<=255;)il[e*2+1]=9,e++,d[9]++;for(;e<=279;)il[e*2+1]=7,e++,d[7]++;for(;e<=287;)il[e*2+1]=8,e++,d[8]++;xl(il,287,d);for(e=0;e<30;e++)jl[e*2+1]=5,jl[e*2]=wl(e,5);pl=new ol(il,el,257,286,15);ql=new ol(jl,
fl,0,30,15);rl=new ol([],gl,0,19,7);Il=!0}c.xc=new sl(c.ra,pl);c.oc=new sl(c.hb,ql);c.td=new sl(c.ja,rl);c.oa=0;c.ia=0;yl(c);c=0}else c=Kl(b,-2);c===0&&(b=b.state,b.Ud=2*b.la,Ll(b.head),b.Wc=Wl[b.level].Ne,b.yd=Wl[b.level].Be,b.Ed=Wl[b.level].Qe,b.Cd=Wl[b.level].Me,b.v=0,b.va=0,b.D=0,b.sa=0,b.T=b.wa=2,b.lb=0,b.R=0);b=c}}else b=-2;if(b!==0)throw Error(cl[b]);a.header&&(b=this.P)&&b.state&&b.state.wrap===2&&(b.state.I=a.header);if(a.dictionary){var l;typeof a.dictionary==="string"?l=Wk(a.dictionary):
$l.call(a.dictionary)==="[object ArrayBuffer]"?l=new Uint8Array(a.dictionary):l=a.dictionary;a=this.P;f=l;g=f.length;if(a&&a.state)if(l=a.state,b=l.wrap,b===2||b===1&&l.status!==42||l.D)b=-2;else{b===1&&(a.J=Xk(a.J,f,g,0));l.wrap=0;g>=l.la&&(b===0&&(Ll(l.head),l.v=0,l.va=0,l.sa=0),c=new O.rb(l.la),O.ub(c,f,g-l.la,l.la,0),f=c,g=l.la);c=a.na;d=a.nb;e=a.input;a.na=g;a.nb=0;a.input=f;for(Ql(l);l.D>=3;){f=l.v;g=l.D-2;do l.R=(l.R<<l.Ma^l.window[f+3-1])&l.La,l.Ia[f&l.eb]=l.head[l.R],l.head[l.R]=f,f++;while(--g);
l.v=f;l.D=2;Ql(l)}l.v+=l.D;l.va=l.v;l.sa=l.D;l.D=0;l.T=l.wa=2;l.lb=0;a.nb=d;a.input=e;a.na=c;l.wrap=b;b=0}else b=-2;if(b!==0)throw Error(cl[b]);this.zh=!0}}
am.prototype.push=function(a,b){var c=this.P,d=this.options.chunkSize;if(this.ended)return!1;var e=b===~~b?b:b===!0?4:0;typeof a==="string"?c.input=Wk(a):$l.call(a)==="[object ArrayBuffer]"?c.input=new Uint8Array(a):c.input=a;c.nb=0;c.na=c.input.length;do{c.S===0&&(c.output=new O.rb(d),c.Gb=0,c.S=d);a=Yl(c,e);if(a!==1&&a!==0)return bm(this,a),this.ended=!0,!1;if(c.S===0||c.na===0&&(e===4||e===2))if(this.options.to==="string"){var f=O.jd(c.output,c.Gb);b=f;f=f.length;if(f<65537&&(b.subarray&&Vk||!b.subarray))b=
String.fromCharCode.apply(null,O.jd(b,f));else{for(var g="",h=0;h<f;h++)g+=String.fromCharCode(b[h]);b=g}this.chunks.push(b)}else b=O.jd(c.output,c.Gb),this.chunks.push(b)}while((c.na>0||c.S===0)&&a!==1);if(e===4)return(c=this.P)&&c.state?(d=c.state.status,d!==42&&d!==69&&d!==73&&d!==91&&d!==103&&d!==113&&d!==666?a=Kl(c,-2):(c.state=null,a=d===113?Kl(c,-3):0)):a=-2,bm(this,a),this.ended=!0,a===0;e===2&&(bm(this,0),c.S=0);return!0};
function bm(a,b){b===0&&(a.result=a.options.to==="string"?a.chunks.join(""):O.wd(a.chunks));a.chunks=[];a.err=b;a.msg=a.P.msg}
function cm(a,b){b=b||{};b.gzip=!0;b=new am(b);b.push(a,!0);if(b.err)throw b.msg||cl[b.err];return b.result}
;function dm(a){return a?(a=a.privateDoNotAccessOrElseSafeScriptWrappedValue)?Fb(a):null:null}
function em(a){return a?(a=a.privateDoNotAccessOrElseTrustedResourceUrlWrappedValue)?lb(a):null:null}
;function fm(a){return lb(a===null?"null":a===void 0?"undefined":a)}
;function gm(a){this.name=a}
;var hm=new gm("rawColdConfigGroup");var im=new gm("rawHotConfigGroup");function jm(a){this.F=L(a)}
v(jm,M);function km(a){this.F=L(a)}
v(km,M);km.prototype.setTrackingParams=function(a){if(a!=null)if(typeof a==="string")a=a?new Ad(a,zd):Cd||(Cd=new Ad(null,zd));else if(a.constructor!==Ad)if(ud&&a!=null&&a instanceof Uint8Array)a instanceof Uint8Array||Array.isArray(a),a=a.length?new Ad(new Uint8Array(a),zd):Cd||(Cd=new Ad(null,zd));else throw Error();return vf(this,1,a)};var lm=new gm("continuationCommand");var mm=new gm("webCommandMetadata");var nm=new gm("signalServiceEndpoint");var om={Wf:"EMBEDDED_PLAYER_MODE_UNKNOWN",Tf:"EMBEDDED_PLAYER_MODE_DEFAULT",Vf:"EMBEDDED_PLAYER_MODE_PFP",Uf:"EMBEDDED_PLAYER_MODE_PFL"};var pm=new gm("feedbackEndpoint");var he={bh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_UNKNOWN",tg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_FOR_TESTING",Lg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_RESUME_TO_HOME_TTL",Tg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_START_TO_SHORTS_ANALYSIS_SLICE",ig:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_DEVICE_LAYER_SLICE",ah:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_UNIFIED_LAYER_SLICE",eh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_VISITOR_LAYER_SLICE",Sg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_SHOW_SHEET_COMMAND_HANDLER_BLOCK",
gh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WIZ_NEXT_MIGRATED_COMPONENT",fh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WIZ_NEXT_CHANNEL_NAME_TOOLTIP",Og:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ROTATION_LOCK_SUPPORTED",Vg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_THEATER_MODE_ENABLED",kh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_SHOW_PIN_SUGGESTION",jh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_SHOW_LONG_PRESS_EDU_TOAST",ih:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_SHOW_AMBIENT",Wg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_TIME_WATCHED_PANEL",
Qg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_SEARCH_FROM_SEARCH_BAR_OVERLAY",mh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_SHOW_VOICE_SEARCH_EDU_TOAST",Ug:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_SUGGESTED_LANGUAGE_SELECTED",nh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_TRIGGER_SHORTS_PIP",Ag:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IN_ZP_VOICE_CRASHY_SET",Hg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_REEL_FAST_SWIPE_SUPPRESSED",Gg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_REEL_FAST_SWIPE_ALLOWED",Jg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_REEL_PULL_TO_REFRESH_ATTEMPT",
hh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_WOULD_BLOCK_KABUKI",Kg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_REEL_TALL_SCREEN",Ig:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_REEL_NORMAL_SCREEN",ag:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ACCESSIBILITY_MODE_ENABLED",Zf:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ACCESSIBILITY_MODE_DISABLED",cg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_AUTOPLAY_ENABLED",dg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_CAST_MATCH_OCCURRED",mg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EMC3DS_ELIGIBLE",pg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ENDSCREEN_TRIGGERED",
Fg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_POSTPLAY_TRIGGERED",Eg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_POSTPLAY_LACT_THRESHOLD_EXCEEDED",ug:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_STATE_MATCHED_ON_REMOTE_CONNECTION",wg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_STATE_SWITCHABLE_ON_REMOTE_CONNECTION",vg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_STATE_MISATTRIBUTED_ON_REMOTE_CONNECTION",zg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_TV_IS_SIGNED_IN_ON_REMOTE_CONNECTION",Yg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_TV_START_TYPE_COLD_ON_REMOTE_CONNECTION",
Zg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_TV_START_TYPE_NON_COLD_ON_REMOTE_CONNECTION",Cg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ON_REMOTE_CONNECTION",hg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_COBALT_PERSISTENT_SETTINGS_TEST_VALID",fg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_COBALT_PERSISTENT_SETTINGS_TEST_INVALID",gg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_COBALT_PERSISTENT_SETTINGS_TEST_UNDEFINED",eg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_COBALT_PERSISTENT_SETTINGS_TEST_DEFINED",Bg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_LACT_THRESHOLD_EXCEEDED",
Pg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ROUND_TRIP_HANDLING_ON_REMOTE_CONNECTION",yg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_STATE_SWITCHED_ON_REMOTE_CONNECTION_BEFORE_APP_RELOAD",xg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_IDENTITIES_STATE_SWITCHED_ON_REMOTE_CONNECTION_AFTER_APP_RELOAD",ng:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EMC3DS_INELIGIBLE",Xg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_TVHTML5_MID_ROLL_THRESHOLD_REACHED",rg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EXP_COBALT_HTTP3_CONFIG_PENDING",
qg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EXP_COBALT_HTTP3_CONFIG_ACTIVATED",og:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EMC3DS_M2_ELIGIBLE",Mg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ROTATE_DEVICE_TO_LANDSCAPE",Ng:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ROTATE_DEVICE_TO_PORTRAIT",lg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EMBEDS_FACEOFF_UI_EVENT",sg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_EXP_COBALT_HTTP3_CONFIG_RECEIVED",kg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_ELIGIBLE_TO_SUPPRESS_TRANSPORT_CONTROLS_BUTTONS",
dh:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_USER_HAS_THEATER_MODE_COOKIE_ENABLED",jg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_DOCUMENT_PICTURE_IN_PICTURE_SUPPORTED",Rg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_SHORTS_NON_DEFAULT_ASPECT_RATIO",Dg:"GENERIC_CLIENT_EXPERIMENT_EVENT_TYPE_PLAYER_IN_SQUEEZEBACK"};var qm=new gm("shareEndpoint"),rm=new gm("shareEntityEndpoint"),sm=new gm("shareEntityServiceEndpoint"),tm=new gm("webPlayerShareEntityServiceEndpoint");var um=new gm("playlistEditEndpoint");var wm=new gm("modifyChannelNotificationPreferenceEndpoint");var xm=new gm("undoFeedbackEndpoint");var ym=new gm("unsubscribeEndpoint");var zm=new gm("subscribeEndpoint");function Am(){var a=Bm;F("yt.ads.biscotti.getId_")||E("yt.ads.biscotti.getId_",a)}
function Cm(a){E("yt.ads.biscotti.lastId_",a)}
;function Dm(a,b){b.length>1?a[b[0]]=b[1]:b.length===1&&Object.assign(a,b[0])}
;var Em=D.window,Fm,Gm,Hm=(Em==null?void 0:(Fm=Em.yt)==null?void 0:Fm.config_)||(Em==null?void 0:(Gm=Em.ytcfg)==null?void 0:Gm.data_)||{};E("yt.config_",Hm);function Im(){Dm(Hm,arguments)}
function R(a,b){return a in Hm?Hm[a]:b}
function Jm(a){var b=Hm.EXPERIMENT_FLAGS;return b?b[a]:void 0}
;var Km=[];function Lm(a){Km.forEach(function(b){return b(a)})}
function Mm(a){return a&&window.yterr?function(){try{return a.apply(this,arguments)}catch(b){Nm(b)}}:a}
function Nm(a){var b=F("yt.logging.errors.log");b?b(a,"ERROR",void 0,void 0,void 0,void 0,void 0):(b=R("ERRORS",[]),b.push([a,"ERROR",void 0,void 0,void 0,void 0,void 0]),Im("ERRORS",b));Lm(a)}
function Om(a,b,c,d,e){var f=F("yt.logging.errors.log");f?f(a,"WARNING",b,c,d,void 0,e):(f=R("ERRORS",[]),f.push([a,"WARNING",b,c,d,void 0,e]),Im("ERRORS",f))}
;var Pm=/^[\w.]*$/,Qm={q:!0,search_query:!0};function Rm(a,b){b=a.split(b);for(var c={},d=0,e=b.length;d<e;d++){var f=b[d].split("=");if(f.length===1&&f[0]||f.length===2)try{var g=Sm(f[0]||""),h=Sm(f[1]||"");if(g in c){var k=c[g];Array.isArray(k)?Xb(k,h):c[g]=[k,h]}else c[g]=h}catch(r){var l=r,m=f[0],n=String(Rm);l.args=[{key:m,value:f[1],query:a,method:Tm===n?"unchanged":n}];Qm.hasOwnProperty(m)||Om(l)}}return c}
var Tm=String(Rm);function Um(a){var b=[];sg(a,function(c,d){var e=encodeURIComponent(String(d));c=Array.isArray(c)?c:[c];Pb(c,function(f){f==""?b.push(e):b.push(e+"="+encodeURIComponent(String(f)))})});
return b.join("&")}
function Vm(a){a.charAt(0)==="?"&&(a=a.substring(1));return Rm(a,"&")}
function Wm(a){return a.indexOf("?")!==-1?(a=(a||"").split("#")[0],a=a.split("?",2),Vm(a.length>1?a[1]:a[0])):{}}
function Xm(a,b){return Ym(a,b||{},!0)}
function Ym(a,b,c){var d=a.split("#",2);a=d[0];d=d.length>1?"#"+d[1]:"";var e=a.split("?",2);a=e[0];e=Vm(e[1]||"");for(var f in b)!c&&e!==null&&f in e||(e[f]=b[f]);return pc(a,e)+d}
function Zm(a){if(!b)var b=window.location.href;var c=a.match(fc)[1]||null,d=ic(a);c&&d?(a=a.match(fc),b=b.match(fc),a=a[3]==b[3]&&a[1]==b[1]&&a[4]==b[4]):a=d?ic(b)===d&&(Number(b.match(fc)[4]||null)||null)===(Number(a.match(fc)[4]||null)||null):!0;return a}
function Sm(a){return a&&a.match(Pm)?a:dc(a)}
;function $m(a){var b=an;a=a===void 0?F("yt.ads.biscotti.lastId_")||"":a;var c=Object,d=c.assign,e={};e.dt=Rj;e.flash="0";a:{try{var f=b.h.top.location.href}catch(Oa){f=2;break a}f=f?f===b.i.location.href?0:1:2}e=(e.frm=f,e);try{e.u_tz=-(new Date).getTimezoneOffset();try{var g=Jj.history.length}catch(Oa){g=0}e.u_his=g;var h;e.u_h=(h=Jj.screen)==null?void 0:h.height;var k;e.u_w=(k=Jj.screen)==null?void 0:k.width;var l;e.u_ah=(l=Jj.screen)==null?void 0:l.availHeight;var m;e.u_aw=(m=Jj.screen)==null?
void 0:m.availWidth;var n;e.u_cd=(n=Jj.screen)==null?void 0:n.colorDepth}catch(Oa){}var r;g=b.h;try{var t=g.screenX;var w=g.screenY}catch(Oa){}try{var x=g.outerWidth;var z=g.outerHeight}catch(Oa){}try{var G=g.innerWidth;var H=g.innerHeight}catch(Oa){}try{var U=g.screenLeft;var Z=g.screenTop}catch(Oa){}try{G=g.innerWidth,H=g.innerHeight}catch(Oa){}try{var mb=g.screen.availWidth;var Qb=g.screen.availTop}catch(Oa){}t=[U,Z,t,w,mb,Qb,x,z,G,H];try{var ca=(b.h.top||window).document,$a=ca.compatMode=="CSS1Compat"?
ca.documentElement:ca.body;var Pa=(new rg($a.clientWidth,$a.clientHeight)).round()}catch(Oa){Pa=new rg(-12245933,-12245933)}ca=Pa;Pa={};var Qa=Qa===void 0?D:Qa;$a=new Xj;"SVGElement"in Qa&&"createElementNS"in Qa.document&&$a.set(0);w=Oj();w["allow-top-navigation-by-user-activation"]&&$a.set(1);w["allow-popups-to-escape-sandbox"]&&$a.set(2);Qa.crypto&&Qa.crypto.subtle&&$a.set(3);"TextDecoder"in Qa&&"TextEncoder"in Qa&&$a.set(4);Qa=Yj($a);Pa.bc=Qa;Pa.bih=ca.height;Pa.biw=ca.width;Pa.brdim=t.join();
b=b.i;b=b.prerendering?3:(r={visible:1,hidden:2,prerender:3,preview:4,unloaded:5,"":0}[b.visibilityState||b.webkitVisibilityState||b.mozVisibilityState||""])!=null?r:0;r=(Pa.vis=b,Pa.wgl=!!Jj.WebGLRenderingContext,Pa);c=d.call(c,e,r);c.ca_type="image";a&&(c.bid=a);return c}
var an=new function(){var a=window.document;this.h=window;this.i=a};
E("yt.ads_.signals_.getAdSignalsString",function(a){return Um($m(a))});Xa();navigator.userAgent.indexOf(" (CrKey ");var bn="XMLHttpRequest"in D?function(){return new XMLHttpRequest}:null;
function cn(){if(!bn)return null;var a=bn();return"open"in a?a:null}
function dn(a){switch(a&&"status"in a?a.status:-1){case 200:case 201:case 202:case 203:case 204:case 205:case 206:case 304:return!0;default:return!1}}
;function en(a,b){typeof a==="function"&&(a=Mm(a));return window.setTimeout(a,b)}
;var fn="client_dev_domain client_dev_expflag client_dev_regex_map client_dev_root_url client_rollout_override expflag forcedCapability jsfeat jsmode mods".split(" ");[].concat(A(fn),["client_dev_set_cookie"]);function S(a){a=gn(a);return typeof a==="string"&&a==="false"?!1:!!a}
function hn(a,b){a=gn(a);return a===void 0&&b!==void 0?b:Number(a||0)}
function gn(a){return R("EXPERIMENT_FLAGS",{})[a]}
function jn(){for(var a=[],b=R("EXPERIMENTS_FORCED_FLAGS",{}),c=y(Object.keys(b)),d=c.next();!d.done;d=c.next())d=d.value,a.push({key:d,value:String(b[d])});c=R("EXPERIMENT_FLAGS",{});d=y(Object.keys(c));for(var e=d.next();!e.done;e=d.next())e=e.value,e.startsWith("force_")&&b[e]===void 0&&a.push({key:e,value:String(c[e])});return a}
;var kn={Authorization:"AUTHORIZATION","X-Goog-EOM-Visitor-Id":"EOM_VISITOR_DATA","X-Goog-Visitor-Id":"SANDBOXED_VISITOR_ID","X-Youtube-Domain-Admin-State":"DOMAIN_ADMIN_STATE","X-Youtube-Chrome-Connected":"CHROME_CONNECTED_HEADER","X-YouTube-Client-Name":"INNERTUBE_CONTEXT_CLIENT_NAME","X-YouTube-Client-Version":"INNERTUBE_CONTEXT_CLIENT_VERSION","X-YouTube-Delegation-Context":"INNERTUBE_CONTEXT_SERIALIZED_DELEGATION_CONTEXT","X-YouTube-Device":"DEVICE","X-Youtube-Identity-Token":"ID_TOKEN","X-YouTube-Page-CL":"PAGE_CL",
"X-YouTube-Page-Label":"PAGE_BUILD_LABEL","X-Goog-AuthUser":"SESSION_INDEX","X-Goog-PageId":"DELEGATED_SESSION_ID"},ln="app debugcss debugjs expflag force_ad_params force_ad_encrypted force_viral_ad_response_params forced_experiments innertube_snapshots innertube_goldens internalcountrycode internalipoverride absolute_experiments conditional_experiments sbb sr_bns_address".split(" ").concat(A(fn)),mn=!1;function nn(a,b,c,d,e,f,g,h,k){function l(){(m&&"readyState"in m?m.readyState:0)===4&&b&&Mm(b)(m)}
c=c===void 0?"GET":c;d=d===void 0?"":d;h=h===void 0?!1:h;var m=cn();if(!m)return null;"onloadend"in m?m.addEventListener("loadend",l,!1):m.onreadystatechange=l;S("debug_forward_web_query_parameters")&&(a=on(a));m.open(c,a,!0);f&&(m.responseType=f);g&&(m.withCredentials=!0);c=c==="POST"&&(window.FormData===void 0||!(d instanceof FormData));if(e=pn(a,e))for(var n in e)m.setRequestHeader(n,e[n]),"content-type"===n.toLowerCase()&&(c=!1);c&&m.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
k&&"onprogress"in m&&(m.onprogress=function(){k(m.responseText)});
if(h&&"setAttributionReporting"in XMLHttpRequest.prototype){a={eventSourceEligible:!0,triggerEligible:!1};try{m.setAttributionReporting(a)}catch(r){Om(r)}}m.send(d);return m}
function pn(a,b){b=b===void 0?{}:b;var c=Zm(a),d=R("INNERTUBE_CLIENT_NAME"),e=S("web_ajax_ignore_global_headers_if_set"),f;for(f in kn){var g=R(kn[f]),h=f==="X-Goog-AuthUser"||f==="X-Goog-PageId";f!=="X-Goog-Visitor-Id"||g||(g=R("VISITOR_DATA"));var k;if(!(k=!g)){if(!(k=c||(ic(a)?!1:!0))){k=a;var l;if(l=S("add_auth_headers_to_remarketing_google_dot_com_ping")&&f==="Authorization"&&(d==="TVHTML5"||d==="TVHTML5_UNPLUGGED"||d==="TVHTML5_SIMPLY"))l=ic(k),l=l!==null?l.split(".").reverse():null,l=l===null?
!1:l[1]==="google"?!0:l[2]==="google"?l[0]==="au"&&l[1]==="com"?!0:l[0]==="uk"&&l[1]==="co"?!0:!1:!1;l&&(k=jc(k)||"",k=k.split("/"),k="/"+(k.length>1?k[1]:""),l=k==="/pagead");k=l?!0:!1}k=!k}k||e&&b[f]!==void 0||d==="TVHTML5_UNPLUGGED"&&h||(b[f]=g)}"X-Goog-EOM-Visitor-Id"in b&&"X-Goog-Visitor-Id"in b&&delete b["X-Goog-Visitor-Id"];if(c||!ic(a))b["X-YouTube-Utc-Offset"]=String(-(new Date).getTimezoneOffset());if(c||!ic(a)){try{var m=(new Intl.DateTimeFormat).resolvedOptions().timeZone}catch(n){}m&&
(b["X-YouTube-Time-Zone"]=m)}document.location.hostname.endsWith("youtubeeducation.com")||!c&&ic(a)||(b["X-YouTube-Ad-Signals"]=Um($m()));return b}
function qn(a,b){b.method="POST";b.postParams||(b.postParams={});return rn(a,b)}
function rn(a,b){var c=b.format||"JSON";a=sn(a,b);var d=tn(a,b),e=!1,f=un(a,function(k){if(!e){e=!0;h&&window.clearTimeout(h);var l=dn(k),m=null,n=400<=k.status&&k.status<500,r=500<=k.status&&k.status<600;if(l||n||r)m=vn(a,c,k,b.convertToSafeHtml);l&&(l=wn(c,k,m));m=m||{};n=b.context||D;l?b.onSuccess&&b.onSuccess.call(n,k,m):b.onError&&b.onError.call(n,k,m);b.onFinish&&b.onFinish.call(n,k,m)}},b.method,d,b.headers,b.responseType,b.withCredentials,!1,b.onProgress);
d=b.timeout||0;if(b.onTimeout&&d>0){var g=b.onTimeout;var h=en(function(){e||(e=!0,f.abort(),window.clearTimeout(h),g.call(b.context||D,f))},d)}return f}
function sn(a,b){b.includeDomain&&(a=document.location.protocol+"//"+document.location.hostname+(document.location.port?":"+document.location.port:"")+a);var c=R("XSRF_FIELD_NAME");if(b=b.urlParams)b[c]&&delete b[c],a=Xm(a,b);return a}
function tn(a,b){var c=R("XSRF_FIELD_NAME"),d=R("XSRF_TOKEN"),e=b.postBody||"",f=b.postParams,g=R("XSRF_FIELD_NAME"),h;b.headers&&(h=b.headers["Content-Type"]);b.excludeXsrf||ic(a)&&!b.withCredentials&&ic(a)!==document.location.hostname||b.method!=="POST"||h&&h!=="application/x-www-form-urlencoded"||b.postParams&&b.postParams[g]||(f||(f={}),f[c]=d);(S("ajax_parse_query_data_only_when_filled")&&f&&Object.keys(f).length>0||f)&&typeof e==="string"&&(e=Vm(e),Dg(e,f),e=b.postBodyFormat&&b.postBodyFormat===
"JSON"?JSON.stringify(e):oc(e));f=e||f&&!wg(f);!mn&&f&&b.method!=="POST"&&(mn=!0,Nm(Error("AJAX request with postData should use POST")));return e}
function vn(a,b,c,d){var e=null;switch(b){case "JSON":try{var f=c.responseText}catch(g){throw d=Error("Error reading responseText"),d.params=a,Om(d),g;}a=c.getResponseHeader("Content-Type")||"";f&&a.indexOf("json")>=0&&(f.substring(0,5)===")]}'\n"&&(f=f.substring(5)),e=JSON.parse(f));break;case "XML":if(a=(a=c.responseXML)?xn(a):null)e={},Pb(a.getElementsByTagName("*"),function(g){e[g.tagName]=yn(g)})}d&&zn(e);
return e}
function zn(a){if(Ma(a))for(var b in a){var c;(c=b==="html_content")||(c=b.length-5,c=c>=0&&b.indexOf("_html",c)==c);if(c){c=a[b];var d=jb();c=d?d.createHTML(c):c;a[b]=new Cb(c)}else zn(a[b])}}
function wn(a,b,c){if(b&&b.status===204)return!0;switch(a){case "JSON":return!!c;case "XML":return Number(c&&c.return_code)===0;case "RAW":return!0;default:return!!c}}
function xn(a){return a?(a=("responseXML"in a?a.responseXML:a).getElementsByTagName("root"))&&a.length>0?a[0]:null:null}
function yn(a){var b="";Pb(a.childNodes,function(c){b+=c.nodeValue});
return b}
function on(a){var b=window.location.search,c=ic(a);S("debug_handle_relative_url_for_query_forward_killswitch")||!c&&Zm(a)&&(c=document.location.hostname);var d=jc(a);d=(c=c&&(c.endsWith("youtube.com")||c.endsWith("youtube-nocookie.com")))&&d&&d.startsWith("/api/");if(!c||d)return a;var e=Vm(b),f={};Pb(ln,function(g){e[g]&&(f[g]=e[g])});
return Ym(a,f||{},!1)}
var un=nn;var An=[{Xc:function(a){return"Cannot read property '"+a.key+"'"},
zc:{Error:[{regexp:/(Permission denied) to access property "([^']+)"/,groups:["reason","key"]}],TypeError:[{regexp:/Cannot read property '([^']+)' of (null|undefined)/,groups:["key","value"]},{regexp:/\u65e0\u6cd5\u83b7\u53d6\u672a\u5b9a\u4e49\u6216 (null|undefined) \u5f15\u7528\u7684\u5c5e\u6027\u201c([^\u201d]+)\u201d/,groups:["value","key"]},{regexp:/\uc815\uc758\ub418\uc9c0 \uc54a\uc74c \ub610\ub294 (null|undefined) \ucc38\uc870\uc778 '([^']+)' \uc18d\uc131\uc744 \uac00\uc838\uc62c \uc218 \uc5c6\uc2b5\ub2c8\ub2e4./,
groups:["value","key"]},{regexp:/No se puede obtener la propiedad '([^']+)' de referencia nula o sin definir/,groups:["key"]},{regexp:/Unable to get property '([^']+)' of (undefined or null) reference/,groups:["key","value"]},{regexp:/(null) is not an object \(evaluating '(?:([^.]+)\.)?([^']+)'\)/,groups:["value","base","key"]}]}},{Xc:function(a){return"Cannot call '"+a.key+"'"},
zc:{TypeError:[{regexp:/(?:([^ ]+)?\.)?([^ ]+) is not a function/,groups:["base","key"]},{regexp:/([^ ]+) called on (null or undefined)/,groups:["key","value"]},{regexp:/Object (.*) has no method '([^ ]+)'/,groups:["base","key"]},{regexp:/Object doesn't support property or method '([^ ]+)'/,groups:["key"]},{regexp:/\u30aa\u30d6\u30b8\u30a7\u30af\u30c8\u306f '([^']+)' \u30d7\u30ed\u30d1\u30c6\u30a3\u307e\u305f\u306f\u30e1\u30bd\u30c3\u30c9\u3092\u30b5\u30dd\u30fc\u30c8\u3057\u3066\u3044\u307e\u305b\u3093/,
groups:["key"]},{regexp:/\uac1c\uccb4\uac00 '([^']+)' \uc18d\uc131\uc774\ub098 \uba54\uc11c\ub4dc\ub97c \uc9c0\uc6d0\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4./,groups:["key"]}]}},{Xc:function(a){return a.key+" is not defined"},
zc:{ReferenceError:[{regexp:/(.*) is not defined/,groups:["key"]},{regexp:/Can't find variable: (.*)/,groups:["key"]}]}}];var Dn={Za:[],Ua:[{callback:Bn,weight:500},{callback:Cn,weight:500}]};function Bn(a){if(a.name==="JavaException")return!0;a=a.stack;return a.includes("chrome://")||a.includes("-extension://")||a.includes("webkit-masked-url://")}
function Cn(a){if(!a.stack)return!0;var b=!a.stack.includes("\n");return b&&a.stack.includes("ErrorType: ")||b&&a.stack.includes("Anonymous function (Unknown script")||a.stack.toLowerCase()==="not available"||a.fileName==="user-script"||a.fileName.startsWith("user-script:")?!0:!1}
;function En(){this.Ua=[];this.Za=[]}
var Fn;function Gn(){if(!Fn){var a=Fn=new En;a.Za.length=0;a.Ua.length=0;Hn(a,Dn)}return Fn}
function Hn(a,b){b.Za&&a.Za.push.apply(a.Za,b.Za);b.Ua&&a.Ua.push.apply(a.Ua,b.Ua)}
;var In=new N;function Jn(a){function b(){return a.charCodeAt(d++)}
var c=a.length,d=0;do{var e=Kn(b);if(e===Infinity)break;var f=e>>3;switch(e&7){case 0:e=Kn(b);if(f===2)return e;break;case 1:if(f===2)return;d+=8;break;case 2:e=Kn(b);if(f===2)return a.substr(d,e);d+=e;break;case 5:if(f===2)return;d+=4;break;default:return}}while(d<c)}
function Kn(a){var b=a(),c=b&127;if(b<128)return c;b=a();c|=(b&127)<<7;if(b<128)return c;b=a();c|=(b&127)<<14;if(b<128)return c;b=a();return b<128?c|(b&127)<<21:Infinity}
;function Ln(a,b,c,d){if(a)if(Array.isArray(a)){var e=d;for(d=0;d<a.length&&!(a[d]&&(e+=Mn(d,a[d],b,c),e>500));d++);d=e}else if(typeof a==="object")for(e in a){if(a[e]){var f=e;var g=a[e],h=b,k=c;f=typeof g!=="string"||f!=="clickTrackingParams"&&f!=="trackingParams"?0:(g=Jn(atob(g.replace(/-/g,"+").replace(/_/g,"/"))))?Mn(f+".ve",g,h,k):0;d+=f;d+=Mn(e,a[e],b,c);if(d>500)break}}else c[b]=Nn(a),d+=c[b].length;else c[b]=Nn(a),d+=c[b].length;return d}
function Mn(a,b,c,d){c+="."+a;a=Nn(b);d[c]=a;return c.length+a.length}
function Nn(a){try{return(typeof a==="string"?a:String(JSON.stringify(a))).substr(0,500)}catch(b){return"unable to serialize "+typeof a+" ("+b.message+")"}}
;function On(a){var b=this;this.i=void 0;this.h=!1;a.addEventListener("beforeinstallprompt",function(c){c.preventDefault();b.i=c});
a.addEventListener("appinstalled",function(){b.h=!0},{once:!0})}
function Pn(){if(!D.matchMedia)return"WEB_DISPLAY_MODE_UNKNOWN";try{return D.matchMedia("(display-mode: standalone)").matches?"WEB_DISPLAY_MODE_STANDALONE":D.matchMedia("(display-mode: minimal-ui)").matches?"WEB_DISPLAY_MODE_MINIMAL_UI":D.matchMedia("(display-mode: fullscreen)").matches?"WEB_DISPLAY_MODE_FULLSCREEN":D.matchMedia("(display-mode: browser)").matches?"WEB_DISPLAY_MODE_BROWSER":"WEB_DISPLAY_MODE_UNKNOWN"}catch(a){return"WEB_DISPLAY_MODE_UNKNOWN"}}
;function Qn(){this.Qd=!0}
function Rn(){Qn.instance||(Qn.instance=new Qn);return Qn.instance}
function Sn(a,b){a={};var c=[];"USER_SESSION_ID"in Hm&&c.push({key:"u",value:R("USER_SESSION_ID")});if(c=kg(c))a.Authorization=c,c=b=b==null?void 0:b.sessionIndex,c===void 0&&(c=Number(R("SESSION_INDEX",0)),c=isNaN(c)?0:c),S("voice_search_auth_header_removal")||(a["X-Goog-AuthUser"]=c.toString()),"INNERTUBE_HOST_OVERRIDE"in Hm||(a["X-Origin"]=window.location.origin),b===void 0&&"DELEGATED_SESSION_ID"in Hm&&(a["X-Goog-PageId"]=R("DELEGATED_SESSION_ID"));return a}
;var Tn={identityType:"UNAUTHENTICATED_IDENTITY_TYPE_UNKNOWN"};function Un(a,b,c,d,e){hg.set(""+a,b,{Xb:c,path:"/",domain:d===void 0?"youtube.com":d,secure:e===void 0?!1:e})}
function Vn(a){return hg.get(""+a,void 0)}
function Wn(a,b,c){hg.remove(""+a,b===void 0?"/":b,c===void 0?"youtube.com":c)}
function Xn(){if(S("embeds_web_enable_cookie_detection_fix")){if(!D.navigator.cookieEnabled)return!1}else if(!hg.isEnabled())return!1;if(hg.h.cookie)return!0;S("embeds_web_enable_cookie_detection_fix")?hg.set("TESTCOOKIESENABLED","1",{Xb:60,ff:"none",secure:!0}):hg.set("TESTCOOKIESENABLED","1",{Xb:60});if(hg.get("TESTCOOKIESENABLED")!=="1")return!1;hg.remove("TESTCOOKIESENABLED");return!0}
;var Yn=F("ytglobal.prefsUserPrefsPrefs_")||{};E("ytglobal.prefsUserPrefsPrefs_",Yn);function Zn(){this.h=R("ALT_PREF_COOKIE_NAME","PREF");this.i=R("ALT_PREF_COOKIE_DOMAIN","youtube.com");var a=Vn(this.h);a&&this.parse(a)}
var $n;function ao(){$n||($n=new Zn);return $n}
p=Zn.prototype;p.get=function(a,b){bo(a);co(a);a=Yn[a]!==void 0?Yn[a].toString():null;return a!=null?a:b?b:""};
p.set=function(a,b){bo(a);co(a);if(b==null)throw Error("ExpectedNotNull");Yn[a]=b.toString()};
function eo(a){return!!((fo("f"+(Math.floor(a/31)+1))||0)&1<<a%31)}
p.remove=function(a){bo(a);co(a);delete Yn[a]};
p.clear=function(){for(var a in Yn)delete Yn[a]};
function co(a){if(/^f([1-9][0-9]*)$/.test(a))throw Error("ExpectedRegexMatch: "+a);}
function bo(a){if(!/^\w+$/.test(a))throw Error("ExpectedRegexMismatch: "+a);}
function fo(a){a=Yn[a]!==void 0?Yn[a].toString():null;return a!=null&&/^[A-Fa-f0-9]+$/.test(a)?parseInt(a,16):null}
p.parse=function(a){a=decodeURIComponent(a).split("&");for(var b=0;b<a.length;b++){var c=a[b].split("="),d=c[0];(c=c[1])&&(Yn[d]=c.toString())}};var go={bluetooth:"CONN_DISCO",cellular:"CONN_CELLULAR_UNKNOWN",ethernet:"CONN_WIFI",none:"CONN_NONE",wifi:"CONN_WIFI",wimax:"CONN_CELLULAR_4G",other:"CONN_UNKNOWN",unknown:"CONN_UNKNOWN","slow-2g":"CONN_CELLULAR_2G","2g":"CONN_CELLULAR_2G","3g":"CONN_CELLULAR_3G","4g":"CONN_CELLULAR_4G"},ho={"slow-2g":"EFFECTIVE_CONNECTION_TYPE_SLOW_2G","2g":"EFFECTIVE_CONNECTION_TYPE_2G","3g":"EFFECTIVE_CONNECTION_TYPE_3G","4g":"EFFECTIVE_CONNECTION_TYPE_4G"};
function io(){var a=D.navigator;return a?a.connection:void 0}
function jo(){var a=io();if(a){var b=go[a.type||"unknown"]||"CONN_UNKNOWN";a=go[a.effectiveType||"unknown"]||"CONN_UNKNOWN";b==="CONN_CELLULAR_UNKNOWN"&&a!=="CONN_UNKNOWN"&&(b=a);if(b!=="CONN_UNKNOWN")return b;if(a!=="CONN_UNKNOWN")return a}}
function ko(){var a=io();if(a!=null&&a.effectiveType)return ho.hasOwnProperty(a.effectiveType)?ho[a.effectiveType]:"EFFECTIVE_CONNECTION_TYPE_UNKNOWN"}
;function T(a){var b=C.apply(1,arguments);var c=Error.call(this,a);this.message=c.message;"stack"in c&&(this.stack=c.stack);this.args=[].concat(A(b));Object.setPrototypeOf(this,this.constructor.prototype)}
v(T,Error);function lo(){try{return mo(),!0}catch(a){return!1}}
function mo(a){if(R("DATASYNC_ID")!==void 0)return R("DATASYNC_ID");throw new T("Datasync ID not set",a===void 0?"unknown":a);}
;function no(){}
function oo(a,b){return Wj.Sa(a,0,b)}
no.prototype.pa=function(a,b){return this.Sa(a,1,b)};
no.prototype.Lb=function(a){var b=F("yt.scheduler.instance.addImmediateJob");b?b(a):a()};var po=hn("web_emulated_idle_callback_delay",300),qo=1E3/60-3,ro=[8,5,4,3,2,1,0];
function so(a){a=a===void 0?{}:a;I.call(this);this.i=[];this.j={};this.Z=this.h=0;this.Y=this.u=!1;this.M=[];this.U=this.ha=!1;for(var b=y(ro),c=b.next();!c.done;c=b.next())this.i[c.value]=[];this.o=0;this.Jc=a.timeout||1;this.G=qo;this.A=0;this.xa=this.Se.bind(this);this.Kb=this.zf.bind(this);this.Qa=this.be.bind(this);this.Ra=this.Ce.bind(this);this.fb=this.Ze.bind(this);this.Fa=!!window.requestIdleCallback&&!!window.cancelIdleCallback&&!S("disable_scheduler_requestIdleCallback");(this.ma=a.useRaf!==
!1&&!!window.requestAnimationFrame)&&document.addEventListener("visibilitychange",this.xa)}
v(so,I);p=so.prototype;p.Lb=function(a){var b=Xa();to(this,a);a=Xa()-b;this.u||(this.G-=a)};
p.Sa=function(a,b,c){++this.Z;if(b===10)return this.Lb(a),this.Z;var d=this.Z;this.j[d]=a;this.u&&!c?this.M.push({id:d,priority:b}):(this.i[b].push(d),this.Y||this.u||(this.h!==0&&uo(this)!==this.A&&this.stop(),this.start()));return d};
p.qa=function(a){delete this.j[a]};
function vo(a){a.M.length=0;for(var b=5;b>=0;b--)a.i[b].length=0;a.i[8].length=0;a.j={};a.stop()}
p.isHidden=function(){return!!document.hidden||!1};
function wo(a){return!a.isHidden()&&a.ma}
function uo(a){if(a.i[8].length){if(a.U)return 4;if(wo(a))return 3}for(var b=5;b>=a.o;b--)if(a.i[b].length>0)return b>0?wo(a)?3:2:1;return 0}
p.Ha=function(a){var b=F("yt.logging.errors.log");b&&b(a)};
function to(a,b){try{b()}catch(c){a.Ha(c)}}
function xo(a){for(var b=y(ro),c=b.next();!c.done;c=b.next())if(a.i[c.value].length)return!0;return!1}
p.Ce=function(a){var b=void 0;a&&(b=a.timeRemaining());this.ha=!0;yo(this,b);this.ha=!1};
p.zf=function(){yo(this)};
p.be=function(){zo(this)};
p.Ze=function(a){this.U=!0;var b=uo(this);b===4&&b!==this.A&&(this.stop(),this.start());yo(this,void 0,a);this.U=!1};
p.Se=function(){this.isHidden()||zo(this);this.h&&(this.stop(),this.start())};
function zo(a){a.stop();a.u=!0;for(var b=Xa(),c=a.i[8];c.length;){var d=c.shift(),e=a.j[d];delete a.j[d];e&&to(a,e)}Ao(a);a.u=!1;xo(a)&&a.start();b=Xa()-b;a.G-=b}
function Ao(a){for(var b=0,c=a.M.length;b<c;b++){var d=a.M[b];a.i[d.priority].push(d.id)}a.M.length=0}
function yo(a,b,c){a.U&&a.A===4&&a.h||a.stop();a.u=!0;b=Xa()+(b||a.G);for(var d=a.i[5];d.length;){var e=d.shift(),f=a.j[e];delete a.j[e];if(f){e=a;try{f(c)}catch(l){e.Ha(l)}}}for(d=a.i[4];d.length;)c=d.shift(),f=a.j[c],delete a.j[c],f&&to(a,f);d=a.ha?0:1;d=a.o>d?a.o:d;if(!(Xa()>=b)){do{a:{c=a;f=d;for(e=3;e>=f;e--)for(var g=c.i[e];g.length;){var h=g.shift(),k=c.j[h];delete c.j[h];if(k){c=k;break a}}c=null}c&&to(a,c)}while(c&&Xa()<b)}a.u=!1;Ao(a);a.G=qo;xo(a)&&a.start()}
p.start=function(){this.Y=!1;if(this.h===0)switch(this.A=uo(this),this.A){case 1:var a=this.Ra;this.h=this.Fa?window.requestIdleCallback(a,{timeout:3E3}):window.setTimeout(a,po);break;case 2:this.h=window.setTimeout(this.Kb,this.Jc);break;case 3:this.h=window.requestAnimationFrame(this.fb);break;case 4:this.h=window.setTimeout(this.Qa,0)}};
p.pause=function(){this.stop();this.Y=!0};
p.stop=function(){if(this.h){switch(this.A){case 1:var a=this.h;this.Fa?window.cancelIdleCallback(a):window.clearTimeout(a);break;case 2:case 4:window.clearTimeout(this.h);break;case 3:window.cancelAnimationFrame(this.h)}this.h=0}};
p.ba=function(){vo(this);this.stop();this.ma&&document.removeEventListener("visibilitychange",this.xa);I.prototype.ba.call(this)};var Bo=F("yt.scheduler.instance.timerIdMap_")||{},Co=hn("kevlar_tuner_scheduler_soft_state_timer_ms",800),Do=0,Eo=0;function Fo(){var a=F("ytglobal.schedulerInstanceInstance_");if(!a||a.ea)a=new so(R("scheduler")||{}),E("ytglobal.schedulerInstanceInstance_",a);return a}
function Go(){Ho();var a=F("ytglobal.schedulerInstanceInstance_");a&&(vc(a),E("ytglobal.schedulerInstanceInstance_",null))}
function Ho(){vo(Fo());for(var a in Bo)Bo.hasOwnProperty(a)&&delete Bo[Number(a)]}
function Io(a,b,c){if(!c)return c=c===void 0,-Fo().Sa(a,b,c);var d=window.setTimeout(function(){var e=Fo().Sa(a,b);Bo[d]=e},c);
return d}
function Jo(a){Fo().Lb(a)}
function Ko(a){var b=Fo();if(a<0)b.qa(-a);else{var c=Bo[a];c?(b.qa(c),delete Bo[a]):window.clearTimeout(a)}}
function Lo(){Mo()}
function Mo(){window.clearTimeout(Do);Fo().start()}
function No(){Fo().pause();window.clearTimeout(Do);Do=window.setTimeout(Lo,Co)}
function Oo(){window.clearTimeout(Eo);Eo=window.setTimeout(function(){Po(0)},Co)}
function Po(a){Oo();var b=Fo();b.o=a;b.start()}
function Qo(a){Oo();var b=Fo();b.o>a&&(b.o=a,b.start())}
function Ro(){window.clearTimeout(Eo);var a=Fo();a.o=0;a.start()}
function So(){F("yt.scheduler.initialized")||(E("yt.scheduler.instance.dispose",Go),E("yt.scheduler.instance.addJob",Io),E("yt.scheduler.instance.addImmediateJob",Jo),E("yt.scheduler.instance.cancelJob",Ko),E("yt.scheduler.instance.cancelAllJobs",Ho),E("yt.scheduler.instance.start",Mo),E("yt.scheduler.instance.pause",No),E("yt.scheduler.instance.setPriorityThreshold",Po),E("yt.scheduler.instance.enablePriorityThreshold",Qo),E("yt.scheduler.instance.clearPriorityThreshold",Ro),E("yt.scheduler.initialized",
!0))}
;function To(){no.apply(this,arguments)}
v(To,no);function Uo(){To.instance||(To.instance=new To);return To.instance}
To.prototype.Sa=function(a,b,c){c!==void 0&&Number.isNaN(Number(c))&&(c=void 0);var d=F("yt.scheduler.instance.addJob");return d?d(a,b,c):c===void 0?(a(),NaN):en(a,c||0)};
To.prototype.qa=function(a){if(a===void 0||!Number.isNaN(Number(a))){var b=F("yt.scheduler.instance.cancelJob");b?b(a):window.clearTimeout(a)}};
To.prototype.start=function(){var a=F("yt.scheduler.instance.start");a&&a()};
To.prototype.pause=function(){var a=F("yt.scheduler.instance.pause");a&&a()};
var Wj=Uo();S("web_scheduler_auto_init")&&So();function Vo(a){var b=new wk;this.h=(a=b.isAvailable()?a?new xk(b,a):b:null)?new rk(a):null;this.i=document.domain||window.location.hostname}
Vo.prototype.set=function(a,b,c,d){c=c||31104E3;this.remove(a);if(this.h)try{this.h.set(a,b,Date.now()+c*1E3);return}catch(f){}var e="";if(d)try{e=escape((new Si).serialize(b))}catch(f){return}else e=escape(b);Un(a,e,c,this.i)};
Vo.prototype.get=function(a,b){var c=void 0,d=!this.h;if(!d)try{c=this.h.get(a)}catch(e){d=!0}if(d&&(c=Vn(a))&&(c=unescape(c),b))try{c=JSON.parse(c)}catch(e){this.remove(a),c=void 0}return c};
Vo.prototype.remove=function(a){this.h&&this.h.remove(a);Wn(a,"/",this.i)};var Wo=function(){var a;return function(){a||(a=new Vo("ytidb"));return a}}();
function Xo(){var a;return(a=Wo())==null?void 0:a.get("LAST_RESULT_ENTRY_KEY",!0)}
;var Yo=[],Zo,$o=!1;function ap(){var a={};for(Zo=new bp(a.handleError===void 0?cp:a.handleError,a.logEvent===void 0?dp:a.logEvent);Yo.length>0;)switch(a=Yo.shift(),a.type){case "ERROR":Zo.Ha(a.payload);break;case "EVENT":Zo.logEvent(a.eventType,a.payload)}}
function ep(a){$o||(Zo?Zo.Ha(a):(Yo.push({type:"ERROR",payload:a}),Yo.length>10&&Yo.shift()))}
function fp(a,b){$o||(Zo?Zo.logEvent(a,b):(Yo.push({type:"EVENT",eventType:a,payload:b}),Yo.length>10&&Yo.shift()))}
;function gp(a){if(a.indexOf(":")>=0)throw Error("Database name cannot contain ':'");}
function hp(a){return a.substr(0,a.indexOf(":"))||a}
;var ip=ld||md;function jp(a){var b=Vc();return b?b.toLowerCase().indexOf(a)>=0:!1}
;var kp={},lp=(kp.AUTH_INVALID="No user identifier specified.",kp.EXPLICIT_ABORT="Transaction was explicitly aborted.",kp.IDB_NOT_SUPPORTED="IndexedDB is not supported.",kp.MISSING_INDEX="Index not created.",kp.MISSING_OBJECT_STORES="Object stores not created.",kp.DB_DELETED_BY_MISSING_OBJECT_STORES="Database is deleted because expected object stores were not created.",kp.DB_REOPENED_BY_MISSING_OBJECT_STORES="Database is reopened because expected object stores were not created.",kp.UNKNOWN_ABORT="Transaction was aborted for unknown reasons.",
kp.QUOTA_EXCEEDED="The current transaction exceeded its quota limitations.",kp.QUOTA_MAYBE_EXCEEDED="The current transaction may have failed because of exceeding quota limitations.",kp.EXECUTE_TRANSACTION_ON_CLOSED_DB="Can't start a transaction on a closed database",kp.INCOMPATIBLE_DB_VERSION="The binary is incompatible with the database version",kp),mp={},np=(mp.AUTH_INVALID="ERROR",mp.EXECUTE_TRANSACTION_ON_CLOSED_DB="WARNING",mp.EXPLICIT_ABORT="IGNORED",mp.IDB_NOT_SUPPORTED="ERROR",mp.MISSING_INDEX=
"WARNING",mp.MISSING_OBJECT_STORES="ERROR",mp.DB_DELETED_BY_MISSING_OBJECT_STORES="WARNING",mp.DB_REOPENED_BY_MISSING_OBJECT_STORES="WARNING",mp.QUOTA_EXCEEDED="WARNING",mp.QUOTA_MAYBE_EXCEEDED="WARNING",mp.UNKNOWN_ABORT="WARNING",mp.INCOMPATIBLE_DB_VERSION="WARNING",mp),op={},pp=(op.AUTH_INVALID=!1,op.EXECUTE_TRANSACTION_ON_CLOSED_DB=!1,op.EXPLICIT_ABORT=!1,op.IDB_NOT_SUPPORTED=!1,op.MISSING_INDEX=!1,op.MISSING_OBJECT_STORES=!1,op.DB_DELETED_BY_MISSING_OBJECT_STORES=!1,op.DB_REOPENED_BY_MISSING_OBJECT_STORES=
!1,op.QUOTA_EXCEEDED=!1,op.QUOTA_MAYBE_EXCEEDED=!0,op.UNKNOWN_ABORT=!0,op.INCOMPATIBLE_DB_VERSION=!1,op);function qp(a,b,c,d,e){b=b===void 0?{}:b;c=c===void 0?lp[a]:c;d=d===void 0?np[a]:d;e=e===void 0?pp[a]:e;T.call(this,c,Object.assign({},{name:"YtIdbKnownError",isSw:self.document===void 0,isIframe:self!==self.top,type:a},b));this.type=a;this.message=c;this.level=d;this.h=e;Object.setPrototypeOf(this,qp.prototype)}
v(qp,T);function rp(a,b){qp.call(this,"MISSING_OBJECT_STORES",{expectedObjectStores:b,foundObjectStores:a},lp.MISSING_OBJECT_STORES);Object.setPrototypeOf(this,rp.prototype)}
v(rp,qp);function sp(a,b){var c=Error.call(this);this.message=c.message;"stack"in c&&(this.stack=c.stack);this.index=a;this.objectStore=b;Object.setPrototypeOf(this,sp.prototype)}
v(sp,Error);var tp=["The database connection is closing","Can't start a transaction on a closed database","A mutation operation was attempted on a database that did not allow mutations"];
function up(a,b,c,d){b=hp(b);var e=a instanceof Error?a:Error("Unexpected error: "+a);if(e instanceof qp)return e;a={objectStoreNames:c,dbName:b,dbVersion:d};if(e.name==="QuotaExceededError")return new qp("QUOTA_EXCEEDED",a);if(nd&&e.name==="UnknownError")return new qp("QUOTA_MAYBE_EXCEEDED",a);if(e instanceof sp)return new qp("MISSING_INDEX",Object.assign({},a,{objectStore:e.objectStore,index:e.index}));if(e.name==="InvalidStateError"&&tp.some(function(f){return e.message.includes(f)}))return new qp("EXECUTE_TRANSACTION_ON_CLOSED_DB",
a);
if(e.name==="AbortError")return new qp("UNKNOWN_ABORT",a,e.message);e.args=[Object.assign({},a,{name:"IdbError",Gd:e.name})];e.level="WARNING";return e}
function vp(a,b,c){var d=Xo();return new qp("IDB_NOT_SUPPORTED",{context:{caller:a,publicName:b,version:c,hasSucceededOnce:d==null?void 0:d.hasSucceededOnce}})}
;function wp(a){if(!a)throw Error();throw a;}
function xp(a){return a}
function yp(a){this.h=a}
function zp(a){function b(e){if(d.state.status==="PENDING"){d.state={status:"REJECTED",reason:e};e=y(d.i);for(var f=e.next();!f.done;f=e.next())f=f.value,f()}}
function c(e){if(d.state.status==="PENDING"){d.state={status:"FULFILLED",value:e};e=y(d.h);for(var f=e.next();!f.done;f=e.next())f=f.value,f()}}
var d=this;this.state={status:"PENDING"};this.h=[];this.i=[];a=a.h;try{a(c,b)}catch(e){b(e)}}
zp.all=function(a){return new zp(new yp(function(b,c){var d=[],e=a.length;e===0&&b(d);for(var f={Bb:0};f.Bb<a.length;f={Bb:f.Bb},++f.Bb)zp.resolve(a[f.Bb]).then(function(g){return function(h){d[g.Bb]=h;e--;e===0&&b(d)}}(f)).catch(function(g){c(g)})}))};
zp.resolve=function(a){return new zp(new yp(function(b,c){a instanceof zp?a.then(b,c):b(a)}))};
zp.reject=function(a){return new zp(new yp(function(b,c){c(a)}))};
zp.prototype.then=function(a,b){var c=this,d=a!=null?a:xp,e=b!=null?b:wp;return new zp(new yp(function(f,g){c.state.status==="PENDING"?(c.h.push(function(){Ap(c,c,d,f,g)}),c.i.push(function(){Bp(c,c,e,f,g)})):c.state.status==="FULFILLED"?Ap(c,c,d,f,g):c.state.status==="REJECTED"&&Bp(c,c,e,f,g)}))};
zp.prototype.catch=function(a){return this.then(void 0,a)};
function Ap(a,b,c,d,e){try{if(a.state.status!=="FULFILLED")throw Error("calling handleResolve before the promise is fulfilled.");var f=c(a.state.value);f instanceof zp?Cp(a,b,f,d,e):d(f)}catch(g){e(g)}}
function Bp(a,b,c,d,e){try{if(a.state.status!=="REJECTED")throw Error("calling handleReject before the promise is rejected.");var f=c(a.state.reason);f instanceof zp?Cp(a,b,f,d,e):d(f)}catch(g){e(g)}}
function Cp(a,b,c,d,e){b===c?e(new TypeError("Circular promise chain detected.")):c.then(function(f){f instanceof zp?Cp(a,b,f,d,e):d(f)},function(f){e(f)})}
;function Dp(a,b,c){function d(){c(a.error);f()}
function e(){b(a.result);f()}
function f(){try{a.removeEventListener("success",e),a.removeEventListener("error",d)}catch(g){}}
a.addEventListener("success",e);a.addEventListener("error",d)}
function Ep(a){return new Promise(function(b,c){Dp(a,b,c)})}
function Fp(a){return new zp(new yp(function(b,c){Dp(a,b,c)}))}
;function Gp(a,b){return new zp(new yp(function(c,d){function e(){var f=a?b(a):null;f?f.then(function(g){a=g;e()},d):c()}
e()}))}
;var Hp=window,V=Hp.ytcsi&&Hp.ytcsi.now?Hp.ytcsi.now:Hp.performance&&Hp.performance.timing&&Hp.performance.now&&Hp.performance.timing.navigationStart?function(){return Hp.performance.timing.navigationStart+Hp.performance.now()}:function(){return(new Date).getTime()};function Ip(a,b){this.h=a;this.options=b;this.transactionCount=0;this.j=Math.round(V());this.i=!1}
p=Ip.prototype;p.add=function(a,b,c){return Jp(this,[a],{mode:"readwrite",ka:!0},function(d){return d.objectStore(a).add(b,c)})};
p.clear=function(a){return Jp(this,[a],{mode:"readwrite",ka:!0},function(b){return b.objectStore(a).clear()})};
p.close=function(){this.h.close();var a;((a=this.options)==null?0:a.closed)&&this.options.closed()};
p.count=function(a,b){return Jp(this,[a],{mode:"readonly",ka:!0},function(c){return c.objectStore(a).count(b)})};
function Kp(a,b,c){a=a.h.createObjectStore(b,c);return new Lp(a)}
p.delete=function(a,b){return Jp(this,[a],{mode:"readwrite",ka:!0},function(c){return c.objectStore(a).delete(b)})};
p.get=function(a,b){return Jp(this,[a],{mode:"readonly",ka:!0},function(c){return c.objectStore(a).get(b)})};
function Mp(a,b,c){return Jp(a,[b],{mode:"readwrite",ka:!0},function(d){d=d.objectStore(b);return Fp(d.h.put(c,void 0))})}
p.objectStoreNames=function(){return Array.from(this.h.objectStoreNames)};
function Jp(a,b,c,d){var e,f,g,h,k,l,m,n,r,t,w,x;return B(function(z){switch(z.h){case 1:var G={mode:"readonly",ka:!1,tag:"IDB_TRANSACTION_TAG_UNKNOWN"};typeof c==="string"?G.mode=c:Object.assign(G,c);e=G;a.transactionCount++;f=e.ka?3:1;g=0;case 2:if(h){z.B(4);break}g++;k=Math.round(V());wa(z,5);l=a.h.transaction(b,e.mode);G=z.yield;var H=new Np(l);H=Op(H,d);return G.call(z,H,7);case 7:return m=z.i,n=Math.round(V()),Pp(a,k,n,g,void 0,b.join(),e),z.return(m);case 5:r=ya(z);t=Math.round(V());w=up(r,
a.h.name,b.join(),a.h.version);if((x=w instanceof qp&&!w.h)||g>=f)Pp(a,k,t,g,w,b.join(),e),h=w;z.B(2);break;case 4:return z.return(Promise.reject(h))}})}
function Pp(a,b,c,d,e,f,g){b=c-b;e?(e instanceof qp&&(e.type==="QUOTA_EXCEEDED"||e.type==="QUOTA_MAYBE_EXCEEDED")&&fp("QUOTA_EXCEEDED",{dbName:hp(a.h.name),objectStoreNames:f,transactionCount:a.transactionCount,transactionMode:g.mode}),e instanceof qp&&e.type==="UNKNOWN_ABORT"&&(c-=a.j,c<0&&c>=2147483648&&(c=0),fp("TRANSACTION_UNEXPECTEDLY_ABORTED",{objectStoreNames:f,transactionDuration:b,transactionCount:a.transactionCount,dbDuration:c}),a.i=!0),Qp(a,!1,d,f,b,g.tag),ep(e)):Qp(a,!0,d,f,b,g.tag)}
function Qp(a,b,c,d,e,f){fp("TRANSACTION_ENDED",{objectStoreNames:d,connectionHasUnknownAbortedTransaction:a.i,duration:e,isSuccessful:b,tryCount:c,tag:f===void 0?"IDB_TRANSACTION_TAG_UNKNOWN":f})}
p.getName=function(){return this.h.name};
function Lp(a){this.h=a}
p=Lp.prototype;p.add=function(a,b){return Fp(this.h.add(a,b))};
p.autoIncrement=function(){return this.h.autoIncrement};
p.clear=function(){return Fp(this.h.clear()).then(function(){})};
function Rp(a,b,c){a.h.createIndex(b,c,{unique:!1})}
p.count=function(a){return Fp(this.h.count(a))};
function Sp(a,b){return Tp(a,{query:b},function(c){return c.delete().then(function(){return Up(c)})}).then(function(){})}
p.delete=function(a){return a instanceof IDBKeyRange?Sp(this,a):Fp(this.h.delete(a))};
p.get=function(a){return Fp(this.h.get(a))};
p.index=function(a){try{return new Vp(this.h.index(a))}catch(b){if(b instanceof Error&&b.name==="NotFoundError")throw new sp(a,this.h.name);throw b;}};
p.getName=function(){return this.h.name};
p.keyPath=function(){return this.h.keyPath};
function Tp(a,b,c){a=a.h.openCursor(b.query,b.direction);return Wp(a).then(function(d){return Gp(d,c)})}
function Np(a){var b=this;this.h=a;this.i=new Map;this.aborted=!1;this.done=new Promise(function(c,d){b.h.addEventListener("complete",function(){c()});
b.h.addEventListener("error",function(e){e.currentTarget===e.target&&d(b.h.error)});
b.h.addEventListener("abort",function(){var e=b.h.error;if(e)d(e);else if(!b.aborted){e=qp;for(var f=b.h.objectStoreNames,g=[],h=0;h<f.length;h++){var k=f.item(h);if(k===null)throw Error("Invariant: item in DOMStringList is null");g.push(k)}e=new e("UNKNOWN_ABORT",{objectStoreNames:g.join(),dbName:b.h.db.name,mode:b.h.mode});d(e)}})})}
function Op(a,b){var c=new Promise(function(d,e){try{b(a).then(function(f){d(f)}).catch(e)}catch(f){e(f),a.abort()}});
return Promise.all([c,a.done]).then(function(d){return y(d).next().value})}
Np.prototype.abort=function(){this.h.abort();this.aborted=!0;throw new qp("EXPLICIT_ABORT");};
Np.prototype.objectStore=function(a){a=this.h.objectStore(a);var b=this.i.get(a);b||(b=new Lp(a),this.i.set(a,b));return b};
function Vp(a){this.h=a}
p=Vp.prototype;p.count=function(a){return Fp(this.h.count(a))};
p.delete=function(a){return Xp(this,{query:a},function(b){return b.delete().then(function(){return Up(b)})})};
p.get=function(a){return Fp(this.h.get(a))};
p.keyPath=function(){return this.h.keyPath};
p.unique=function(){return this.h.unique};
function Xp(a,b,c){a=a.h.openCursor(b.query===void 0?null:b.query,b.direction===void 0?"next":b.direction);return Wp(a).then(function(d){return Gp(d,c)})}
function Yp(a,b){this.request=a;this.cursor=b}
function Wp(a){return Fp(a).then(function(b){return b?new Yp(a,b):null})}
function Up(a){a.cursor.continue(void 0);return Wp(a.request)}
Yp.prototype.delete=function(){return Fp(this.cursor.delete()).then(function(){})};
Yp.prototype.getValue=function(){return this.cursor.value};
Yp.prototype.update=function(a){return Fp(this.cursor.update(a))};function Zp(a,b,c){return new Promise(function(d,e){function f(){r||(r=new Ip(g.result,{closed:n}));return r}
var g=b!==void 0?self.indexedDB.open(a,b):self.indexedDB.open(a);var h=c.ee,k=c.blocking,l=c.xf,m=c.upgrade,n=c.closed,r;g.addEventListener("upgradeneeded",function(t){try{if(t.newVersion===null)throw Error("Invariant: newVersion on IDbVersionChangeEvent is null");if(g.transaction===null)throw Error("Invariant: transaction on IDbOpenDbRequest is null");t.dataLoss&&t.dataLoss!=="none"&&fp("IDB_DATA_CORRUPTED",{reason:t.dataLossMessage||"unknown reason",dbName:hp(a)});var w=f(),x=new Np(g.transaction);
m&&m(w,function(z){return t.oldVersion<z&&t.newVersion>=z},x);
x.done.catch(function(z){e(z)})}catch(z){e(z)}});
g.addEventListener("success",function(){var t=g.result;k&&t.addEventListener("versionchange",function(){k(f())});
t.addEventListener("close",function(){fp("IDB_UNEXPECTEDLY_CLOSED",{dbName:hp(a),dbVersion:t.version});l&&l()});
d(f())});
g.addEventListener("error",function(){e(g.error)});
h&&g.addEventListener("blocked",function(){h()})})}
function $p(a,b,c){c=c===void 0?{}:c;return Zp(a,b,c)}
function aq(a,b){b=b===void 0?{}:b;var c,d,e,f;return B(function(g){if(g.h==1)return wa(g,2),c=self.indexedDB.deleteDatabase(a),d=b,(e=d.ee)&&c.addEventListener("blocked",function(){e()}),g.yield(Ep(c),4);
if(g.h!=2)return xa(g,0);f=ya(g);throw up(f,a,"",-1);})}
;function bq(a,b){this.name=a;this.options=b;this.j=!0;this.u=this.o=0}
bq.prototype.i=function(a,b,c){c=c===void 0?{}:c;return $p(a,b,c)};
bq.prototype.delete=function(a){a=a===void 0?{}:a;return aq(this.name,a)};
function cq(a,b){return new qp("INCOMPATIBLE_DB_VERSION",{dbName:a.name,oldVersion:a.options.version,newVersion:b})}
function dq(a,b){if(!b)throw vp("openWithToken",hp(a.name));return a.open()}
bq.prototype.open=function(){function a(){var f,g,h,k,l,m,n,r,t,w;return B(function(x){switch(x.h){case 1:return g=(f=Error().stack)!=null?f:"",wa(x,2),x.yield(c.i(c.name,c.options.version,e),4);case 4:for(var z=h=x.i,G=c.options,H=[],U=y(Object.keys(G.Hb)),Z=U.next();!Z.done;Z=U.next()){Z=Z.value;var mb=G.Hb[Z],Qb=mb.af===void 0?Number.MAX_VALUE:mb.af;!(z.h.version>=mb.Nb)||z.h.version>=Qb||z.h.objectStoreNames.contains(Z)||H.push(Z)}k=H;if(k.length===0){x.B(5);break}l=Object.keys(c.options.Hb);
m=h.objectStoreNames();if(c.u<hn("ytidb_reopen_db_retries",0))return c.u++,h.close(),ep(new qp("DB_REOPENED_BY_MISSING_OBJECT_STORES",{dbName:c.name,expectedObjectStores:l,foundObjectStores:m})),x.return(a());if(!(c.o<hn("ytidb_remake_db_retries",1))){x.B(6);break}c.o++;return x.yield(c.delete(),7);case 7:return ep(new qp("DB_DELETED_BY_MISSING_OBJECT_STORES",{dbName:c.name,expectedObjectStores:l,foundObjectStores:m})),x.return(a());case 6:throw new rp(m,l);case 5:return x.return(h);case 2:n=ya(x);
if(n instanceof DOMException?n.name!=="VersionError":"DOMError"in self&&n instanceof DOMError?n.name!=="VersionError":!(n instanceof Object&&"message"in n)||n.message!=="An attempt was made to open a database using a lower version than the existing version."){x.B(8);break}return x.yield(c.i(c.name,void 0,Object.assign({},e,{upgrade:void 0})),9);case 9:r=x.i;t=r.h.version;if(c.options.version!==void 0&&t>c.options.version+1)throw r.close(),c.j=!1,cq(c,t);return x.return(r);case 8:throw b(),n instanceof
Error&&!S("ytidb_async_stack_killswitch")&&(n.stack=n.stack+"\n"+g.substring(g.indexOf("\n")+1)),up(n,c.name,"",(w=c.options.version)!=null?w:-1);}})}
function b(){c.h===d&&(c.h=void 0)}
var c=this;if(!this.j)throw cq(this);if(this.h)return this.h;var d,e={blocking:function(f){f.close()},
closed:b,xf:b,upgrade:this.options.upgrade};return this.h=d=a()};var eq=new bq("YtIdbMeta",{Hb:{databases:{Nb:1}},upgrade:function(a,b){b(1)&&Kp(a,"databases",{keyPath:"actualName"})}});
function fq(a,b){var c;return B(function(d){if(d.h==1)return d.yield(dq(eq,b),2);c=d.i;return d.return(Jp(c,["databases"],{ka:!0,mode:"readwrite"},function(e){var f=e.objectStore("databases");return f.get(a.actualName).then(function(g){if(g?a.actualName!==g.actualName||a.publicName!==g.publicName||a.userIdentifier!==g.userIdentifier:1)return Fp(f.h.put(a,void 0)).then(function(){})})}))})}
function gq(a,b){var c;return B(function(d){if(d.h==1)return a?d.yield(dq(eq,b),2):d.return();c=d.i;return d.return(c.delete("databases",a))})}
function hq(a,b){var c,d;return B(function(e){return e.h==1?(c=[],e.yield(dq(eq,b),2)):e.h!=3?(d=e.i,e.yield(Jp(d,["databases"],{ka:!0,mode:"readonly"},function(f){c.length=0;return Tp(f.objectStore("databases"),{},function(g){a(g.getValue())&&c.push(g.getValue());return Up(g)})}),3)):e.return(c)})}
function iq(a){return hq(function(b){return b.publicName==="LogsDatabaseV2"&&b.userIdentifier!==void 0},a)}
function jq(a,b,c){return hq(function(d){return c?d.userIdentifier!==void 0&&!a.includes(d.userIdentifier)&&c.includes(d.publicName):d.userIdentifier!==void 0&&!a.includes(d.userIdentifier)},b)}
function kq(a){var b,c;return B(function(d){if(d.h==1)return b=mo("YtIdbMeta hasAnyMeta other"),d.yield(hq(function(e){return e.userIdentifier!==void 0&&e.userIdentifier!==b},a),2);
c=d.i;return d.return(c.length>0)})}
;var lq,mq=new function(){}(new function(){});
function nq(){var a,b,c,d;return B(function(e){switch(e.h){case 1:a=Xo();if((b=a)==null?0:b.hasSucceededOnce)return e.return(!0);var f;if(f=ip)f=/WebKit\/([0-9]+)/.exec(Vc()),f=!!(f&&parseInt(f[1],10)>=600);f&&(f=/WebKit\/([0-9]+)/.exec(Vc()),f=!(f&&parseInt(f[1],10)>=602));if(f||hd)return e.return(!1);try{if(c=self,!(c.indexedDB&&c.IDBIndex&&c.IDBKeyRange&&c.IDBObjectStore))return e.return(!1)}catch(g){return e.return(!1)}if(!("IDBTransaction"in self&&"objectStoreNames"in IDBTransaction.prototype))return e.return(!1);
wa(e,2);d={actualName:"yt-idb-test-do-not-use",publicName:"yt-idb-test-do-not-use",userIdentifier:void 0};return e.yield(fq(d,mq),4);case 4:return e.yield(gq("yt-idb-test-do-not-use",mq),5);case 5:return e.return(!0);case 2:return ya(e),e.return(!1)}})}
function oq(){if(lq!==void 0)return lq;$o=!0;return lq=nq().then(function(a){$o=!1;var b;if((b=Wo())!=null&&b.h){var c;b={hasSucceededOnce:((c=Xo())==null?void 0:c.hasSucceededOnce)||a};var d;(d=Wo())==null||d.set("LAST_RESULT_ENTRY_KEY",b,2592E3,!0)}return a})}
function pq(){return F("ytglobal.idbToken_")||void 0}
function qq(){var a=pq();return a?Promise.resolve(a):oq().then(function(b){(b=b?mq:void 0)&&E("ytglobal.idbToken_",b);return b})}
;var rq=0;function sq(a,b){rq||(rq=Wj.pa(function(){var c,d,e,f,g;return B(function(h){switch(h.h){case 1:return h.yield(qq(),2);case 2:c=h.i;if(!c)return h.return();d=!0;wa(h,3);return h.yield(jq(a,c,b),5);case 5:e=h.i;if(!e.length){d=!1;h.B(6);break}f=e[0];return h.yield(aq(f.actualName),7);case 7:return h.yield(gq(f.actualName,c),6);case 6:xa(h,4);break;case 3:g=ya(h),ep(g),d=!1;case 4:Wj.qa(rq),rq=0,d&&sq(a,b),h.h=0}})}))}
function tq(){var a;return B(function(b){return b.h==1?b.yield(qq(),2):(a=b.i)?b.return(kq(a)):b.return(!1)})}
new yj;function uq(a){if(!lo())throw a=new qp("AUTH_INVALID",{dbName:a}),ep(a),a;var b=mo();return{actualName:a+":"+b,publicName:a,userIdentifier:b}}
function vq(a,b,c,d){var e,f,g,h,k,l;return B(function(m){switch(m.h){case 1:return f=(e=Error().stack)!=null?e:"",m.yield(qq(),2);case 2:g=m.i;if(!g)throw h=vp("openDbImpl",a,b),S("ytidb_async_stack_killswitch")||(h.stack=h.stack+"\n"+f.substring(f.indexOf("\n")+1)),ep(h),h;gp(a);k=c?{actualName:a,publicName:a,userIdentifier:void 0}:uq(a);wa(m,3);return m.yield(fq(k,g),5);case 5:return m.yield($p(k.actualName,b,d),6);case 6:return m.return(m.i);case 3:return l=ya(m),wa(m,7),m.yield(gq(k.actualName,
g),9);case 9:xa(m,8);break;case 7:ya(m);case 8:throw l;}})}
function wq(a,b,c){c=c===void 0?{}:c;return vq(a,b,!1,c)}
function xq(a,b,c){c=c===void 0?{}:c;return vq(a,b,!0,c)}
function yq(a,b){b=b===void 0?{}:b;var c,d;return B(function(e){if(e.h==1)return e.yield(qq(),2);if(e.h!=3){c=e.i;if(!c)return e.return();gp(a);d=uq(a);return e.yield(aq(d.actualName,b),3)}return e.yield(gq(d.actualName,c),0)})}
function zq(a,b,c){a=a.map(function(d){return B(function(e){return e.h==1?e.yield(aq(d.actualName,b),2):e.yield(gq(d.actualName,c),0)})});
return Promise.all(a).then(function(){})}
function Aq(){var a=a===void 0?{}:a;var b,c;return B(function(d){if(d.h==1)return d.yield(qq(),2);if(d.h!=3){b=d.i;if(!b)return d.return();gp("LogsDatabaseV2");return d.yield(iq(b),3)}c=d.i;return d.yield(zq(c,a,b),0)})}
function Bq(a,b){b=b===void 0?{}:b;var c;return B(function(d){if(d.h==1)return d.yield(qq(),2);if(d.h!=3){c=d.i;if(!c)return d.return();gp(a);return d.yield(aq(a,b),3)}return d.yield(gq(a,c),0)})}
;function Cq(a,b){bq.call(this,a,b);this.options=b;gp(a)}
v(Cq,bq);function Dq(a,b){var c;return function(){c||(c=new Cq(a,b));return c}}
Cq.prototype.i=function(a,b,c){c=c===void 0?{}:c;return(this.options.shared?xq:wq)(a,b,Object.assign({},c))};
Cq.prototype.delete=function(a){a=a===void 0?{}:a;return(this.options.shared?Bq:yq)(this.name,a)};
function Eq(a,b){return Dq(a,b)}
;var Fq={},Gq=Eq("ytGcfConfig",{Hb:(Fq.coldConfigStore={Nb:1},Fq.hotConfigStore={Nb:1},Fq),shared:!1,upgrade:function(a,b){b(1)&&(Rp(Kp(a,"hotConfigStore",{keyPath:"key",autoIncrement:!0}),"hotTimestampIndex","timestamp"),Rp(Kp(a,"coldConfigStore",{keyPath:"key",autoIncrement:!0}),"coldTimestampIndex","timestamp"))},
version:1});function Hq(a){return dq(Gq(),a)}
function Iq(a,b,c){var d,e,f;return B(function(g){switch(g.h){case 1:return d={config:a,hashData:b,timestamp:V()},g.yield(Hq(c),2);case 2:return e=g.i,g.yield(e.clear("hotConfigStore"),3);case 3:return g.yield(Mp(e,"hotConfigStore",d),4);case 4:return f=g.i,g.return(f)}})}
function Jq(a,b,c,d){var e,f,g;return B(function(h){switch(h.h){case 1:return e={config:a,hashData:b,configData:c,timestamp:V()},h.yield(Hq(d),2);case 2:return f=h.i,h.yield(f.clear("coldConfigStore"),3);case 3:return h.yield(Mp(f,"coldConfigStore",e),4);case 4:return g=h.i,h.return(g)}})}
function Kq(a){var b,c;return B(function(d){return d.h==1?d.yield(Hq(a),2):d.h!=3?(b=d.i,c=void 0,d.yield(Jp(b,["coldConfigStore"],{mode:"readwrite",ka:!0},function(e){return Xp(e.objectStore("coldConfigStore").index("coldTimestampIndex"),{direction:"prev"},function(f){c=f.getValue()})}),3)):d.return(c)})}
function Lq(a){var b,c;return B(function(d){return d.h==1?d.yield(Hq(a),2):d.h!=3?(b=d.i,c=void 0,d.yield(Jp(b,["hotConfigStore"],{mode:"readwrite",ka:!0},function(e){return Xp(e.objectStore("hotConfigStore").index("hotTimestampIndex"),{direction:"prev"},function(f){c=f.getValue()})}),3)):d.return(c)})}
;function Mq(){I.call(this);this.i=[];this.h=[];var a=F("yt.gcf.config.hotUpdateCallbacks");a?(this.i=[].concat(A(a)),this.h=a):(this.h=[],E("yt.gcf.config.hotUpdateCallbacks",this.h))}
v(Mq,I);Mq.prototype.ba=function(){for(var a=y(this.i),b=a.next();!b.done;b=a.next()){var c=this.h;b=c.indexOf(b.value);b>=0&&c.splice(b,1)}this.i.length=0;I.prototype.ba.call(this)};function Nq(){this.h=0;this.i=new Mq}
function Oq(){var a;return(a=F("yt.gcf.config.hotConfigGroup"))!=null?a:R("RAW_HOT_CONFIG_GROUP")}
function Pq(a,b,c){var d,e,f;return B(function(g){switch(g.h){case 1:if(!S("start_client_gcf")){g.B(0);break}c&&(a.j=c,E("yt.gcf.config.hotConfigGroup",a.j||null));a.o(b);d=pq();if(!d){g.B(3);break}if(c){g.B(4);break}return g.yield(Lq(d),5);case 5:e=g.i,c=(f=e)==null?void 0:f.config;case 4:return g.yield(Iq(c,b,d),3);case 3:if(c)for(var h=c,k=y(a.i.h),l=k.next();!l.done;l=k.next())l=l.value,l(h);g.h=0}})}
function Qq(a,b,c){var d,e,f,g;return B(function(h){if(h.h==1){if(!S("start_client_gcf"))return h.B(0);a.coldHashData=b;E("yt.gcf.config.coldHashData",a.coldHashData||null);return(d=pq())?c?h.B(4):h.yield(Kq(d),5):h.B(0)}h.h!=4&&(e=h.i,c=(f=e)==null?void 0:f.config);if(!c)return h.B(0);g=c.configData;return h.yield(Jq(c,b,g,d),0)})}
function Rq(){if(!Nq.instance){var a=new Nq;Nq.instance=a}a=Nq.instance;var b=V()-a.h;if(!(a.h!==0&&b<hn("send_config_hash_timer"))){b=F("yt.gcf.config.coldConfigData");var c=F("yt.gcf.config.hotHashData"),d=F("yt.gcf.config.coldHashData");b&&c&&d&&(a.h=V());return{coldConfigData:b,hotHashData:c,coldHashData:d}}}
Nq.prototype.o=function(a){this.hotHashData=a;E("yt.gcf.config.hotHashData",this.hotHashData||null)};function Sq(){return"INNERTUBE_API_KEY"in Hm&&"INNERTUBE_API_VERSION"in Hm}
function Tq(){return{innertubeApiKey:R("INNERTUBE_API_KEY"),innertubeApiVersion:R("INNERTUBE_API_VERSION"),De:R("INNERTUBE_CONTEXT_CLIENT_CONFIG_INFO"),Ad:R("INNERTUBE_CONTEXT_CLIENT_NAME","WEB"),Lh:R("INNERTUBE_CONTEXT_CLIENT_NAME",1),innertubeContextClientVersion:R("INNERTUBE_CONTEXT_CLIENT_VERSION"),Fe:R("INNERTUBE_CONTEXT_HL"),Ee:R("INNERTUBE_CONTEXT_GL"),Ge:R("INNERTUBE_HOST_OVERRIDE")||"",He:!!R("INNERTUBE_USE_THIRD_PARTY_AUTH",!1),Mh:!!R("INNERTUBE_OMIT_API_KEY_WHEN_AUTH_HEADER_IS_PRESENT",
!1),appInstallData:R("SERIALIZED_CLIENT_CONFIG_DATA")}}
function Uq(a){var b={client:{hl:a.Fe,gl:a.Ee,clientName:a.Ad,clientVersion:a.innertubeContextClientVersion,configInfo:a.De}};navigator.userAgent&&(b.client.userAgent=String(navigator.userAgent));var c=D.devicePixelRatio;c&&c!=1&&(b.client.screenDensityFloat=String(c));c=R("EXPERIMENTS_TOKEN","");c!==""&&(b.client.experimentsToken=c);c=jn();c.length>0&&(b.request={internalExperimentFlags:c});c=a.Ad;if((c==="WEB"||c==="MWEB"||c===1||c===2)&&b){var d;b.client.mainAppWebInfo=(d=b.client.mainAppWebInfo)!=
null?d:{};b.client.mainAppWebInfo.webDisplayMode=Pn()}(d=F("yt.embedded_player.embed_url"))&&b&&(b.thirdParty={embedUrl:d});var e;if(S("web_log_memory_total_kbytes")&&((e=D.navigator)==null?0:e.deviceMemory)){var f;e=(f=D.navigator)==null?void 0:f.deviceMemory;b&&(b.client.memoryTotalKbytes=""+e*1E6)}a.appInstallData&&b&&(b.client.configInfo=b.client.configInfo||{},b.client.configInfo.appInstallData=a.appInstallData);(a=jo())&&b&&(b.client.connectionType=a);S("web_log_effective_connection_type")&&
(a=ko())&&b&&(b.client.effectiveConnectionType=a);S("start_client_gcf")&&(e=Rq())&&(a=e.coldConfigData,f=e.coldHashData,e=e.hotHashData,b&&(b.client.configInfo=b.client.configInfo||{},a&&(b.client.configInfo.coldConfigData=a),f&&(b.client.configInfo.coldHashData=f),e&&(b.client.configInfo.hotHashData=e)));R("DELEGATED_SESSION_ID")&&!S("pageid_as_header_web")&&(b.user={onBehalfOfUser:R("DELEGATED_SESSION_ID")});!S("fill_delegate_context_in_gel_killswitch")&&(a=R("INNERTUBE_CONTEXT_SERIALIZED_DELEGATION_CONTEXT"))&&
(b.user=Object.assign({},b.user,{serializedDelegationContext:a}));a=R("INNERTUBE_CONTEXT");var g;if(S("enable_persistent_device_token")&&(a==null?0:(g=a.client)==null?0:g.rolloutToken)){var h;b.client.rolloutToken=a==null?void 0:(h=a.client)==null?void 0:h.rolloutToken}g=Object;h=g.assign;a=b.client;f={};e=y(Object.entries(Vm(R("DEVICE",""))));for(d=e.next();!d.done;d=e.next())c=y(d.value),d=c.next().value,c=c.next().value,d==="cbrand"?f.deviceMake=c:d==="cmodel"?f.deviceModel=c:d==="cbr"?f.browserName=
c:d==="cbrver"?f.browserVersion=c:d==="cos"?f.osName=c:d==="cosver"?f.osVersion=c:d==="cplatform"&&(f.platform=c);b.client=h.call(g,a,f);return b}
function Vq(a,b,c){c=c===void 0?{}:c;var d={};R("EOM_VISITOR_DATA")?d={"X-Goog-EOM-Visitor-Id":R("EOM_VISITOR_DATA")}:d={"X-Goog-Visitor-Id":c.visitorData||R("VISITOR_DATA","")};if(b&&b.includes("www.youtube-nocookie.com"))return d;b=c.authorization||R("AUTHORIZATION");b||(a?b="Bearer "+F("gapi.auth.getToken")().Ah:(a=Sn(Rn()),S("pageid_as_header_web")||delete a["X-Goog-PageId"],d=Object.assign({},d,a)));b&&(d.Authorization=b);return d}
;var Wq=typeof TextEncoder!=="undefined"?new TextEncoder:null,Xq=Wq?function(a){return Wq.encode(a)}:function(a){for(var b=[],c=0,d=0;d<a.length;d++){var e=a.charCodeAt(d);
e<128?b[c++]=e:(e<2048?b[c++]=e>>6|192:((e&64512)==55296&&d+1<a.length&&(a.charCodeAt(d+1)&64512)==56320?(e=65536+((e&1023)<<10)+(a.charCodeAt(++d)&1023),b[c++]=e>>18|240,b[c++]=e>>12&63|128):b[c++]=e>>12|224,b[c++]=e>>6&63|128),b[c++]=e&63|128)}a=new Uint8Array(b.length);for(c=0;c<a.length;c++)a[c]=b[c];return a};var Yq={next:"wn_s",browse:"br_s",search:"sr_s",reel:"r_wrs",player:"ps_s"},Zq={next:"wn_r",browse:"br_r",search:"sr_r",reel:"r_wrr",player:"ps_r"};function $q(a,b){this.version=a;this.args=b}
$q.prototype.serialize=function(){return{version:this.version,args:this.args}};function ar(a,b){this.topic=a;this.h=b}
ar.prototype.toString=function(){return this.topic};var br=F("ytPubsub2Pubsub2Instance")||new N;N.prototype.subscribe=N.prototype.subscribe;N.prototype.unsubscribeByKey=N.prototype.fc;N.prototype.publish=N.prototype.sb;N.prototype.clear=N.prototype.clear;E("ytPubsub2Pubsub2Instance",br);var cr=F("ytPubsub2Pubsub2SubscribedKeys")||{};E("ytPubsub2Pubsub2SubscribedKeys",cr);var dr=F("ytPubsub2Pubsub2TopicToKeys")||{};E("ytPubsub2Pubsub2TopicToKeys",dr);var er=F("ytPubsub2Pubsub2IsAsync")||{};E("ytPubsub2Pubsub2IsAsync",er);
E("ytPubsub2Pubsub2SkipSubKey",null);function fr(a,b){var c=gr();c&&c.publish.call(c,a.toString(),a,b)}
function hr(a){var b=ir,c=gr();if(!c)return 0;var d=c.subscribe(b.toString(),function(e,f){var g=F("ytPubsub2Pubsub2SkipSubKey");g&&g==d||(g=function(){if(cr[d])try{if(f&&b instanceof ar&&b!=e)try{var h=b.h,k=f;if(!k.args||!k.version)throw Error("yt.pubsub2.Data.deserialize(): serializedData is incomplete.");try{if(!h.Sd){var l=new h;h.Sd=l.version}var m=h.Sd}catch(n){}if(!m||k.version!=m)throw Error("yt.pubsub2.Data.deserialize(): serializedData version is incompatible.");try{f=Reflect.construct(h,
Wb(k.args))}catch(n){throw n.message="yt.pubsub2.Data.deserialize(): "+n.message,n;}}catch(n){throw n.message="yt.pubsub2.pubsub2 cross-binary conversion error for "+b.toString()+": "+n.message,n;}a.call(window,f)}catch(n){Nm(n)}},er[b.toString()]?F("yt.scheduler.instance")?Wj.pa(g):en(g,0):g())});
cr[d]=!0;dr[b.toString()]||(dr[b.toString()]=[]);dr[b.toString()].push(d);return d}
function jr(){var a=kr,b=hr(function(c){a.apply(void 0,arguments);lr(b)});
return b}
function lr(a){var b=gr();b&&(typeof a==="number"&&(a=[a]),Pb(a,function(c){b.unsubscribeByKey(c);delete cr[c]}))}
function gr(){return F("ytPubsub2Pubsub2Instance")}
;function mr(a,b,c){c=c===void 0?{sampleRate:.1}:c;Math.random()<Math.min(.02,c.sampleRate/100)&&fr("meta_logging_csi_event",{timerName:a,ii:b})}
;var nr=void 0,or=void 0;function pr(){or||(or=em(R("WORKER_SERIALIZATION_URL")));return or||void 0}
function qr(){var a=pr();nr||a===void 0||(nr=new Worker(nb(a),void 0));return nr}
;var rr=hn("max_body_size_to_compress",5E5),sr=hn("min_body_size_to_compress",500),tr=!0,ur=0,vr=0,wr=hn("compression_performance_threshold_lr",250),xr=hn("slow_compressions_before_abandon_count",4),yr=!1,zr=new Map,Ar=1,Br=!0;function Cr(){if(typeof Worker==="function"&&pr()&&!yr){var a=function(c){c=c.data;if(c.op==="gzippedGelBatch"){var d=zr.get(c.key);d&&(Dr(c.gzippedBatch,d.latencyPayload,d.url,d.options,d.sendFn),zr.delete(c.key))}},b=qr();
b&&(b.addEventListener("message",a),b.onerror=function(){zr.clear()},yr=!0)}}
function Er(a,b,c,d,e){e=e===void 0?!1:e;var f={startTime:V(),ticks:{},infos:{}};if(tr)try{var g=Fr(b);if(g!=null&&(g>rr||g<sr))d(a,c);else{if(S("gzip_gel_with_worker")&&(S("initial_gzip_use_main_thread")&&!Br||!S("initial_gzip_use_main_thread"))){yr||Cr();var h=qr();if(h&&!e){zr.set(Ar,{latencyPayload:f,url:a,options:c,sendFn:d});h.postMessage({op:"gelBatchToGzip",serializedBatch:b,key:Ar});Ar++;return}}var k=cm(Xq(b));Dr(k,f,a,c,d)}}catch(l){Om(l),d(a,c)}else d(a,c)}
function Dr(a,b,c,d,e){Br=!1;var f=V();b.ticks.gelc=f;vr++;S("disable_compression_due_to_performance_degredation")&&f-b.startTime>=wr&&(ur++,S("abandon_compression_after_N_slow_zips")?vr===hn("compression_disable_point")&&ur>xr&&(tr=!1):tr=!1);Gr(b);d.headers||(d.headers={});d.headers["Content-Encoding"]="gzip";d.postBody=a;d.postParams=void 0;e(c,d)}
function Hr(a){var b=b===void 0?!1:b;var c=c===void 0?!1:c;var d=V(),e={startTime:d,ticks:{},infos:{}},f=b?F("yt.logging.gzipForFetch",!1):!0;if(tr&&f){if(!a.body)return a;try{var g=c?a.body:typeof a.body==="string"?a.body:JSON.stringify(a.body);f=g;if(!c&&typeof g==="string"){var h=Fr(g);if(h!=null&&(h>rr||h<sr))return a;c=b?{level:1}:void 0;f=cm(Xq(g),c);var k=V();e.ticks.gelc=k;if(b){vr++;if((S("disable_compression_due_to_performance_degredation")||S("disable_compression_due_to_performance_degradation_lr"))&&
k-d>=wr)if(ur++,S("abandon_compression_after_N_slow_zips")||S("abandon_compression_after_N_slow_zips_lr")){b=ur/vr;var l=xr/hn("compression_disable_point");vr>0&&vr%hn("compression_disable_point")===0&&b>=l&&(tr=!1)}else tr=!1;Gr(e)}}a.headers=Object.assign({},{"Content-Encoding":"gzip"},a.headers||{});a.body=f;return a}catch(m){return Om(m),a}}else return a}
function Fr(a){try{return(new Blob(a.split(""))).size}catch(b){return Om(b),null}}
function Gr(a){S("gel_compression_csi_killswitch")||!S("log_gel_compression_latency")&&!S("log_gel_compression_latency_lr")||mr("gel_compression",a,{sampleRate:.1})}
;function Ir(a){a=Object.assign({},a);delete a.Authorization;var b=kg();if(b){var c=new ak;c.update(R("INNERTUBE_API_KEY"));c.update(b);a.hash=qd(c.digest(),3)}return a}
;var Jr;function Kr(){Jr||(Jr=new Vo("yt.innertube"));return Jr}
function Lr(a,b,c,d){if(d)return null;d=Kr().get("nextId",!0)||1;var e=Kr().get("requests",!0)||{};e[d]={method:a,request:b,authState:Ir(c),requestTime:Math.round(V())};Kr().set("nextId",d+1,86400,!0);Kr().set("requests",e,86400,!0);return d}
function Mr(a){var b=Kr().get("requests",!0)||{};delete b[a];Kr().set("requests",b,86400,!0)}
function Nr(a){var b=Kr().get("requests",!0);if(b){for(var c in b){var d=b[c];if(!(Math.round(V())-d.requestTime<6E4)){var e=d.authState,f=Ir(Vq(!1));zg(e,f)&&(e=d.request,"requestTimeMs"in e&&(e.requestTimeMs=Math.round(V())),Or(a,d.method,e,{}));delete b[c]}}Kr().set("requests",b,86400,!0)}}
;function Pr(a){this.jc=this.h=!1;this.potentialEsfErrorCounter=this.i=0;this.handleError=function(){};
this.zb=function(){};
this.now=Date.now;this.Sb=!1;var b;this.Rd=(b=a.Rd)!=null?b:100;var c;this.Ld=(c=a.Ld)!=null?c:1;var d;this.Jd=(d=a.Jd)!=null?d:2592E6;var e;this.Id=(e=a.Id)!=null?e:12E4;var f;this.Kd=(f=a.Kd)!=null?f:5E3;var g;this.V=(g=a.V)!=null?g:void 0;this.qc=!!a.qc;var h;this.nc=(h=a.nc)!=null?h:.1;var k;this.Bc=(k=a.Bc)!=null?k:10;a.handleError&&(this.handleError=a.handleError);a.zb&&(this.zb=a.zb);a.Sb&&(this.Sb=a.Sb);a.jc&&(this.jc=a.jc);this.W=a.W;this.Ca=a.Ca;this.ga=a.ga;this.fa=a.fa;this.sendFn=a.sendFn;
this.dd=a.dd;this.Zc=a.Zc;Qr(this)&&(!this.W||this.W("networkless_logging"))&&Rr(this)}
function Rr(a){Qr(a)&&!a.Sb&&(a.h=!0,a.qc&&Math.random()<=a.nc&&a.ga.he(a.V),Sr(a),a.fa.ta()&&a.ec(),a.fa.listen(a.dd,a.ec.bind(a)),a.fa.listen(a.Zc,a.ud.bind(a)))}
p=Pr.prototype;p.writeThenSend=function(a,b){var c=this;b=b===void 0?{}:b;if(Qr(this)&&this.h){var d={url:a,options:b,timestamp:this.now(),status:"NEW",sendCount:0};this.ga.set(d,this.V).then(function(e){d.id=e;c.fa.ta()&&Tr(c,d)}).catch(function(e){Tr(c,d);
Ur(c,e)})}else this.sendFn(a,b)};
p.sendThenWrite=function(a,b,c){var d=this;b=b===void 0?{}:b;if(Qr(this)&&this.h){var e={url:a,options:b,timestamp:this.now(),status:"NEW",sendCount:0};this.W&&this.W("nwl_skip_retry")&&(e.skipRetry=c);if(this.fa.ta()||this.W&&this.W("nwl_aggressive_send_then_write")&&!e.skipRetry){if(!e.skipRetry){var f=b.onError?b.onError:function(){};
b.onError=function(g,h){return B(function(k){if(k.h==1)return k.yield(d.ga.set(e,d.V).catch(function(l){Ur(d,l)}),2);
f(g,h);k.h=0})}}this.sendFn(a,b,e.skipRetry)}else this.ga.set(e,this.V).catch(function(g){d.sendFn(a,b,e.skipRetry);
Ur(d,g)})}else this.sendFn(a,b,this.W&&this.W("nwl_skip_retry")&&c)};
p.sendAndWrite=function(a,b){var c=this;b=b===void 0?{}:b;if(Qr(this)&&this.h){var d={url:a,options:b,timestamp:this.now(),status:"NEW",sendCount:0},e=!1,f=b.onSuccess?b.onSuccess:function(){};
d.options.onSuccess=function(g,h){d.id!==void 0?c.ga.xb(d.id,c.V):e=!0;c.fa.mb&&c.W&&c.W("vss_network_hint")&&c.fa.mb(!0);f(g,h)};
this.sendFn(d.url,d.options,void 0,!0);this.ga.set(d,this.V).then(function(g){d.id=g;e&&c.ga.xb(d.id,c.V)}).catch(function(g){Ur(c,g)})}else this.sendFn(a,b,void 0,!0)};
p.ec=function(){var a=this;if(!Qr(this))throw Error("IndexedDB is not supported: throttleSend");this.i||(this.i=this.Ca.pa(function(){var b;return B(function(c){if(c.h==1)return c.yield(a.ga.xd("NEW",a.V),2);if(c.h!=3)return b=c.i,b?c.yield(Tr(a,b),3):(a.ud(),c.return());a.i&&(a.i=0,a.ec());c.h=0})},this.Rd))};
p.ud=function(){this.Ca.qa(this.i);this.i=0};
function Tr(a,b){var c;return B(function(d){switch(d.h){case 1:if(!Qr(a))throw Error("IndexedDB is not supported: immediateSend");if(b.id===void 0){d.B(2);break}return d.yield(a.ga.Le(b.id,a.V),3);case 3:(c=d.i)||a.zb(Error("The request cannot be found in the database."));case 2:if(Vr(a,b,a.Jd)){d.B(4);break}a.zb(Error("Networkless Logging: Stored logs request expired age limit"));if(b.id===void 0){d.B(5);break}return d.yield(a.ga.xb(b.id,a.V),5);case 5:return d.return();case 4:b.skipRetry||(b=Wr(a,
b));if(!b){d.B(0);break}if(!b.skipRetry||b.id===void 0){d.B(8);break}return d.yield(a.ga.xb(b.id,a.V),8);case 8:a.sendFn(b.url,b.options,!!b.skipRetry),d.h=0}})}
function Wr(a,b){if(!Qr(a))throw Error("IndexedDB is not supported: updateRequestHandlers");var c=b.options.onError?b.options.onError:function(){};
b.options.onError=function(e,f){var g,h,k,l;return B(function(m){switch(m.h){case 1:g=Xr(f);(h=Yr(f))&&a.W&&a.W("web_enable_error_204")&&a.handleError(Error("Request failed due to compression"),b.url,f);if(!(a.W&&a.W("nwl_consider_error_code")&&g||a.W&&!a.W("nwl_consider_error_code")&&a.potentialEsfErrorCounter<=a.Bc)){m.B(2);break}if(!a.fa.Fc){m.B(3);break}return m.yield(a.fa.Fc(),3);case 3:if(a.fa.ta()){m.B(2);break}c(e,f);if(!a.W||!a.W("nwl_consider_error_code")||((k=b)==null?void 0:k.id)===void 0){m.B(6);
break}return m.yield(a.ga.ed(b.id,a.V,!1),6);case 6:return m.return();case 2:if(a.W&&a.W("nwl_consider_error_code")&&!g&&a.potentialEsfErrorCounter>a.Bc)return m.return();a.potentialEsfErrorCounter++;if(((l=b)==null?void 0:l.id)===void 0){m.B(8);break}return b.sendCount<a.Ld?m.yield(a.ga.ed(b.id,a.V,!0,h?!1:void 0),12):m.yield(a.ga.xb(b.id,a.V),8);case 12:a.Ca.pa(function(){a.fa.ta()&&a.ec()},a.Kd);
case 8:c(e,f),m.h=0}})};
var d=b.options.onSuccess?b.options.onSuccess:function(){};
b.options.onSuccess=function(e,f){var g;return B(function(h){if(h.h==1)return((g=b)==null?void 0:g.id)===void 0?h.B(2):h.yield(a.ga.xb(b.id,a.V),2);a.fa.mb&&a.W&&a.W("vss_network_hint")&&a.fa.mb(!0);d(e,f);h.h=0})};
return b}
function Vr(a,b,c){b=b.timestamp;return a.now()-b>=c?!1:!0}
function Sr(a){if(!Qr(a))throw Error("IndexedDB is not supported: retryQueuedRequests");a.ga.xd("QUEUED",a.V).then(function(b){b&&!Vr(a,b,a.Id)?a.Ca.pa(function(){return B(function(c){if(c.h==1)return b.id===void 0?c.B(2):c.yield(a.ga.ed(b.id,a.V),2);Sr(a);c.h=0})}):a.fa.ta()&&a.ec()})}
function Ur(a,b){a.Vd&&!a.fa.ta()?a.Vd(b):a.handleError(b)}
function Qr(a){return!!a.V||a.jc}
function Xr(a){var b;return(a=a==null?void 0:(b=a.error)==null?void 0:b.code)&&a>=400&&a<=599?!1:!0}
function Yr(a){var b;a=a==null?void 0:(b=a.error)==null?void 0:b.code;return!(a!==400&&a!==415)}
;var Zr;
function $r(){if(Zr)return Zr();var a={};Zr=Eq("LogsDatabaseV2",{Hb:(a.LogsRequestsStore={Nb:2},a),shared:!1,upgrade:function(b,c,d){c(2)&&Kp(b,"LogsRequestsStore",{keyPath:"id",autoIncrement:!0});c(3);c(5)&&(d=d.objectStore("LogsRequestsStore"),d.h.indexNames.contains("newRequest")&&d.h.deleteIndex("newRequest"),Rp(d,"newRequestV2",["status","interface","timestamp"]));c(7)&&b.h.objectStoreNames.contains("sapisid")&&b.h.deleteObjectStore("sapisid");c(9)&&b.h.objectStoreNames.contains("SWHealthLog")&&b.h.deleteObjectStore("SWHealthLog")},
version:9});return Zr()}
;function as(a){return dq($r(),a)}
function bs(a,b){var c,d,e,f;return B(function(g){if(g.h==1)return c={startTime:V(),infos:{transactionType:"YT_IDB_TRANSACTION_TYPE_WRITE"},ticks:{}},g.yield(as(b),2);if(g.h!=3)return d=g.i,e=Object.assign({},a,{options:JSON.parse(JSON.stringify(a.options)),interface:R("INNERTUBE_CONTEXT_CLIENT_NAME",0)}),g.yield(Mp(d,"LogsRequestsStore",e),3);f=g.i;c.ticks.tc=V();cs(c);return g.return(f)})}
function ds(a,b){var c,d,e,f,g,h,k,l,m;return B(function(n){if(n.h==1)return c={startTime:V(),infos:{transactionType:"YT_IDB_TRANSACTION_TYPE_READ"},ticks:{}},n.yield(as(b),2);if(n.h!=3)return d=n.i,e=R("INNERTUBE_CONTEXT_CLIENT_NAME",0),f=[a,e,0],g=[a,e,V()],h=IDBKeyRange.bound(f,g),k="prev",S("use_fifo_for_networkless")&&(k="next"),l=void 0,m=a==="NEW"?"readwrite":"readonly",S("use_readonly_for_get_most_recent_by_status_killswitch")&&(m="readwrite"),n.yield(Jp(d,["LogsRequestsStore"],{mode:m,ka:!0},
function(r){return Xp(r.objectStore("LogsRequestsStore").index("newRequestV2"),{query:h,direction:k},function(t){t.getValue()&&(l=t.getValue(),a==="NEW"&&(l.status="QUEUED",t.update(l)))})}),3);
c.ticks.tc=V();cs(c);return n.return(l)})}
function es(a,b){var c;return B(function(d){if(d.h==1)return d.yield(as(b),2);c=d.i;return d.return(Jp(c,["LogsRequestsStore"],{mode:"readwrite",ka:!0},function(e){var f=e.objectStore("LogsRequestsStore");return f.get(a).then(function(g){if(g)return g.status="QUEUED",Fp(f.h.put(g,void 0)).then(function(){return g})})}))})}
function gs(a,b,c,d){c=c===void 0?!0:c;var e;return B(function(f){if(f.h==1)return f.yield(as(b),2);e=f.i;return f.return(Jp(e,["LogsRequestsStore"],{mode:"readwrite",ka:!0},function(g){var h=g.objectStore("LogsRequestsStore");return h.get(a).then(function(k){return k?(k.status="NEW",c&&(k.sendCount+=1),d!==void 0&&(k.options.compress=d),Fp(h.h.put(k,void 0)).then(function(){return k})):zp.resolve(void 0)})}))})}
function hs(a,b){var c;return B(function(d){if(d.h==1)return d.yield(as(b),2);c=d.i;return d.return(c.delete("LogsRequestsStore",a))})}
function is(a){var b,c;return B(function(d){if(d.h==1)return d.yield(as(a),2);b=d.i;c=V()-2592E6;return d.yield(Jp(b,["LogsRequestsStore"],{mode:"readwrite",ka:!0},function(e){return Tp(e.objectStore("LogsRequestsStore"),{},function(f){if(f.getValue().timestamp<=c)return f.delete().then(function(){return Up(f)})})}),0)})}
function js(){B(function(a){return a.yield(Aq(),0)})}
function cs(a){S("nwl_csi_killswitch")||mr("networkless_performance",a,{sampleRate:1})}
;var ks={accountStateChangeSignedIn:23,accountStateChangeSignedOut:24,delayedEventMetricCaptured:11,latencyActionBaselined:6,latencyActionInfo:7,latencyActionTicked:5,offlineTransferStatusChanged:2,offlineImageDownload:335,playbackStartStateChanged:9,systemHealthCaptured:3,mangoOnboardingCompleted:10,mangoPushNotificationReceived:230,mangoUnforkDbMigrationError:121,mangoUnforkDbMigrationSummary:122,mangoUnforkDbMigrationPreunforkDbVersionNumber:133,mangoUnforkDbMigrationPhoneMetadata:134,mangoUnforkDbMigrationPhoneStorage:135,
mangoUnforkDbMigrationStep:142,mangoAsyncApiMigrationEvent:223,mangoDownloadVideoResult:224,mangoHomepageVideoCount:279,mangoHomeV3State:295,mangoImageClientCacheHitEvent:273,sdCardStatusChanged:98,framesDropped:12,thumbnailHovered:13,deviceRetentionInfoCaptured:14,thumbnailLoaded:15,backToAppEvent:318,streamingStatsCaptured:17,offlineVideoShared:19,appCrashed:20,youThere:21,offlineStateSnapshot:22,mdxSessionStarted:25,mdxSessionConnected:26,mdxSessionDisconnected:27,bedrockResourceConsumptionSnapshot:28,
nextGenWatchWatchSwiped:29,kidsAccountsSnapshot:30,zeroStepChannelCreated:31,tvhtml5SearchCompleted:32,offlineSharePairing:34,offlineShareUnlock:35,mdxRouteDistributionSnapshot:36,bedrockRepetitiveActionTimed:37,unpluggedDegradationInfo:229,uploadMp4HeaderMoved:38,uploadVideoTranscoded:39,uploadProcessorStarted:46,uploadProcessorEnded:47,uploadProcessorReady:94,uploadProcessorRequirementPending:95,uploadProcessorInterrupted:96,uploadFrontendEvent:241,assetPackDownloadStarted:41,assetPackDownloaded:42,
assetPackApplied:43,assetPackDeleted:44,appInstallAttributionEvent:459,playbackSessionStopped:45,adBlockerMessagingShown:48,distributionChannelCaptured:49,dataPlanCpidRequested:51,detailedNetworkTypeCaptured:52,sendStateUpdated:53,receiveStateUpdated:54,sendDebugStateUpdated:55,receiveDebugStateUpdated:56,kidsErrored:57,mdxMsnSessionStatsFinished:58,appSettingsCaptured:59,mdxWebSocketServerHttpError:60,mdxWebSocketServer:61,startupCrashesDetected:62,coldStartInfo:435,offlinePlaybackStarted:63,liveChatMessageSent:225,
liveChatUserPresent:434,liveChatBeingModerated:457,liveCreationCameraUpdated:64,liveCreationEncodingCaptured:65,liveCreationError:66,liveCreationHealthUpdated:67,liveCreationVideoEffectsCaptured:68,liveCreationStageOccured:75,liveCreationBroadcastScheduled:123,liveCreationArchiveReplacement:149,liveCreationCostreamingConnection:421,liveCreationStreamWebrtcStats:288,mdxSessionRecoveryStarted:69,mdxSessionRecoveryCompleted:70,mdxSessionRecoveryStopped:71,visualElementShown:72,visualElementHidden:73,
visualElementGestured:78,visualElementStateChanged:208,screenCreated:156,playbackAssociated:202,visualElementAttached:215,playbackContextEvent:214,cloudCastingPlaybackStarted:74,webPlayerApiCalled:76,tvhtml5AccountDialogOpened:79,foregroundHeartbeat:80,foregroundHeartbeatScreenAssociated:111,kidsOfflineSnapshot:81,mdxEncryptionSessionStatsFinished:82,playerRequestCompleted:83,liteSchedulerStatistics:84,mdxSignIn:85,spacecastMetadataLookupRequested:86,spacecastBatchLookupRequested:87,spacecastSummaryRequested:88,
spacecastPlayback:89,spacecastDiscovery:90,tvhtml5LaunchUrlComponentChanged:91,mdxBackgroundPlaybackRequestCompleted:92,mdxBrokenAdditionalDataDeviceDetected:93,tvhtml5LocalStorage:97,tvhtml5DeviceStorageStatus:147,autoCaptionsAvailable:99,playbackScrubbingEvent:339,flexyState:100,interfaceOrientationCaptured:101,mainAppBrowseFragmentCache:102,offlineCacheVerificationFailure:103,offlinePlaybackExceptionDigest:217,vrCopresenceStats:104,vrCopresenceSyncStats:130,vrCopresenceCommsStats:137,vrCopresencePartyStats:153,
vrCopresenceEmojiStats:213,vrCopresenceEvent:141,vrCopresenceFlowTransitEvent:160,vrCowatchPartyEvent:492,vrCowatchUserStartOrJoinEvent:504,vrPlaybackEvent:345,kidsAgeGateTracking:105,offlineDelayAllowedTracking:106,mainAppAutoOfflineState:107,videoAsThumbnailDownload:108,videoAsThumbnailPlayback:109,liteShowMore:110,renderingError:118,kidsProfilePinGateTracking:119,abrTrajectory:124,scrollEvent:125,streamzIncremented:126,kidsProfileSwitcherTracking:127,kidsProfileCreationTracking:129,buyFlowStarted:136,
mbsConnectionInitiated:138,mbsPlaybackInitiated:139,mbsLoadChildren:140,liteProfileFetcher:144,mdxRemoteTransaction:146,reelPlaybackError:148,reachabilityDetectionEvent:150,mobilePlaybackEvent:151,courtsidePlayerStateChanged:152,musicPersistentCacheChecked:154,musicPersistentCacheCleared:155,playbackInterrupted:157,playbackInterruptionResolved:158,fixFopFlow:159,anrDetection:161,backstagePostCreationFlowEnded:162,clientError:163,gamingAccountLinkStatusChanged:164,liteHousewarming:165,buyFlowEvent:167,
kidsParentalGateTracking:168,kidsSignedOutSettingsStatus:437,kidsSignedOutPauseHistoryFixStatus:438,tvhtml5WatchdogViolation:444,ypcUpgradeFlow:169,yongleStudy:170,ypcUpdateFlowStarted:171,ypcUpdateFlowCancelled:172,ypcUpdateFlowSucceeded:173,ypcUpdateFlowFailed:174,liteGrowthkitPromo:175,paymentFlowStarted:341,transactionFlowShowPaymentDialog:405,transactionFlowStarted:176,transactionFlowSecondaryDeviceStarted:222,transactionFlowSecondaryDeviceSignedOutStarted:383,transactionFlowCancelled:177,transactionFlowPaymentCallBackReceived:387,
transactionFlowPaymentSubmitted:460,transactionFlowPaymentSucceeded:329,transactionFlowSucceeded:178,transactionFlowFailed:179,transactionFlowPlayBillingConnectionStartEvent:428,transactionFlowSecondaryDeviceSuccess:458,transactionFlowErrorEvent:411,liteVideoQualityChanged:180,watchBreakEnablementSettingEvent:181,watchBreakFrequencySettingEvent:182,videoEffectsCameraPerformanceMetrics:183,adNotify:184,startupTelemetry:185,playbackOfflineFallbackUsed:186,outOfMemory:187,ypcPauseFlowStarted:188,ypcPauseFlowCancelled:189,
ypcPauseFlowSucceeded:190,ypcPauseFlowFailed:191,uploadFileSelected:192,ypcResumeFlowStarted:193,ypcResumeFlowCancelled:194,ypcResumeFlowSucceeded:195,ypcResumeFlowFailed:196,adsClientStateChange:197,ypcCancelFlowStarted:198,ypcCancelFlowCancelled:199,ypcCancelFlowSucceeded:200,ypcCancelFlowFailed:201,ypcCancelFlowGoToPaymentProcessor:402,ypcDeactivateFlowStarted:320,ypcRedeemFlowStarted:203,ypcRedeemFlowCancelled:204,ypcRedeemFlowSucceeded:205,ypcRedeemFlowFailed:206,ypcFamilyCreateFlowStarted:258,
ypcFamilyCreateFlowCancelled:259,ypcFamilyCreateFlowSucceeded:260,ypcFamilyCreateFlowFailed:261,ypcFamilyManageFlowStarted:262,ypcFamilyManageFlowCancelled:263,ypcFamilyManageFlowSucceeded:264,ypcFamilyManageFlowFailed:265,restoreContextEvent:207,embedsAdEvent:327,autoplayTriggered:209,clientDataErrorEvent:210,experimentalVssValidation:211,tvhtml5TriggeredEvent:212,tvhtml5FrameworksFieldTrialResult:216,tvhtml5FrameworksFieldTrialStart:220,musicOfflinePreferences:218,watchTimeSegment:219,appWidthLayoutError:221,
accountRegistryChange:226,userMentionAutoCompleteBoxEvent:227,downloadRecommendationEnablementSettingEvent:228,musicPlaybackContentModeChangeEvent:231,offlineDbOpenCompleted:232,kidsFlowEvent:233,kidsFlowCorpusSelectedEvent:234,videoEffectsEvent:235,unpluggedOpsEogAnalyticsEvent:236,playbackAudioRouteEvent:237,interactionLoggingDebugModeError:238,offlineYtbRefreshed:239,kidsFlowError:240,musicAutoplayOnLaunchAttempted:242,deviceContextActivityEvent:243,deviceContextEvent:244,templateResolutionException:245,
musicSideloadedPlaylistServiceCalled:246,embedsStorageAccessNotChecked:247,embedsHasStorageAccessResult:248,embedsItpPlayedOnReload:249,embedsRequestStorageAccessResult:250,embedsShouldRequestStorageAccessResult:251,embedsRequestStorageAccessState:256,embedsRequestStorageAccessFailedState:257,embedsItpWatchLaterResult:266,searchSuggestDecodingPayloadFailure:252,siriShortcutActivated:253,tvhtml5KeyboardPerformance:254,latencyActionSpan:255,elementsLog:267,ytbFileOpened:268,tfliteModelError:269,apiTest:270,
yongleUsbSetup:271,touStrikeInterstitialEvent:272,liteStreamToSave:274,appBundleClientEvent:275,ytbFileCreationFailed:276,adNotifyFailure:278,ytbTransferFailed:280,blockingRequestFailed:281,liteAccountSelector:282,liteAccountUiCallbacks:283,dummyPayload:284,browseResponseValidationEvent:285,entitiesError:286,musicIosBackgroundFetch:287,mdxNotificationEvent:289,layersValidationError:290,musicPwaInstalled:291,liteAccountCleanup:292,html5PlayerHealthEvent:293,watchRestoreAttempt:294,liteAccountSignIn:296,
notaireEvent:298,kidsVoiceSearchEvent:299,adNotifyFilled:300,delayedEventDropped:301,analyticsSearchEvent:302,systemDarkThemeOptOutEvent:303,flowEvent:304,networkConnectivityBaselineEvent:305,ytbFileImported:306,downloadStreamUrlExpired:307,directSignInEvent:308,lyricImpressionEvent:309,accessibilityStateEvent:310,tokenRefreshEvent:311,genericAttestationExecution:312,tvhtml5VideoSeek:313,unpluggedAutoPause:314,scrubbingEvent:315,bedtimeReminderEvent:317,tvhtml5UnexpectedRestart:319,tvhtml5StabilityTraceEvent:478,
tvhtml5OperationHealth:467,tvhtml5WatchKeyEvent:321,voiceLanguageChanged:322,tvhtml5LiveChatStatus:323,parentToolsCorpusSelectedEvent:324,offerAdsEnrollmentInitiated:325,networkQualityIntervalEvent:326,deviceStartupMetrics:328,heartbeatActionPlayerTransitioned:330,tvhtml5Lifecycle:331,heartbeatActionPlayerHalted:332,adaptiveInlineMutedSettingEvent:333,mainAppLibraryLoadingState:334,thirdPartyLogMonitoringEvent:336,appShellAssetLoadReport:337,tvhtml5AndroidAttestation:338,tvhtml5StartupSoundEvent:340,
iosBackgroundRefreshTask:342,iosBackgroundProcessingTask:343,sliEventBatch:344,postImpressionEvent:346,musicSideloadedPlaylistExport:347,idbUnexpectedlyClosed:348,voiceSearchEvent:349,mdxSessionCastEvent:350,idbQuotaExceeded:351,idbTransactionEnded:352,idbTransactionAborted:353,tvhtml5KeyboardLogging:354,idbIsSupportedCompleted:355,creatorStudioMobileEvent:356,idbDataCorrupted:357,parentToolsAppChosenEvent:358,webViewBottomSheetResized:359,activeStateControllerScrollPerformanceSummary:360,navigatorValidation:361,
mdxSessionHeartbeat:362,clientHintsPolyfillDiagnostics:363,clientHintsPolyfillEvent:364,proofOfOriginTokenError:365,kidsAddedAccountSummary:366,musicWearableDevice:367,ypcRefundFlowEvent:368,tvhtml5PlaybackMeasurementEvent:369,tvhtml5WatermarkMeasurementEvent:370,clientExpGcfPropagationEvent:371,mainAppReferrerIntent:372,leaderLockEnded:373,leaderLockAcquired:374,googleHatsEvent:375,persistentLensLaunchEvent:376,parentToolsChildWelcomeChosenEvent:378,browseThumbnailPreloadEvent:379,finalPayload:380,
mdxDialAdditionalDataUpdateEvent:381,webOrchestrationTaskLifecycleRecord:382,startupSignalEvent:384,accountError:385,gmsDeviceCheckEvent:386,accountSelectorEvent:388,accountUiCallbacks:389,mdxDialAdditionalDataProbeEvent:390,downloadsSearchIcingApiStats:391,downloadsSearchIndexUpdatedEvent:397,downloadsSearchIndexSnapshot:398,dataPushClientEvent:392,kidsCategorySelectedEvent:393,mdxDeviceManagementSnapshotEvent:394,prefetchRequested:395,prefetchableCommandExecuted:396,gelDebuggingEvent:399,webLinkTtsPlayEnd:400,
clipViewInvalid:401,persistentStorageStateChecked:403,cacheWipeoutEvent:404,playerEvent:410,sfvEffectPipelineStartedEvent:412,sfvEffectPipelinePausedEvent:429,sfvEffectPipelineEndedEvent:413,sfvEffectChosenEvent:414,sfvEffectLoadedEvent:415,sfvEffectUserInteractionEvent:465,sfvEffectFirstFrameProcessedLatencyEvent:416,sfvEffectAggregatedFramesProcessedLatencyEvent:417,sfvEffectAggregatedFramesDroppedEvent:418,sfvEffectPipelineErrorEvent:430,sfvEffectGraphFrozenEvent:419,sfvEffectGlThreadBlockedEvent:420,
mdeQosEvent:510,mdeVideoChangedEvent:442,mdePlayerPerformanceMetrics:472,mdeExporterEvent:497,genericClientExperimentEvent:423,homePreloadTaskScheduled:424,homePreloadTaskExecuted:425,homePreloadCacheHit:426,polymerPropertyChangedInObserver:427,applicationStarted:431,networkCronetRttBatch:432,networkCronetRttSummary:433,repeatChapterLoopEvent:436,seekCancellationEvent:462,lockModeTimeoutEvent:483,externalVideoShareToYoutubeAttempt:501,parentCodeEvent:502,offlineTransferStarted:4,musicOfflineMixtapePreferencesChanged:16,
mangoDailyNewVideosNotificationAttempt:40,mangoDailyNewVideosNotificationError:77,dtwsPlaybackStarted:112,dtwsTileFetchStarted:113,dtwsTileFetchCompleted:114,dtwsTileFetchStatusChanged:145,dtwsKeyframeDecoderBufferSent:115,dtwsTileUnderflowedOnNonkeyframe:116,dtwsBackfillFetchStatusChanged:143,dtwsBackfillUnderflowed:117,dtwsAdaptiveLevelChanged:128,blockingVisitorIdTimeout:277,liteSocial:18,mobileJsInvocation:297,biscottiBasedDetection:439,coWatchStateChange:440,embedsVideoDataDidChange:441,shortsFirst:443,
cruiseControlEvent:445,qoeClientLoggingContext:446,atvRecommendationJobExecuted:447,tvhtml5UserFeedback:448,producerProjectCreated:449,producerProjectOpened:450,producerProjectDeleted:451,producerProjectElementAdded:453,producerProjectElementRemoved:454,producerAppStateChange:509,producerProjectDiskInsufficientExportFailure:516,producerMediaServicesResetDetails:522,tvhtml5ShowClockEvent:455,deviceCapabilityCheckMetrics:456,youtubeClearcutEvent:461,offlineBrowseFallbackEvent:463,getCtvTokenEvent:464,
startupDroppedFramesSummary:466,screenshotEvent:468,miniAppPlayEvent:469,elementsDebugCounters:470,fontLoadEvent:471,webKillswitchReceived:473,webKillswitchExecuted:474,cameraOpenEvent:475,manualSmoothnessMeasurement:476,tvhtml5AppQualityEvent:477,polymerPropertyAccessEvent:479,miniAppSdkUsage:480,cobaltTelemetryEvent:481,crossDevicePlayback:482,channelCreatedWithObakeImage:484,channelEditedWithObakeImage:485,offlineDeleteEvent:486,crossDeviceNotificationTransfer:487,androidIntentEvent:488,unpluggedAmbientInterludesCounterfactualEvent:489,
keyPlaysPlayback:490,shortsCreationFallbackEvent:493,vssData:491,castMatch:494,miniAppPerformanceMetrics:495,userFeedbackEvent:496,kidsGuestSessionMismatch:498,musicSideloadedPlaylistMigrationEvent:499,sleepTimerSessionFinishEvent:500,watchEpPromoConflict:503,innertubeResponseCacheMetrics:505,miniAppAdEvent:506,dataPlanUpsellEvent:507,producerProjectRenamed:508,producerMediaSelectionEvent:511,embedsAutoplayStatusChanged:512,remoteConnectEvent:513,connectedSessionMisattributionEvent:514,producerProjectElementModified:515,
adsSeenClientLogging:517,producerEvent:518,tvhtml5CleanStart:519,deviceAccountMetricsEvent:520,derpLogEvent:521,playablesPortalEvent:523,ipValidationStarted:524,ipValidationReceived:525};var ls={},ms=Eq("ServiceWorkerLogsDatabase",{Hb:(ls.SWHealthLog={Nb:1},ls),shared:!0,upgrade:function(a,b){b(1)&&Rp(Kp(a,"SWHealthLog",{keyPath:"id",autoIncrement:!0}),"swHealthNewRequest",["interface","timestamp"])},
version:1});function ns(a){return dq(ms(),a)}
function ps(a){var b,c;B(function(d){if(d.h==1)return d.yield(ns(a),2);b=d.i;c=V()-2592E6;return d.yield(Jp(b,["SWHealthLog"],{mode:"readwrite",ka:!0},function(e){return Tp(e.objectStore("SWHealthLog"),{},function(f){if(f.getValue().timestamp<=c)return f.delete().then(function(){return Up(f)})})}),0)})}
function qs(a){var b;return B(function(c){if(c.h==1)return c.yield(ns(a),2);b=c.i;return c.yield(b.clear("SWHealthLog"),0)})}
;var rs={},ss=0;function ts(a){var b=b===void 0?{}:b;var c=new Image,d=""+ss++;rs[d]=c;c.onload=c.onerror=function(){delete rs[d]};
b.di&&(c.referrerPolicy="no-referrer");c.src=a}
;var us;function vs(){us||(us=new Vo("yt.offline"));return us}
function ws(a){if(S("offline_error_handling")){var b=vs().get("errors",!0)||{};b[a.message]={name:a.name,stack:a.stack};a.level&&(b[a.message].level=a.level);vs().set("errors",b,2592E3,!0)}}
;function xs(){this.h=new Map;this.i=!1}
function ys(){if(!xs.instance){var a=F("yt.networkRequestMonitor.instance")||new xs;E("yt.networkRequestMonitor.instance",a);xs.instance=a}return xs.instance}
xs.prototype.requestComplete=function(a,b){b&&(this.i=!0);a=this.removeParams(a);this.h.get(a)||this.h.set(a,b)};
xs.prototype.isEndpointCFR=function(a){a=this.removeParams(a);return(a=this.h.get(a))?!1:a===!1&&this.i?!0:null};
xs.prototype.removeParams=function(a){return a.split("?")[0]};
xs.prototype.removeParams=xs.prototype.removeParams;xs.prototype.isEndpointCFR=xs.prototype.isEndpointCFR;xs.prototype.requestComplete=xs.prototype.requestComplete;xs.getInstance=ys;function zs(){ei.call(this);var a=this;this.j=!1;this.h=Vj();this.h.listen("networkstatus-online",function(){if(a.j&&S("offline_error_handling")){var b=vs().get("errors",!0);if(b){for(var c in b)if(b[c]){var d=new T(c,"sent via offline_errors");d.name=b[c].name;d.stack=b[c].stack;d.level=b[c].level;Nm(d)}vs().set("errors",{},2592E3,!0)}}})}
v(zs,ei);function As(){if(!zs.instance){var a=F("yt.networkStatusManager.instance")||new zs;E("yt.networkStatusManager.instance",a);zs.instance=a}return zs.instance}
p=zs.prototype;p.ta=function(){return this.h.ta()};
p.mb=function(a){this.h.h=a};
p.Ae=function(){var a=window.navigator.onLine;return a===void 0?!0:a};
p.qe=function(){this.j=!0};
p.listen=function(a,b){return this.h.listen(a,b)};
p.Fc=function(a){a=Tj(this.h,a);a.then(function(b){S("use_cfr_monitor")&&ys().requestComplete("generate_204",b)});
return a};
zs.prototype.sendNetworkCheckRequest=zs.prototype.Fc;zs.prototype.listen=zs.prototype.listen;zs.prototype.enableErrorFlushing=zs.prototype.qe;zs.prototype.getWindowStatus=zs.prototype.Ae;zs.prototype.networkStatusHint=zs.prototype.mb;zs.prototype.isNetworkAvailable=zs.prototype.ta;zs.getInstance=As;function Bs(a){a=a===void 0?{}:a;ei.call(this);var b=this;this.h=this.u=0;this.j=As();var c=F("yt.networkStatusManager.instance.listen").bind(this.j);c&&(a.rateLimit?(this.rateLimit=a.rateLimit,c("networkstatus-online",function(){Cs(b,"publicytnetworkstatus-online")}),c("networkstatus-offline",function(){Cs(b,"publicytnetworkstatus-offline")})):(c("networkstatus-online",function(){fi(b,"publicytnetworkstatus-online")}),c("networkstatus-offline",function(){fi(b,"publicytnetworkstatus-offline")})))}
v(Bs,ei);Bs.prototype.ta=function(){var a=F("yt.networkStatusManager.instance.isNetworkAvailable");return a?a.bind(this.j)():!0};
Bs.prototype.mb=function(a){var b=F("yt.networkStatusManager.instance.networkStatusHint").bind(this.j);b&&b(a)};
Bs.prototype.Fc=function(a){var b=this,c;return B(function(d){c=F("yt.networkStatusManager.instance.sendNetworkCheckRequest").bind(b.j);return S("skip_network_check_if_cfr")&&ys().isEndpointCFR("generate_204")?d.return(new Promise(function(e){var f;b.mb(((f=window.navigator)==null?void 0:f.onLine)||!0);e(b.ta())})):c?d.return(c(a)):d.return(!0)})};
function Cs(a,b){a.rateLimit?a.h?(Wj.qa(a.u),a.u=Wj.pa(function(){a.o!==b&&(fi(a,b),a.o=b,a.h=V())},a.rateLimit-(V()-a.h))):(fi(a,b),a.o=b,a.h=V()):fi(a,b)}
;var Ds;function Es(){var a=Pr.call;Ds||(Ds=new Bs({Rh:!0,Hh:!0}));a.call(Pr,this,{ga:{he:is,xb:hs,xd:ds,Le:es,ed:gs,set:bs},fa:Ds,handleError:function(b,c,d){var e,f=d==null?void 0:(e=d.error)==null?void 0:e.code;if(f===400||f===415){var g;b=new T(b.message,c,d==null?void 0:(g=d.error)==null?void 0:g.code);Om(b,void 0,void 0,void 0,!0)}else Nm(b)},
zb:Om,sendFn:Fs,now:V,Vd:ws,Ca:Uo(),dd:"publicytnetworkstatus-online",Zc:"publicytnetworkstatus-offline",qc:!0,nc:.1,Bc:hn("potential_esf_error_limit",10),W:S,Sb:!(lo()&&Gs())});this.j=new yj;S("networkless_immediately_drop_all_requests")&&js();Bq("LogsDatabaseV2")}
v(Es,Pr);function Hs(){var a=F("yt.networklessRequestController.instance");a||(a=new Es,E("yt.networklessRequestController.instance",a),S("networkless_logging")&&qq().then(function(b){a.V=b;Rr(a);a.j.resolve();a.qc&&Math.random()<=a.nc&&a.V&&ps(a.V);S("networkless_immediately_drop_sw_health_store")&&Is(a)}));
return a}
Es.prototype.writeThenSend=function(a,b){b||(b={});b=Js(a,b);lo()||(this.h=!1);Pr.prototype.writeThenSend.call(this,a,b)};
Es.prototype.sendThenWrite=function(a,b,c){b||(b={});b=Js(a,b);lo()||(this.h=!1);Pr.prototype.sendThenWrite.call(this,a,b,c)};
Es.prototype.sendAndWrite=function(a,b){b||(b={});b=Js(a,b);lo()||(this.h=!1);Pr.prototype.sendAndWrite.call(this,a,b)};
Es.prototype.awaitInitialization=function(){return this.j.promise};
function Is(a){var b;B(function(c){if(!a.V)throw b=vp("clearSWHealthLogsDb"),b;return c.return(qs(a.V).catch(function(d){a.handleError(d)}))})}
function Fs(a,b,c,d){d=d===void 0?!1:d;b=S("web_fp_via_jspb")?Object.assign({},b):b;S("use_cfr_monitor")&&Ks(a,b);if(S("use_request_time_ms_header"))b.headers&&Zm(a)&&(b.headers["X-Goog-Request-Time"]=JSON.stringify(Math.round(V())));else{var e;if((e=b.postParams)==null?0:e.requestTimeMs)b.postParams.requestTimeMs=Math.round(V())}if(c&&Object.keys(b).length===0){var f=f===void 0?"":f;var g=g===void 0?!1:g;var h=h===void 0?!1:h;if(a)if(f)nn(a,void 0,"POST",f,void 0);else if(R("USE_NET_AJAX_FOR_PING_TRANSPORT",
!1)||h)nn(a,void 0,"GET","",void 0,void 0,g,h);else{b:{try{c:{var k=new cb({url:a});if(k.h.dsh==="1")var l=null;else{var m=k.h.ae;if(m==="1"){var n=k.h.adurl;if(n)try{l={version:3,oe:decodeURIComponent(n),de:ab(k.i,"act=1","ri=1",db(k))};break c}catch(Z){}}l=m==="2"?{version:4,oe:ab(k.i,"dct=1","suid="+k.j,""),de:ab(k.i,"act=1","ri=1","suid="+k.j)}:null}}if(l){var r=jc(a),t;if(!(t=!r||!r.endsWith("/aclk"))){var w=a.search(rc),x=qc(a,0,"ri",w);if(x<0)var z=null;else{var G=a.indexOf("&",x);if(G<0||
G>w)G=w;z=dc(a.slice(x+3,G!==-1?G:0))}t=z!=="1"}var H=!t;break b}}catch(Z){}H=!1}if(H){b:{try{if(window.navigator&&window.navigator.sendBeacon&&window.navigator.sendBeacon(a,"")){var U=!0;break b}}catch(Z){}U=!1}c=U?!0:!1}else c=!1;c||ts(a)}}else b.compress?b.postBody?(typeof b.postBody!=="string"&&(b.postBody=JSON.stringify(b.postBody)),Er(a,b.postBody,b,rn,d)):Er(a,JSON.stringify(b.postParams),b,qn,d):rn(a,b)}
function Js(a,b){S("use_event_time_ms_header")&&Zm(a)&&(b.headers||(b.headers={}),b.headers["X-Goog-Event-Time"]=JSON.stringify(Math.round(V())));return b}
function Ks(a,b){var c=b.onError?b.onError:function(){};
b.onError=function(e,f){ys().requestComplete(a,!1);c(e,f)};
var d=b.onSuccess?b.onSuccess:function(){};
b.onSuccess=function(e,f){ys().requestComplete(a,!0);d(e,f)}}
function Gs(){return ic(document.location.toString())!=="www.youtube-nocookie.com"}
;var Ls=!1,Ms=D.ytNetworklessLoggingInitializationOptions||{isNwlInitialized:Ls};E("ytNetworklessLoggingInitializationOptions",Ms);function Ns(){var a;B(function(b){if(b.h==1)return b.yield(qq(),2);a=b.i;if(!a||!lo()&&!S("nwl_init_require_datasync_id_killswitch")||!Gs())return b.B(0);Ls=!0;Ms.isNwlInitialized=Ls;return b.yield(Hs().awaitInitialization(),0)})}
;function Os(a){var b=this;this.config_=null;a?this.config_=a:Sq()&&(this.config_=Tq());oo(function(){Nr(b)},5E3)}
Os.prototype.isReady=function(){!this.config_&&Sq()&&(this.config_=Tq());return!!this.config_};
function Or(a,b,c,d){function e(n){n=n===void 0?!1:n;var r;if(d.retry&&h!="www.youtube-nocookie.com"&&(n||S("skip_ls_gel_retry")||g.headers["Content-Type"]!=="application/json"||(r=Lr(b,c,l,k)),r)){var t=g.onSuccess,w=g.onFetchSuccess;g.onSuccess=function(G,H){Mr(r);t(G,H)};
c.onFetchSuccess=function(G,H){Mr(r);w(G,H)}}try{if(n&&d.retry&&!d.networklessOptions.bypassNetworkless)g.method="POST",d.networklessOptions.writeThenSend?Hs().writeThenSend(m,g):Hs().sendAndWrite(m,g);
else if(d.compress){var x=!d.networklessOptions.writeThenSend;if(g.postBody){var z=g.postBody;typeof z!=="string"&&(z=JSON.stringify(g.postBody));Er(m,z,g,rn,x)}else Er(m,JSON.stringify(g.postParams),g,qn,x)}else S("web_all_payloads_via_jspb")?rn(m,g):qn(m,g)}catch(G){if(G.name==="InvalidAccessError")r&&(Mr(r),r=0),Om(Error("An extension is blocking network request."));else throw G;}r&&oo(function(){Nr(a)},5E3)}
!R("VISITOR_DATA")&&b!=="visitor_id"&&Math.random()<.01&&Om(new T("Missing VISITOR_DATA when sending innertube request.",b,c,d));if(!a.isReady()){var f=new T("innertube xhrclient not ready",b,c,d);Nm(f);throw f;}var g={headers:d.headers||{},method:"POST",postParams:c,postBody:d.postBody,postBodyFormat:d.postBodyFormat||"JSON",onTimeout:function(){d.onTimeout()},
onFetchTimeout:d.onTimeout,onSuccess:function(n,r){if(d.onSuccess)d.onSuccess(r)},
onFetchSuccess:function(n){if(d.onSuccess)d.onSuccess(n)},
onProgress:function(n){if(d.onProgress)d.onProgress(n)},
onError:function(n,r){if(d.onError)d.onError(r)},
onFetchError:function(n){if(d.onError)d.onError(n)},
timeout:d.timeout,withCredentials:!0,compress:d.compress};g.headers["Content-Type"]||(g.headers["Content-Type"]="application/json");var h="";(f=a.config_.Ge)&&(h=f);var k=a.config_.He||!1,l=Vq(k,h,d);Object.assign(g.headers,l);g.headers.Authorization&&!h&&k&&(g.headers["x-origin"]=window.location.origin);var m=Xm(""+h+("/youtubei/"+a.config_.innertubeApiVersion+"/"+b),{alt:"json"});(F("ytNetworklessLoggingInitializationOptions")?Ms.isNwlInitialized:Ls)?oq().then(function(n){e(n)}):e(!1)}
;var Ps=0,Qs=jd?"webkit":id?"moz":gd?"ms":fd?"o":"";E("ytDomDomGetNextId",F("ytDomDomGetNextId")||function(){return++Ps});var Rs={stopImmediatePropagation:1,stopPropagation:1,preventMouseEvent:1,preventManipulation:1,preventDefault:1,layerX:1,layerY:1,screenX:1,screenY:1,scale:1,rotation:1,webkitMovementX:1,webkitMovementY:1};
function Ss(a){this.type="";this.state=this.source=this.data=this.currentTarget=this.relatedTarget=this.target=null;this.charCode=this.keyCode=0;this.metaKey=this.shiftKey=this.ctrlKey=this.altKey=!1;this.rotation=this.clientY=this.clientX=0;this.scale=1;this.changedTouches=this.touches=null;try{if(a=a||window.event){this.event=a;for(var b in a)b in Rs||(this[b]=a[b]);this.scale=a.scale;this.rotation=a.rotation;var c=a.target||a.srcElement;c&&c.nodeType==3&&(c=c.parentNode);this.target=c;var d=a.relatedTarget;
if(d)try{d=d.nodeName?d:null}catch(e){d=null}else this.type=="mouseover"?d=a.fromElement:this.type=="mouseout"&&(d=a.toElement);this.relatedTarget=d;this.clientX=a.clientX!=void 0?a.clientX:a.pageX;this.clientY=a.clientY!=void 0?a.clientY:a.pageY;this.keyCode=a.keyCode?a.keyCode:a.which;this.charCode=a.charCode||(this.type=="keypress"?this.keyCode:0);this.altKey=a.altKey;this.ctrlKey=a.ctrlKey;this.shiftKey=a.shiftKey;this.metaKey=a.metaKey;this.h=a.pageX;this.i=a.pageY}}catch(e){}}
function Xs(a){if(document.body&&document.documentElement){var b=document.body.scrollTop+document.documentElement.scrollTop;a.h=a.clientX+(document.body.scrollLeft+document.documentElement.scrollLeft);a.i=a.clientY+b}}
Ss.prototype.preventDefault=function(){this.event&&(this.event.returnValue=!1,this.event.preventDefault&&this.event.preventDefault())};
Ss.prototype.stopPropagation=function(){this.event&&(this.event.cancelBubble=!0,this.event.stopPropagation&&this.event.stopPropagation())};
Ss.prototype.stopImmediatePropagation=function(){this.event&&(this.event.cancelBubble=!0,this.event.stopImmediatePropagation&&this.event.stopImmediatePropagation())};var vg=D.ytEventsEventsListeners||{};E("ytEventsEventsListeners",vg);var Ys=D.ytEventsEventsCounter||{count:0};E("ytEventsEventsCounter",Ys);
function Zs(a,b,c,d){d=d===void 0?{}:d;a.addEventListener&&(b!="mouseenter"||"onmouseenter"in document?b!="mouseleave"||"onmouseenter"in document?b=="mousewheel"&&"MozBoxSizing"in document.documentElement.style&&(b="MozMousePixelScroll"):b="mouseout":b="mouseover");return ug(function(e){var f=typeof e[4]==="boolean"&&e[4]==!!d,g=Ma(e[4])&&Ma(d)&&zg(e[4],d);return!!e.length&&e[0]==a&&e[1]==b&&e[2]==c&&(f||g)})}
function $s(a,b,c,d){d=d===void 0?{}:d;if(!a||!a.addEventListener&&!a.attachEvent)return"";var e=Zs(a,b,c,d);if(e)return e;e=++Ys.count+"";var f=!(b!="mouseenter"&&b!="mouseleave"||!a.addEventListener||"onmouseenter"in document);var g=f?function(h){h=new Ss(h);if(!Jg(h.relatedTarget,function(k){return k==a}))return h.currentTarget=a,h.type=b,c.call(a,h)}:function(h){h=new Ss(h);
h.currentTarget=a;return c.call(a,h)};
g=Mm(g);a.addEventListener?(b=="mouseenter"&&f?b="mouseover":b=="mouseleave"&&f?b="mouseout":b=="mousewheel"&&"MozBoxSizing"in document.documentElement.style&&(b="MozMousePixelScroll"),at()||typeof d==="boolean"?a.addEventListener(b,g,d):a.addEventListener(b,g,!!d.capture)):a.attachEvent("on"+b,g);vg[e]=[a,b,c,g,d];return e}
function bt(a){a&&(typeof a=="string"&&(a=[a]),Pb(a,function(b){if(b in vg){var c=vg[b],d=c[0],e=c[1],f=c[3];c=c[4];d.removeEventListener?at()||typeof c==="boolean"?d.removeEventListener(e,f,c):d.removeEventListener(e,f,!!c.capture):d.detachEvent&&d.detachEvent("on"+e,f);delete vg[b]}}))}
var at=ui(function(){var a=!1;try{var b=Object.defineProperty({},"capture",{get:function(){a=!0}});
window.addEventListener("test",null,b)}catch(c){}return a});function ct(a){this.G=a;this.h=null;this.o=0;this.A=null;this.u=0;this.i=[];for(a=0;a<4;a++)this.i.push(0);this.j=0;this.U=$s(window,"mousemove",Va(this.Y,this));a=Va(this.M,this);typeof a==="function"&&(a=Mm(a));this.Z=window.setInterval(a,25)}
Za(ct,I);ct.prototype.Y=function(a){a.h===void 0&&Xs(a);var b=a.h;a.i===void 0&&Xs(a);this.h=new qg(b,a.i)};
ct.prototype.M=function(){if(this.h){var a=V();if(this.o!=0){var b=this.A,c=this.h,d=b.x-c.x;b=b.y-c.y;d=Math.sqrt(d*d+b*b)/(a-this.o);this.i[this.j]=Math.abs((d-this.u)/this.u)>.5?1:0;for(c=b=0;c<4;c++)b+=this.i[c]||0;b>=3&&this.G();this.u=d}this.o=a;this.A=this.h;this.j=(this.j+1)%4}};
ct.prototype.ba=function(){window.clearInterval(this.Z);bt(this.U)};var dt={};
function et(a){var b=a===void 0?{}:a;a=b.Xe===void 0?!1:b.Xe;b=b.re===void 0?!0:b.re;if(F("_lact",window)==null){var c=parseInt(R("LACT"),10);c=isFinite(c)?Date.now()-Math.max(c,0):-1;E("_lact",c,window);E("_fact",c,window);c==-1&&ft();$s(document,"keydown",ft);$s(document,"keyup",ft);$s(document,"mousedown",ft);$s(document,"mouseup",ft);a?$s(window,"touchmove",function(){gt("touchmove",200)},{passive:!0}):($s(window,"resize",function(){gt("resize",200)}),b&&$s(window,"scroll",function(){gt("scroll",200)}));
new ct(function(){gt("mouse",100)});
$s(document,"touchstart",ft,{passive:!0});$s(document,"touchend",ft,{passive:!0})}}
function gt(a,b){dt[a]||(dt[a]=!0,Wj.pa(function(){ft();dt[a]=!1},b))}
function ft(){F("_lact",window)==null&&et();var a=Date.now();E("_lact",a,window);F("_fact",window)==-1&&E("_fact",a,window);(a=F("ytglobal.ytUtilActivityCallback_"))&&a()}
function ht(){var a=F("_lact",window);return a==null?-1:Math.max(Date.now()-a,0)}
;var jt=D.ytPubsubPubsubInstance||new N,kt=D.ytPubsubPubsubSubscribedKeys||{},lt=D.ytPubsubPubsubTopicToKeys||{},mt=D.ytPubsubPubsubIsSynchronous||{};function nt(a,b){var c=ot();if(c&&b){var d=c.subscribe(a,function(){function e(){kt[d]&&b.apply&&typeof b.apply=="function"&&b.apply(window,f)}
var f=arguments;try{mt[a]?e():en(e,0)}catch(g){Nm(g)}},void 0);
kt[d]=!0;lt[a]||(lt[a]=[]);lt[a].push(d);return d}return 0}
function pt(a){var b=ot();b&&(typeof a==="number"?a=[a]:typeof a==="string"&&(a=[parseInt(a,10)]),Pb(a,function(c){b.unsubscribeByKey(c);delete kt[c]}))}
function qt(a,b){var c=ot();c&&c.publish.apply(c,arguments)}
function rt(a){var b=ot();if(b)if(b.clear(a),a)st(a);else for(var c in lt)st(c)}
function ot(){return D.ytPubsubPubsubInstance}
function st(a){lt[a]&&(a=lt[a],Pb(a,function(b){kt[b]&&delete kt[b]}),a.length=0)}
N.prototype.subscribe=N.prototype.subscribe;N.prototype.unsubscribeByKey=N.prototype.fc;N.prototype.publish=N.prototype.sb;N.prototype.clear=N.prototype.clear;E("ytPubsubPubsubInstance",jt);E("ytPubsubPubsubTopicToKeys",lt);E("ytPubsubPubsubIsSynchronous",mt);E("ytPubsubPubsubSubscribedKeys",kt);var tt=Symbol("injectionDeps");function ut(a){this.name=a}
ut.prototype.toString=function(){return"InjectionToken("+this.name+")"};
function vt(a){this.key=a}
function wt(a){return new vt(a)}
function xt(){this.i=new Map;this.j=new Map;this.h=new Map}
function zt(a,b){a.i.set(b.pb,b);var c=a.j.get(b.pb);if(c)try{c.ai(a.resolve(b.pb))}catch(d){c.Yh(d)}}
xt.prototype.resolve=function(a){return a instanceof vt?At(this,a.key,[],!0):At(this,a,[])};
function At(a,b,c,d){d=d===void 0?!1:d;if(c.indexOf(b)>-1)throw Error("Deps cycle for: "+b);if(a.h.has(b))return a.h.get(b);if(!a.i.has(b)){if(d)return;throw Error("No provider for: "+b);}d=a.i.get(b);c.push(b);if(d.nd!==void 0)var e=d.nd;else if(d.Ff)e=d[tt]?Bt(a,d[tt],c):[],e=d.Ff.apply(d,A(e));else if(d.Ic){e=d.Ic;var f=e[tt]?Bt(a,e[tt],c):[];e=new (Function.prototype.bind.apply(e,[null].concat(A(f))))}else throw Error("Could not resolve providers for: "+b);c.pop();d.hi||a.h.set(b,e);return e}
function Bt(a,b,c){return b?b.map(function(d){return d instanceof vt?At(a,d.key,c,!0):At(a,d,c)}):[]}
;var Ct;function Dt(){Ct||(Ct=new xt);return Ct}
;var Et=window;function Ft(){var a,b;return"h5vcc"in Et&&((a=Et.h5vcc.traceEvent)==null?0:a.traceBegin)&&((b=Et.h5vcc.traceEvent)==null?0:b.traceEnd)?1:"performance"in Et&&Et.performance.mark&&Et.performance.measure?2:0}
function Gt(a){var b=Ft();switch(b){case 1:Et.h5vcc.traceEvent.traceBegin("YTLR",a);break;case 2:Et.performance.mark(a+"-start");break;case 0:break;default:Bb(b,"unknown trace type")}}
function Ht(a){var b=Ft();switch(b){case 1:Et.h5vcc.traceEvent.traceEnd("YTLR",a);break;case 2:b=a+"-start";var c=a+"-end";Et.performance.mark(c);Et.performance.measure(a,b,c);break;case 0:break;default:Bb(b,"unknown trace type")}}
;var It=S("web_enable_lifecycle_monitoring")&&Ft()!==0,Jt=S("web_enable_lifecycle_monitoring");function Kt(a){var b,c;(c=(b=window).onerror)==null||c.call(b,a.message,"",0,0,a)}
;function Lt(a){var b=this;var c=c===void 0?0:c;var d=d===void 0?Uo():d;this.j=c;this.scheduler=d;this.i=new yj;this.h=a;for(a={jb:0};a.jb<this.h.length;a={Ac:void 0,jb:a.jb},a.jb++)a.Ac=this.h[a.jb],c=function(e){return function(){e.Ac.Sc();b.h[e.jb].Cc=!0;b.h.every(function(f){return f.Cc===!0})&&b.i.resolve()}}(a),d=this.getPriority(a.Ac),d=this.scheduler.Sa(c,d),this.h[a.jb]=Object.assign({},a.Ac,{Sc:c,
jobId:d})}
function Mt(a){var b=Array.from(a.h.keys()).sort(function(d,e){return a.getPriority(a.h[e])-a.getPriority(a.h[d])});
b=y(b);for(var c=b.next();!c.done;c=b.next())c=a.h[c.value],c.jobId===void 0||c.Cc||(a.scheduler.qa(c.jobId),a.scheduler.Sa(c.Sc,10))}
Lt.prototype.cancel=function(){for(var a=y(this.h),b=a.next();!b.done;b=a.next())b=b.value,b.jobId===void 0||b.Cc||this.scheduler.qa(b.jobId),b.Cc=!0;this.i.resolve()};
Lt.prototype.getPriority=function(a){var b;return(b=a.priority)!=null?b:this.j};function Nt(a){this.state=a;this.plugins=[];this.o=void 0;this.A={};It&&Gt(this.state)}
p=Nt.prototype;p.install=function(a){this.plugins.push(a);return this};
p.uninstall=function(){var a=this;C.apply(0,arguments).forEach(function(b){b=a.plugins.indexOf(b);b>-1&&a.plugins.splice(b,1)})};
p.transition=function(a,b){var c=this;It&&Ht(this.state);var d=this.transitions.find(function(f){return Array.isArray(f.from)?f.from.find(function(g){return g===c.state&&f.to===a}):f.from===c.state&&f.to===a});
if(d){this.j&&(Mt(this.j),this.j=void 0);Ot(this,a,b);this.state=a;It&&Gt(this.state);d=d.action.bind(this);var e=this.plugins.filter(function(f){return f[a]}).map(function(f){return f[a]});
d(Pt(this,e),b)}else throw Error("no transition specified from "+this.state+" to "+a);};
function Pt(a,b){var c=b.filter(function(e){return Qt(a,e)===10}),d=b.filter(function(e){return Qt(a,e)!==10});
return a.A.gi?function(){var e=C.apply(0,arguments);return B(function(f){if(f.h==1)return f.yield(a.df.apply(a,[c].concat(A(e))),2);a.Nd.apply(a,[d].concat(A(e)));f.h=0})}:function(){var e=C.apply(0,arguments);
a.ef.apply(a,[c].concat(A(e)));a.Nd.apply(a,[d].concat(A(e)))}}
p.ef=function(a){for(var b=C.apply(1,arguments),c=Uo(),d=y(a),e=d.next(),f={};!e.done;f={Ub:void 0},e=d.next())f.Ub=e.value,c.Lb(function(g){return function(){Rt(g.Ub.name);St(function(){return g.Ub.callback.apply(g.Ub,A(b))});
Tt(g.Ub.name)}}(f))};
p.df=function(a){var b=C.apply(1,arguments),c,d,e,f,g;return B(function(h){h.h==1&&(c=Uo(),d=y(a),e=d.next(),f={});if(h.h!=3){if(e.done)return h.B(0);f.Ya=e.value;f.hc=void 0;g=function(k){return function(){Rt(k.Ya.name);var l=St(function(){return k.Ya.callback.apply(k.Ya,A(b))});
ie(l)?k.hc=S("web_lifecycle_error_handling_killswitch")?l.then(function(){Tt(k.Ya.name)}):l.then(function(){Tt(k.Ya.name)},function(m){Kt(m);
Tt(k.Ya.name)}):Tt(k.Ya.name)}}(f);
c.Lb(g);return f.hc?h.yield(f.hc,3):h.B(3)}f={Ya:void 0,hc:void 0};e=d.next();return h.B(2)})};
p.Nd=function(a){var b=C.apply(1,arguments),c=this,d=a.map(function(e){return{Sc:function(){Rt(e.name);St(function(){return e.callback.apply(e,A(b))});
Tt(e.name)},
priority:Qt(c,e)}});
d.length&&(this.j=new Lt(d))};
function Qt(a,b){var c,d;return(d=(c=a.o)!=null?c:b.priority)!=null?d:0}
function Rt(a){It&&a&&Gt(a)}
function Tt(a){It&&a&&Ht(a)}
function Ot(a,b,c){Jt&&console.groupCollapsed&&console.groupEnd&&(console.groupCollapsed("["+a.constructor.name+"] '"+a.state+"' to '"+b+"'"),console.log("with message: ",c),console.groupEnd())}
ea.Object.defineProperties(Nt.prototype,{currentState:{configurable:!0,enumerable:!0,get:function(){return this.state}}});
function St(a){if(S("web_lifecycle_error_handling_killswitch"))return a();try{return a()}catch(b){Kt(b)}}
;function Ut(a){Nt.call(this,a===void 0?"none":a);this.h=null;this.o=10;this.transitions=[{from:"none",to:"application_navigating",action:this.i},{from:"application_navigating",to:"none",action:this.u},{from:"application_navigating",to:"application_navigating",action:function(){}},
{from:"none",to:"none",action:function(){}}]}
var Vt;v(Ut,Nt);Ut.prototype.i=function(a,b){var c=this;this.h=oo(function(){c.currentState==="application_navigating"&&c.transition("none")},5E3);
a(b==null?void 0:b.event)};
Ut.prototype.u=function(a,b){this.h&&(Wj.qa(this.h),this.h=null);a(b==null?void 0:b.event)};
function Wt(){Vt||(Vt=new Ut);return Vt}
;var Xt=[];E("yt.logging.transport.getScrapedGelPayloads",function(){return Xt});function Yt(){this.store={};this.h={}}
Yt.prototype.storePayload=function(a,b){a=Zt(a);this.store[a]?this.store[a].push(b):(this.h={},this.store[a]=[b]);S("more_accurate_gel_parser")&&(b=new CustomEvent("TRANSPORTING_NEW_EVENT"),window.dispatchEvent(b));return a};
Yt.prototype.smartExtractMatchingEntries=function(a){if(!a.keys.length)return[];for(var b=$t(this,a.keys.splice(0,1)[0]),c=[],d=0;d<b.length;d++)this.store[b[d]]&&a.sizeLimit&&(this.store[b[d]].length<=a.sizeLimit?(c.push.apply(c,A(this.store[b[d]])),delete this.store[b[d]]):c.push.apply(c,A(this.store[b[d]].splice(0,a.sizeLimit))));(a==null?0:a.sizeLimit)&&c.length<(a==null?void 0:a.sizeLimit)&&(a.sizeLimit-=c.length,c.push.apply(c,A(this.smartExtractMatchingEntries(a))));return c};
Yt.prototype.extractMatchingEntries=function(a){a=$t(this,a);for(var b=[],c=0;c<a.length;c++)this.store[a[c]]&&(b.push.apply(b,A(this.store[a[c]])),delete this.store[a[c]]);return b};
Yt.prototype.getSequenceCount=function(a){a=$t(this,a);for(var b=0,c=0;c<a.length;c++){var d=void 0;b+=((d=this.store[a[c]])==null?void 0:d.length)||0}return b};
function $t(a,b){var c=Zt(b);if(a.h[c])return a.h[c];var d=Object.keys(a.store)||[];if(d.length<=1&&Zt(b)===d[0])return d;for(var e=[],f=0;f<d.length;f++){var g=d[f].split("/");if(au(b.auth,g[0])){var h=b.isJspb;au(h===void 0?"undefined":h?"true":"false",g[1])&&au(b.cttAuthInfo,g[2])&&(h=b.tier,h=h===void 0?"undefined":JSON.stringify(h),au(h,g[3])&&e.push(d[f]))}}return a.h[c]=e}
function au(a,b){return a===void 0||a==="undefined"?!0:a===b}
Yt.prototype.getSequenceCount=Yt.prototype.getSequenceCount;Yt.prototype.extractMatchingEntries=Yt.prototype.extractMatchingEntries;Yt.prototype.smartExtractMatchingEntries=Yt.prototype.smartExtractMatchingEntries;Yt.prototype.storePayload=Yt.prototype.storePayload;function Zt(a){return[a.auth===void 0?"undefined":a.auth,a.isJspb===void 0?"undefined":a.isJspb,a.cttAuthInfo===void 0?"undefined":a.cttAuthInfo,a.tier===void 0?"undefined":a.tier].join("/")}
;function bu(a,b){if(a)return a[b.name]}
;var cu=hn("initial_gel_batch_timeout",2E3),du=hn("gel_queue_timeout_max_ms",6E4),eu=hn("gel_min_batch_size",5),fu=void 0;function gu(){this.o=this.h=this.i=0;this.j=!1}
var hu=new gu,iu=new gu,ju=new gu,ku=new gu,lu,mu=!0,nu=D.ytLoggingTransportTokensToCttTargetIds_||{};E("ytLoggingTransportTokensToCttTargetIds_",nu);var ou={};function pu(){var a=F("yt.logging.ims");a||(a=new Yt,E("yt.logging.ims",a));return a}
function qu(a,b){if(a.endpoint==="log_event"){ru(a);var c=su(a),d=tu(a.payload)||"";a:{if(S("enable_web_tiered_gel")){var e=ks[d||""];var f,g,h,k=Dt().resolve(wt(Nq))==null?void 0:(f=Oq())==null?void 0:(g=f.loggingHotConfig)==null?void 0:(h=g.eventLoggingConfig)==null?void 0:h.payloadPolicies;if(k)for(f=0;f<k.length;f++)if(k[f].payloadNumber===e){e=k[f];break a}}e=void 0}k=200;if(e){if(e.enabled===!1&&!S("web_payload_policy_disabled_killswitch"))return;k=uu(e.tier);if(k===400){vu(a,b);return}}ou[c]=
!0;c={cttAuthInfo:c,isJspb:!1,tier:k};pu().storePayload(c,a.payload);wu(b,c,d==="gelDebuggingEvent")}}
function wu(a,b,c){function d(){xu({writeThenSend:!0},void 0,e,b.tier)}
var e=!1;e=e===void 0?!1:e;c=c===void 0?!1:c;a&&(fu=new a);a=hn("tvhtml5_logging_max_batch_ads_fork")||hn("tvhtml5_logging_max_batch")||hn("web_logging_max_batch")||100;var f=V(),g=yu(e,b.tier),h=g.o;c&&(g.j=!0);c=0;b&&(c=pu().getSequenceCount(b));c>=1E3?d():c>=a?lu||(lu=zu(function(){d();lu=void 0},0)):f-h>=10&&(Au(e,b.tier),g.o=f)}
function vu(a,b){if(a.endpoint==="log_event"){S("more_accurate_gel_parser")&&pu().storePayload({isJspb:!1},a.payload);ru(a);var c=su(a),d=new Map;d.set(c,[a.payload]);var e=tu(a.payload)||"";b&&(fu=new b);return new vi(function(f,g){fu&&fu.isReady()?Bu(d,fu,f,g,{bypassNetworkless:!0},!0,e==="gelDebuggingEvent"):f()})}}
function su(a){var b="";if(a.dangerousLogToVisitorSession)b="visitorOnlyApprovedKey";else if(a.cttAuthInfo){b=a.cttAuthInfo;var c={};b.videoId?c.videoId=b.videoId:b.playlistId&&(c.playlistId=b.playlistId);nu[a.cttAuthInfo.token]=c;b=a.cttAuthInfo.token}return b}
function xu(a,b,c,d){a=a===void 0?{}:a;c=c===void 0?!1:c;new vi(function(e,f){var g=yu(c,d),h=g.j;g.j=!1;Cu(g.i);Cu(g.h);g.h=0;fu&&fu.isReady()?d===void 0&&S("enable_web_tiered_gel")?Du(e,f,a,b,c,300,h):Du(e,f,a,b,c,d,h):(Au(c,d),e())})}
function Du(a,b,c,d,e,f,g){var h=fu;c=c===void 0?{}:c;e=e===void 0?!1:e;f=f===void 0?200:f;g=g===void 0?!1:g;var k=new Map,l={isJspb:e,cttAuthInfo:d,tier:f};e={isJspb:e,cttAuthInfo:d};if(d!==void 0)f=S("enable_web_tiered_gel")?pu().smartExtractMatchingEntries({keys:[l,e],sizeLimit:1E3}):pu().extractMatchingEntries(e),k.set(d,f);else for(d=y(Object.keys(ou)),l=d.next();!l.done;l=d.next())l=l.value,e=S("enable_web_tiered_gel")?pu().smartExtractMatchingEntries({keys:[{isJspb:!1,cttAuthInfo:l,tier:f},
{isJspb:!1,cttAuthInfo:l}],sizeLimit:1E3}):pu().extractMatchingEntries({isJspb:!1,cttAuthInfo:l}),e.length>0&&k.set(l,e),(S("web_fp_via_jspb_and_json")&&c.writeThenSend||!S("web_fp_via_jspb_and_json"))&&delete ou[l];Bu(k,h,a,b,c,!1,g)}
function Au(a,b){function c(){xu({writeThenSend:!0},void 0,a,b)}
a=a===void 0?!1:a;b=b===void 0?200:b;var d=yu(a,b),e=d===ku||d===ju?5E3:du;S("web_gel_timeout_cap")&&!d.h&&(e=zu(function(){c()},e),d.h=e);
Cu(d.i);e=R("LOGGING_BATCH_TIMEOUT",hn("web_gel_debounce_ms",1E4));S("shorten_initial_gel_batch_timeout")&&mu&&(e=cu);e=zu(function(){hn("gel_min_batch_size")>0?pu().getSequenceCount({cttAuthInfo:void 0,isJspb:a,tier:b})>=eu&&c():c()},e);
d.i=e}
function Bu(a,b,c,d,e,f,g){e=e===void 0?{}:e;var h=Math.round(V()),k=a.size,l=(g===void 0?0:g)&&S("vss_through_gel_video_stats")?"video_stats":"log_event";a=y(a);var m=a.next();for(g={};!m.done;g={Yc:void 0,batchRequest:void 0,dangerousLogToVisitorSession:void 0,cd:void 0,bd:void 0},m=a.next()){var n=y(m.value);m=n.next().value;n=n.next().value;g.batchRequest=Bg({context:Uq(b.config_||Tq())});if(!La(n)&&!S("throw_err_when_logevent_malformed_killswitch")){d();break}g.batchRequest.events=n;(n=nu[m])&&
Eu(g.batchRequest,m,n);delete nu[m];g.dangerousLogToVisitorSession=m==="visitorOnlyApprovedKey";Fu(g.batchRequest,h,g.dangerousLogToVisitorSession);S("always_send_and_write")&&(e.writeThenSend=!1);g.cd=function(r){S("start_client_gcf")&&Wj.pa(function(){return B(function(t){return t.yield(Gu(r),0)})});
k--;k||c()};
g.Yc=0;g.bd=function(r){return function(){r.Yc++;if(e.bypassNetworkless&&r.Yc===1)try{Or(b,l,r.batchRequest,Hu({writeThenSend:!0},r.dangerousLogToVisitorSession,r.cd,r.bd,f)),mu=!1}catch(t){Nm(t),d()}k--;k||c()}}(g);
try{Or(b,l,g.batchRequest,Hu(e,g.dangerousLogToVisitorSession,g.cd,g.bd,f)),mu=!1}catch(r){Nm(r),d()}}}
function Hu(a,b,c,d,e){a={retry:!0,onSuccess:c,onError:d,networklessOptions:a,dangerousLogToVisitorSession:b,Bh:!!e,headers:{},postBodyFormat:"",postBody:"",compress:S("compress_gel")||S("compress_gel_lr")};Iu()&&(a.headers["X-Goog-Request-Time"]=JSON.stringify(Math.round(V())));return a}
function Fu(a,b,c){Iu()||(a.requestTimeMs=String(b));S("unsplit_gel_payloads_in_logs")&&(a.unsplitGelPayloadsInLogs=!0);!c&&(b=R("EVENT_ID"))&&((c=R("BATCH_CLIENT_COUNTER")||0)||(c=Math.floor(Math.random()*65535/2)),c++,c>65535&&(c=1),Im("BATCH_CLIENT_COUNTER",c),a.serializedClientEventId={serializedEventId:b,clientCounter:String(c)})}
function Eu(a,b,c){if(c.videoId)var d="VIDEO";else if(c.playlistId)d="PLAYLIST";else return;a.credentialTransferTokenTargetId=c;a.context=a.context||{};a.context.user=a.context.user||{};a.context.user.credentialTransferTokens=[{token:b,scope:d}]}
function ru(a){var b=gn("il_payload_scraping");b=(b!==void 0?String(b):"")==="enable_il_payload_scraping";if(!F("yt.logging.transport.enableScrapingForTest"))if(b)Xt=[],E("yt.logging.transport.enableScrapingForTest",!0),E("yt.logging.transport.scrapedPayloadsForTesting",Xt),E("yt.logging.transport.payloadToScrape","visualElementShown visualElementHidden visualElementAttached screenCreated visualElementGestured visualElementStateChanged".split(" ")),E("yt.logging.transport.getScrapedPayloadFromClientEventsFunction"),
E("yt.logging.transport.scrapeClientEvent",!0);else return;b=F("yt.logging.transport.scrapedPayloadsForTesting");var c=F("yt.logging.transport.payloadToScrape"),d=F("yt.logging.transport.scrapeClientEvent");if(c&&c.length>=1)for(var e=0;e<c.length;e++)if(a&&a.payload[c[e]])if(d)b.push(a.payload);else{var f=void 0;b.push(((f=a)==null?void 0:f.payload)[c[e]])}E("yt.logging.transport.scrapedPayloadsForTesting",b)}
function Iu(){return S("use_request_time_ms_header")||S("lr_use_request_time_ms_header")}
function zu(a,b){return S("transport_use_scheduler")===!1?en(a,b):S("logging_avoid_blocking_during_navigation")||S("lr_logging_avoid_blocking_during_navigation")?oo(function(){if(Wt().currentState==="none")a();else{var c={};Wt().install((c.none={callback:a},c))}},b):oo(a,b)}
function Cu(a){S("transport_use_scheduler")?Wj.qa(a):window.clearTimeout(a)}
function Gu(a){var b,c,d,e,f,g,h,k,l,m;return B(function(n){return n.h==1?(d=(b=a)==null?void 0:(c=b.responseContext)==null?void 0:c.globalConfigGroup,e=bu(d,im),g=(f=d)==null?void 0:f.hotHashData,h=bu(d,hm),l=(k=d)==null?void 0:k.coldHashData,(m=Dt().resolve(wt(Nq)))?g?e?n.yield(Pq(m,g,e),2):n.yield(Pq(m,g),2):n.B(2):n.return()):l?h?n.yield(Qq(m,l,h),0):n.yield(Qq(m,l),0):n.B(0)})}
function yu(a,b){b=b===void 0?200:b;return a?b===300?ku:iu:b===300?ju:hu}
function tu(a){a=Object.keys(a);a=y(a);for(var b=a.next();!b.done;b=a.next())if(b=b.value,ks[b])return b}
function uu(a){switch(a){case "DELAYED_EVENT_TIER_UNSPECIFIED":return 0;case "DELAYED_EVENT_TIER_DEFAULT":return 100;case "DELAYED_EVENT_TIER_DISPATCH_TO_EMPTY":return 200;case "DELAYED_EVENT_TIER_FAST":return 300;case "DELAYED_EVENT_TIER_IMMEDIATE":return 400;default:return 200}}
;var Ju=D.ytLoggingGelSequenceIdObj_||{};E("ytLoggingGelSequenceIdObj_",Ju);
function Ku(a,b,c,d){d=d===void 0?{}:d;var e={},f=Math.round(d.timestamp||V());e.eventTimeMs=f<Number.MAX_SAFE_INTEGER?f:0;e[a]=b;a=ht();e.context={lastActivityMs:String(d.timestamp||!isFinite(a)?-1:a)};d.sequenceGroup&&!S("web_gel_sequence_info_killswitch")&&(a=e.context,b=d.sequenceGroup,Ju[b]=b in Ju?Ju[b]+1:0,a.sequence={index:Ju[b],groupKey:b},d.endOfSequence&&delete Ju[d.sequenceGroup]);S("web_tag_automated_log_events")&&(e.context.automatedLogEventSource=d.automatedLogEventSource);(d.sendIsolatedPayload?
vu:qu)({endpoint:"log_event",payload:e,cttAuthInfo:d.cttAuthInfo,dangerousLogToVisitorSession:d.dangerousLogToVisitorSession},c)}
;function dp(a,b,c){c=c===void 0?{}:c;var d=Os;R("ytLoggingEventsDefaultDisabled",!1)&&Os===Os&&(d=null);Ku(a,b,d,c)}
;var Lu=new Set,Mu=0,Nu=0,Ou=0,Pu=[],Qu=[],Ru=["PhantomJS","Googlebot","TO STOP THIS SECURITY SCAN go/scan"];function Su(){Pb(R("ERRORS")||[],function(a){Tu.apply(null,a)});
Im("ERRORS",[])}
function cp(a){Tu(a)}
function Uu(a){Tu(a,"WARNING")}
function Vu(a){a instanceof Error?Tu(a):(a=Ma(a)?JSON.stringify(a):String(a),a=new T(a),a.name="RejectedPromiseError",Uu(a))}
function Wu(a,b,c,d,e,f){b=b===void 0?"Unknown file":b;c=c===void 0?0:c;var g=!1,h=Jm("log_window_onerror_fraction");if(h&&Math.random()<h)g=!0;else{h=document.getElementsByTagName("script");for(var k=0,l=h.length;k<l;k++)if(h[k].src.indexOf("/debug-")>0){g=!0;break}}if(g){g=!1;e?g=!0:(typeof a==="string"?h=a:ErrorEvent&&a instanceof ErrorEvent?(g=!0,h=a.message,b=a.filename,c=a.lineno,d=a.colno):(h="Unknown error",b="Unknown file",c=0),e=new T(h),e.name="UnhandledWindowError",e.message=h,e.fileName=
b,e.lineNumber=c,isNaN(d)?delete e.columnNumber:e.columnNumber=d);if(!S("wiz_enable_component_stack_propagation_killswitch")){a=e;var m;if((m=f)==null||!m.componentStack)if(m=a.ke)f||(f={}),f.componentStack=m}f&&Xu(e,f);g?Tu(e):Uu(e)}}
function Tu(a,b,c,d,e,f,g,h){f=f===void 0?{}:f;f.name=c||R("INNERTUBE_CONTEXT_CLIENT_NAME",1);f.version=d||R("INNERTUBE_CONTEXT_CLIENT_VERSION");c=f;b=b===void 0?"ERROR":b;g=g===void 0?!1:g;b=b===void 0?"ERROR":b;g=g===void 0?!1:g;if(a&&(a.hasOwnProperty("level")&&a.level&&(b=a.level),S("console_log_js_exceptions")&&(d=[],d.push("Name: "+a.name),d.push("Message: "+a.message),a.hasOwnProperty("params")&&d.push("Error Params: "+JSON.stringify(a.params)),a.hasOwnProperty("args")&&d.push("Error args: "+
JSON.stringify(a.args)),d.push("File name: "+a.fileName),d.push("Stacktrace: "+a.stack),d=d.join("\n"),window.console.log(d,a)),!(Mu>=5))){d=[];e=y(Qu);for(f=e.next();!f.done;f=e.next()){f=f.value;try{f()&&d.push(f())}catch(z){}}d=[].concat(A(Pu),A(d));var k=$b(a);e=k.message||"Unknown Error";f=k.name||"UnknownError";var l=k.stack||a.i||"Not available";if(l.startsWith(f+": "+e)){var m=l.split("\n");m.shift();l=m.join("\n")}m=k.lineNumber||"Not available";k=k.fileName||"Not available";var n=0;if(a.hasOwnProperty("args")&&
a.args&&a.args.length)for(var r=0;r<a.args.length&&!(n=Ln(a.args[r],"params."+r,c,n),n>=500);r++);else if(a.hasOwnProperty("params")&&a.params){var t=a.params;if(typeof a.params==="object")for(r in t){if(t[r]){var w="params."+r,x=Nn(t[r]);c[w]=x;n+=w.length+x.length;if(n>500)break}}else c.params=Nn(t)}if(d.length)for(r=0;r<d.length&&!(n=Ln(d[r],"params.context."+r,c,n),n>=500);r++);navigator.vendor&&!c.hasOwnProperty("vendor")&&(c["device.vendor"]=navigator.vendor);r={message:e,name:f,lineNumber:m,
fileName:k,stack:l,params:c,sampleWeight:1};c=Number(a.columnNumber);isNaN(c)||(r.lineNumber=r.lineNumber+":"+c);if(a.level==="IGNORED")a=0;else a:{a=Gn();c=y(a.Za);for(d=c.next();!d.done;d=c.next())if(d=d.value,r.message&&r.message.match(d.Th)){a=d.weight;break a}a=y(a.Ua);for(c=a.next();!c.done;c=a.next())if(c=c.value,c.callback(r)){a=c.weight;break a}a=1}r.sampleWeight=a;a=y(An);for(c=a.next();!c.done;c=a.next())if(c=c.value,c.zc[r.name])for(e=y(c.zc[r.name]),d=e.next();!d.done;d=e.next())if(f=
d.value,d=r.message.match(f.regexp)){r.params["params.error.original"]=d[0];e=f.groups;f={};for(m=0;m<e.length;m++)f[e[m]]=d[m+1],r.params["params.error."+e[m]]=d[m+1];r.message=c.Xc(f);break}r.params||(r.params={});a=Gn();r.params["params.errorServiceSignature"]="msg="+a.Za.length+"&cb="+a.Ua.length;r.params["params.serviceWorker"]="false";D.document&&D.document.querySelectorAll&&(r.params["params.fscripts"]=String(document.querySelectorAll("script:not([nonce])").length));(new Eg(Fg,"sample")).constructor!==
Eg&&(r.params["params.fconst"]="true");window.yterr&&typeof window.yterr==="function"&&window.yterr(r);if(r.sampleWeight!==0&&!Lu.has(r.message)){if(g&&S("web_enable_error_204"))Yu(b===void 0?"ERROR":b,r);else{b=b===void 0?"ERROR":b;b==="ERROR"?(In.sb("handleError",r),S("record_app_crashed_web")&&Ou===0&&r.sampleWeight===1&&(Ou++,g={appCrashType:"APP_CRASH_TYPE_BREAKPAD"},S("report_client_error_with_app_crash_ks")||(g.systemHealth={crashData:{clientError:{logMessage:{message:r.message}}}}),dp("appCrashed",
g)),Nu++):b==="WARNING"&&In.sb("handleWarning",r);if(S("kevlar_gel_error_routing")){g=b;h=h===void 0?{}:h;b:{a=y(Ru);for(c=a.next();!c.done;c=a.next())if(jp(c.value.toLowerCase())){a=!0;break b}a=!1}if(a)h=void 0;else{c={stackTrace:r.stack};r.fileName&&(c.filename=r.fileName);a=r.lineNumber&&r.lineNumber.split?r.lineNumber.split(":"):[];a.length!==0&&(a.length!==1||isNaN(Number(a[0]))?a.length!==2||isNaN(Number(a[0]))||isNaN(Number(a[1]))||(c.lineNumber=Number(a[0]),c.columnNumber=Number(a[1])):c.lineNumber=
Number(a[0]));a={level:"ERROR_LEVEL_UNKNOWN",message:r.message,errorClassName:r.name,sampleWeight:r.sampleWeight};g==="ERROR"?a.level="ERROR_LEVEL_ERROR":g==="WARNING"&&(a.level="ERROR_LEVEL_WARNNING");c={isObfuscated:!0,browserStackInfo:c};h.pageUrl=window.location.href;h.kvPairs=[];R("FEXP_EXPERIMENTS")&&(h.experimentIds=R("FEXP_EXPERIMENTS"));d=R("LATEST_ECATCHER_SERVICE_TRACKING_PARAMS");if(!Jm("web_disable_gel_stp_ecatcher_killswitch")&&d)for(e=y(Object.keys(d)),f=e.next();!f.done;f=e.next())f=
f.value,h.kvPairs.push({key:f,value:String(d[f])});if(d=r.params)for(e=y(Object.keys(d)),f=e.next();!f.done;f=e.next())f=f.value,h.kvPairs.push({key:"client."+f,value:String(d[f])});d=R("SERVER_NAME");e=R("SERVER_VERSION");d&&e&&(h.kvPairs.push({key:"server.name",value:d}),h.kvPairs.push({key:"server.version",value:e}));h={errorMetadata:h,stackTrace:c,logMessage:a}}h&&(dp("clientError",h),(g==="ERROR"||S("errors_flush_gel_always_killswitch"))&&xu(void 0,void 0,!1))}S("suppress_error_204_logging")||
Yu(b,r)}try{Lu.add(r.message)}catch(z){}Mu++}}}
function Yu(a,b){var c=b.params||{};a={urlParams:{a:"logerror",t:"jserror",type:b.name,msg:b.message.substr(0,250),line:b.lineNumber,level:a,"client.name":c.name},postParams:{url:R("PAGE_NAME",window.location.href),file:b.fileName},method:"POST"};c.version&&(a["client.version"]=c.version);if(a.postParams){b.stack&&(a.postParams.stack=b.stack);b=y(Object.keys(c));for(var d=b.next();!d.done;d=b.next())d=d.value,a.postParams["client."+d]=c[d];if(c=R("LATEST_ECATCHER_SERVICE_TRACKING_PARAMS"))for(b=y(Object.keys(c)),
d=b.next();!d.done;d=b.next())d=d.value,a.postParams[d]=c[d];(c=R("LAVA_VERSION"))&&(a.postParams["lava.version"]=c);c=R("SERVER_NAME");b=R("SERVER_VERSION");c&&b&&(a.postParams["server.name"]=c,a.postParams["server.version"]=b)}rn(R("ECATCHER_REPORT_HOST","")+"/error_204",a)}
function Xu(a){var b=C.apply(1,arguments);a.args||(a.args=[]);Array.isArray(a.args)&&a.args.push.apply(a.args,A(b))}
;function Zu(){this.register=new Map}
function $u(a){a=y(a.register.values());for(var b=a.next();!b.done;b=a.next())b.value.Xh("ABORTED")}
Zu.prototype.clear=function(){$u(this);this.register.clear()};
var av=new Zu;var bv=Date.now().toString();
function cv(){a:{if(window.crypto&&window.crypto.getRandomValues)try{var a=Array(16),b=new Uint8Array(16);window.crypto.getRandomValues(b);for(var c=0;c<a.length;c++)a[c]=b[c];var d=a;break a}catch(e){}d=Array(16);for(a=0;a<16;a++){b=Date.now();for(c=0;c<b%23;c++)d[a]=Math.random();d[a]=Math.floor(Math.random()*256)}if(bv)for(a=1,b=0;b<bv.length;b++)d[a%16]^=d[(a-1)%16]/4^bv.charCodeAt(b),a++}a=[];for(b=0;b<d.length;b++)a.push("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_".charAt(d[b]&63));
return a.join("")}
;var dv,ev=D.ytLoggingDocDocumentNonce_;ev||(ev=cv(),E("ytLoggingDocDocumentNonce_",ev));dv=ev;function fv(a){this.h=a}
p=fv.prototype;p.getAsJson=function(){var a={};this.h.trackingParams!==void 0?a.trackingParams=this.h.trackingParams:(a.veType=this.h.veType,this.h.veCounter!==void 0&&(a.veCounter=this.h.veCounter),this.h.elementIndex!==void 0&&(a.elementIndex=this.h.elementIndex));this.h.dataElement!==void 0&&(a.dataElement=this.h.dataElement.getAsJson());this.h.youtubeData!==void 0&&(a.youtubeData=this.h.youtubeData);this.h.isCounterfactual&&(a.isCounterfactual=!0);return a};
p.getAsJspb=function(){var a=new km;this.h.trackingParams!==void 0?a.setTrackingParams(this.h.trackingParams):(this.h.veType!==void 0&&vf(a,2,Je(this.h.veType)),this.h.veCounter!==void 0&&vf(a,6,Je(this.h.veCounter)),this.h.elementIndex!==void 0&&vf(a,3,Je(this.h.elementIndex)),this.h.isCounterfactual&&vf(a,5,Fe(!0)));if(this.h.dataElement!==void 0){var b=this.h.dataElement.getAsJspb();Ff(a,km,7,b)}this.h.youtubeData!==void 0&&Ff(a,jm,8,this.h.jspbYoutubeData);return a};
p.toString=function(){return JSON.stringify(this.getAsJson())};
p.isClientVe=function(){return!this.h.trackingParams&&!!this.h.veType};
p.getLoggingDirectives=function(){return this.h.loggingDirectives};function gv(a){return R("client-screen-nonce-store",{})[a===void 0?0:a]}
function hv(a,b){b=b===void 0?0:b;var c=R("client-screen-nonce-store");c||(c={},Im("client-screen-nonce-store",c));c[b]=a}
function iv(a){a=a===void 0?0:a;return a===0?"ROOT_VE_TYPE":"ROOT_VE_TYPE."+a}
function jv(a){return R(iv(a===void 0?0:a))}
E("yt_logging_screen.getRootVeType",jv);function kv(){var a=R("csn-to-ctt-auth-info");a||(a={},Im("csn-to-ctt-auth-info",a));return a}
function lv(){return Object.values(R("client-screen-nonce-store",{})).filter(function(a){return a!==void 0})}
function mv(a){a=gv(a===void 0?0:a);if(!a&&!R("USE_CSN_FALLBACK",!0))return null;a||(a="UNDEFINED_CSN");return a?a:null}
E("yt_logging_screen.getCurrentCsn",mv);function nv(a,b,c){var d=kv();(c=mv(c))&&delete d[c];b&&(d[a]=b)}
function ov(a){return kv()[a]}
E("yt_logging_screen.getCttAuthInfo",ov);E("yt_logging_screen.setCurrentScreen",function(a,b,c,d){c=c===void 0?0:c;if(a!==gv(c)||b!==R(iv(c)))if(nv(a,d,c),hv(a,c),Im(iv(c),b),b=function(){setTimeout(function(){a&&dp("foregroundHeartbeatScreenAssociated",{clientDocumentNonce:dv,clientScreenNonce:a})},0)},"requestAnimationFrame"in window)try{window.requestAnimationFrame(b)}catch(e){b()}else b()});function pv(){var a=Ag(qv),b;return(new vi(function(c,d){a.onSuccess=function(e){dn(e)?c(new rv(e)):d(new sv("Request failed, status="+(e&&"status"in e?e.status:-1),"net.badstatus",e))};
a.onError=function(e){d(new sv("Unknown request error","net.unknown",e))};
a.onTimeout=function(e){d(new sv("Request timed out","net.timeout",e))};
b=rn("//googleads.g.doubleclick.net/pagead/id",a)})).Hc(function(c){if(c instanceof Ei){var d;
(d=b)==null||d.abort()}return Ai(c)})}
function sv(a,b,c){eb.call(this,a+", errorCode="+b);this.errorCode=b;this.xhr=c;this.name="PromiseAjaxError"}
v(sv,eb);function rv(a){this.xhr=a}
;function tv(){this.X=0;this.h=null}
tv.prototype.then=function(a,b,c){return this.X===1&&a?(a=a.call(c,this.h))&&typeof a.then==="function"?a:uv(a):this.X===2&&b?(a=b.call(c,this.h))&&typeof a.then==="function"?a:vv(a):this};
tv.prototype.getValue=function(){return this.h};
tv.prototype.isRejected=function(){return this.X==2};
tv.prototype.$goog_Thenable=!0;function vv(a){var b=new tv;a=a===void 0?null:a;b.X=2;b.h=a===void 0?null:a;return b}
function uv(a){var b=new tv;a=a===void 0?null:a;b.X=1;b.h=a===void 0?null:a;return b}
;function wv(a){var b=R("INNERTUBE_HOST_OVERRIDE");b&&(a=String(b)+String(kc(a)));return a}
function xv(a){var b={};S("json_condensed_response")&&(b.prettyPrint="false");return a=Ym(a,b||{},!1)}
function yv(a,b){var c=c===void 0?{}:c;a={method:b===void 0?"POST":b,mode:Zm(a)?"same-origin":"cors",credentials:Zm(a)?"same-origin":"include"};b={};for(var d=y(Object.keys(c)),e=d.next();!e.done;e=d.next())e=e.value,c[e]&&(b[e]=c[e]);Object.keys(b).length>0&&(a.headers=b);return a}
;function zv(){return ig()||(ld||md)&&jp("applewebkit")&&!jp("version")&&(!jp("safari")||jp("gsa/"))||kd&&jp("version/")?!0:R("EOM_VISITOR_DATA")?!1:!0}
;function Av(a){var b=a.docid||a.video_id||a.videoId||a.id;if(b)return b;b=a.raw_player_response;b||(a=a.player_response)&&(b=JSON.parse(a));return b&&b.videoDetails&&b.videoDetails.videoId||null}
;function Bv(a){a:{var b="EMBEDDED_PLAYER_MODE_UNKNOWN";window.location.hostname.includes("youtubeeducation.com")&&(b="EMBEDDED_PLAYER_MODE_PFL");var c=a.raw_embedded_player_response;if(!c&&(a=a.embedded_player_response))try{c=JSON.parse(a)}catch(e){break a}if(c)b:for(var d in om)if(om[d]==c.embeddedPlayerMode){b=om[d];break b}}return b==="EMBEDDED_PLAYER_MODE_PFL"}
;function Cv(a){eb.call(this,a.message||a.description||a.name);this.isMissing=a instanceof Dv;this.isTimeout=a instanceof sv&&a.errorCode=="net.timeout";this.isCanceled=a instanceof Ei}
v(Cv,eb);Cv.prototype.name="BiscottiError";function Dv(){eb.call(this,"Biscotti ID is missing from server")}
v(Dv,eb);Dv.prototype.name="BiscottiMissingError";var qv={format:"RAW",method:"GET",timeout:5E3,withCredentials:!0},Ev=null;function Fv(){if(S("disable_biscotti_fetch_entirely_for_all_web_clients"))return Error("Biscotti id fetching has been disabled entirely.");if(!zv())return Error("User has not consented - not fetching biscotti id.");var a=R("PLAYER_VARS",{});if(yg(a)=="1")return Error("Biscotti ID is not available in private embed mode");if(Bv(a))return Error("Biscotti id fetching has been disabled for pfl.")}
function Bm(){var a=Fv();if(a!==void 0)return Ai(a);Ev||(Ev=pv().then(Gv).Hc(function(b){return Hv(2,b)}));
return Ev}
function Gv(a){a=a.xhr.responseText;if(a.lastIndexOf(")]}'",0)!=0)throw new Dv;a=JSON.parse(a.substr(4));if((a.type||1)>1)throw new Dv;a=a.id;Cm(a);Ev=uv(a);Iv(18E5,2);return a}
function Hv(a,b){b=new Cv(b);Cm("");Ev=vv(b);a>0&&Iv(12E4,a-1);throw b;}
function Iv(a,b){en(function(){pv().then(Gv,function(c){return Hv(b,c)}).Hc(ti)},a)}
function Jv(){try{var a=F("yt.ads.biscotti.getId_");return a?a():Bm()}catch(b){return Ai(b)}}
;var Kb=pa(["data-"]);function Kv(a){a&&(a.dataset?a.dataset[Lv()]="true":Lb(a))}
function Mv(a){return a?a.dataset?a.dataset[Lv()]:a.getAttribute("data-loaded"):null}
var Nv={};function Lv(){return Nv.loaded||(Nv.loaded="loaded".replace(/\-([a-z])/g,function(a,b){return b.toUpperCase()}))}
;function Ov(a){a=a||{};var b={},c={};this.url=a.url||"";this.args=a.args||Ag(b);this.assets=a.assets||{};this.attrs=a.attrs||Ag(c);this.fallback=a.fallback||null;this.fallbackMessage=a.fallbackMessage||null;this.html5=!!a.html5;this.disable=a.disable||{};this.loaded=!!a.loaded;this.messages=a.messages||{}}
Ov.prototype.clone=function(){var a=new Ov,b;for(b in this)if(this.hasOwnProperty(b)){var c=this[b];Ka(c)=="object"?a[b]=Ag(c):a[b]=c}return a};var Pv=["att/get"],Qv=["share/get_share_panel"],Rv=["share/get_web_player_share_panel"],Sv=["feedback"],Tv=["notification/modify_channel_preference"],Uv=["browse/edit_playlist"],Vv=["subscription/subscribe"],Wv=["subscription/unsubscribe"];var Xv=window.yt&&window.yt.msgs_||window.ytcfg&&window.ytcfg.msgs||{};E("yt.msgs_",Xv);function Yv(a){Dm(Xv,arguments)}
;function Zv(a,b,c){$v(a,b,c===void 0?null:c)}
function aw(a){a=bw(a);var b=document.getElementById(a);b&&(rt(a),b.parentNode.removeChild(b))}
function cw(a,b){a&&b&&(a=""+Na(b),(a=dw[a])&&pt(a))}
function $v(a,b,c){c=c===void 0?null:c;var d=bw(typeof a==="string"?a:a.toString()),e=document.getElementById(d),f=e&&Mv(e),g=e&&!f;f?b&&b():(b&&(f=nt(d,b),b=""+Na(b),dw[b]=f),g||(e=ew(a,d,function(){Mv(e)||(Kv(e),qt(d),en(function(){rt(d)},0))},c)))}
function ew(a,b,c,d){d=d===void 0?null:d;var e=Hg("SCRIPT");e.id=b;e.onload=function(){c&&setTimeout(c,0)};
e.onreadystatechange=function(){switch(e.readyState){case "loaded":case "complete":e.onload()}};
d&&e.setAttribute("nonce",d);Ib(e,typeof a==="string"?fm(a):a);a=document.getElementsByTagName("head")[0]||document.body;a.insertBefore(e,a.firstChild);return e}
function bw(a){var b=document.createElement("a");Ab(b,a);a=b.href.replace(/^[a-zA-Z]+:\/\//,"//");return"js-"+ec(a)}
var dw={};function fw(a){var b=gw(a),c=document.getElementById(b),d=c&&Mv(c);d||c&&!d||(c=hw(a,b,function(){if(!Mv(c)){Kv(c);qt(b);var e=Wa(rt,b);en(e,0)}}))}
function hw(a,b,c){var d=document.createElement("link");d.id=b;d.onload=function(){c&&setTimeout(c,0)};
a=fm(a);Nb(d,a);(document.getElementsByTagName("head")[0]||document.body).appendChild(d);return d}
function gw(a){var b=Hg("A");Ab(b,new tb(a));a=b.href.replace(/^[a-zA-Z]+:\/\//,"//");return"css-"+ec(a)}
;function iw(a){var b=C.apply(1,arguments);if(!jw(a)||b.some(function(d){return!jw(d)}))throw Error("Only objects may be merged.");
b=y(b);for(var c=b.next();!c.done;c=b.next())kw(a,c.value)}
function kw(a,b){for(var c in b)if(jw(b[c])){if(c in a&&!jw(a[c]))throw Error("Cannot merge an object into a non-object.");c in a||(a[c]={});kw(a[c],b[c])}else if(lw(b[c])){if(c in a&&!lw(a[c]))throw Error("Cannot merge an array into a non-array.");c in a||(a[c]=[]);mw(a[c],b[c])}else a[c]=b[c];return a}
function mw(a,b){b=y(b);for(var c=b.next();!c.done;c=b.next())c=c.value,jw(c)?a.push(kw({},c)):lw(c)?a.push(mw([],c)):a.push(c);return a}
function jw(a){return typeof a==="object"&&!Array.isArray(a)}
function lw(a){return typeof a==="object"&&Array.isArray(a)}
;var nw="absolute_experiments app conditional_experiments debugcss debugjs expflag forced_experiments pbj pbjreload sbb spf spfreload sr_bns_address sttick".split(" ");
function ow(a,b){var c=c===void 0?!0:c;var d=R("VALID_SESSION_TEMPDATA_DOMAINS",[]),e=ic(window.location.href);e&&d.push(e);e=ic(a);if(Ob(d,e)>=0||!e&&a.lastIndexOf("/",0)==0)if(d=document.createElement("a"),Ab(d,a),a=d.href)if(a=kc(a),a=lc(a))if(c&&!b.csn&&(b.itct||b.ved)&&(b=Object.assign({csn:mv()},b)),f){var f=parseInt(f,10);isFinite(f)&&f>0&&pw(a,b,f)}else pw(a,b)}
function pw(a,b,c){a=qw(a);b=b?oc(b):"";c=c||5;zv()&&Un(a,b,c)}
function qw(a){for(var b=y(nw),c=b.next();!c.done;c=b.next())a=tc(a,c.value);return"ST-"+ec(a).toString(36)}
;function rw(a){$q.call(this,1,arguments);this.csn=a}
v(rw,$q);var ir=new ar("screen-created",rw),sw=[],tw=0,uw=new Map,vw=new Map,ww=new Map;
function xw(a,b,c,d,e,f){e=e===void 0?!1:e;f=f===void 0?{}:f;Object.assign(f,yw({cttAuthInfo:ov(b)||void 0},b));for(var g=y(d),h=g.next();!h.done;h=g.next()){h=h.value;var k=h.getAsJson();(wg(k)||!k.trackingParams&&!k.veType)&&Uu(Error("Child VE logged with no data"));if(S("no_client_ve_attach_unless_shown")){var l=zw(h,b);if(k.veType&&!vw.has(l)&&!ww.has(l)&&!e){if(!S("il_attach_cache_limit")||uw.size<1E3){uw.set(l,[a,b,c,h]);return}S("il_attach_cache_limit")&&uw.size>1E3&&Uu(new T("IL Attach cache exceeded limit"))}h=
zw(c,b);uw.has(h)?Aw(c,b):ww.set(h,!0)}}d=d.filter(function(m){m.csn!==b?(m.csn=b,m=!0):m=!1;return m});
c={csn:b,parentVe:c.getAsJson(),childVes:Sb(d,function(m){return m.getAsJson()})};
b==="UNDEFINED_CSN"?Bw("visualElementAttached",f,c):a?Ku("visualElementAttached",c,a,f):dp("visualElementAttached",c,f)}
function Bw(a,b,c){sw.push({We:a,payload:c,Oh:void 0,options:b});tw||(tw=jr())}
function kr(a){if(sw){for(var b=y(sw),c=b.next();!c.done;c=b.next())c=c.value,c.payload&&(c.payload.csn=a.csn,dp(c.We,c.payload,c.options));sw.length=0}tw=0}
function zw(a,b){return""+a.getAsJson().veType+a.getAsJson().veCounter+b}
function Aw(a,b){a=zw(a,b);if(uw.has(a)){b=uw.get(a)||[];var c=c===void 0?{}:c;xw(b[0],b[1],b[2],[b[3]],!0,c);uw.delete(a)}}
function yw(a,b){S("log_sequence_info_on_gel_web")&&(a.sequenceGroup=b);return a}
;function Cw(){try{return!!self.localStorage}catch(a){return!1}}
;function Dw(a){a=a.match(/(.*)::.*::.*/);if(a!==null)return a[1]}
function Ew(a){if(Cw()){var b=Object.keys(window.localStorage);b=y(b);for(var c=b.next();!c.done;c=b.next()){c=c.value;var d=Dw(c);d===void 0||a.includes(d)||self.localStorage.removeItem(c)}}}
function Fw(){if(!Cw())return!1;var a=mo(),b=Object.keys(window.localStorage);b=y(b);for(var c=b.next();!c.done;c=b.next())if(c=Dw(c.value),c!==void 0&&c!==a)return!0;return!1}
;function Gw(){var a=!1;try{a=!!window.sessionStorage.getItem("session_logininfo")}catch(b){a=!0}return(R("INNERTUBE_CLIENT_NAME")==="WEB"||R("INNERTUBE_CLIENT_NAME")==="WEB_CREATOR")&&a}
function Hw(){var a=a===void 0?!0:a;try{window.sessionStorage.removeItem("stickiness_reload");window.sessionStorage.removeItem("session_logininfo");Im("LOGIN_INFO","");a&&window.sessionStorage.setItem("from_switch_account","1");a=!0;a=a===void 0?!1:a;var b,c=Iw;c||(c=document.querySelector("#persist_identity"));if(b=c){var d=b.src?(new URL(b.src)).origin:"*";if(a){var e;(e=b.contentWindow)==null||e.postMessage({action:"clear"},d)}else if(!(Number(window.sessionStorage.getItem("stickiness_reload"))>=
2)){var f=window.sessionStorage.getItem("session_logininfo");if(f){var g;(g=b.contentWindow)==null||g.postMessage({loginInfo:f},d)}}}}catch(h){}}
function Jw(a){if(a)if(a.startsWith("https://accounts.google.com/AddSession"))Hw();else if(a.startsWith("https://accounts.google.com/ServiceLogin"))Hw();else{var b;if(b=a.startsWith("https://myaccount.google.com"))b=(a instanceof Bk?a.clone():new Bk(a)).h.endsWith("/youtubeoptions");b&&Hw()}if(R("LOGGED_IN",!0)&&Gw()){b=R("VALID_SESSION_TEMPDATA_DOMAINS",[]);var c=ic(window.location.href);c&&b.push(c);c=ic(a);Ob(b,c)>=0||!c&&a.lastIndexOf("/",0)==0?(b=kc(a),(b=lc(b))?(b=qw(b),b=(b=Vn(b)||null)?Vm(b):
{}):b=null):b=null;b==null&&(b={});c=b;var d=void 0;Gw()?(d||(d=R("LOGIN_INFO")),d?(c.session_logininfo=d,c=!0):c=!1):c=!1;c&&ow(a,b)}}
var Iw=null;function Kw(a,b,c){b=b===void 0?{}:b;c=c===void 0?!1:c;var d=R("EVENT_ID");d&&(b.ei||(b.ei=d));b&&ow(a,b);if(c)return!1;Jw(a);var e=e===void 0?{}:e;var f=f===void 0?"":f;var g=g===void 0?window:g;b=pc(a,e);Jw(b);a=void 0;a=a===void 0?xb:a;a:if(f=b+f,a=a===void 0?xb:a,!(f instanceof tb)){for(b=0;b<a.length;++b)if(c=a[b],c instanceof vb&&c.Je(f)){f=new tb(f);break a}f=void 0}g=g.location;f=zb(f||ub);f!==void 0&&(g.href=f);return!0}
;function Lw(a){if(yg(R("PLAYER_VARS",{}))!="1"){a&&Am();try{Jv().then(function(){},function(){}),en(Lw,18E5)}catch(b){Nm(b)}}}
;var Mw=new Map([["dark","USER_INTERFACE_THEME_DARK"],["light","USER_INTERFACE_THEME_LIGHT"]]);function Nw(){var a=a===void 0?window.location.href:a;if(S("kevlar_disable_theme_param"))return null;var b=jc(a);if(S("enable_dark_theme_only_on_shorts")&&b!=null&&b.startsWith("/shorts/"))return"USER_INTERFACE_THEME_DARK";try{var c=Wm(a).theme;return Mw.get(c)||null}catch(d){}return null}
;function Ow(){this.h={};if(this.i=Xn()){var a=Vn("CONSISTENCY");a&&Pw(this,{encryptedTokenJarContents:a})}}
Ow.prototype.handleResponse=function(a,b){if(!b)throw Error("request needs to be passed into ConsistencyService");var c,d;b=((c=b.Ga.context)==null?void 0:(d=c.request)==null?void 0:d.consistencyTokenJars)||[];var e;if(a=(e=a.responseContext)==null?void 0:e.consistencyTokenJar){e=y(b);for(c=e.next();!c.done;c=e.next())delete this.h[c.value.encryptedTokenJarContents];Pw(this,a)}};
function Pw(a,b){if(b.encryptedTokenJarContents&&(a.h[b.encryptedTokenJarContents]=b,typeof b.expirationSeconds==="string")){var c=Number(b.expirationSeconds);setTimeout(function(){delete a.h[b.encryptedTokenJarContents]},c*1E3);
a.i&&Un("CONSISTENCY",b.encryptedTokenJarContents,c,void 0,!0)}}
;var Qw=window.location.hostname.split(".").slice(-2).join(".");function Rw(){this.i=-1;var a=R("LOCATION_PLAYABILITY_TOKEN");R("INNERTUBE_CLIENT_NAME")==="TVHTML5"&&(this.localStorage=Sw(this))&&(a=this.localStorage.get("yt-location-playability-token"));a&&(this.locationPlayabilityToken=a,this.h=void 0)}
var Tw;function Uw(){Tw=F("yt.clientLocationService.instance");Tw||(Tw=new Rw,E("yt.clientLocationService.instance",Tw));return Tw}
p=Rw.prototype;
p.setLocationOnInnerTubeContext=function(a){a.client||(a.client={});if(this.h)a.client.locationInfo||(a.client.locationInfo={}),a.client.locationInfo.latitudeE7=Math.floor(this.h.coords.latitude*1E7),a.client.locationInfo.longitudeE7=Math.floor(this.h.coords.longitude*1E7),a.client.locationInfo.horizontalAccuracyMeters=Math.round(this.h.coords.accuracy),a.client.locationInfo.forceLocationPlayabilityTokenRefresh=!0;else if(this.j||this.locationPlayabilityToken)a.client.locationPlayabilityToken=this.j||
this.locationPlayabilityToken};
p.handleResponse=function(a){var b;a=(b=a.responseContext)==null?void 0:b.locationPlayabilityToken;a!==void 0&&(this.locationPlayabilityToken=a,this.h=void 0,R("INNERTUBE_CLIENT_NAME")==="TVHTML5"?(this.localStorage=Sw(this))&&this.localStorage.set("yt-location-playability-token",a,15552E3):Un("YT_CL",JSON.stringify({loctok:a}),15552E3,Qw,!0))};
function Sw(a){return a.localStorage===void 0?new Vo("yt-client-location"):a.localStorage}
p.clearLocationPlayabilityToken=function(a){a==="TVHTML5"?(this.localStorage=Sw(this))&&this.localStorage.remove("yt-location-playability-token"):Wn("YT_CL");this.j=void 0;this.i!==-1&&(clearTimeout(this.i),this.i=-1)};
p.getCurrentPositionFromGeolocation=function(){var a=this;if(!(navigator&&navigator.geolocation&&navigator.geolocation.getCurrentPosition))return Promise.reject(Error("Geolocation unsupported"));var b=!1,c=1E4;R("INNERTUBE_CLIENT_NAME")==="MWEB"&&(b=!0,c=15E3);return new Promise(function(d,e){navigator.geolocation.getCurrentPosition(function(f){a.h=f;d(f)},function(f){e(f)},{enableHighAccuracy:b,
maximumAge:0,timeout:c})})};
p.createUnpluggedLocationInfo=function(a){var b={};a=a.coords;if(a==null?0:a.latitude)b.latitudeE7=Math.floor(a.latitude*1E7);if(a==null?0:a.longitude)b.longitudeE7=Math.floor(a.longitude*1E7);if(a==null?0:a.accuracy)b.locationRadiusMeters=Math.round(a.accuracy);return b};
p.createLocationInfo=function(a){var b={};a=a.coords;if(a==null?0:a.latitude)b.latitudeE7=Math.floor(a.latitude*1E7);if(a==null?0:a.longitude)b.longitudeE7=Math.floor(a.longitude*1E7);return b};function Vw(a,b,c){b=b===void 0?!1:b;c=c===void 0?!1:c;var d=R("INNERTUBE_CONTEXT");if(!d)return Tu(Error("Error: No InnerTubeContext shell provided in ytconfig.")),{};d=Bg(d);S("web_no_tracking_params_in_shell_killswitch")||delete d.clickTracking;d.client||(d.client={});var e=d.client;e.clientName==="MWEB"&&e.clientFormFactor!=="AUTOMOTIVE_FORM_FACTOR"&&(e.clientFormFactor=R("IS_TABLET")?"LARGE_FORM_FACTOR":"SMALL_FORM_FACTOR");e.screenWidthPoints=window.innerWidth;e.screenHeightPoints=window.innerHeight;
e.screenPixelDensity=Math.round(window.devicePixelRatio||1);e.screenDensityFloat=window.devicePixelRatio||1;e.utcOffsetMinutes=-Math.floor((new Date).getTimezoneOffset());var f=f===void 0?!1:f;ao();var g="USER_INTERFACE_THEME_LIGHT";eo(165)?g="USER_INTERFACE_THEME_DARK":eo(174)?g="USER_INTERFACE_THEME_LIGHT":!S("kevlar_legacy_browsers")&&window.matchMedia&&window.matchMedia("(prefers-color-scheme)").matches&&window.matchMedia("(prefers-color-scheme: dark)").matches&&(g="USER_INTERFACE_THEME_DARK");
f=f?g:Nw()||g;e.userInterfaceTheme=f;if(!b){if(f=jo())e.connectionType=f;S("web_log_effective_connection_type")&&(f=ko())&&(d.client.effectiveConnectionType=f)}var h;if(S("web_log_memory_total_kbytes")&&((h=D.navigator)==null?0:h.deviceMemory)){var k;h=(k=D.navigator)==null?void 0:k.deviceMemory;d.client.memoryTotalKbytes=""+h*1E6}S("web_gcf_hashes_innertube")&&(f=Rq())&&(k=f.coldConfigData,h=f.coldHashData,f=f.hotHashData,d.client.configInfo=d.client.configInfo||{},k&&(d.client.configInfo.coldConfigData=
k),h&&(d.client.configInfo.coldHashData=h),f&&(d.client.configInfo.hotHashData=f));k=Wm(D.location.href);!S("web_populate_internal_geo_killswitch")&&k.internalcountrycode&&(e.internalGeo=k.internalcountrycode);e.clientName==="MWEB"||e.clientName==="WEB"?(e.mainAppWebInfo||(e.mainAppWebInfo={}),e.mainAppWebInfo.graftUrl=D.location.href,S("kevlar_woffle")&&On.instance&&(k=On.instance,e.mainAppWebInfo.pwaInstallabilityStatus=!k.h&&k.i?"PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED":"PWA_INSTALLABILITY_STATUS_UNKNOWN"),
e.mainAppWebInfo.webDisplayMode=Pn(),e.mainAppWebInfo.isWebNativeShareAvailable=navigator&&navigator.share!==void 0):e.clientName==="TVHTML5"&&(!S("web_lr_app_quality_killswitch")&&(k=R("LIVING_ROOM_APP_QUALITY"))&&(e.tvAppInfo=Object.assign(e.tvAppInfo||{},{appQuality:k})),k=R("LIVING_ROOM_CERTIFICATION_SCOPE"))&&(e.tvAppInfo=Object.assign(e.tvAppInfo||{},{certificationScope:k}));if(!S("web_populate_time_zone_itc_killswitch")){a:{if(typeof Intl!=="undefined")try{var l=(new Intl.DateTimeFormat).resolvedOptions().timeZone;
break a}catch(Z){}l=void 0}l&&(e.timeZone=l)}(l=R("EXPERIMENTS_TOKEN",""))?e.experimentsToken=l:delete e.experimentsToken;l=jn();Ow.instance||(Ow.instance=new Ow);d.request=Object.assign({},d.request,{internalExperimentFlags:l,consistencyTokenJars:tg(Ow.instance.h)});!S("web_prequest_context_killswitch")&&(l=R("INNERTUBE_CONTEXT_PREQUEST_CONTEXT"))&&(d.request.externalPrequestContext=l);e=ao();l=eo(58);e=e.get("gsml","");d.user=Object.assign({},d.user);l&&(d.user.enableSafetyMode=l);e&&(d.user.lockedSafetyMode=
!0);S("warm_op_csn_cleanup")?c&&(b=mv())&&(d.clientScreenNonce=b):!b&&(b=mv())&&(d.clientScreenNonce=b);a&&(d.clickTracking={clickTrackingParams:a});if(a=F("yt.mdx.remote.remoteClient_"))d.remoteClient=a;Uw().setLocationOnInnerTubeContext(d);try{var m=$m(),n=m.bid;delete m.bid;d.adSignalsInfo={params:[],bid:n};for(var r=y(Object.entries(m)),t=r.next();!t.done;t=r.next()){var w=y(t.value),x=w.next().value,z=w.next().value;m=x;n=z;a=void 0;(a=d.adSignalsInfo.params)==null||a.push({key:m,value:""+n})}var G,
H;if(((G=d.client)==null?void 0:G.clientName)==="TVHTML5"||((H=d.client)==null?void 0:H.clientName)==="TVHTML5_UNPLUGGED"){var U=R("INNERTUBE_CONTEXT");U.adSignalsInfo&&(d.adSignalsInfo.advertisingId=U.adSignalsInfo.advertisingId,d.adSignalsInfo.advertisingIdSignalType="DEVICE_ID_TYPE_CONNECTED_TV_IFA",d.adSignalsInfo.limitAdTracking=U.adSignalsInfo.limitAdTracking)}}catch(Z){Tu(Z)}return d}
;function Ww(a){var b={"Content-Type":"application/json"};R("EOM_VISITOR_DATA")?b["X-Goog-EOM-Visitor-Id"]=R("EOM_VISITOR_DATA"):R("VISITOR_DATA")&&(b["X-Goog-Visitor-Id"]=R("VISITOR_DATA"));b["X-Youtube-Bootstrap-Logged-In"]=R("LOGGED_IN",!1);R("DEBUG_SETTINGS_METADATA")&&(b["X-Debug-Settings-Metadata"]=R("DEBUG_SETTINGS_METADATA"));a!=="cors"&&((a=R("INNERTUBE_CONTEXT_CLIENT_NAME"))&&(b["X-Youtube-Client-Name"]=a),(a=R("INNERTUBE_CONTEXT_CLIENT_VERSION"))&&(b["X-Youtube-Client-Version"]=a),(a=R("CHROME_CONNECTED_HEADER"))&&
(b["X-Youtube-Chrome-Connected"]=a),(a=R("DOMAIN_ADMIN_STATE"))&&(b["X-Youtube-Domain-Admin-State"]=a),R("ENABLE_LAVA_HEADER_ON_IT_EXPANSION")&&(a=R("SERIALIZED_LAVA_DEVICE_CONTEXT"))&&(b["X-YouTube-Lava-Device-Context"]=a));return b}
;function Xw(){this.h={}}
p=Xw.prototype;p.contains=function(a){return Object.prototype.hasOwnProperty.call(this.h,a)};
p.get=function(a){if(this.contains(a))return this.h[a]};
p.set=function(a,b){this.h[a]=b};
p.Tb=function(){return Object.keys(this.h)};
p.remove=function(a){delete this.h[a]};function Yw(){this.mappings=new Xw}
Yw.prototype.getModuleId=function(a){return a.serviceId.getModuleId()};
Yw.prototype.get=function(a){a:{var b=this.mappings.get(a.toString());switch(b.type){case "mapping":a=b.value;break a;case "factory":b=b.value();this.mappings.set(a.toString(),{type:"mapping",value:b});a=b;break a;default:a=Bb(b)}}return a};
new Yw;function Zw(a){return function(){return new a}}
;var $w={},ax=($w.WEB_UNPLUGGED="^unplugged/",$w.WEB_UNPLUGGED_ONBOARDING="^unplugged/",$w.WEB_UNPLUGGED_OPS="^unplugged/",$w.WEB_UNPLUGGED_PUBLIC="^unplugged/",$w.WEB_CREATOR="^creator/",$w.WEB_KIDS="^kids/",$w.WEB_EXPERIMENTS="^experiments/",$w.WEB_MUSIC="^music/",$w.WEB_REMIX="^music/",$w.WEB_MUSIC_EMBEDDED_PLAYER="^music/",$w.WEB_MUSIC_EMBEDDED_PLAYER="^main_app/|^sfv/",$w);
function bx(a){var b=b===void 0?"UNKNOWN_INTERFACE":b;if(a.length===1)return a[0];var c=ax[b];if(c){c=new RegExp(c);for(var d=y(a),e=d.next();!e.done;e=d.next())if(e=e.value,c.exec(e))return e}var f=[];Object.entries(ax).forEach(function(g){var h=y(g);g=h.next().value;h=h.next().value;b!==g&&f.push(h)});
c=new RegExp(f.join("|"));a.sort(function(g,h){return g.length-h.length});
d=y(a);for(e=d.next();!e.done;e=d.next())if(e=e.value,!c.exec(e))return e;return a[0]}
;function cx(){}
cx.prototype.u=function(a,b,c){b=b===void 0?{}:b;c=c===void 0?Tn:c;var d={context:Vw(a.clickTrackingParams,!1,this.o)};var e=this.i(a);if(e){this.h(d,e,b);var f;b="/youtubei/v1/"+bx(this.j());(e=(f=bu(a.commandMetadata,mm))==null?void 0:f.apiUrl)&&(b=e);f=xv(wv(b));a=Object.assign({},{command:a},void 0);d={input:f,ab:yv(f),Ga:d,config:a};d.config.Ob?d.config.Ob.identity=c:d.config.Ob={identity:c};return d}c=new T("Error: Failed to create Request from Command.",a);Tu(c)};
ea.Object.defineProperties(cx.prototype,{o:{configurable:!0,enumerable:!0,get:function(){return!1}}});
function dx(){}
v(dx,cx);function ex(){}
v(ex,dx);ex.prototype.u=function(){return{input:"/getDatasyncIdsEndpoint",ab:yv("/getDatasyncIdsEndpoint","GET"),Ga:{}}};
ex.prototype.j=function(){return[]};
ex.prototype.i=function(){};
ex.prototype.h=function(){};var fx={},gx=(fx.GET_DATASYNC_IDS=Zw(ex),fx);function hx(a){var b;(b=F("ytcsi."+(a||"")+"data_"))||(b={tick:{},info:{}},E("ytcsi."+(a||"")+"data_",b));return b}
function ix(){var a=hx();a.info||(a.info={});return a.info}
function jx(a){a=hx(a);a.metadata||(a.metadata={});return a.metadata}
function kx(a){a=hx(a);a.tick||(a.tick={});return a.tick}
function lx(a){a=hx(a);if(a.gel){var b=a.gel;b.gelInfos||(b.gelInfos={});b.gelTicks||(b.gelTicks={})}else a.gel={gelTicks:{},gelInfos:{}};return a.gel}
function mx(a){a=lx(a);a.gelInfos||(a.gelInfos={});return a.gelInfos}
function nx(a){var b=hx(a).nonce;b||(b=cv(),hx(a).nonce=b);return b}
;function ox(){var a=F("ytcsi.debug");a||(a=[],E("ytcsi.debug",a),E("ytcsi.reference",{}));return a}
function px(a){a=a||"";var b=F("ytcsi.reference");b||(ox(),b=F("ytcsi.reference"));if(b[a])return b[a];var c=ox(),d={timerName:a,info:{},tick:{},span:{},jspbInfo:[]};c.push(d);return b[a]=d}
;var W={},qx=(W.auto_search="LATENCY_ACTION_AUTO_SEARCH",W.ad_to_ad="LATENCY_ACTION_AD_TO_AD",W.ad_to_video="LATENCY_ACTION_AD_TO_VIDEO",W.app_startup="LATENCY_ACTION_APP_STARTUP",W.browse="LATENCY_ACTION_BROWSE",W.cast_splash="LATENCY_ACTION_CAST_SPLASH",W.channel_activity="LATENCY_ACTION_KIDS_CHANNEL_ACTIVITY",W.channels="LATENCY_ACTION_CHANNELS",W.chips="LATENCY_ACTION_CHIPS",W.commerce_transaction="LATENCY_ACTION_COMMERCE_TRANSACTION",W.direct_playback="LATENCY_ACTION_DIRECT_PLAYBACK",W.editor=
"LATENCY_ACTION_EDITOR",W.embed="LATENCY_ACTION_EMBED",W.embed_no_video="LATENCY_ACTION_EMBED_NO_VIDEO",W.entity_key_serialization_perf="LATENCY_ACTION_ENTITY_KEY_SERIALIZATION_PERF",W.entity_key_deserialization_perf="LATENCY_ACTION_ENTITY_KEY_DESERIALIZATION_PERF",W.explore="LATENCY_ACTION_EXPLORE",W.favorites="LATENCY_ACTION_FAVORITES",W.home="LATENCY_ACTION_HOME",W.inboarding="LATENCY_ACTION_INBOARDING",W.landing="LATENCY_ACTION_LANDING",W.learning="LATENCY_ACTION_LEARNING",W.learning_journey_browse=
"LATENCY_ACTION_LEARNING_JOURNEY_BROWSE",W.learning_journey_watch="LATENCY_ACTION_LEARNING_JOURNEY_WATCH",W.library="LATENCY_ACTION_LIBRARY",W.live="LATENCY_ACTION_LIVE",W.live_pagination="LATENCY_ACTION_LIVE_PAGINATION",W.management="LATENCY_ACTION_MANAGEMENT",W.mini_app="LATENCY_ACTION_MINI_APP_PLAY",W.notification_settings="LATENCY_ACTION_KIDS_NOTIFICATION_SETTINGS",W.onboarding="LATENCY_ACTION_ONBOARDING",W.parent_profile_settings="LATENCY_ACTION_KIDS_PARENT_PROFILE_SETTINGS",W.parent_tools_collection=
"LATENCY_ACTION_PARENT_TOOLS_COLLECTION",W.parent_tools_dashboard="LATENCY_ACTION_PARENT_TOOLS_DASHBOARD",W.player_att="LATENCY_ACTION_PLAYER_ATTESTATION",W.prebuffer="LATENCY_ACTION_PREBUFFER",W.prefetch="LATENCY_ACTION_PREFETCH",W.profile_settings="LATENCY_ACTION_KIDS_PROFILE_SETTINGS",W.profile_switcher="LATENCY_ACTION_LOGIN",W.projects="LATENCY_ACTION_PROJECTS",W.reel_watch="LATENCY_ACTION_REEL_WATCH",W.results="LATENCY_ACTION_RESULTS",W.red="LATENCY_ACTION_PREMIUM_PAGE_GET_BROWSE",W.premium=
"LATENCY_ACTION_PREMIUM_PAGE_GET_BROWSE",W.privacy_policy="LATENCY_ACTION_KIDS_PRIVACY_POLICY",W.review="LATENCY_ACTION_REVIEW",W.search_overview_answer="LATENCY_ACTION_SEARCH_OVERVIEW_ANSWER",W.search_ui="LATENCY_ACTION_SEARCH_UI",W.search_suggest="LATENCY_ACTION_SUGGEST",W.search_zero_state="LATENCY_ACTION_SEARCH_ZERO_STATE",W.secret_code="LATENCY_ACTION_KIDS_SECRET_CODE",W.seek="LATENCY_ACTION_PLAYER_SEEK",W.settings="LATENCY_ACTION_SETTINGS",W.store="LATENCY_ACTION_STORE",W.supervision_dashboard=
"LATENCY_ACTION_KIDS_SUPERVISION_DASHBOARD",W.tenx="LATENCY_ACTION_TENX",W.video_preview="LATENCY_ACTION_VIDEO_PREVIEW",W.video_to_ad="LATENCY_ACTION_VIDEO_TO_AD",W.watch="LATENCY_ACTION_WATCH",W.watch_it_again="LATENCY_ACTION_KIDS_WATCH_IT_AGAIN",W["watch,watch7"]="LATENCY_ACTION_WATCH",W["watch,watch7_html5"]="LATENCY_ACTION_WATCH",W["watch,watch7ad"]="LATENCY_ACTION_WATCH",W["watch,watch7ad_html5"]="LATENCY_ACTION_WATCH",W.wn_comments="LATENCY_ACTION_LOAD_COMMENTS",W.ww_rqs="LATENCY_ACTION_WHO_IS_WATCHING",
W.voice_assistant="LATENCY_ACTION_VOICE_ASSISTANT",W.cast_load_by_entity_to_watch="LATENCY_ACTION_CAST_LOAD_BY_ENTITY_TO_WATCH",W.networkless_performance="LATENCY_ACTION_NETWORKLESS_PERFORMANCE",W.gel_compression="LATENCY_ACTION_GEL_COMPRESSION",W.gel_jspb_serialize="LATENCY_ACTION_GEL_JSPB_SERIALIZE",W.attestation_challenge_fetch="LATENCY_ACTION_ATTESTATION_CHALLENGE_FETCH",W);function rx(a,b){$q.call(this,1,arguments);this.timer=b}
v(rx,$q);var sx=new ar("aft-recorded",rx);E("ytLoggingGelSequenceIdObj_",D.ytLoggingGelSequenceIdObj_||{});var tx=D.ytLoggingLatencyUsageStats_||{};E("ytLoggingLatencyUsageStats_",tx);function ux(){this.h=0}
function vx(){ux.instance||(ux.instance=new ux);return ux.instance}
ux.prototype.tick=function(a,b,c,d){wx(this,"tick_"+a+"_"+b)||dp("latencyActionTicked",{tickName:a,clientActionNonce:b},{timestamp:c,cttAuthInfo:d})};
ux.prototype.info=function(a,b,c){var d=Object.keys(a).join("");wx(this,"info_"+d+"_"+b)||(a=Object.assign({},a),a.clientActionNonce=b,dp("latencyActionInfo",a,{cttAuthInfo:c}))};
ux.prototype.jspbInfo=function(){};
ux.prototype.span=function(a,b,c){var d=Object.keys(a).join("");wx(this,"span_"+d+"_"+b)||(a.clientActionNonce=b,dp("latencyActionSpan",a,{cttAuthInfo:c}))};
function wx(a,b){tx[b]=tx[b]||{count:0};var c=tx[b];c.count++;c.time=V();a.h||(a.h=oo(function(){var d=V(),e;for(e in tx)tx[e]&&d-tx[e].time>6E4&&delete tx[e];a&&(a.h=0)},5E3));
return c.count>5?(c.count===6&&Math.random()*1E5<1&&(c=new T("CSI data exceeded logging limit with key",b.split("_")),b.indexOf("plev")>=0||Uu(c)),!0):!1}
;var xx=window;function yx(){this.timing={};this.clearResourceTimings=function(){};
this.webkitClearResourceTimings=function(){};
this.mozClearResourceTimings=function(){};
this.msClearResourceTimings=function(){};
this.oClearResourceTimings=function(){}}
function zx(){var a;if(S("csi_use_performance_navigation_timing")){var b,c,d,e=X==null?void 0:(a=X.getEntriesByType)==null?void 0:(b=a.call(X,"navigation"))==null?void 0:(c=b[0])==null?void 0:(d=c.toJSON)==null?void 0:d.call(c);e?(e.requestStart=Ax(e.requestStart),e.responseEnd=Ax(e.responseEnd),e.redirectStart=Ax(e.redirectStart),e.redirectEnd=Ax(e.redirectEnd),e.domainLookupEnd=Ax(e.domainLookupEnd),e.connectStart=Ax(e.connectStart),e.connectEnd=Ax(e.connectEnd),e.responseStart=Ax(e.responseStart),
e.secureConnectionStart=Ax(e.secureConnectionStart),e.domainLookupStart=Ax(e.domainLookupStart),e.isPerformanceNavigationTiming=!0,a=e):a=X.timing}else a=S("csi_performance_timing_to_object")?JSON.parse(JSON.stringify(X.timing)):X.timing;return a}
function Ax(a){return Math.round(Bx()+a)}
function Bx(){return(S("csi_use_time_origin")||S("csi_use_time_origin_tvhtml5"))&&X.timeOrigin?Math.floor(X.timeOrigin):X.timing.navigationStart}
var X=xx.performance||xx.mozPerformance||xx.msPerformance||xx.webkitPerformance||new yx;var Cx=!1,Dx=!1,Ex={'script[name="scheduler/scheduler"]':"sj",'script[name="player/base"]':"pj",'link[rel="preload"][name="player/embed"]':"pej",'link[rel="stylesheet"][name="www-player"]':"pc",'link[rel="stylesheet"][name="player/www-player"]':"pc",'script[name="desktop_polymer/desktop_polymer"]':"dpj",'link[rel="import"][name="desktop_polymer"]':"dph",'script[name="mobile-c3"]':"mcj",'link[rel="stylesheet"][name="mobile-c3"]':"mcc",'script[name="player-plasma-ias-phone/base"]':"mcppj",'script[name="player-plasma-ias-tablet/base"]':"mcptj",
'link[rel="stylesheet"][name="mobile-polymer-player-ias"]':"mcpc",'link[rel="stylesheet"][name="mobile-polymer-player-svg-ias"]':"mcpsc",'script[name="mobile_blazer_core_mod"]':"mbcj",'link[rel="stylesheet"][name="mobile_blazer_css"]':"mbc",'script[name="mobile_blazer_logged_in_users_mod"]':"mbliuj",'script[name="mobile_blazer_logged_out_users_mod"]':"mblouj",'script[name="mobile_blazer_noncore_mod"]':"mbnj","#player_css":"mbpc",'script[name="mobile_blazer_desktopplayer_mod"]':"mbpj",'link[rel="stylesheet"][name="mobile_blazer_tablet_css"]':"mbtc",
'script[name="mobile_blazer_watch_mod"]':"mbwj",'script[name="embed_client"]':"ecj",'link[rel="stylesheet"][name="embed-ui"]':"ecc"};Va(X.clearResourceTimings||X.webkitClearResourceTimings||X.mozClearResourceTimings||X.msClearResourceTimings||X.oClearResourceTimings||ti,X);function Fx(a,b){if(!S("web_csi_action_sampling_enabled")||!hx(b).actionDisabled){var c=px(b||"");iw(c.info,a);a.loadType&&(c=a.loadType,jx(b).loadType=c);iw(mx(b),a);c=nx(b);b=hx(b).cttAuthInfo;vx().info(a,c,b)}}
function Gx(){var a,b,c,d;return((d=Dt().resolve(wt(Nq))==null?void 0:(a=Oq())==null?void 0:(b=a.loggingHotConfig)==null?void 0:(c=b.csiConfig)==null?void 0:c.debugTicks)!=null?d:[]).map(function(e){return Object.values(e)[0]})}
function Hx(a,b,c){if(!S("web_csi_action_sampling_enabled")||!hx(c).actionDisabled){var d=nx(c),e;if(e=S("web_csi_debug_sample_enabled")&&d){(Dt().resolve(wt(Nq))==null?0:Oq())&&!Dx&&(Dx=!0,Hx("gcfl",V(),c));var f,g,h;e=(Dt().resolve(wt(Nq))==null?void 0:(f=Oq())==null?void 0:(g=f.loggingHotConfig)==null?void 0:(h=g.csiConfig)==null?void 0:h.debugSampleWeight)||0;if(f=e!==0)b:{f=Gx();if(f.length>0)for(g=0;g<f.length;g++)if(a===f[g]){f=!0;break b}f=!1}if(f){for(g=f=0;g<d.length;g++)f=f*31+d.charCodeAt(g),
g<d.length-1&&(f%=0x800000000000);e=f%1E5%e!==0;hx(c).debugTicksExcludedLogged||(f={},f.debugTicksExcluded=e,Fx(f,c));hx(c).debugTicksExcludedLogged=!0}else e=!1}if(!e){if(a[0]!=="_"&&(e=a,f=b,X.mark))if(e.startsWith("mark_")||(e="mark_"+e),c&&(e+=" ("+c+")"),f===void 0||S("web_csi_disable_alt_time_performance_mark"))X.mark(e);else{f=S("csi_use_performance_navigation_timing")?f-X.timeOrigin:f-(X.timeOrigin||X.timing.navigationStart);try{X.mark(e,{startTime:f})}catch(k){}}e=px(c||"");e.tick[a]=b||
V();if(e.callback&&e.callback[a])for(e=y(e.callback[a]),f=e.next();!f.done;f=e.next())f=f.value,f();e=lx(c);e.gelTicks&&(e.gelTicks[a]=!0);f=kx(c);e=b||V();S("log_repeated_ytcsi_ticks")?a in f||(f[a]=e):f[a]=e;f=hx(c).cttAuthInfo;a==="_start"?(a=vx(),wx(a,"baseline_"+d)||dp("latencyActionBaselined",{clientActionNonce:d},{timestamp:b,cttAuthInfo:f})):vx().tick(a,d,b,f);Ix(c);return e}}}
function Jx(){var a=document;if("visibilityState"in a)a=a.visibilityState;else{var b=Qs+"VisibilityState";a=b in a?a[b]:void 0}switch(a){case "hidden":return 0;case "visible":return 1;case "prerender":return 2;case "unloaded":return 3;default:return-1}}
function Kx(){function a(f,g,h){g=g.match("_rid")?g.split("_rid")[0]:g;typeof h==="number"&&(h=JSON.stringify(h));f.requestIds?f.requestIds.push({endpoint:g,id:h}):f.requestIds=[{endpoint:g,id:h}]}
for(var b={},c=y(Object.entries(R("TIMING_INFO",{}))),d=c.next();!d.done;d=c.next()){var e=y(d.value);d=e.next().value;e=e.next().value;switch(d){case "GetBrowse_rid":a(b,d,e);break;case "GetGuide_rid":a(b,d,e);break;case "GetHome_rid":a(b,d,e);break;case "GetPlayer_rid":a(b,d,e);break;case "GetSearch_rid":a(b,d,e);break;case "GetSettings_rid":a(b,d,e);break;case "GetTrending_rid":a(b,d,e);break;case "GetWatchNext_rid":a(b,d,e);break;case "yt_red":b.isRedSubscriber=!!e;break;case "yt_ad":b.isMonetized=
!!e}}return b}
function Lx(a,b){a=document.querySelector(a);if(!a)return!1;var c="",d=a.nodeName;d==="SCRIPT"?(c=a.src,c||(c=a.getAttribute("data-timing-href"))&&(c=window.location.protocol+c)):d==="LINK"&&(c=a.href);Db(document)&&a.setAttribute("nonce",Db(document));return c?(a=X.getEntriesByName(c))&&a[0]&&(a=a[0],c=Bx(),Hx("rsf_"+b,c+Math.round(a.fetchStart)),Hx("rse_"+b,c+Math.round(a.responseEnd)),a.transferSize!==void 0&&a.transferSize===0)?!0:!1:!1}
function Mx(){var a=window.location.protocol,b=X.getEntriesByType("resource");b=Rb(b,function(c){return c.name.indexOf(a+"//fonts.gstatic.com/s/")===0});
(b=Tb(b,function(c,d){return d.duration>c.duration?d:c},{duration:0}))&&b.startTime>0&&b.responseEnd>0&&(Hx("wffs",Ax(b.startTime)),Hx("wffe",Ax(b.responseEnd)))}
function Nx(a){var b=Ox("aft",a);if(b)return b;b=R((a||"")+"TIMING_AFT_KEYS",["ol"]);for(var c=b.length,d=0;d<c;d++){var e=Ox(b[d],a);if(e)return e}return NaN}
function Ox(a,b){if(a=kx(b)[a])return typeof a==="number"?a:a[a.length-1]}
function Ix(a){var b=Ox("_start",a),c=Nx(a),d=!Cx;b&&c&&d&&(fr(sx,new rx(Math.round(c-b),a)),Cx=!0)}
function Px(){if(X.getEntriesByType){var a=X.getEntriesByType("paint");if(a=Ub(a,function(c){return c.name==="first-paint"}))return Ax(a.startTime)}var b;
S("csi_use_performance_navigation_timing")?b=X.getEntriesByType("first-paint")[0].startTime:b=X.timing.Vh;return b?Math.max(0,b):0}
;function Qx(a,b){Mm(function(){px("").info.actionType=a;b&&Im("TIMING_AFT_KEYS",b);Im("TIMING_ACTION",a);var c=Kx();Object.keys(c).length>0&&Fx(c);c={isNavigation:!0,actionType:qx[R("TIMING_ACTION")]||"LATENCY_ACTION_UNKNOWN"};var d=R("PREVIOUS_ACTION");d&&(c.previousAction=qx[d]||"LATENCY_ACTION_UNKNOWN");if(d=R("CLIENT_PROTOCOL"))c.httpProtocol=d;if(d=R("CLIENT_TRANSPORT"))c.transportProtocol=d;(d=mv())&&d!=="UNDEFINED_CSN"&&(c.clientScreenNonce=d);d=Jx();if(d===1||d===-1)c.isVisible=!0;jx();ix();
c.loadType="cold";d=ix();var e=zx(),f=Bx(),g=R("CSI_START_TIMESTAMP_MILLIS",0);g>0&&!S("embeds_web_enable_csi_start_override_killswitch")&&(f=g);f&&(Hx("srt",e.responseStart),d.prerender!==1&&Hx("_start",f,void 0));d=Px();d>0&&Hx("fpt",d);d=zx();d.isPerformanceNavigationTiming&&Fx({performanceNavigationTiming:!0},void 0);Hx("nreqs",d.requestStart,void 0);Hx("nress",d.responseStart,void 0);Hx("nrese",d.responseEnd,void 0);d.redirectEnd-d.redirectStart>0&&(Hx("nrs",d.redirectStart,void 0),Hx("nre",
d.redirectEnd,void 0));d.domainLookupEnd-d.domainLookupStart>0&&(Hx("ndnss",d.domainLookupStart,void 0),Hx("ndnse",d.domainLookupEnd,void 0));d.connectEnd-d.connectStart>0&&(Hx("ntcps",d.connectStart,void 0),Hx("ntcpe",d.connectEnd,void 0));d.secureConnectionStart>=Bx()&&d.connectEnd-d.secureConnectionStart>0&&(Hx("nstcps",d.secureConnectionStart,void 0),Hx("ntcpe",d.connectEnd,void 0));X&&"getEntriesByType"in X&&Mx();d=[];if(document.querySelector&&X&&X.getEntriesByName)for(var h in Ex)Ex.hasOwnProperty(h)&&
(e=Ex[h],Lx(h,e)&&d.push(e));if(d.length>0)for(c.resourceInfo=[],h=y(d),d=h.next();!d.done;d=h.next())c.resourceInfo.push({resourceCache:d.value});Fx(c);c=lx();c.preLoggedGelInfos||(c.preLoggedGelInfos=[]);h=c.preLoggedGelInfos;c=mx();d=void 0;for(e=0;e<h.length;e++)if(f=h[e],f.loadType){d=f.loadType;break}if(jx().loadType==="cold"&&(c.loadType==="cold"||d==="cold")){d=kx();e=lx();e=e.gelTicks?e.gelTicks:e.gelTicks={};for(var k in d)if(!(k in e))if(typeof d[k]==="number")Hx(k,Ox(k));else if(S("log_repeated_ytcsi_ticks"))for(f=
y(d[k]),g=f.next();!g.done;g=f.next())g=g.value,Hx(k.slice(1),g);k={};d=!1;h=y(h);for(e=h.next();!e.done;e=h.next())d=e.value,iw(c,d),iw(k,d),d=!0;d&&Fx(k)}E("ytglobal.timingready_",!0);k=R("TIMING_ACTION");F("ytglobal.timingready_")&&k&&Rx()&&Nx()&&Ix()})()}
function Rx(a){return Mm(function(){return Sx("_start",a)})()}
function Tx(a,b,c){Mm(Fx)(a,b,c===void 0?!1:c)}
function Ux(a,b,c){return Mm(Hx)(a,b,c)}
function Sx(a,b){return Mm(function(){var c=kx(b);return a in c})()}
function Vx(a){if(!S("universal_csi_network_ticks"))return"";a=jc(a)||"";for(var b=Object.keys(Yq),c=0;c<b.length;c++){var d=b[c];if(a.includes(d))return d}return""}
function Wx(a){if(!S("universal_csi_network_ticks"))return function(){};
var b=Yq[a];return b?(Xx(b),function(){var c=S("universal_csi_network_ticks")?(c=Zq[a])?Xx(c):!1:!1;return c}):function(){}}
function Xx(a){return Mm(function(){if(Sx(a))return!1;Ux(a,void 0,void 0);return!0})()}
function Yx(a){Mm(function(){if(!Rx("attestation_challenge_fetch")||Sx(a,"attestation_challenge_fetch"))return!1;Ux(a,void 0,"attestation_challenge_fetch");return!0})()}
function Zx(){Mm(function(){var a=nx();requestAnimationFrame(function(){setTimeout(function(){a===nx()&&Ux("ol",void 0,void 0)},0)})})()}
var $x=window;$x.ytcsi&&($x.ytcsi.infoGel=Tx,$x.ytcsi.tick=Ux);var ay="tokens consistency service_params mss client_location entities adblock_detection response_received_commands store PLAYER_PRELOAD shorts_prefetch".split(" "),by=["type.googleapis.com/youtube.api.pfiinnertube.YoutubeApiInnertube.BrowseResponse","type.googleapis.com/youtube.api.pfiinnertube.YoutubeApiInnertube.PlayerResponse"];function cy(a,b,c,d){this.u=a;this.fa=b;this.j=c;this.o=d;this.i=void 0;this.h=new Map;a.cc||(a.cc={});a.cc=Object.assign({},gx,a.cc)}
function dy(a,b,c,d){if(cy.instance!==void 0){if(d=cy.instance,a=[a!==d.u,b!==d.fa,c!==d.j,!1,!1,!1,void 0!==d.i],a.some(function(e){return e}))throw new T("InnerTubeTransportService is already initialized",a);
}else cy.instance=new cy(a,b,c,d)}
function ey(a){var b={signalServiceEndpoint:{signal:"GET_DATASYNC_IDS"}};var c=c===void 0?Tn:c;var d=fy(a,b);return d?new vi(function(e,f){var g,h,k,l,m;return B(function(n){switch(n.h){case 1:return n.yield(d,2);case 2:g=n.i;h=g.u(b,void 0,c);if(!h){f(new T("Error: Failed to build request for command.",b));n.B(0);break}Jw(h.input);l=((k=h.ab)==null?void 0:k.mode)==="cors"?"cors":void 0;if(a.j.Qd){m=gy(h.config,l);n.B(4);break}return n.yield(hy(h.config,l),5);case 5:m=n.i;case 4:e(iy(a,h,m)),n.h=
0}})}):Ai(new T("Error: No request builder found for command.",b))}
function jy(a,b){function c(){}
var d="/youtubei/v1/"+bx(Pv);var e=e===void 0?{Ob:{identity:Tn}}:e;var f=f===void 0?!0:f;c=Wx(Vx(d));b.context||(b.context=Vw(void 0,f));return new vi(function(g){var h,k,l,m,n;return B(function(r){if(r.h==1)return h=wv(d),k=Zm(h)?"same-origin":"cors",a.j.Qd?(l=gy(e,k),r.B(2)):r.yield(hy(e,k),3);r.h!=2&&(l=r.i);m=xv(wv(d));n={input:m,ab:yv(m),Ga:b,config:e};g(iy(a,n,l,c));r.h=0})})}
function ky(a,b,c){var d;if(b&&!(b==null?0:(d=b.sequenceMetaData)==null?0:d.skipProcessing)&&a.o){d=y(ay);for(var e=d.next();!e.done;e=d.next())e=e.value,a.o[e]&&a.o[e].handleResponse(b,c)}}
function iy(a,b,c,d){d=d===void 0?function(){}:d;
var e,f,g,h,k,l,m,n,r,t,w,x,z,G,H,U,Z,mb,Qb,ca,$a,Pa,Qa,Oa,vh,wh,Ts,Us,Vs,Ws;return B(function(ia){switch(ia.h){case 1:ia.B(2);break;case 3:if((e=ia.i)&&!e.isExpired())return ia.return(Promise.resolve(e.h()));case 2:if(!((f=b)==null?0:(g=f.Ga)==null?0:g.context)){ia.B(4);break}h=b.Ga.context;ia.B(5);break;case 5:k=y([]),l=k.next();case 8:if(l.done){ia.B(4);break}m=l.value;return ia.yield(m.Wh(h),9);case 9:l=k.next();ia.B(8);break;case 4:if((n=a.i)==null||!n.fi(b.input,b.Ga)){ia.B(12);break}return ia.yield(a.i.Qh(b.input,
b.Ga),13);case 13:return r=ia.i,ky(a,r,b),ia.return(r);case 12:return(x=(w=b.config)==null?void 0:w.Zh)&&a.h.has(x)?t=a.h.get(x):(z=JSON.stringify(b.Ga),U=(H=(G=b.ab)==null?void 0:G.headers)!=null?H:{},b.ab=Object.assign({},b.ab,{headers:Object.assign({},U,c)}),Z=Object.assign({},b.ab),b.ab.method==="POST"&&(Z=Object.assign({},Z,{body:z})),((mb=b.config)==null?0:mb.bf)&&Ux(b.config.bf),Qb=function(){return a.fa.fetch(b.input,Z,b.config)},t=Qb(),x&&a.h.set(x,t)),ia.yield(t,14);
case 14:(ca=ia.i)&&S("web_streaming_player")&&Array.isArray(ca)&&(ca=ca[0].playerResponse);if(ca&&"error"in ca&&(($a=ca)==null?0:(Pa=$a.error)==null?0:Pa.details))for(Qa=ca.error.details,Oa=y(Qa),vh=Oa.next();!vh.done;vh=Oa.next())wh=vh.value,(Ts=wh["@type"])&&by.indexOf(Ts)>-1&&(delete wh["@type"],ca=wh);x&&a.h.has(x)&&a.h.delete(x);((Us=b.config)==null?0:Us.cf)&&Ux(b.config.cf);if(ca||(Vs=a.i)==null||!Vs.Dh(b.input,b.Ga)){ia.B(15);break}return ia.yield(a.i.Ph(b.input,b.Ga),16);case 16:ca=ia.i;case 15:return ky(a,
ca,b),((Ws=b.config)==null?0:Ws.Ye)&&Ux(b.config.Ye),d(),ia.return(ca||void 0)}})}
function fy(a,b){a:{a=a.u;var c,d=(c=bu(b,nm))==null?void 0:c.signal;if(d&&a.cc&&(c=a.cc[d])){var e=c();break a}var f;if((c=(f=bu(b,lm))==null?void 0:f.request)&&a.le&&(f=a.le[c])){e=f();break a}for(e in b)if(a.Lc[e]&&(b=a.Lc[e])){e=b();break a}e=void 0}if(e!==void 0)return Promise.resolve(e)}
function hy(a,b){var c,d,e,f;return B(function(g){if(g.h==1){e=(c=a)==null?void 0:(d=c.Ob)==null?void 0:d.sessionIndex;var h=g.yield;var k=Sn(0,{sessionIndex:e});if(!(k instanceof vi)){var l=new vi(ti);wi(l,2,k);k=l}return h.call(g,k,2)}f=g.i;return g.return(Promise.resolve(Object.assign({},Ww(b),f)))})}
function gy(a,b){var c;a=a==null?void 0:(c=a.Ob)==null?void 0:c.sessionIndex;c=Sn(0,{sessionIndex:a});return Object.assign({},Ww(b),c)}
;var ly=new ut("INNERTUBE_TRANSPORT_TOKEN");function my(){}
v(my,dx);my.prototype.j=function(){return Vv};
my.prototype.i=function(a){return bu(a,zm)||void 0};
my.prototype.h=function(a,b,c){c=c===void 0?{}:c;b.channelIds&&(a.channelIds=b.channelIds);b.siloName&&(a.siloName=b.siloName);b.params&&(a.params=b.params);c.botguardResponse&&(a.botguardResponse=c.botguardResponse);c.feature&&(a.clientFeature=c.feature)};
ea.Object.defineProperties(my.prototype,{o:{configurable:!0,enumerable:!0,get:function(){return!0}}});function ny(){}
v(ny,dx);ny.prototype.j=function(){return Wv};
ny.prototype.i=function(a){return bu(a,ym)||void 0};
ny.prototype.h=function(a,b){b.channelIds&&(a.channelIds=b.channelIds);b.siloName&&(a.siloName=b.siloName);b.params&&(a.params=b.params)};
ea.Object.defineProperties(ny.prototype,{o:{configurable:!0,enumerable:!0,get:function(){return!0}}});var oy=new ut("SHARE_CLIENT_PARAMS_PROVIDER_TOKEN");function py(a){this.H=a}
v(py,dx);py.prototype.j=function(){return Qv};
py.prototype.i=function(a){return bu(a,rm)||bu(a,sm)||bu(a,qm)};
py.prototype.h=function(a,b){b.serializedShareEntity&&(a.serializedSharedEntity=b.serializedShareEntity);if(b.clientParamIdentifier){var c;if((c=this.H)==null?0:c.h(b.clientParamIdentifier))a.clientParams=this.H.i(b.clientParamIdentifier)}};
py[tt]=[oy];function qy(){}
v(qy,dx);qy.prototype.j=function(){return Sv};
qy.prototype.i=function(a){return bu(a,pm)||void 0};
qy.prototype.h=function(a,b,c){a.feedbackTokens=[];b.feedbackToken&&a.feedbackTokens.push(b.feedbackToken);if(b=b.cpn||c.cpn)a.feedbackContext={cpn:b};a.isFeedbackTokenUnencrypted=!!c.is_feedback_token_unencrypted;a.shouldMerge=!1;c.extra_feedback_tokens&&(a.shouldMerge=!0,a.feedbackTokens=a.feedbackTokens.concat(c.extra_feedback_tokens))};
ea.Object.defineProperties(qy.prototype,{o:{configurable:!0,enumerable:!0,get:function(){return!0}}});function ry(){}
v(ry,dx);ry.prototype.j=function(){return Tv};
ry.prototype.i=function(a){return bu(a,wm)||void 0};
ry.prototype.h=function(a,b){b.params&&(a.params=b.params);b.secondaryParams&&(a.secondaryParams=b.secondaryParams)};function sy(){}
v(sy,dx);sy.prototype.j=function(){return Uv};
sy.prototype.i=function(a){return bu(a,um)||void 0};
sy.prototype.h=function(a,b){b.actions&&(a.actions=b.actions);b.params&&(a.params=b.params);b.playlistId&&(a.playlistId=b.playlistId)};function ty(){}
v(ty,dx);ty.prototype.j=function(){return Rv};
ty.prototype.i=function(a){return bu(a,tm)};
ty.prototype.h=function(a,b,c){c=c===void 0?{}:c;b.serializedShareEntity&&(a.serializedSharedEntity=b.serializedShareEntity);c.includeListId&&(a.includeListId=!0)};var uy=new ut("FETCH_FN_TOKEN"),vy=new ut("PARSE_FN_TOKEN"),wy=new ut("WINDOW_REQUEST_TOKEN"),xy=new ut("TEXT_DECODER_TOKEN");function yy(a,b){var c=C.apply(2,arguments);a=a===void 0?0:a;T.call(this,b,c);this.errorType=a;Object.setPrototypeOf(this,this.constructor.prototype)}
v(yy,T);var zy=new ut("NETWORK_SLI_TOKEN");function Ay(a,b,c,d){this.h=a;this.i=b;this.j=c;this.o=d}
Ay.prototype.fetch=function(a,b,c){var d=this,e,f,g;return B(function(h){e=By(d,a,b);g=(f=d.i)!=null?f:fetch;return h.return(g(e).then(function(k){return d.handleResponse(k,c)}).catch(function(k){Uu(k);
if((c==null?0:c.ue)&&k instanceof yy&&k.errorType===1)return Promise.reject(k)}))})};
function By(a,b,c){if(a.h){var d=jc(tc(b,"key"))||"/UNKNOWN_PATH";a.h.start(d)}d=c;S("wug_networking_gzip_request")&&(d=Hr(c));var e;return new ((e=a.o)!=null?e:window.Request)(b,d)}
Ay.prototype.handleResponse=function(a,b){var c,d=(c=this.j)!=null?c:JSON.parse;c=a.text().then(function(e){if((b==null?0:b.Ke)&&a.ok)return Nf(b.Ke,e);e=e.replace(")]}'","");if((b==null?0:b.ue)&&e)try{var f=d(e)}catch(h){throw new yy(1,"JSON parsing failed after fetch");}var g;return(g=f)!=null?g:d(e)});
a.redirected||a.ok?this.h&&this.h.success():(this.h&&this.h.Jh(),c=c.then(function(e){Uu(new T("Error: API fetch failed",a.status,a.url,e));return Object.assign({},e,{errorMetadata:{status:a.status}})}));
return c};
Ay[tt]=[wt(zy),wt(uy),wt(vy),wt(wy),wt(xy)];var Cy=new ut("NETWORK_MANAGER_TOKEN");var Dy;function Ey(a){var b=new tj;if(a.interpreterJavascript){var c=dm(a.interpreterJavascript);c=Gb(c).toString();var d=new rj;Kf(d,6,c);Ff(b,rj,1,d,be)}else a.interpreterUrl&&(c=em(a.interpreterUrl),c=nb(c).toString(),d=new sj,Kf(d,4,c),Ff(b,sj,2,d,be));a.interpreterHash&&Lf(b,3,a.interpreterHash);a.program&&Lf(b,4,a.program);a.globalName&&Lf(b,5,a.globalName);a.clientExperimentsStateBlob&&Lf(b,7,a.clientExperimentsStateBlob);return b}
function Fy(a){var b={};a=y(a.split("&"));for(var c=a.next();!c.done;c=a.next())c=c.value.split("="),c.length===2&&(b[c[0]]=c[1]);return b}
;function zc(){if(S("bg_st_hr"))return"havuokmhhs-0";var a,b=((a=performance)==null?void 0:a.timeOrigin)||0;return"havuokmhhs-"+Math.floor(b)}
function Gy(a){this.h=a}
Gy.prototype.bindInnertubeChallengeFetcher=function(a){this.h.bicf(a)};
Gy.prototype.registerChallengeFetchedCallback=function(a){this.h.bcr(a)};
Gy.prototype.getLatestChallengeResponse=function(){return this.h.blc()};
function Hy(){return new Promise(function(a){var b=window;b.ntpevasrs!==void 0?a(new Gy(b.ntpevasrs)):(b.ntpqfbel===void 0&&(b.ntpqfbel=[]),b.ntpqfbel.push(function(c){a(new Gy(c))}))})}
;var Iy=pa(["https://static.doubleclick.net/instream/ad_status.js"]),Jy=[],Ky=function(a){var b=C.apply(1,arguments);if(b.length===0)return lb(a[0]);for(var c=a[0],d=0;d<b.length;d++)c+=encodeURIComponent(b[d])+a[d+1];return lb(c)}(Iy),Ly=!1;
function My(){if(zv()){var a=R("PLAYER_VARS",{});if(yg(a)!="1"&&!Bv(a)){var b=function(){Ly=!0;"google_ad_status"in window?Im("DCLKSTAT",1):Im("DCLKSTAT",2)};
try{Zv(Ky,b)}catch(c){}Jy.push(Wj.pa(function(){if(!(Ly||"google_ad_status"in window)){try{cw(Ky.toString(),b)}catch(c){}Ly=!0;Im("DCLKSTAT",3)}},5E3))}}}
function Ny(){var a=Number(R("DCLKSTAT",0));return isNaN(a)?0:a}
;function Y(a){this.h=a}
[new Y("b.f_"),new Y("j.s_"),new Y("r.s_"),new Y("e.h_"),new Y("i.s_"),new Y("s.t_"),new Y("p.h_"),new Y("s.i_"),new Y("f.i_"),new Y("a.b_"),new Y("a.o_"),new Y("g.o_"),new Y("p.i_"),new Y("p.m_"),new Y("n.k_"),new Y("i.f_"),new Y("a.s_"),new Y("m.c_"),new Y("n.h_"),new Y("o.p_"),new Y("m.p_"),new Y("o.a_"),new Y("d.p_"),new Y("e.i_")].reduce(function(a,b){a[b.h]=b;return a},{});function Oy(a,b,c){var d=this;this.network=a;this.options=b;this.o=c;this.h=null;if(b.Ef){var e=new yj;this.h=e.promise;D.ytAtRC&&Wj.Sa(function(){var f,g;return B(function(h){if(h.h==1){if(!D.ytAtRC)return h.return();f=Py(null);return h.yield(d.ib(f),2)}g=h.i;D.ytAtRC&&D.ytAtRC(JSON.stringify(g));h.h=0})},2);
Hy().then(function(f){var g,h,k,l;return B(function(m){if(m.h==1)return f.bindInnertubeChallengeFetcher(function(n){return d.ib(Py(n))}),m.yield(yc(),2);
g=m.i;h=f.getLatestChallengeResponse();k=h.challenge;if(!k)throw Error("BGE_MACIL");l={challenge:k,gb:Fy(k),vm:g,bgChallenge:new tj};e.resolve(l);f.registerChallengeFetchedCallback(function(n){n=n.challenge;if(!n)throw Error("BGE_MACR");n={challenge:n,gb:Fy(n),vm:g,bgChallenge:new tj};d.h=Promise.resolve(n)});
m.h=0})})}else b.preload&&Qy(this,new Promise(function(f){oo(function(){f(Ry(d))},0)}))}
Oy.prototype.j=function(){var a=this;return B(function(b){return b.h==1?b.yield(Promise.race([a.h,null]),2):b.return(!!b.i)})};
Oy.prototype.i=function(a,b,c){var d=this,e,f,g;return B(function(h){d.h===null&&Qy(d,Ry(d));e=!1;f={};g=function(){var k,l,m;return B(function(n){switch(n.h){case 1:return n.yield(d.h,2);case 2:k=n.i;f.challenge=k.challenge;if(!k.vm){"c1a"in k.gb&&(f.error="ATTESTATION_ERROR_VM_NOT_INITIALIZED");n.B(3);break}l=Object.assign({},{c:k.challenge,e:a},b);wa(n,4);e=!0;return n.yield(k.vm.snapshot({Pb:l}),6);case 6:(m=n.i)?f.webResponse=m:f.error="ATTESTATION_ERROR_VM_NO_RESPONSE";xa(n,3);break;case 4:ya(n),
f.error="ATTESTATION_ERROR_VM_INTERNAL_ERROR";case 3:if(a==="ENGAGEMENT_TYPE_PLAYBACK"){var r=k.gb,t={};r.c6a&&(t.reportingStatus=String(Number(r.c)^Ny()));r.c6b&&(t.broadSpectrumDetectionResult=String(Number(r.c)^Number(R("CATSTAT",0))));f.adblockReporting=t}return n.return(f)}})};
return h.return(Promise.race([g(),Sy(c,function(){var k=Object.assign({},f);e&&(k.error="ATTESTATION_ERROR_VM_TIMEOUT");return k})]))})};
function Py(a){var b={engagementType:"ENGAGEMENT_TYPE_UNBOUND"};a&&(b.interpreterHash=a);return b}
function Ry(a,b){b=b===void 0?0:b;var c,d,e,f,g,h,k,l,m,n,r,t;return B(function(w){switch(w.h){case 1:c=Py(Dj().h);if(S("att_fet_ks"))return wa(w,7),w.yield(a.ib(c),9);wa(w,4);return w.yield(Ty(a,c),6);case 6:g=w.i;e=g.Te;f=g.Ue;d=g;xa(w,3);break;case 4:return ya(w),Uu(Error("Failed to fetch attestation challenge after "+(b+" attempts; not retrying for 24h."))),Uy(a,864E5),w.return({challenge:"",gb:{},vm:void 0,bgChallenge:void 0});case 9:d=w.i;if(!d)throw Error("Fetching Attestation challenge returned falsy");
if(!d.challenge)throw Error("Missing Attestation challenge");e=d.challenge;f=Fy(e);if("c1a"in f&&(!d.bgChallenge||!d.bgChallenge.program))throw Error("Expected bg challenge but missing.");xa(w,3);break;case 7:h=ya(w);Uu(h);b++;if(b>=5)return Uu(Error("Failed to fetch attestation challenge after "+(b+" attempts; not retrying for 24h."))),Uy(a,864E5),w.return({challenge:"",gb:{},vm:void 0,bgChallenge:void 0});k=1E3*Math.pow(2,b-1)+Math.random()*1E3;return w.return(new Promise(function(x){oo(function(){x(Ry(a,
b))},k)}));
case 3:l=Number(f.t)||7200;Uy(a,l*1E3);m=void 0;if(!("c1a"in f&&d.bgChallenge)){w.B(10);break}n=Ey(d.bgChallenge);wa(w,11);return w.yield(Ej(Dj(),n),13);case 13:xa(w,12);break;case 11:return r=ya(w),Uu(r),w.return({challenge:e,gb:f,vm:m,bgChallenge:n});case 12:return wa(w,14),m=new Aj({challenge:n,Dd:{Da:"aGIf"}}),w.yield(m.hd,16);case 16:xa(w,10);break;case 14:t=ya(w),Uu(t),m=void 0;case 10:return w.return({challenge:e,gb:f,vm:m,bgChallenge:n})}})}
Oy.prototype.ib=function(a){var b=this,c;return B(function(d){c=b.o;if(!c||c.ta())return d.return(b.network.ib(a));Yx("att_pna");return d.return(new Promise(function(e){ai(c,"publicytnetworkstatus-online",function(){b.network.ib(a).then(e)})}))})};
function Vy(a){if(!a)throw Error("Fetching Attestation challenge returned falsy");if(!a.challenge)throw Error("Missing Attestation challenge");var b=a.challenge,c=Fy(b);if("c1a"in c&&(!a.bgChallenge||!a.bgChallenge.program))throw Error("Expected bg challenge but missing.");return Object.assign({},a,{Te:b,Ue:c})}
function Ty(a,b){var c,d,e,f,g;return B(function(h){switch(h.h){case 1:c=void 0,d=0,e={};case 2:if(!(d<5)){h.B(4);break}if(!(d>0)){h.B(5);break}e.sd=1E3*Math.pow(2,d-1)+Math.random()*1E3;return h.yield(new Promise(function(k){return function(l){oo(function(){l(void 0)},k.sd)}}(e)),5);
case 5:return wa(h,7),h.yield(a.ib(b),9);case 9:return f=h.i,h.return(Vy(f));case 7:c=g=ya(h),g instanceof Error&&Uu(g);case 8:d++;e={sd:void 0};h.B(2);break;case 4:throw c;}})}
function Qy(a,b){a.h=b}
function Wy(a){var b,c,d;return B(function(e){if(e.h==1)return e.yield(Promise.race([a.h,null]),2);b=e.i;var f=Ry(a);a.h=f;(c=b)==null||(d=c.vm)==null||d.dispose();e.h=0})}
function Uy(a,b){function c(){var e;return B(function(f){e=d-Date.now();return e<1E3?f.yield(Wy(a),0):(oo(c,Math.min(e,6E4)),f.B(0))})}
var d=Date.now()+b;c()}
function Sy(a,b){return new Promise(function(c){oo(function(){c(b())},a)})}
;function Xy(a){this.h=a}
Xy.prototype.ib=function(a){Yx("att_fsr");return jy(this.h,a).then(function(b){Yx("att_frr");return b})};function Yy(){var a,b,c;return B(function(d){if(d.h==1)return a=Dt().resolve(ly),a?d.yield(ey(a),2):(Uu(Error("InnertubeTransportService unavailable in fetchDatasyncIds")),d.return(void 0));if(b=d.i){if(b.errorMetadata)return Uu(Error("Datasync IDs fetch responded with "+b.errorMetadata.status+": "+b.error)),d.return(void 0);c=b.Fh;return d.return(c)}Uu(Error("Network request to get Datasync IDs failed."));return d.return(void 0)})}
;function Zy(){}
v(Zy,dx);Zy.prototype.j=function(){return Sv};
Zy.prototype.i=function(a){return bu(a,xm)};
Zy.prototype.h=function(a,b){b.undoToken&&(a.feedbackTokens=[b.undoToken]);b.isUndoTokenUnencrypted&&(a.isFeedbackTokenUnencrypted=b.isUndoTokenUnencrypted)};
ea.Object.defineProperties(Zy.prototype,{o:{configurable:!0,enumerable:!0,get:function(){return!0}}});function $y(){var a=a===void 0?Wu:a;var b=b===void 0?{}:b;E("yt.logging.errors.log",Tu);Su();Hn(Gn(),b);window.onerror=a;Mi=Vu;window.addEventListener("unhandledrejection",function(c){if(c.reason instanceof Error){var d=c.reason;Xu(d,{source:"unhandledrejection"});d.name==="AbortError"&&(d.level="WARNING")}Vu(c.reason);c.preventDefault()})}
;function az(){var a;return(a=R("WEB_PLAYER_CONTEXT_CONFIGS"))==null?void 0:a.WEB_PLAYER_CONTEXT_CONFIG_ID_EMBEDDED_PLAYER}
;var bz=D.caches,cz;function dz(a){var b=a.indexOf(":");return b===-1?{Gd:a}:{Gd:a.substring(0,b),datasyncId:a.substring(b+1)}}
function ez(){return B(function(a){if(cz!==void 0)return a.return(cz);cz=new Promise(function(b){var c;return B(function(d){switch(d.h){case 1:return wa(d,2),d.yield(bz.open("test-only"),4);case 4:return d.yield(bz.delete("test-only"),5);case 5:xa(d,3);break;case 2:if(c=ya(d),c instanceof Error&&c.name==="SecurityError")return b(!1),d.return();case 3:b("caches"in window),d.h=0}})});
return a.return(cz)})}
function fz(a){var b,c,d,e,f,g,h;B(function(k){if(k.h==1)return k.yield(ez(),2);if(k.h!=3){if(!k.i)return k.return(!1);b=[];return k.yield(bz.keys(),3)}c=k.i;d=y(c);for(e=d.next();!e.done;e=d.next())f=e.value,g=dz(f),h=g.datasyncId,!h||a.includes(h)||b.push(bz.delete(f));return k.return(Promise.all(b).then(function(l){return l.some(function(m){return m})}))})}
function gz(){var a,b,c,d,e,f,g;return B(function(h){if(h.h==1)return h.yield(ez(),2);if(h.h!=3){if(!h.i)return h.return(!1);a=mo("cache contains other");return h.yield(bz.keys(),3)}b=h.i;c=y(b);for(d=c.next();!d.done;d=c.next())if(e=d.value,f=dz(e),(g=f.datasyncId)&&g!==a)return h.return(!0);return h.return(!1)})}
;function hz(){try{return!!self.sessionStorage}catch(a){return!1}}
;function iz(a){a=a.match(/(.*)::.*::.*/);if(a!==null)return a[1]}
function jz(a){if(hz()){var b=Object.keys(window.sessionStorage);b=y(b);for(var c=b.next();!c.done;c=b.next()){c=c.value;var d=iz(c);d===void 0||a.includes(d)||self.sessionStorage.removeItem(c)}}}
function kz(){if(!hz())return!1;var a=mo(),b=Object.keys(window.sessionStorage);b=y(b);for(var c=b.next();!c.done;c=b.next())if(c=iz(c.value),c!==void 0&&c!==a)return!0;return!1}
;function lz(){Yy().then(function(a){a&&(sq(a),fz(a),Ew(a),jz(a))})}
function mz(){var a=new Bs;Wj.pa(function(){var b,c,d,e,f;return B(function(g){switch(g.h){case 1:if(S("ytidb_clear_optimizations_killswitch")){g.B(2);break}b=mo("clear");if(b.startsWith("V")&&b.endsWith("||")){var h=[b];sq(h);fz(h);Ew(h);jz(h);return g.return()}c=Fw();d=kz();return g.yield(gz(),3);case 3:return e=g.i,g.yield(tq(),4);case 4:if(f=g.i,!(c||d||e||f))return g.return();case 2:a.ta()?lz():ai(a,"publicytnetworkstatus-online",lz),g.h=0}})})}
;var nz=["www.youtube-nocookie.com","www.youtubeeducation.com","youtube.googleapis.com"];function oz(){this.state=1;this.vm=null;this.h=void 0}
p=oz.prototype;p.initialize=function(a,b,c,d){this.h=d;if(a.program){var e;d=(e=a.interpreterUrl)!=null?e:null;if(a.interpreterSafeScript)e=dm(a.interpreterSafeScript);else{var f;e=(f=a.interpreterScript)!=null?f:null}a.interpreterSafeUrl&&(d=em(a.interpreterSafeUrl).toString());pz(this,e,d,a.program,b,c)}else Uu(Error("BL:CIP"))};
function pz(a,b,c,d,e,f){var g=g===void 0?"trayride":g;c?(a.state=2,Zv(fm(c),function(){window[g]?qz(a,d,g,e):(a.state=3,aw(c),Uu(new T("BL:ULB",""+c)))},f)):b?(f=Hg("SCRIPT"),b instanceof Eb?(f.textContent=Gb(b),Hb(f)):f.textContent=b,f.nonce=Db(document),document.head.appendChild(f),document.head.removeChild(f),window[g]?qz(a,d,g,e):(a.state=4,Uu(new T("BL:ULBJ")))):Uu(new T("BL:ULV"))}
p.isLoading=function(){return this.state===2};
function qz(a,b,c,d){a.state=5;var e=!!a.h&&nz.includes(ic(a.h)||"");try{var f=new Aj({program:b,globalName:c,Dd:{disable:!S("att_web_record_metrics")||!S("att_skip_metrics_for_cookieless_domains_ks")&&e,Da:"aGIf"}});f.hd.then(function(){a.state=6;d&&d(b)});
a.gd(f)}catch(g){a.state=7,g instanceof Error&&Uu(g)}}
p.invoke=function(a){a=a===void 0?{}:a;return this.od()?this.Td({Pb:a}):null};
p.dispose=function(){this.gd(null);this.state=8};
p.od=function(){return!!this.vm};
p.Td=function(a){return this.vm.Od(a)};
p.gd=function(a){vc(this.vm);this.vm=a};function rz(){var a=F("yt.abuse.playerAttLoader");return a&&["bgvma","bgvmb","bgvmc"].every(function(b){return b in a})?a:null}
;function sz(){oz.apply(this,arguments)}
v(sz,oz);sz.prototype.gd=function(a){var b;(b=rz())==null||b.bgvma();a?(b={bgvma:a.dispose.bind(a),bgvmb:a.snapshot.bind(a),bgvmc:a.Od.bind(a)},E("yt.abuse.playerAttLoader",b),E("yt.abuse.playerAttLoaderRun",function(c){return a.snapshot(c)})):(E("yt.abuse.playerAttLoader",null),E("yt.abuse.playerAttLoaderRun",null))};
sz.prototype.od=function(){return!!rz()};
sz.prototype.Td=function(a){return rz().bgvmc(a)};var tz=new ut("AUTH_SERVICE_TOKEN");function uz(a){Nt.call(this,a===void 0?"document_active":a);var b=this;this.o=10;this.h=new Map;this.transitions=[{from:"document_active",to:"document_disposed_preventable",action:this.G},{from:"document_active",to:"document_disposed",action:this.u},{from:"document_disposed_preventable",to:"document_disposed",action:this.u},{from:"document_disposed_preventable",to:"flush_logs",action:this.H},{from:"document_disposed_preventable",to:"document_active",action:this.i},{from:"document_disposed",to:"flush_logs",
action:this.H},{from:"document_disposed",to:"document_active",action:this.i},{from:"document_disposed",to:"document_disposed",action:function(){}},
{from:"flush_logs",to:"document_active",action:this.i}];window.addEventListener("pagehide",function(c){b.transition("document_disposed",{event:c})});
window.addEventListener("beforeunload",function(c){b.transition("document_disposed_preventable",{event:c})})}
v(uz,Nt);uz.prototype.G=function(a,b){if(!this.h.get("document_disposed_preventable")){a(b==null?void 0:b.event);var c,d;if((b==null?0:(c=b.event)==null?0:c.defaultPrevented)||(b==null?0:(d=b.event)==null?0:d.returnValue)){b.event.returnValue||(b.event.returnValue=!0);b.event.defaultPrevented||b.event.preventDefault();this.h=new Map;this.transition("document_active");return}}this.h.set("document_disposed_preventable",!0);this.h.get("document_disposed")?this.transition("flush_logs"):this.transition("document_disposed")};
uz.prototype.u=function(a,b){this.h.get("document_disposed")?this.transition("document_active"):(a(b==null?void 0:b.event),this.h.set("document_disposed",!0),this.transition("flush_logs"))};
uz.prototype.H=function(a,b){a(b==null?void 0:b.event);this.transition("document_active")};
uz.prototype.i=function(){this.h=new Map};function vz(a){Nt.call(this,a===void 0?"document_visibility_unknown":a);var b=this;this.transitions=[{from:"document_visibility_unknown",to:"document_visible",action:this.i},{from:"document_visibility_unknown",to:"document_hidden",action:this.h},{from:"document_visibility_unknown",to:"document_foregrounded",action:this.H},{from:"document_visibility_unknown",to:"document_backgrounded",action:this.u},{from:"document_visible",to:"document_hidden",action:this.h},{from:"document_visible",to:"document_foregrounded",
action:this.H},{from:"document_visible",to:"document_visible",action:this.i},{from:"document_foregrounded",to:"document_visible",action:this.i},{from:"document_foregrounded",to:"document_hidden",action:this.h},{from:"document_foregrounded",to:"document_foregrounded",action:this.H},{from:"document_hidden",to:"document_visible",action:this.i},{from:"document_hidden",to:"document_backgrounded",action:this.u},{from:"document_hidden",to:"document_hidden",action:this.h},{from:"document_backgrounded",to:"document_hidden",
action:this.h},{from:"document_backgrounded",to:"document_backgrounded",action:this.u},{from:"document_backgrounded",to:"document_visible",action:this.i}];document.addEventListener("visibilitychange",function(c){document.visibilityState==="visible"?b.transition("document_visible",{event:c}):b.transition("document_hidden",{event:c})});
S("visibility_lifecycles_dynamic_backgrounding")&&(window.addEventListener("blur",function(c){b.transition("document_backgrounded",{event:c})}),window.addEventListener("focus",function(c){b.transition("document_foregrounded",{event:c})}))}
v(vz,Nt);vz.prototype.i=function(a,b){a(b==null?void 0:b.event);S("visibility_lifecycles_dynamic_backgrounding")&&this.transition("document_foregrounded")};
vz.prototype.h=function(a,b){a(b==null?void 0:b.event);S("visibility_lifecycles_dynamic_backgrounding")&&this.transition("document_backgrounded")};
vz.prototype.u=function(a,b){a(b==null?void 0:b.event)};
vz.prototype.H=function(a,b){a(b==null?void 0:b.event)};function wz(){this.o=new uz;this.u=new vz}
wz.prototype.install=function(){var a=C.apply(0,arguments),b=this;a.forEach(function(c){b.o.install(c)});
a.forEach(function(c){b.u.install(c)})};function xz(){this.o=[];this.i=new Map;this.h=new Map;this.j=new Set}
xz.prototype.clickCommand=function(a,b,c){var d=a.clickTrackingParams;c=c===void 0?0:c;if(d)if(c=mv(c===void 0?0:c)){a=this.client;d=new fv({trackingParams:d});var e=void 0;if(S("no_client_ve_attach_unless_shown")){var f=zw(d,c);vw.set(f,!0);Aw(d,c)}e=e||"INTERACTION_LOGGING_GESTURE_TYPE_GENERIC_CLICK";f=yw({cttAuthInfo:ov(c)||void 0},c);d={csn:c,ve:d.getAsJson(),gestureType:e};b&&(d.clientData=b);c==="UNDEFINED_CSN"?Bw("visualElementGestured",f,d):a?Ku("visualElementGestured",d,a,f):dp("visualElementGestured",
d,f);b=!0}else b=!1;else b=!1;return b};
xz.prototype.stateChanged=function(a,b,c){this.visualElementStateChanged(new fv({trackingParams:a}),b,c===void 0?0:c)};
xz.prototype.visualElementStateChanged=function(a,b,c){c=c===void 0?0:c;if(c===0&&this.j.has(c))this.o.push([a,b]);else{var d=c;d=d===void 0?0:d;c=mv(d);a||(a=(a=jv(d===void 0?0:d))?new fv({veType:a,youtubeData:void 0,jspbYoutubeData:void 0}):null);var e=a;c&&e&&(a=this.client,d=yw({cttAuthInfo:ov(c)||void 0},c),b={csn:c,ve:e.getAsJson(),clientData:b},c==="UNDEFINED_CSN"?Bw("visualElementStateChanged",d,b):a?Ku("visualElementStateChanged",b,a,d):dp("visualElementStateChanged",b,d))}};
function yz(a,b){if(b===void 0)for(var c=lv(),d=0;d<c.length;d++)c[d]!==void 0&&yz(a,c[d]);else a.i.forEach(function(e,f){(f=a.h.get(f))&&xw(a.client,b,f,e)}),a.i.clear(),a.h.clear()}
;function zz(){wz.call(this);var a={};this.install((a.document_disposed={callback:this.h},a));S("combine_ve_grafts")&&(a={},this.install((a.document_disposed={callback:this.i},a)));a={};this.install((a.flush_logs={callback:this.j},a));S("web_log_cfg_cee_ks")||oo(Az)}
v(zz,wz);zz.prototype.j=function(){dp("finalPayload",{csn:mv()})};
zz.prototype.h=function(){$u(av)};
zz.prototype.i=function(){var a=yz;xz.instance||(xz.instance=new xz);a(xz.instance)};
function Az(){var a=R("CLIENT_EXPERIMENT_EVENTS");if(a){var b=ge();a=y(a);for(var c=a.next();!c.done;c=a.next())c=c.value,b(c)&&dp("genericClientExperimentEvent",{eventType:c});delete Hm.CLIENT_EXPERIMENT_EVENTS}}
;function Bz(){}
function Cz(){var a=F("ytglobal.storage_");a||(a=new Bz,E("ytglobal.storage_",a));return a}
Bz.prototype.estimate=function(){var a,b,c;return B(function(d){a=navigator;return((b=a.storage)==null?0:b.estimate)?d.return(a.storage.estimate()):((c=a.webkitTemporaryStorage)==null?0:c.queryUsageAndQuota)?d.return(Dz()):d.return()})};
function Dz(){var a=navigator;return new Promise(function(b,c){var d;(d=a.webkitTemporaryStorage)!=null&&d.queryUsageAndQuota?a.webkitTemporaryStorage.queryUsageAndQuota(function(e,f){b({usage:e,quota:f})},function(e){c(e)}):c(Error("webkitTemporaryStorage is not supported."))})}
E("ytglobal.storageClass_",Bz);function bp(a,b){var c=this;this.handleError=a;this.h=b;this.i=!1;self.document===void 0||self.addEventListener("beforeunload",function(){c.i=!0});
this.j=Math.random()<=.2}
bp.prototype.Ha=function(a){this.handleError(a)};
bp.prototype.logEvent=function(a,b){switch(a){case "IDB_DATA_CORRUPTED":S("idb_data_corrupted_killswitch")||this.h("idbDataCorrupted",b);break;case "IDB_UNEXPECTEDLY_CLOSED":this.h("idbUnexpectedlyClosed",b);break;case "IS_SUPPORTED_COMPLETED":S("idb_is_supported_completed_killswitch")||this.h("idbIsSupportedCompleted",b);break;case "QUOTA_EXCEEDED":Ez(this,b);break;case "TRANSACTION_ENDED":this.j&&Math.random()<=.1&&this.h("idbTransactionEnded",b);break;case "TRANSACTION_UNEXPECTEDLY_ABORTED":a=
Object.assign({},b,{hasWindowUnloaded:this.i}),this.h("idbTransactionAborted",a)}};
function Ez(a,b){Cz().estimate().then(function(c){c=Object.assign({},b,{isSw:self.document===void 0,isIframe:self!==self.top,deviceStorageUsageMbytes:Fz(c==null?void 0:c.usage),deviceStorageQuotaMbytes:Fz(c==null?void 0:c.quota)});a.h("idbQuotaExceeded",c)})}
function Fz(a){return typeof a==="undefined"?"-1":String(Math.ceil(a/1048576))}
;var Gz={Lc:{feedbackEndpoint:Zw(qy),modifyChannelNotificationPreferenceEndpoint:Zw(ry),playlistEditEndpoint:Zw(sy),shareEntityEndpoint:Zw(py),subscribeEndpoint:Zw(my),undoFeedbackEndpoint:Zw(Zy),unsubscribeEndpoint:Zw(ny),webPlayerShareEntityServiceEndpoint:Zw(ty)}};function Hz(){var a=Dt();zt(a,{pb:Cy,Ic:Ay});zt(a,{pb:tz,Ic:Qn});var b=Uw(),c=a.resolve(tz),d=a.resolve(Cy),e={};b&&(e.client_location=b);dy(Gz,d,c,e);zt(a,{pb:ly,nd:cy.instance})}
;var Iz={},Jz=(Iz["api.invalidparam"]=2,Iz.auth=150,Iz["drm.auth"]=150,Iz["heartbeat.net"]=150,Iz["heartbeat.servererror"]=150,Iz["heartbeat.stop"]=150,Iz["html5.unsupportedads"]=5,Iz["fmt.noneavailable"]=5,Iz["fmt.decode"]=5,Iz["fmt.unplayable"]=5,Iz["html5.missingapi"]=5,Iz["html5.unsupportedlive"]=5,Iz["drm.unavailable"]=5,Iz["mrm.blocked"]=151,Iz["embedder.identity.denied"]=152,Iz["embedder.identity.missing.referrer"]=153,Iz);var Kz=new Set("endSeconds startSeconds mediaContentUrl suggestedQuality videoId rct rctn playmuted muted_autoplay_duration_mode".split(" "));function Lz(a){return(a.search("cue")===0||a.search("load")===0)&&a!=="loadModule"}
function Mz(a,b,c){if(typeof a==="string")return{videoId:a,startSeconds:b,suggestedQuality:c};b={};c=y(Kz);for(var d=c.next();!d.done;d=c.next())d=d.value,a[d]&&(b[d]=a[d]);if(a=a.embedConfig||a.embed_config)if(typeof a==="string")b.embed_config=a;else if(Ma(a))try{var e=JSON.stringify(a);b.embed_config=e}catch(f){console.error("Invalid embedConfig JSON",f)}return b}
function Nz(a,b,c,d){if(Ma(a)&&!Array.isArray(a)){b="playlist list listType index startSeconds suggestedQuality".split(" ");c={};for(d=0;d<b.length;d++){var e=b[d];a[e]&&(c[e]=a[e])}return c}b={index:b,startSeconds:c,suggestedQuality:d};typeof a==="string"&&a.length===16?b.list="PL"+a:b.playlist=a;return b}
;function Oz(a,b){I.call(this);var c=this;this.api=a;this.A=this.G=!1;this.M=[];this.U={};this.j=[];this.i=[];this.Z=!1;this.sessionId=this.h=null;this.targetOrigin="*";this.Y=S("web_player_split_event_bus_iframe");this.u=R("POST_MESSAGE_ORIGIN")||document.location.protocol+"//"+document.location.hostname;this.o=function(d){c.onMessage(d)};
Pz.addEventListener("message",this.o);if(a=R("WIDGET_ID"))this.sessionId=a;b&&this.o(b);Qz(this,"onReady",function(){c.G=!0;var d=c.api.getVideoData();if(!d.isPlayable){c.Z=!0;d=d.errorCode;var e=e===void 0?5:e;c.errorCode=d?Jz[d]||e:e;c.sendMessage("onError",Number(c.errorCode))}Rz(c)});
Qz(this,"onVideoProgress",this.pf.bind(this));Qz(this,"onVolumeChange",this.qf.bind(this));Qz(this,"onApiChange",this.gf.bind(this));Qz(this,"onPlaybackQualityChange",this.lf.bind(this));Qz(this,"onPlaybackRateChange",this.mf.bind(this));Qz(this,"onStateChange",this.nf.bind(this));Qz(this,"onWebglSettingsChanged",this.rf.bind(this));Qz(this,"onCaptionsTrackListChanged",this.hf.bind(this));Qz(this,"captionssettingschanged",this.jf.bind(this))}
v(Oz,I);function Rz(a){if(a.G&&a.h&&!a.A){a.A=!0;a.G=!1;a.sendMessage("initialDelivery",Sz(a));a.sendMessage("onReady");Ux("ep_init_ar");for(var b=y(a.M),c=b.next();!c.done;c=b.next())Tz(a,c.value);a.M=[]}}
function Uz(a,b){a.sendMessage("infoDelivery",b)}
p=Oz.prototype;p.sendMessage=function(a,b){a={event:a,info:b===void 0?null:b};this.A?Tz(this,a):this.M.push(a)};
function Vz(a,b,c){return function(d){b==="onError"?a.api.logApiCall(b+" invocation",c,d):a.api.logApiCall(b+" invocation",c);a.sendMessage(b,d)}}
function Qz(a,b,c){a.j.push({eventType:b,listener:c});a.api.addEventListener(b,c)}
function Sz(a){if(!a.api)return null;var b=a.api.getApiInterface();Vb(b,"getVideoData");for(var c={apiInterface:b},d=0,e=b.length;d<e;d++){var f=b[d];if(f.search("get")===0||f.search("is")===0){var g=0;f.search("get")===0?g=3:f.search("is")===0&&(g=2);g=f.charAt(g).toLowerCase()+f.substring(g+1);try{var h=a.api[f]();c[g]=h}catch(k){}}}c.videoData=a.api.getVideoData();c.currentTimeLastUpdated_=Date.now()/1E3;return c}
p.nf=function(a){a={playerState:a,currentTime:this.api.getCurrentTime(),duration:this.api.getDuration(),videoData:this.api.getVideoData(),videoStartBytes:0,videoBytesTotal:this.api.getVideoBytesTotal(),videoLoadedFraction:this.api.getVideoLoadedFraction(),playbackQuality:this.api.getPlaybackQuality(),availableQualityLevels:this.api.getAvailableQualityLevels(),currentTimeLastUpdated_:Date.now()/1E3,playbackRate:this.api.getPlaybackRate(),mediaReferenceTime:this.api.getMediaReferenceTime()};this.api.getVideoUrl&&
(a.videoUrl=this.api.getVideoUrl());this.api.getVideoContentRect&&(a.videoContentRect=this.api.getVideoContentRect());this.api.getProgressState&&(a.progressState=this.api.getProgressState());this.api.getPlaylist&&(a.playlist=this.api.getPlaylist());this.api.getPlaylistIndex&&(a.playlistIndex=this.api.getPlaylistIndex());Uz(this,a)};
p.lf=function(a){a={playbackQuality:a};this.api.getAvailableQualityLevels&&(a.availableQualityLevels=this.api.getAvailableQualityLevels());this.api.getPreferredQuality&&(a.preferredQuality=this.api.getPreferredQuality());Uz(this,a)};
p.mf=function(a){Uz(this,{playbackRate:a})};
p.gf=function(){for(var a=this.api.getOptions(),b={namespaces:a},c=0,d=a.length;c<d;c++){var e=a[c],f=this.api.getOptions(e);a.join(", ");b[e]={options:f};for(var g=0,h=f.length;g<h;g++){var k=f[g],l=this.api.getOption(e,k);b[e][k]=l}}this.sendMessage("apiInfoDelivery",b)};
p.qf=function(){Uz(this,{muted:this.api.isMuted(),volume:this.api.getVolume()})};
p.pf=function(a){a={currentTime:a,videoBytesLoaded:this.api.getVideoBytesLoaded(),videoLoadedFraction:this.api.getVideoLoadedFraction(),currentTimeLastUpdated_:Date.now()/1E3,playbackRate:this.api.getPlaybackRate(),mediaReferenceTime:this.api.getMediaReferenceTime()};this.api.getProgressState&&(a.progressState=this.api.getProgressState());Uz(this,a)};
p.rf=function(){Uz(this,{sphericalProperties:this.api.getSphericalProperties()})};
p.hf=function(){if(this.api.getCaptionTracks){var a={captionTracks:this.api.getCaptionTracks()};Uz(this,a)}};
p.jf=function(){if(this.api.getSubtitlesUserSettings){var a={subtitlesUserSettings:this.api.getSubtitlesUserSettings()};Uz(this,a)}};
p.onMessage=function(a){if(!(this.u!=="*"&&a.origin!==this.u||this.h&&a.source!==this.h||typeof a.data!=="string")){try{var b=JSON.parse(a.data)}catch(f){return}if(b)switch(b.event){case "listening":var c=a.source;a=a.origin;b=b.id;a!=="null"&&(this.u=this.targetOrigin=a);this.h=c;this.sessionId=b;Rz(this);break;case "command":if(c=b.func,b=b.args,c==="addEventListener"&&b)c=b[0],b=a.origin,c==="onReady"?this.api.logApiCall(c+" invocation",b):c==="onError"&&this.Z&&(this.api.logApiCall(c+" invocation",
b,this.errorCode),this.errorCode=void 0),this.api.logApiCall(c+" registration",b),this.U[c]||c==="onReady"||(a=Vz(this,c,b),this.i.push({eventType:c,listener:a,origin:b}),this.Y?this.api.handleExternalCall("addEventListener",[c,a],b):this.api.addEventListener(c,a),this.U[c]=!0);else if(a=a.origin,this.api.isExternalMethodAvailable(c,a)){b=b||[];if(b.length>0&&Lz(c)){var d=b;if(Ma(d[0])&&!Array.isArray(d[0]))var e=d[0];else switch(e={},c){case "loadVideoById":case "cueVideoById":e=Mz(d[0],d[1]!==void 0?
Number(d[1]):void 0,d[2]);break;case "loadVideoByUrl":case "cueVideoByUrl":e=d[0];typeof e==="string"&&(e={mediaContentUrl:e,startSeconds:d[1]!==void 0?Number(d[1]):void 0,suggestedQuality:d[2]});b:{if((d=e.mediaContentUrl)&&(d=/\/([ve]|embed)\/([^#?]+)/.exec(d))&&d[2]){d=d[2];break b}d=null}e.videoId=d;e=Mz(e);break;case "loadPlaylist":case "cuePlaylist":e=Nz(d[0],d[1],d[2],d[3])}b.length=1;b[0]=e}this.api.handleExternalCall(c,b,a);Lz(c)&&Uz(this,Sz(this))}}}};
function Tz(a,b){if(a.h){b.channel="widget";a.sessionId&&(b.id=a.sessionId);try{var c=JSON.stringify(b);a.h.postMessage(c,a.targetOrigin)}catch(d){Uu(d)}}}
p.ba=function(){I.prototype.ba.call(this);Pz.removeEventListener("message",this.o);for(var a=0;a<this.j.length;a++){var b=this.j[a];this.api.removeEventListener(b.eventType,b.listener)}this.j=[];for(a=0;a<this.i.length;a++)b=this.i[a],this.Y?this.api.handleExternalCall("removeEventListener",[b.eventType,b.listener],b.origin):this.api.removeEventListener(b.eventType,b.listener);this.i=[]};
var Pz=window;function Wz(a,b,c){I.call(this);var d=this;this.api=a;this.id=b;this.origin=c;this.h={};this.j=S("web_player_split_event_bus_iframe");this.i=function(e){d.onMessage(e)};
Xz.addEventListener("message",this.i);Yz(this,"RECEIVING")}
v(Wz,I);p=Wz.prototype;p.addListener=function(a,b){if(!(a in this.h)){var c=this.kf.bind(this,a);this.h[a]=c;this.addEventListener(a,c,b)}};
p.kf=function(a,b){this.ea||Yz(this,a,Zz(a,b))};
p.removeListener=function(a,b){a in this.h&&(this.removeEventListener(a,this.h[a],b),delete this.h[a])};
p.addEventListener=function(a,b,c){this.j?a==="onReady"?this.api.addEventListener(a,b):this.api.handleExternalCall("addEventListener",[a,b],c||null):this.api.addEventListener(a,b)};
p.removeEventListener=function(a,b,c){this.j?a==="onReady"?this.api.removeEventListener(a,b):this.api.handleExternalCall("removeEventListener",[a,b],c||null):this.api.removeEventListener(a,b)};
function $z(a,b){switch(a){case "loadVideoById":return[Mz(b)];case "cueVideoById":return[Mz(b)];case "loadVideoByPlayerVars":return[b];case "cueVideoByPlayerVars":return[b];case "loadPlaylist":return[Nz(b)];case "cuePlaylist":return[Nz(b)];case "seekTo":return[b.seconds,b.allowSeekAhead];case "playVideoAt":return[b.index];case "setVolume":return[b.volume];case "setPlaybackQuality":return[b.suggestedQuality];case "setPlaybackRate":return[b.suggestedRate];case "setLoop":return[b.loopPlaylists];case "setShuffle":return[b.shufflePlaylist];
case "getOptions":return[b.module];case "getOption":return[b.module,b.option];case "setOption":return[b.module,b.option,b.value];case "handleGlobalKeyDown":return[b.keyCode,b.shiftKey,b.ctrlKey,b.altKey,b.metaKey,b.key,b.code]}return[]}
function aA(a,b){switch(a){case "isMuted":return{muted:b};case "getVolume":return{volume:b};case "getPlaybackRate":return{playbackRate:b};case "getAvailablePlaybackRates":return{availablePlaybackRates:b};case "getVideoLoadedFraction":return{videoLoadedFraction:b};case "getPlayerState":return{playerState:b};case "getCurrentTime":return{currentTime:b};case "getPlaybackQuality":return{playbackQuality:b};case "getAvailableQualityLevels":return{availableQualityLevels:b};case "getDuration":return{duration:b};
case "getVideoUrl":return{videoUrl:b};case "getVideoEmbedCode":return{videoEmbedCode:b};case "getPlaylist":return{playlist:b};case "getPlaylistIndex":return{playlistIndex:b};case "getOptions":return{options:b};case "getOption":return{option:b}}}
function Zz(a,b){switch(a){case "onReady":return;case "onStateChange":return{playerState:b};case "onPlaybackQualityChange":return{playbackQuality:b};case "onPlaybackRateChange":return{playbackRate:b};case "onError":return{errorCode:b}}if(b!=null)return{value:b}}
function Yz(a,b,c){a.ea||(b={id:a.id,command:b},c&&(b.data=c),bA.postMessage(JSON.stringify(b),a.origin))}
p.onMessage=function(a){if(a.origin===this.origin){var b=a.data;if(typeof b==="string"){try{b=JSON.parse(b)}catch(e){return}if(b.command){var c=b.command;b=b.data;a=a.origin;if(!this.ea){var d=b||{};switch(c){case "addEventListener":typeof d.event==="string"&&this.addListener(d.event,a);break;case "removeEventListener":typeof d.event==="string"&&this.removeListener(d.event,a);break;default:this.api.isReady()&&this.api.isExternalMethodAvailable(c,a||null)&&(b=$z(c,b||{}),b=this.api.handleExternalCall(c,
b,a||null),(b=aA(c,b))&&Yz(this,c,b))}}}}}};
p.ba=function(){Xz.removeEventListener("message",this.i);for(var a in this.h)this.h.hasOwnProperty(a)&&this.removeListener(a);I.prototype.ba.call(this)};
var Xz=window,bA=window.parent;var cA=new sz;function dA(){return cA.od()}
function eA(a){a=a===void 0?{}:a;return cA.invoke(a)}
;function fA(a,b,c,d,e){I.call(this);var f=this;this.A=b;this.webPlayerContextConfig=d;this.Kb=e;this.Qa=!1;this.api={};this.ma=this.u=null;this.U=new N;this.h={};this.Z=this.xa=this.elementId=this.Ra=this.config=null;this.Y=!1;this.j=this.G=null;this.Fa={};this.Jc=["onReady"];this.lastError=null;this.fb=NaN;this.M={};this.ha=0;this.i=this.o=a;xc(this,this.U);gA(this);c?this.ha=setTimeout(function(){f.loadNewVideoConfig(c)},0):d&&(hA(this),iA(this))}
v(fA,I);p=fA.prototype;p.getId=function(){return this.A};
p.loadNewVideoConfig=function(a){if(!this.ea){this.ha&&(clearTimeout(this.ha),this.ha=0);var b=a||{};b instanceof Ov||(b=new Ov(b));this.config=b;this.setConfig(a);iA(this);this.isReady()&&jA(this)}};
function hA(a){var b;a.webPlayerContextConfig?b=a.webPlayerContextConfig.rootElementId:b=a.config.attrs.id;a.elementId=b||a.elementId;a.elementId==="video-player"&&(a.elementId=a.A,a.webPlayerContextConfig?a.webPlayerContextConfig.rootElementId=a.A:a.config.attrs.id=a.A);var c;((c=a.i)==null?void 0:c.id)===a.elementId&&(a.elementId+="-player",a.webPlayerContextConfig?a.webPlayerContextConfig.rootElementId=a.elementId:a.config.attrs.id=a.elementId)}
p.setConfig=function(a){this.Ra=a;this.config=kA(a);hA(this);if(!this.xa){var b;this.xa=lA(this,((b=this.config.args)==null?void 0:b.jsapicallback)||"onYouTubePlayerReady")}this.config.args?this.config.args.jsapicallback=null:this.config.args={jsapicallback:null};var c;if((c=this.config)==null?0:c.attrs)a=this.config.attrs,(b=a.width)&&this.i&&(this.i.style.width=Qj(Number(b)||b)),(a=a.height)&&this.i&&(this.i.style.height=Qj(Number(a)||a))};
function jA(a){if(a.config&&a.config.loaded!==!0)if(a.config.loaded=!0,!a.config.args||a.config.args.autoplay!=="0"&&a.config.args.autoplay!==0&&a.config.args.autoplay!==!1){var b;a.api.loadVideoByPlayerVars((b=a.config.args)!=null?b:null)}else a.api.cueVideoByPlayerVars(a.config.args)}
function mA(a){var b=!0,c=nA(a);c&&a.config&&(b=c.dataset.version===oA(a));return b&&!!F("yt.player.Application.create")}
function iA(a){if(!a.ea&&!a.Y){var b=mA(a);if(b&&(nA(a)?"html5":null)==="html5")a.Z="html5",a.isReady()||pA(a);else if(qA(a),a.Z="html5",b&&a.j&&a.o)a.o.appendChild(a.j),pA(a);else{a.config&&(a.config.loaded=!0);var c=!1;a.G=function(){c=!0;var d=rA(a,"player_bootstrap_method")?F("yt.player.Application.createAlternate")||F("yt.player.Application.create"):F("yt.player.Application.create");var e=a.config?kA(a.config):void 0;d&&d(a.o,e,a.webPlayerContextConfig,a.Kb);pA(a)};
a.Y=!0;b?a.G():(Zv(oA(a),a.G),(b=sA(a))&&fw(b||""),tA(a)&&!c&&E("yt.player.Application.create",null))}}}
function nA(a){var b=Gg(a.elementId);!b&&a.i&&a.i.querySelector&&(b=a.i.querySelector("#"+a.elementId));return b}
function pA(a){if(!a.ea){var b=nA(a),c=!1;b&&b.getApiInterface&&b.getApiInterface()&&(c=!0);if(c){a.Y=!1;if(!rA(a,"html5_remove_not_servable_check_killswitch")){var d;if((b==null?0:b.isNotServable)&&a.config&&(b==null?0:b.isNotServable((d=a.config.args)==null?void 0:d.video_id)))return}uA(a)}else a.fb=setTimeout(function(){pA(a)},50)}}
function uA(a){gA(a);a.Qa=!0;var b=nA(a);if(b){a.u=vA(a,b,"addEventListener");a.ma=vA(a,b,"removeEventListener");var c=b.getApiInterface();c=c.concat(b.getInternalApiInterface());for(var d=a.api,e=0;e<c.length;e++){var f=c[e];d[f]||(d[f]=vA(a,b,f))}}for(var g in a.h)a.h.hasOwnProperty(g)&&a.u&&a.u(g,a.h[g]);jA(a);a.xa&&a.xa(a.api);a.U.sb("onReady",a.api)}
function vA(a,b,c){var d=b[c];return function(){var e=C.apply(0,arguments);try{return a.lastError=null,d.apply(b,e)}catch(f){if(c!=="sendAbandonmentPing")throw f.params=c,a.lastError=f,e=new T("PlayerProxy error in method call",{error:f,method:c,playerId:a.A}),e.level="WARNING",e;}}}
function gA(a){a.Qa=!1;if(a.ma)for(var b in a.h)a.h.hasOwnProperty(b)&&a.ma(b,a.h[b]);for(var c in a.M)a.M.hasOwnProperty(c)&&clearTimeout(Number(c));a.M={};a.u=null;a.ma=null;b=a.api;for(var d in b)b.hasOwnProperty(d)&&(b[d]=null);b.addEventListener=function(e,f){a.addEventListener(e,f)};
b.removeEventListener=function(e,f){a.removeEventListener(e,f)};
b.destroy=function(){a.dispose()};
b.getLastError=function(){return a.getLastError()};
b.getPlayerType=function(){return a.getPlayerType()};
b.getCurrentVideoConfig=function(){return a.Ra};
b.loadNewVideoConfig=function(e){a.loadNewVideoConfig(e)};
b.isReady=function(){return a.isReady()}}
p.isReady=function(){return this.Qa};
p.addEventListener=function(a,b){var c=this,d=lA(this,b);d&&(Ob(this.Jc,a)>=0||this.h[a]||(b=wA(this,a),this.u&&this.u(a,b)),this.U.subscribe(a,d),a==="onReady"&&this.isReady()&&setTimeout(function(){d(c.api)},0))};
p.removeEventListener=function(a,b){this.ea||(b=lA(this,b))&&this.U.unsubscribe(a,b)};
function lA(a,b){var c=b;if(typeof b==="string"){if(a.Fa[b])return a.Fa[b];c=function(){var d=C.apply(0,arguments),e=F(b);if(e)try{e.apply(D,d)}catch(f){throw d=new T("PlayerProxy error when executing callback",{error:f}),d.level="ERROR",d;}};
a.Fa[b]=c}return c?c:null}
function wA(a,b){function c(d){function e(){if(!a.ea)try{a.U.sb(b,d!=null?d:void 0)}catch(h){var g=new T("PlayerProxy error when creating global callback",{error:h.message,event:b,playerId:a.A,data:d,originalStack:h.stack,componentStack:h.ke});g.level="WARNING";throw g;}}
if(rA(a,"web_player_publish_events_immediately"))e();else{var f=setTimeout(function(){e();var g=a.M,h=String(f);h in g&&delete g[h]},0);
xg(a.M,String(f))}}
return a.h[b]=c}
p.getPlayerType=function(){return this.Z||(nA(this)?"html5":null)};
p.getLastError=function(){return this.lastError};
function qA(a){a.cancel();gA(a);a.Z=null;a.config&&(a.config.loaded=!1);var b=nA(a);b&&(mA(a)||!tA(a)?a.j=b:(b&&b.destroy&&b.destroy(),a.j=null));if(a.o)for(a=a.o;b=a.firstChild;)a.removeChild(b)}
p.cancel=function(){this.G&&cw(oA(this),this.G);clearTimeout(this.fb);this.Y=!1};
p.ba=function(){qA(this);if(this.j&&this.config&&this.j.destroy)try{this.j.destroy()}catch(b){var a=new T("PlayerProxy error during disposal",{error:b});a.level="ERROR";throw a;}this.Fa=null;for(a in this.h)this.h.hasOwnProperty(a)&&delete this.h[a];this.Ra=this.config=this.api=null;delete this.o;delete this.i;I.prototype.ba.call(this)};
function tA(a){var b,c;a=(b=a.config)==null?void 0:(c=b.args)==null?void 0:c.fflags;return!!a&&a.indexOf("player_destroy_old_version=true")!==-1}
function oA(a){return a.webPlayerContextConfig?a.webPlayerContextConfig.jsUrl:(a=a.config.assets)?a.js:""}
function sA(a){return a.webPlayerContextConfig?a.webPlayerContextConfig.cssUrl:(a=a.config.assets)?a.css:""}
function rA(a,b){if(a.webPlayerContextConfig)var c=a.webPlayerContextConfig.serializedExperimentFlags;else{var d;if((d=a.config)==null?0:d.args)c=a.config.args.fflags}return(c||"").split("&").includes(b+"=true")}
function kA(a){for(var b={},c=y(Object.keys(a)),d=c.next();!d.done;d=c.next()){d=d.value;var e=a[d];b[d]=typeof e==="object"?Ag(e):e}return b}
;var xA={},yA="player_uid_"+(Math.random()*1E9>>>0);function zA(a,b){var c="player",d=!1;d=d===void 0?!0:d;c=typeof c==="string"?Gg(c):c;var e=yA+"_"+Na(c),f=xA[e];if(f&&d)return AA(a,b)?f.api.loadVideoByPlayerVars(a.args||null):f.loadNewVideoConfig(a),f.api;f=new fA(c,e,a,b,void 0);xA[e]=f;f.addOnDisposeCallback(function(){delete xA[f.getId()]});
return f.api}
function AA(a,b){return b&&b.serializedExperimentFlags?b.serializedExperimentFlags.includes("web_player_remove_playerproxy=true"):a&&a.args&&a.args.fflags?a.args.fflags.includes("web_player_remove_playerproxy=true"):!1}
;var BA=null,CA=null,DA;
function EA(){Zx();var a=ao(),b=eo(119),c=window.devicePixelRatio>1;if(document.body&&ek(document.body,"exp-invert-logo"))if(c&&!ek(document.body,"inverted-hdpi")){var d=document.body;if(d.classList)d.classList.add("inverted-hdpi");else if(!ek(d,"inverted-hdpi")){var e=ck(d);dk(d,e+(e.length>0?" inverted-hdpi":"inverted-hdpi"))}}else!c&&ek(document.body,"inverted-hdpi")&&fk();if(b!=c){b="f"+(Math.floor(119/31)+1);d=fo(b)||0;d=c?d|67108864:d&-67108865;d===0?delete Yn[b]:(c=d.toString(16),Yn[b]=c.toString());
c=!0;S("web_secure_pref_cookie_killswitch")&&(c=!1);b=a.h;d=[];for(f in Yn)Yn.hasOwnProperty(f)&&d.push(f+"="+encodeURIComponent(String(Yn[f])));var f=d.join("&");Un(b,f,63072E3,a.i,c)}}
function FA(){GA()}
function HA(){Ux("ep_init_pr");GA()}
function GA(){var a=BA.getVideoData(1);a=a.title?a.title+" - YouTube":"YouTube";document.title!==a&&(document.title=a)}
function IA(){BA&&BA.sendAbandonmentPing&&BA.sendAbandonmentPing();R("PL_ATT")&&cA.dispose();for(var a=Wj,b=0,c=Jy.length;b<c;b++)a.qa(Jy[b]);Jy.length=0;aw(Ky.toString());Ly=!1;Im("DCLKSTAT",0);wc(CA);BA&&(BA.removeEventListener("onVideoDataChange",FA),BA.destroy())}
;var JA;S("embeds_no_early_ticks")?JA=V():Ux("ep_init_eps");S("embeds_enable_scheduler")&&So();E("yt.setConfig",Im);E("yt.config.set",Im);E("yt.setMsg",Yv);E("yt.msgs.set",Yv);E("yt.logging.errors.log",Tu);
E("writeEmbed",function(){Ux("ep_init_wes");var a=R("PLAYER_CONFIG");if(!a){var b=R("PLAYER_VARS");b&&(a={args:b})}Lw(!0);a.args.ps==="gvn"&&(document.body.style.backgroundColor="transparent");a.attrs||(a.attrs={width:"100%",height:"100%",id:"video-player"});var c=document.referrer;b=R("POST_MESSAGE_ORIGIN");window!==window.top&&c&&c!==document.URL&&(a.args.loaderUrl=c);c=az();if(!c.serializedForcedExperimentIds){var d=Wm(window.location.href);d.forced_experiments&&(c.serializedForcedExperimentIds=
d.forced_experiments)}var e;((e=a.args)==null?0:e.autoplay)?Qx("watch",["pbs","pbu","pbp"]):a.args&&Av(a.args)?Qx("video_preview",["ol"]):Qx("embed_no_video",["ep_init_pr"]);BA=zA(a,c);BA.addEventListener("onVideoDataChange",FA);BA.addEventListener("onReady",HA);a=R("POST_MESSAGE_ID","player");R("ENABLE_JS_API")?CA=new Oz(BA,DA):R("ENABLE_POST_API")&&typeof a==="string"&&typeof b==="string"&&(CA=new Wz(BA,a,b));DA=void 0;My();S("ytidb_create_logger_embed_killswitch")||ap();a={};zz.h||(zz.h=new zz);
zz.h.install((a.flush_logs={callback:function(){xu()}},a));
Ns();if(S("embeds_enable_separate_ITS")){Hz();var f=function(){return cy.instance}}else f=function(){var g,h;
if(!Dy){var k=Dt();zt(k,{pb:Cy,Ic:Ay});var l={Lc:{feedbackEndpoint:Zw(qy),modifyChannelNotificationPreferenceEndpoint:Zw(ry),playlistEditEndpoint:Zw(sy),shareEntityEndpoint:Zw(py),subscribeEndpoint:Zw(my),unsubscribeEndpoint:Zw(ny),webPlayerShareEntityServiceEndpoint:Zw(ty)}},m=Uw(),n={};m&&(n.client_location=m);g===void 0&&(g=Rn());h===void 0&&(h=k.resolve(Cy));dy(l,h,g,n);zt(k,{pb:ly,nd:cy.instance});Dy=k.resolve(ly)}return Dy};
S("ytidb_clear_embedded_player")&&Wj.pa(function(){f();mz()});
S("enable_rta_manager")&&oo(function(){var g=new Xy(f());var h={preload:!S("enable_rta_npi"),Ef:S("attmusi")},k=!1;if(typeof h==="boolean")var l={preload:h};else typeof h==="undefined"?l={preload:!0}:(l=h,k=!!h.Gh);h=k?void 0:new Bs;Oy.instance=new Oy(g,l,h);g=Oy.instance;l=g.i.bind(g);E("yt.aba.att",l);g=g.j.bind(g);E("yt.aba.att2",g)});
Ux("ep_init_wee")});
E("yt.abuse.player.botguardInitialized",F("yt.abuse.player.botguardInitialized")||dA);E("yt.abuse.player.invokeBotguard",F("yt.abuse.player.invokeBotguard")||eA);E("yt.abuse.dclkstatus.checkDclkStatus",F("yt.abuse.dclkstatus.checkDclkStatus")||Ny);E("yt.player.exports.navigate",F("yt.player.exports.navigate")||Kw);E("yt.util.activity.init",F("yt.util.activity.init")||et);E("yt.util.activity.getTimeSinceActive",F("yt.util.activity.getTimeSinceActive")||ht);
E("yt.util.activity.setTimestamp",F("yt.util.activity.setTimestamp")||ft);window.addEventListener("load",Mm(function(){EA()}));
window.addEventListener("pageshow",Mm(function(a){a.persisted||EA()}));
window.addEventListener("pagehide",Mm(function(a){S("embeds_web_enable_dispose_player_if_page_not_cached_killswitch")?IA():a.persisted||IA()}));
S("embeds_enable_contrib_error_handling")?$y():(window.onerror=function(a,b,c,d,e){Wu(a,b,c,d,e)},Mi=Vu,window.addEventListener("unhandledrejection",function(a){Vu(a.reason)}),Su());
(function(){if(S("embeds_enable_early_message_handler")&&R("ENABLE_JS_API")){var a=function(b){DA=b;window.removeEventListener("message",a)};
window.addEventListener("message",a)}})();
S("embeds_no_early_ticks")&&JA&&Ux("ep_init_eps",JA);Ux("ep_init_epe");}).call(this);
