'use strict';
(async () => {
  const description = document.querySelector('#route-description');
  try {
    const response = await fetch('data/course-workshop.json');
    if (!response.ok) throw new Error('Course data unavailable.');
    const data = await response.json();
    const colors = ['#e53612','#1263a0','#278452','#9b4cb0','#bf7900','#526474'];
    const map = L.map('review-map', {scrollWheelZoom:false,zoomSnap:.25}).setView(data.home,14);
    const streets = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',referrerPolicy:'strict-origin-when-cross-origin',maxZoom:19}).addTo(map);
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{attribution:'Imagery &copy; Esri',maxZoom:19});
    L.control.layers({Streets:streets,Satellite:satellite}).addTo(map);
    const lines = {}, buttons = {}, pins = L.layerGroup().addTo(map);
    let selected;
    function element(tag,text,className) { const e=document.createElement(tag);e.textContent=text;if(className)e.className=className;return e; }
    data.routes.forEach((route,index) => {
      lines[route.id] = L.polyline(route.shape,{color:colors[index],weight:5});
      const button=element('button','','route-card');button.type='button';button.style.setProperty('--route-color',colors[index]);button.setAttribute('aria-pressed','false');
      button.append(element('strong',route.name),element('span',route.kind,'card-type'));
      const bottom=element('span','','card-bottom');bottom.append(element('b','5.00 km'),element('span',route.finish_offset_m===0?'Home finish':`${route.finish_offset_m} m from home`,route.finish_offset_m===0?'home-badge':''));button.append(bottom);
      button.onclick=()=>select(route);buttons[route.id]=button;document.querySelector('#routes').append(button);
    });
    function displayLines() {
      const all=document.querySelector('#show-all').checked;
      for(const [id,line] of Object.entries(lines)) {
        if(all||id===selected.id)line.addTo(map);else map.removeLayer(line);
        line.setStyle({weight:id===selected.id?5:4,opacity:id===selected.id?1:.55});
      }
      lines[selected.id].bringToFront();
    }
    function select(route) {
      selected=route;
      for(const [id,button] of Object.entries(buttons))button.setAttribute('aria-pressed',String(id===route.id));
      displayLines();pins.clearLayers();
      L.circleMarker(route.start,{radius:8,color:'#fff',weight:2,fillColor:'#1c7549',fillOpacity:1}).addTo(pins).bindPopup('Start at the house · 0.00 km');
      if(route.finish_offset_m===0) {
        L.marker(route.finish,{icon:L.divIcon({className:'finish-pin',html:'S/F',iconSize:[34,23],iconAnchor:[17,12]})}).addTo(pins).bindPopup('Start and finish at the house · 5.00 km');
      } else {
        L.marker(route.finish,{icon:L.divIcon({className:'finish-pin',html:'5K',iconSize:[30,23],iconAnchor:[15,12]})}).addTo(pins).bindPopup(`Finish · ${route.finish_offset_m} m ${route.finish_direction} of the start on Kenmore.`);
      }
      const markerGroups=new Map();
      for(const marker of route.markers) {
        const key=marker.point.map(n=>n.toFixed(5)).join(',');
        if(!markerGroups.has(key))markerGroups.set(key,{point:marker.point,kms:[]});
        markerGroups.get(key).kms.push(marker.km);
      }
      for(const marker of markerGroups.values())L.marker(marker.point,{icon:L.divIcon({className:'distance-pin',html:marker.kms.join('/'),iconSize:[30,26],iconAnchor:[15,13]})}).addTo(pins).bindPopup(`${marker.kms.join(' and ')} km from the start`);
      if(route.turnaround)L.marker(route.turnaround,{icon:L.divIcon({className:'finish-pin',html:'↶',iconSize:[26,23],iconAnchor:[13,12]})}).addTo(pins).bindPopup('Turn around here · 2.50 km');
      document.querySelector('#map-label').textContent=route.name;
      document.querySelector('#route-kind').textContent=route.kind;
      document.querySelector('#route-title').textContent=route.name;
      document.querySelector('#finish-distance').textContent=route.finish_offset_m===0?'At home':`${route.finish_offset_m} m`;
      document.querySelector('#finish-label').textContent=route.finish_offset_m===0?'Same start and finish':`${route.finish_direction} of home on Kenmore`;
      description.textContent=route.description;document.querySelector('#route-benefit').textContent=route.benefit;document.querySelector('#route-caution').textContent=route.caution;
      document.querySelector('#download').disabled=false;
      map.fitBounds(document.querySelector('#show-all').checked?L.latLngBounds(data.routes.flatMap(r=>r.shape)):lines[route.id].getBounds(),{padding:[28,28]});
      history.replaceState(null,'','#'+route.id);
    }
    document.querySelector('#show-all').onchange=()=>{displayLines();if(document.querySelector('#show-all').checked){const bounds=L.latLngBounds(data.routes.flatMap(r=>r.shape));map.fitBounds(bounds,{padding:[28,28]});}};
    document.querySelector('#fit-route').onclick=()=>map.fitBounds(lines[selected.id].getBounds(),{padding:[28,28]});
    document.querySelector('#download').onclick=()=>{
      const escape=text=>text.replace(/[<>&"']/g,c=>({'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;',"'":'&apos;'}[c]));
      const xml=`<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="FC5K" xmlns="http://www.topografix.com/GPX/1/1"><metadata><desc>Draft 5,000 m mapped course; verify on foot.</desc></metadata><trk><name>${escape(selected.name)}</name><trkseg>${selected.shape.map(p=>`<trkpt lat="${p[0]}" lon="${p[1]}"/>`).join('')}</trkseg></trk></gpx>`;
      const url=URL.createObjectURL(new Blob([xml],{type:'application/gpx+xml'}));const a=document.createElement('a');a.href=url;a.download=`fc5k-${selected.id}-5k.gpx`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    };
    select(data.routes.find(r=>r.id===location.hash.slice(1))||data.routes[0]);
  } catch(error) {console.error('Course map failed:',error);description.textContent='Could not load the map. Please refresh to try again.';}
})();
