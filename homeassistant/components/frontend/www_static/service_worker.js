"use strict";function setOfCachedUrls(e){return e.keys().then(function(e){return e.map(function(e){return e.url})}).then(function(e){return new Set(e)})}function notificationEventCallback(e,t){firePushCallback({action:t.action,data:t.notification.data,tag:t.notification.tag,type:e},t.notification.data.jwt)}function firePushCallback(e,t){delete e.data.jwt,0===Object.keys(e.data).length&&e.data.constructor===Object&&delete e.data,fetch("/api/notify.html5/callback",{method:"POST",headers:new Headers({"Content-Type":"application/json",Authorization:"Bearer "+t}),body:JSON.stringify(e)})}var precacheConfig=[["/","9734117d88f359d46e384c6d7358485e"],["/frontend/panels/dev-event-c2d5ec676be98d4474d19f94d0262c1e.html","6c55fc819751923ab00c62ae3fbb7222"],["/frontend/panels/dev-info-a9c07bf281fe9791fb15827ec1286825.html","931f9327e368db710fcdf5f7202f2588"],["/frontend/panels/dev-service-ac74f7ce66fd7136d25c914ea12f4351.html","7018929ba2aba240fc86e16d33201490"],["/frontend/panels/dev-state-65e5f791cc467561719bf591f1386054.html","78158786a6597ef86c3fd6f4985cde92"],["/frontend/panels/dev-template-7d744ab7f7c08b6d6ad42069989de400.html","8a6ee994b1cdb45b081299b8609915ed"],["/frontend/panels/map-3b0ca63286cbe80f27bd36dbc2434e89.html","d22eee1c33886ce901851ccd35cb43ed"],["/static/core-ad1ebcd0614c98a390d982087a7ca75c.js","e900a4b42404d2a5a1c0497e7c53c975"],["/static/frontend-920bb20410f9a1b8458600b15a1d40ae.html","bff98f7e4a8414a00dca50791d339381"],["/static/mdi-46a76f877ac9848899b8ed382427c16f.html","a846c4082dd5cffd88ac72cbe943e691"],["static/fonts/roboto/Roboto-Bold.ttf","d329cc8b34667f114a95422aaad1b063"],["static/fonts/roboto/Roboto-Light.ttf","7b5fb88f12bec8143f00e21bc3222124"],["static/fonts/roboto/Roboto-Medium.ttf","fe13e4170719c2fc586501e777bde143"],["static/fonts/roboto/Roboto-Regular.ttf","ac3f799d5bbaf5196fab15ab8de8431c"],["static/icons/favicon-192x192.png","419903b8422586a7e28021bbe9011175"],["static/icons/favicon.ico","04235bda7843ec2fceb1cbe2bc696cf4"],["static/images/card_media_player_bg.png","a34281d1c1835d338a642e90930e61aa"],["static/webcomponents-lite.min.js","89313f9f2126ddea722150f8154aca03"]],cacheName="sw-precache-v2--"+(self.registration?self.registration.scope:""),ignoreUrlParametersMatching=[/^utm_/],addDirectoryIndex=function(e,t){var n=new URL(e);return"/"===n.pathname.slice(-1)&&(n.pathname+=t),n.toString()},createCacheKey=function(e,t,n,a){var c=new URL(e);return a&&c.toString().match(a)||(c.search+=(c.search?"&":"")+encodeURIComponent(t)+"="+encodeURIComponent(n)),c.toString()},isPathWhitelisted=function(e,t){if(0===e.length)return!0;var n=new URL(t).pathname;return e.some(function(e){return n.match(e)})},stripIgnoredUrlParameters=function(e,t){var n=new URL(e);return n.search=n.search.slice(1).split("&").map(function(e){return e.split("=")}).filter(function(e){return t.every(function(t){return!t.test(e[0])})}).map(function(e){return e.join("=")}).join("&"),n.toString()},hashParamName="_sw-precache",urlsToCacheKeys=new Map(precacheConfig.map(function(e){var t=e[0],n=e[1],a=new URL(t,self.location),c=createCacheKey(a,hashParamName,n,!1);return[a.toString(),c]}));self.addEventListener("install",function(e){e.waitUntil(caches.open(cacheName).then(function(e){return setOfCachedUrls(e).then(function(t){return Promise.all(Array.from(urlsToCacheKeys.values()).map(function(n){if(!t.has(n))return e.add(new Request(n,{credentials:"same-origin"}))}))})}).then(function(){return self.skipWaiting()}))}),self.addEventListener("activate",function(e){var t=new Set(urlsToCacheKeys.values());e.waitUntil(caches.open(cacheName).then(function(e){return e.keys().then(function(n){return Promise.all(n.map(function(n){if(!t.has(n.url))return e.delete(n)}))})}).then(function(){return self.clients.claim()}))}),self.addEventListener("fetch",function(e){if("GET"===e.request.method){var t,n=stripIgnoredUrlParameters(e.request.url,ignoreUrlParametersMatching);t=urlsToCacheKeys.has(n);var a="index.html";!t&&a&&(n=addDirectoryIndex(n,a),t=urlsToCacheKeys.has(n));var c="/";!t&&c&&"navigate"===e.request.mode&&isPathWhitelisted(["^((?!(static|api|local|service_worker.js|manifest.json)).)*$"],e.request.url)&&(n=new URL(c,self.location).toString(),t=urlsToCacheKeys.has(n)),t&&e.respondWith(caches.open(cacheName).then(function(e){return e.match(urlsToCacheKeys.get(n)).then(function(e){if(e)return e;throw Error("The cached response that was expected is missing.")})}).catch(function(t){return console.warn('Couldn\'t serve response for "%s" from cache: %O',e.request.url,t),fetch(e.request)}))}}),self.addEventListener("push",function(e){var t;e.data&&(t=e.data.json(),e.waitUntil(self.registration.showNotification(t.title,t).then(function(e){firePushCallback({type:"received",tag:t.tag,data:t.data},t.data.jwt)})))}),self.addEventListener("notificationclick",function(e){var t;notificationEventCallback("clicked",e),e.notification.close(),e.notification.data&&e.notification.data.url&&(t=e.notification.data.url,t&&e.waitUntil(clients.matchAll({type:"window"}).then(function(e){var n,a;for(n=0;n<e.length;n++)if(a=e[n],a.url===t&&"focus"in a)return a.focus();if(clients.openWindow)return clients.openWindow(t)})))}),self.addEventListener("notificationclose",function(e){notificationEventCallback("closed",e)});