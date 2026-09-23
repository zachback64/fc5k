'use strict';
(async () => {
  const description = document.querySelector('#route-description');
  try {
    const [draft, current] = await Promise.all(['data/trail-review.json','data/course.json'].map(async url => {
      const response = await fetch(url); if (!response.ok) throw new Error('Course data unavailable.'); return response.json();
    }));
    const map = L.map('review-map', {scrollWheelZoom: false}).setView(current.start, 14);
    const street = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap contributors', referrerPolicy: 'strict-origin-when-cross-origin', maxZoom:19}).addTo(map);
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {attribution:'Imagery &copy; Esri',maxZoom:19});
    L.control.layers({Streets:street,Satellite:satellite}).addTo(map);
    const lines = {draft:L.polyline(draft.shape,{color:'#ff1e00',weight:5}).addTo(map),current:L.polyline(current.shape,{color:'#1263a0',weight:3,opacity:.3}).addTo(map)};
    L.marker(current.start,{icon:L.icon({iconUrl:'logo.svg',iconSize:[30,30],iconAnchor:[15,15]})}).addTo(map).bindPopup('Start / finish');
    function select(key) {
      for (const [name,line] of Object.entries(lines)) {
        line.setStyle({weight:name===key?5:3,opacity:name===key?1:.25});
        document.getElementById(name).setAttribute('aria-pressed',String(name===key));
      }
      lines[key].bringToFront(); map.fitBounds(lines[key].getBounds(),{padding:[25,25]});
      document.querySelector('#route-title').textContent=key==='draft'?'Prairie Path loop · 4.83 km':'Current park + campus course · 4.91 km';
      description.textContent=key==='draft'?draft.description:'Glos → Wilder → university campus → garden path → home.';
      document.querySelector('#route-detail').textContent=key==='draft'?'Approximately 920 m on the Prairie Path. About 170 m short of 5K; this is a candidate to refine.':'The plotted route repeats approximately 72 m of path in the opposite direction, mostly around a circular feature in Wilder. That needs cleanup before calling it a loop with no backtracking.';
    }
    document.querySelector('#draft').onclick=()=>select('draft');document.querySelector('#current').onclick=()=>select('current');select('draft');
  } catch (error) {console.error('Course map failed:', error); description.textContent='Could not load the map. Please refresh to try again.';}
})();
