---
title: "The First Trillion, to Scale"
weight: 30
description: "A short exercise in division. The first trillion-dollar fortune, set to scale against the net worth of a typical American family, the median income of a country from every United Nations region, the output of nations, and the output of whole UN regions."
summary: "One fortune, divided by everything"
tags: ["data essay", "inequality", "scale"]
showDate: false
showReadingTime: true
showAuthor: false
---

{{< katex >}}

{{< lead >}}
A trillion is not a feeling. It is a number so large that the only way to understand it is to divide it by something familiar, and watch the familiar thing disappear.
{{< /lead >}}

<style>
.prose table, article table, main table, table{width:-webkit-fit-content !important;width:fit-content !important;margin-left:auto !important;margin-right:auto !important;}
</style>

<script>
window.__tc=function(){try{var e=document.querySelector('.prose')||document.querySelector('article')||document.querySelector('main')||document.body;return getComputedStyle(e).color||'#333';}catch(_){return '#333';}};
window.__gc=function(){return 'rgba(128,128,128,0.22)';};
window.__retheme=function(){try{if(!window.Chart)return;var reg=Chart.instances||{};Object.keys(reg).forEach(function(k){var c=reg[k];if(!c||!c.options)return;var tc=window.__tc();if(c.options.plugins&&c.options.plugins.title)c.options.plugins.title.color=tc;if(c.options.plugins&&c.options.plugins.legend&&c.options.plugins.legend.labels)c.options.plugins.legend.labels.color=tc;['x','y'].forEach(function(a){var s=c.options.scales&&c.options.scales[a];if(!s)return;if(s.ticks)s.ticks.color=tc;if(s.title)s.title.color=tc;if(s.grid)s.grid.color=window.__gc();});c.update('none');});}catch(_){}};
try{new MutationObserver(window.__retheme).observe(document.documentElement,{attributes:true,attributeFilter:['class']});}catch(_){}
</script>

On June 12, 2026, the public market debut of SpaceX pushed Elon Musk's combined SpaceX and Tesla stakes past a trillion dollars, the first time any individual has been valued that high.[^1][^2] The figure landed between about 1.0 trillion at the offering price and 1.14 trillion at the close.[^2] This essay uses 1.05 trillion as a round middle and does the only thing that makes a number this size legible: divides it by ordinary things.

## Results First

| The Claim | The Number |
| --- | --- |
| Median U.S. Household Net Worths It Equals | About 5.45 Million |
| Dollars His Paper Wealth Gained per Second on IPO Day | About $8 Million |
| Times That Exceeds a Median Worker's Earning Rate | About 10 Billion |
| Billion-Dollar Fortunes It Contains | About 1,050 |
| Years at the U.S. Median Income to Match It | About 40 Million |
| Years at the World Median Income | About 311 Million |
| National Economies Larger than It | Only About Nineteen |

## One Family, and Then Him

The fairest comparison is net worth against net worth: one family's lifetime of saving against one man's holdings. The median U.S. family net worth, everything owned minus everything owed, is about 192,700 dollars.[^4] Divide:

\\[ \dfrac{1.05 \times 10^{12}\ \text{USD}}{1.927 \times 10^{5}\ \text{USD per family}} \approx 5{,}448{,}884\ \text{families} \\]

One man is not a rich family. He is five and a half million of them. A typical family sits at \\(10^{5}\\) dollars and one man sits at \\(10^{12}\\) dollars, seven orders of magnitude apart.

Against the roughly 127 million households the Census counts,[^7] those 5.45 million families are more than four percent of the country:

\\[ \dfrac{5.45 \times 10^{6}\ \text{households}}{1.27 \times 10^{8}\ \text{households}} \approx 4.3\ \text{percent} \\]

In the block below, every pixel is one household. The counter at the top of the frame tracks how many you have scrolled past, and what they are worth together.

<div id="nwwrap" style="position:relative;width:100%;margin:1.75rem 0;display:block;">
<div style="font-weight:700;font-size:1.05rem;margin-bottom:.3rem;">One Household, One Pixel</div>
<div style="font-size:.92rem;line-height:1.55;margin-bottom:.7rem;">Every pixel is one median U.S. household, 192,700 dollars. The whole block is the 1.05 trillion dollar fortune: 5,448,884 of them. One pixel is barely visible. The white lines mark each additional million households, and the readout counts the line just beneath it. Scroll all the way down and the count reaches the full 5,448,884, the entire fortune, each pixel a family's whole net worth.</div>
<div id="nwscroll" style="position:relative;width:100%;height:78vh;max-height:760px;overflow-y:auto;overflow-x:hidden;background:#06121c;border:1px solid rgba(128,128,128,.45);border-radius:8px;">
<div id="nwodo" style="position:sticky;top:0;z-index:4;background:rgba(4,12,20,.96);color:#fff;font:600 15px/1.35 system-ui,-apple-system,sans-serif;padding:9px 13px;border-bottom:1px solid rgba(255,255,255,.3);">0 Households | $0</div>
<div id="nwinner" style="position:relative;">
<canvas id="nwcanvas" style="display:block;width:100%;height:auto;"></canvas>
</div>
<div id="nwspace" style="width:100%;height:0;"></div>
</div>
</div><script>
(function(){
 var N=5448884, M=192700;
 var sc=document.getElementById('nwscroll'), cv=document.getElementById('nwcanvas'), inner=document.getElementById('nwinner'), odo=document.getElementById('nwodo'), space=document.getElementById('nwspace');
 if(!cv||!cv.getContext) return;
 function clamp(v){return v<0?0:(v>255?255:v);}
 function fmt(n){return Math.round(n).toLocaleString('en-US');}
 var lastW=-1, rows=0, w=0;
 function build(force){
  var CW=Math.floor(sc.clientWidth)||690; w=Math.max(CW,1500);
  if(!force && w===lastW) return; lastW=w;
  rows=Math.ceil(N/w); cv.width=w; cv.height=rows;
  var ctx=cv.getContext('2d'); var img=ctx.createImageData(w,rows); var d=img.data;
  for(var i=0;i<N;i++){ var o=i*4; var n=(Math.random()*64-32)|0; d[o]=clamp(8+n); d[o+1]=clamp(120+n); d[o+2]=clamp(190+n); d[o+3]=255; }
  ctx.putImageData(img,0,0);
 }
 function addBand(val,y,fin){
  var b=document.createElement('div'); b.className='nwband';
  b.style.cssText='position:absolute;left:0;right:0;top:'+y+'px;height:0;border-top:'+(fin?'3px solid #F0E442':'2px solid rgba(255,255,255,.95)')+';pointer-events:none;';
  var lab=document.createElement('span'); lab.textContent=fin?(fmt(val)+' Households, the Whole Fortune'):(fmt(val)+' Households');
  lab.style.cssText='position:absolute;left:8px;'+(fin?'bottom:3px;background:#6b6000;':'top:3px;background:rgba(4,12,20,.92);')+'color:#fff;font:600 12px/1.2 system-ui,sans-serif;padding:2px 7px;border-radius:3px;white-space:nowrap;';
  b.appendChild(lab); inner.appendChild(b);
 }
 function layout(){
  var Hd=cv.clientHeight||1;
  space.style.height=Math.max(0,(sc.clientHeight||0)-(odo.offsetHeight||0))+'px';
  var olds=inner.querySelectorAll('.nwband'); for(var j=0;j<olds.length;j++) olds[j].parentNode.removeChild(olds[j]);
  for(var k=1;k*1000000<N;k++){ addBand(k*1000000,(k*1000000/N)*Hd,false); }
  addBand(N,Hd-1,true);
 }
 function tick(){ var Hd=cv.clientHeight||1; var hh=Math.min(N,Math.max(0,Math.round((sc.scrollTop/Hd)*N))); odo.innerHTML=fmt(hh)+' Households | $'+fmt(hh*M); }
 build(true);
 requestAnimationFrame(function(){layout();tick();});
 sc.addEventListener('scroll',tick);
 window.addEventListener('resize',function(){build(false);requestAnimationFrame(function(){layout();tick();});});
})();
</script>

## Where a Fortune Sits

On a logarithmic scale, where every step is a tenfold jump, the fortune lands among the wealth levels people half-recognize, from a typical U.S. household up. The gap from a household to a billionaire is about the gap from a billionaire to Musk. All five bars are net worth in U.S. dollars.

{{< chart >}}
type: 'bar',
data: {
  labels: ['U.S. Median Household Net Worth', 'U.S. Mean Household Net Worth', 'A $100 Million Fortune', 'A Billionaire', 'Elon Musk'],
  datasets: [{
    label: 'Net Worth, US Dollars',
    data: [192700, 1059470, 100000000, 1000000000, 1050000000000],
    backgroundColor: ['#0072B2', '#369CCF', '#E69F00', '#CC79A7', '#D55E00'], // audit-ok: Okabe-Ito fills kept for CVD identity; bars bordered via borderColor for white-bg legibility
    borderColor: window.__tc(), borderWidth: 1
  }]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 18, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    title: { display: true, color: window.__tc(), text: 'Where the Fortune Sits, From a U.S. Household Up (Net Worth, Log Scale)' }
  },
  scales: {
    x: {
      type: 'logarithmic', min: 10000, max: 10000000000000,
      title: { display: true, color: window.__tc(), text: 'US Dollars of Net Worth (Logarithmic)' },
      ticks: { color: window.__tc(), callback: function(v){ var e=Math.log10(v); if(Math.abs(e-Math.round(e))>0.001) return null; var s=['$1','$10','$100','$1k','$10k','$100k','$1M','$10M','$100M','$1B','$10B','$100B','$1T','$10T']; return s[Math.round(e)]; } },
      grid: { color: window.__gc() }
    },
    y: { ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

A billion is already a number almost no one can hold in the mind, and the fortune is about 1,050 of them:

\\[ \dfrac{1.05 \times 10^{12}\ \text{USD}}{1 \times 10^{9}\ \text{USD}} \approx 1{,}050 \\]

The U.S. mean household net worth, about 1.06 million dollars,[^4] already runs nearly five and a half times the U.S. median, because a few enormous fortunes drag the average up. This one is close to a million times that mean.

## A Second of His Day

On the day of the offering, the IPO lifted the value of Musk's SpaceX shares by about 192.3 billion dollars.[^2] Spread across the 6.5-hour trading day, that is a rate the words cannot keep up with:

\\[ \dfrac{192.3 \times 10^{9}\ \text{USD}}{6.5\ \text{h} \times 3600\ \text{s/h}} \approx 8.2 \times 10^{6}\ \text{USD per second} \\]

A U.S. worker at the median earns about 26,306 dollars a year, which is roughly 0.0008 dollars per second. Set the two earning rates against each other:

\\[ \dfrac{8.2 \times 10^{6}\ \text{USD/s, Musk}}{8.3 \times 10^{-4}\ \text{USD/s, worker}} \approx 10^{10} \\]

About ten billion to one. The worker's entire year of income is what one man's paper wealth gained, on that day, roughly every three thousandths of a second.

{{< chart >}}
type: 'bar',
data: {
  labels: ['A Median U.S. Worker', 'Musk, on IPO Day'],
  datasets: [{
    label: 'Dollars Earned per Second',
    data: [0.000834, 8217949],
    backgroundColor: ['#0072B2', '#D55E00'],
    borderWidth: 0
  }]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 18, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    title: { display: true, color: window.__tc(), text: 'Dollars Earned per Second, Worker Versus Musk (Log Scale)' }
  },
  scales: {
    x: {
      type: 'logarithmic', min: 0.0001, max: 100000000,
      title: { display: true, color: window.__tc(), text: 'US Dollars per Second (Logarithmic)' },
      ticks: { color: window.__tc(), callback: function(v){ var e=Math.log10(v); if(Math.abs(e-Math.round(e))>0.001) return null; var m={'-4':'$0.0001','-3':'$0.001','-2':'$0.01','-1':'$0.10','0':'$1','1':'$10','2':'$100','3':'$1k','4':'$10k','5':'$100k','6':'$1M','7':'$10M','8':'$100M'}; return m[String(Math.round(e))]; } },
      grid: { color: window.__gc() }
    },
    y: { ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

## A Lifetime Is Not Enough

Set the fortune against an ordinary income. Let the net worth be \\(W\\) in dollars and the annual median income be \\(m\\) in dollars per year; then \\(T\\), the years of earning everything and spending nothing to reach \\(W\\), is just division:

\\[ T = \dfrac{W}{m} \\]

A person at the U.S. median lives on about 72 dollars a day, near 26,306 dollars a year:

\\[ T_{\text{US}} = \dfrac{1.05 \times 10^{12}\ \text{USD}}{26{,}306\ \text{USD per year}} \approx 4.0 \times 10^{7}\ \text{years} \\]

Forty million years. The same number reads across people instead of years: about 40 million Americans, each earning the U.S. median for a single year, together holding what one man holds. And the United States sits near the top of the ladder. To stay fair across the whole world rather than only the rich West, the comparison borrows a structure the United Nations already maintains: the M49 standard.[^8] It is the UN's official statistical geography, a system that gives every country a code and files it under a continental region (Africa, the Americas, Asia, Europe, Oceania) and a finer subregion (Northern Africa, the Caribbean, Central Asia, and so on), so that the word region means the same thing from one report to the next. Borrowing it keeps the picks below honest rather than cherry-picked. One country sits near the middle of each of the five continental regions:

{{< mermaid >}}
flowchart TD
  W["World Median | 311M Yrs"] --> EU["Europe | Poland | 74M Yrs"]
  W --> AM["Americas | Mexico | 201M Yrs"]
  W --> OC["Oceania | Fiji | 402M Yrs"]
  W --> AS["Asia | Indonesia | 454M Yrs"]
  W --> AF["Africa | Nigeria | 849M Yrs"]
{{< /mermaid >}}

Each of those is a lifetime of saving every cent, banked and never spent, to match one fortune:

{{< chart >}}
type: 'bar',
data: {
  labels: ['Europe | Poland', 'Americas | Mexico', 'World Median', 'Oceania | Fiji', 'Asia | Indonesia', 'Africa | Nigeria'],
  datasets: [{
    label: 'Millions of Years of Median Income to Equal the Fortune',
    data: [74, 201, 311, 402, 454, 849],
    backgroundColor: ['#E69F00', '#0072B2', '#CC79A7', '#369CCF', '#009E73', '#D55E00'], // audit-ok: Okabe-Ito fills kept for CVD identity; bars bordered via borderColor for white-bg legibility
    borderColor: window.__tc(), borderWidth: 1
  }]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    title: { display: true, color: window.__tc(), text: 'Years to Match the Fortune, One Country per UN Region' }
  },
  scales: {
    x: { title: { display: true, color: window.__tc(), text: 'Millions of Years (Banking 100% of Income)' }, ticks: { color: window.__tc() }, grid: { color: window.__gc() }, beginAtZero: true },
    y: { ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

Pointed the other way, divide by the world median income of about 3,376 dollars a year and count people:

\\[ \dfrac{1.05 \times 10^{12}\ \text{USD}}{3{,}376\ \text{USD per person-year}} \approx 3.1 \times 10^{8}\ \text{person-years} \\]

The fortune is a full year of income for about 311 million people at the world median, roughly the population of the United States. Not their savings. Everything they earn. These spans run off the edge of human history, so the companion essay in this room, which compresses Earth's 4.54 billion years into one 78-year life, is the right ruler: the Nigerian saver would have had to start about fifteen years into that life, deep in the Neoproterozoic, before animals existed.

<div id="rgwrap" style="position:relative;width:100%;margin:1.85rem 0;display:block;">
<div style="font-weight:700;font-size:1.05rem;margin-bottom:.3rem;">One Person, One Pixel, by Region</div>
<div style="font-size:.92rem;line-height:1.55;margin-bottom:.7rem;">Built like the households block above, one pixel per person, the same density. But here each pixel is one person earning the chosen region's median income for a year, and the wall holds every person the fortune could pay for a full year, tens to hundreds of millions of them. Pick a region and scroll: the count climbs to the region's full total, the entire 1.05 trillion dollar fortune. The menu opens on your own part of the world, set from your device time zone, and you can switch it to compare. The wall length tracks the region's median income alone, lower income means a longer wall, so Africa runs longest and Europe shortest. How that total sits against the people who actually live there is the twist: it covers Oceania many times over but reaches only a fraction of the larger regions.</div>
<div style="margin-bottom:.7rem;">
<label for="rgsel" style="font-size:.92rem;font-weight:600;margin-right:.45rem;">Region:</label>
<select id="rgsel" style="font:inherit;font-size:.95rem;padding:5px 9px;border:1px solid currentColor;border-radius:6px;background:transparent;color:inherit;">
<option value="0">Americas</option>
<option value="1">Africa</option>
<option value="2">Asia</option>
<option value="3">Europe</option>
<option value="4">Oceania</option>
</select>
</div>
<div id="rgcap" style="font-size:.92rem;line-height:1.5;margin-bottom:.7rem;"></div>
<div id="rgscroll" style="position:relative;width:100%;height:78vh;max-height:760px;overflow-y:auto;overflow-x:hidden;background:#0b0e12;border:1px solid rgba(128,128,128,.45);border-radius:8px;">
<div id="rgodo" style="position:sticky;top:0;z-index:4;background:rgba(8,10,14,.96);color:#fff;font:600 15px/1.35 system-ui,-apple-system,sans-serif;padding:9px 13px;border-bottom:1px solid rgba(255,255,255,.3);">0 People | $0</div>
<div id="rginner" style="position:relative;width:100%;"></div>
<div id="rgspace" style="width:100%;height:0;"></div>
</div>
</div><script>
(function(){
 var F=1.05e12, W=1500, TILE=1800, BAND=10000000, BUF=1;
 var R=[
  {l:'the Americas',n:'The Americas',v:5244,c:[230,159,0],p:1050000000,pl:'about 1.05 billion'},
  {l:'Africa',n:'Africa',v:1406,c:[213,94,0],p:1520000000,pl:'about 1.5 billion'},
  {l:'Asia',n:'Asia',v:3846,c:[204,121,167],p:4800000000,pl:'about 4.8 billion'},
  {l:'Europe',n:'Europe',v:13949,c:[0,158,115],p:744000000,pl:'about 744 million'},
  {l:'Oceania',n:'Oceania',v:2574,c:[240,228,66],p:46000000,pl:'about 46 million'}
 ];
 R.forEach(function(r){ r.T=Math.round(F/r.v); r.rows=Math.ceil(r.T/W); });
 var sc=document.getElementById('rgscroll'), inner=document.getElementById('rginner'), odo=document.getElementById('rgodo'), space=document.getElementById('rgspace'), sel=document.getElementById('rgsel'), cap=document.getElementById('rgcap');
 if(!sc||!document.createElement('canvas').getContext) return;
 function detectRegion(){
  try{
   var tz=(Intl.DateTimeFormat().resolvedOptions().timeZone||'').toLowerCase();
   var area=tz.split('/')[0];
   var m={america:0,us:0,canada:0,brazil:0,mexico:0,chile:0,cuba:0,jamaica:0,
    africa:1,egypt:1,libya:1,indian:1,
    asia:2,hongkong:2,singapore:2,japan:2,prc:2,roc:2,israel:2,iran:2,
    europe:3,gb:3,eire:3,iceland:3,portugal:3,poland:3,atlantic:3,arctic:3,
    australia:4,pacific:4,nz:4,
    antarctica:0};
   if(Object.prototype.hasOwnProperty.call(m,area)) return m[area];
  }catch(e){}
  return 0;
 }
 var cur=detectRegion(), scale=1, Hd=1, tileH=1, tiles={}, pend=false;
 function clamp(v){return v<0?0:(v>255?255:v);}
 function fmt(n){return Math.round(n).toLocaleString('en-US');}
 function nTiles(){ return Math.ceil(R[cur].rows/TILE); }
 function drawTile(idx){
  var startRow=idx*TILE; var h=Math.min(TILE,R[cur].rows-startRow); if(h<=0) return null;
  var can=document.createElement('canvas'); can.className='rgtile'; can.width=W; can.height=h;
  can.style.cssText='position:absolute;left:0;width:100%;top:'+(startRow*scale)+'px;height:'+(h*scale)+'px;display:block;';
  var ctx=can.getContext('2d'); var img=ctx.createImageData(W,h); var d=img.data;
  var c=R[cur].c, r0=c[0], g0=c[1], b0=c[2];
  var ppl=Math.min(W*h, R[cur].T-startRow*W);
  for(var i=0;i<ppl;i++){ var o=i*4; var n=(Math.random()*64-32)|0; d[o]=clamp(r0+n); d[o+1]=clamp(g0+n); d[o+2]=clamp(b0+n); d[o+3]=255; }
  ctx.putImageData(img,0,0); return can;
 }
 function clearTiles(){ for(var k in tiles){ if(tiles[k].parentNode) inner.removeChild(tiles[k]); delete tiles[k]; } }
 function virtualize(){
  var base=inner.offsetTop||0; var top=sc.scrollTop-base; var bot=top+(sc.clientHeight||0); var nt=nTiles();
  var first=Math.max(0,Math.floor(top/tileH)-BUF); var last=Math.min(nt-1,Math.floor(bot/tileH)+BUF);
  for(var k in tiles){ var ki=+k; if(ki<first||ki>last){ if(tiles[k].parentNode) inner.removeChild(tiles[k]); delete tiles[k]; } }
  for(var idx=first; idx<=last; idx++){ if(!tiles[idx]){ var c=drawTile(idx); if(c){ inner.appendChild(c); tiles[idx]=c; } } }
 }
 function addBand(val,fin){
  var y=fin?(Hd-3):((val/R[cur].T)*Hd);
  var b=document.createElement('div'); b.className='rgband';
  b.style.cssText='position:absolute;left:0;right:0;top:'+y+'px;height:0;border-top:'+(fin?'3px':'2px')+' solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.55);pointer-events:none;z-index:3;';
  var lab=document.createElement('span'); lab.textContent=fin?(fmt(val)+' People, the Whole Fortune'):(fmt(val)+' People');
  lab.style.cssText='position:absolute;left:8px;'+(fin?'bottom:3px;':'top:3px;')+'background:rgba(8,10,14,.92);color:'+(fin?'#F0E442':'#fff')+';font:'+(fin?'700':'600')+' 12px/1.2 system-ui,sans-serif;padding:2px 7px;border-radius:3px;white-space:nowrap;';
  b.appendChild(lab); inner.appendChild(b);
 }
 function bands(){
  var olds=inner.querySelectorAll('.rgband'); for(var j=0;j<olds.length;j++) olds[j].parentNode.removeChild(olds[j]);
  for(var v=BAND; v<R[cur].T; v+=BAND){ addBand(v,false); }
  addBand(R[cur].T,true);
 }
 function metrics(){ scale=(sc.clientWidth||W)/W; Hd=R[cur].rows*scale; tileH=TILE*scale; inner.style.height=Hd+'px'; space.style.height=Math.max(0,(sc.clientHeight||0)-(odo.offsetHeight||0))+'px'; }
 function tick(){ var f=Math.min(1,Math.max(0,sc.scrollTop/Hd)); var ppl=Math.min(R[cur].T,Math.round(f*R[cur].T)); odo.innerHTML=fmt(ppl)+' People | $'+fmt(ppl*R[cur].v); }
 function setCap(){ var r=R[cur]; var rat=r.T/r.p; var comp=rat>=1?('the fortune could pay every one of them a full year at this income about '+Math.round(rat)+' times over.'):('even the whole fortune reaches only about one in '+Math.round(1/rat)+' of them.'); cap.innerHTML='Each pixel is one person at the median income of '+r.l+', about $'+fmt(r.v)+' a year. Scroll all the way down and the count reaches '+fmt(r.T)+' people, the entire 1.05 trillion dollar fortune at that income. '+r.n+' is home to '+r.pl+' people, so '+comp; }
 function rebuild(){ clearTiles(); metrics(); bands(); virtualize(); tick(); }
 sel.addEventListener('change',function(){ cur=parseInt(sel.value,10)||0; sc.scrollTop=0; setCap(); rebuild(); });
 sc.addEventListener('scroll',function(){ if(pend) return; pend=true; requestAnimationFrame(function(){ pend=false; virtualize(); tick(); }); });
 window.addEventListener('resize',function(){ requestAnimationFrame(rebuild); });
 sel.value=String(cur); setCap(); requestAnimationFrame(rebuild);
})();
</script>

## Bigger Than Nations

A person is the small unit. A country is the large one, and the fortune clears almost all of them. Only about nineteen national economies produce more in a year than one man holds on paper.[^2][^6] The twentieth, Switzerland, he matches outright, and the rest he tops:

{{< chart >}}
type: 'bar',
data: {
  labels: ['Elon Musk (1 Person)', 'Switzerland', 'Poland', 'Taiwan', 'Argentina', 'Sweden', 'Singapore'],
  datasets: [{
    label: 'Net Worth or Annual GDP, USD Billions',
    data: [1050, 1044, 1036, 920, 681, 669, 604],
    backgroundColor: ['#D55E00', '#369CCF', '#369CCF', '#369CCF', '#369CCF', '#369CCF', '#369CCF'],
    borderWidth: 0
  }]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    title: { display: true, color: window.__tc(), text: 'One Man Against Entire National Economies (2025 GDP, USD Billions)' }
  },
  scales: {
    x: { title: { display: true, color: window.__tc(), text: 'USD Billions' }, ticks: { color: window.__tc() }, grid: { color: window.__gc() }, beginAtZero: true },
    y: { ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

His paper wealth is about the entire annual output of Switzerland, one of the richest countries on Earth, roughly 1.04 trillion dollars.

For heritage's sake: Spain, at about 1.9 trillion, is still larger than the fortune; Greece, near 280 billion, is not. South Africa, where Musk was born, produces about 427 billion dollars a year, so one man outweighs his birth country by more than two to one.

## Bigger Than Regions

A country is not the largest unit. Drop one level in the same M49 standard, from continents to subregions,[^8] and the fortune swallows whole ones. Summing the IMF output of every country the geoscheme files under a subregion, one man's holdings come to about the entire annual product of Northern Africa, and they top all of West Africa, all of East Africa, the Caribbean, and Central Asia, each home to tens or hundreds of millions of people.

{{< chart >}}
type: 'bar',
data: {
  labels: ['Elon Musk | 1 Person', 'Northern Africa | 263M People', 'Western Africa | 468M People', 'Eastern Africa | 475M People', 'The Caribbean | 44M People', 'Central Asia | 83M People'],
  datasets: [{
    label: 'Net Worth or Combined Regional GDP, USD Billions',
    data: [1050, 975, 717, 607, 595, 566],
    backgroundColor: ['#D55E00', '#009E73', '#009E73', '#009E73', '#009E73', '#009E73'],
    borderWidth: 0
  }]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: false },
    title: { display: true, color: window.__tc(), text: 'One Man Against Entire UN Regions (2025 GDP, USD Billions)' }
  },
  scales: {
    x: { title: { display: true, color: window.__tc(), text: 'USD Billions' }, ticks: { color: window.__tc() }, grid: { color: window.__gc() }, beginAtZero: true },
    y: { ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

Stack the poorer ones and the point sharpens. Three whole subregions together, all of East Africa, all of Middle Africa, and every island nation of the Pacific, twenty-eight countries and more than 700 million people between them, only just reach one man:

{{< chart >}}
type: 'bar',
data: {
  labels: ['Elon Musk', 'Three UN Subregions, Stacked'],
  datasets: [
    { label: 'Eastern Africa (475M People)', data: [0, 607], backgroundColor: '#009E73', borderColor: window.__tc(), borderWidth: 1 },
    { label: 'Middle Africa (211M People)', data: [0, 370], backgroundColor: '#369CCF', borderColor: window.__tc(), borderWidth: 1 },
    { label: 'Pacific Islands (16M People)', data: [0, 71], backgroundColor: '#F0E442', borderColor: window.__tc(), borderWidth: 1 }, // audit-ok: Pacific Islands segment; Okabe-Ito yellow kept for CVD identity, bordered for legibility
    { label: 'Elon Musk (1 Person)', data: [1050, 0], backgroundColor: '#D55E00', borderColor: window.__tc(), borderWidth: 1 }
  ]
},
options: {
  indexAxis: 'y',
  layout: { padding: { top: 8, right: 16, bottom: 8, left: 8 } },
  plugins: {
    legend: { display: true, position: 'bottom', labels: { color: window.__tc() } },
    title: { display: true, color: window.__tc(), text: 'Three UN Subregions, Stacked, to Equal One Man (2025 GDP, USD Billions)' }
  },
  scales: {
    x: { stacked: true, title: { display: true, color: window.__tc(), text: 'USD Billions' }, ticks: { color: window.__tc() }, grid: { color: window.__gc() }, beginAtZero: true },
    y: { stacked: true, ticks: { color: window.__tc() }, grid: { color: window.__gc() } }
  }
}
{{< /chart >}}

In billions, that is the sum laid bare:

\\[ (607 + 370 + 71)\ \text{USD billion} \quad \approx \quad 1{,}048\ \text{USD billion} \quad \approx \quad \text{Him} \\]

That is the whole essay in one image. Three regions of the world, twenty-eight countries, more than 700 million lives, stacked end to end, come out even with one person.

## What This Does Not Mean

A data essay that stopped at the biggest number would be dishonest, so it will not.

The comparison against nations and regions sets a stock against a flow. The family comparison is the fair one: a stock against a stock. A national or regional GDP is a flow, everything an economy makes in one year, and next year it makes roughly that much again. A net worth is a stock, an accumulated total sitting still. "Bigger than Switzerland" is true only in the narrow sense that the number is larger, while Switzerland generates its number every year and the fortune is a snapshot.

The word "paper" matters too. This is not cash. Almost all of it is the market's valuation of shares in two companies, and Musk has said under a tenth of one percent of his net worth is cash. It moves by tens of billions on an ordinary day, and selling at that scale would collapse the very prices that define it. The fortune is real the way a high tide is real: measurable, consequential, impossible to carry away in a bucket.

One wrinkle is specific to the income chart. Richer countries usually report income, poorer ones often report consumption, and the two are not perfectly comparable. None of it changes the conclusion. Whether a typical person needs 74 million years or 849 million, the gap is hundreds of millions of years of labor, and a wrong guess of even a factor of two leaves the point where it stood.

## How These Countries Were Chosen

The income comparison and the regional totals both lean on the United Nations M49 geoscheme,[^8] the standard that assigns every country to one of five regions: Africa, the Americas, Asia, Europe, and Oceania. For the income chart, one country represents each, chosen to sit near the middle of its region rather than at the rich or poor extreme: Nigeria, Mexico, Indonesia, Poland, and Fiji. Each lands close to the World Bank's own regional benchmark.[^5] Nigeria tracks the Sub-Saharan figure, Mexico tracks Latin America and the Caribbean, Poland tracks Europe and Central Asia, and Indonesia falls between the South and East Asian benchmarks.

Two honest caveats. "Middle" is a judgment: a population-weighted regional median would shift some picks, most sharply in the Americas, where the United States pulls the figure up. Oceania is the hardest, genuinely split between high-income Australia and New Zealand and the lower-income Pacific islands that Fiji represents; weighted by population the typical Oceanian would look much more like Australia, where the median is roughly eight times Fiji's. The region defies a single representative, and that is worth seeing rather than smoothing over.

## Methods and Sources

Net worth of roughly 1.05 trillion dollars as of June 12, 2026, from combined SpaceX and Tesla stakes following the SpaceX IPO (Nasdaq ticker SPCX), reported by Bloomberg, CBS News, and CNBC.[^1][^2][^3] Estimates ranged from about 1.0 trillion at the offering price to about 1.14 trillion at the close;[^2] the 192.3 billion one-day gain and the count of economies above a trillion dollars are from the same CBS reporting.[^2] All division here uses 1.05 trillion.

Median and mean U.S. family net worth, about 192,700 dollars and about 1.06 million dollars in 2022 dollars, are from the Federal Reserve's 2022 Survey of Consumer Finances, the most recent available; the 2025 survey is expected in late 2026.[^4] The household share uses the roughly 127 million households counted in the 2020 Census.[^7] The per-second figure is arithmetic on the headline number, using a 6.5-hour trading day and a median full-time worker's income spread evenly across the year.

Median income figures are median income or consumption per person per day, in 2021 PPP international dollars, from the World Bank Poverty and Inequality Platform, via Our World in Data[^5] (latest year per country: Nigeria 2022, Mexico 2024, Indonesia 2024, Poland 2023, Fiji 2019, United States 2024, world median 2024). Daily figures are multiplied by 365. The series mixes income and consumption surveys, a known comparability limit the source documents. Regions follow the United Nations M49 geoscheme.[^8]

National and regional GDP figures are nominal output, 2025 estimate, from the IMF World Economic Outlook (April 2026).[^6] National values used: Switzerland about 1,044 billion, Poland about 1,036, Taiwan about 920, Argentina about 681, Sweden about 669, Singapore about 604, Spain about 1,904, Greece about 280, South Africa about 427. The income chart uses the five continental M49 regions; the output charts use the finer M49 subregions. Subregional totals are the sum of IMF nominal GDP over the countries the standard files under each: Northern Africa about 975 billion, Western Africa about 717, Eastern Africa about 607, the Caribbean about 595, Central Asia about 566, Middle Africa about 370, and the Pacific islands (Melanesia, Micronesia, and Polynesia, all of Oceania except Australia and New Zealand) about 71. The stacked figure adds Eastern Africa, Middle Africa, and the Pacific islands to about 1,048 billion across twenty-eight countries and roughly 700 million people. Regional populations are implied by the same source, dividing each country's GDP by its GDP per capita and summing. The interactive region block divides the fortune by each UN region's median income per person, where that regional figure is the median of the latest national medians of all countries the M49 standard files under the region, drawn from the same World Bank Poverty and Inequality Platform data via Our World in Data,[^5] to count the people a full year of that income would equal; the interactive region block uses the same one-pixel-per-person rendering as the households figure and scrolls through the region's entire count, from about 75 million people for Europe to about 747 million for Africa, drawn in tiles loaded as you scroll so the taller regions render without exceeding browser canvas limits. Each region's count is then set against its own mid-2024 population from the UN World Population Prospects 2024,[^9] which is how the readout reports the figure as a multiple of, or a fraction of, everyone who lives there. The menu opens on the visitor's own region, inferred from the browser time zone with the Americas as the fallback, and no network request or address lookup is involved. The deep-time placement uses the 4.54-billion-year age of the Earth and the 78-year compression from the companion essay in this room.

[^1]: Tom Maloney, [Elon Musk Hits $1 Trillion Net Worth as SpaceX IPO Breaks Records](https://www.bloomberg.com/news/articles/2026-06-12/elon-musk-hits-1-trillion-net-worth-as-spacex-ipo-breaks-records), Bloomberg, June 12, 2026.
[^2]: [Elon Musk becomes the world's first trillionaire with SpaceX's IPO](https://www.cbsnews.com/news/elon-musk-spacex-ipo-trillionaire-wealth/), CBS News, June 12, 2026.
[^3]: [Elon Musk's net worth poised to sail past $1 trillion in SpaceX IPO](https://www.cnbc.com/2026/06/03/elon-musks-net-worth-poised-to-sail-past-1-trillion-in-spacex-ipo.html), CNBC, June 3, 2026.
[^4]: [Changes in U.S. Family Finances from 2019 to 2022: Evidence from the Survey of Consumer Finances](https://www.federalreserve.gov/publications/october-2023-changes-in-us-family-finances-from-2019-to-2022.htm), Board of Governors of the Federal Reserve System, October 2023.
[^5]: [Median income or consumption per day](https://ourworldindata.org/grapher/daily-median-income), World Bank Poverty and Inequality Platform (2026), with major processing by Our World in Data.
[^6]: [World Economic Outlook Database](https://www.imf.org/en/Publications/WEO), International Monetary Fund, April 2026.
[^7]: [Households and Families: 2020](https://www.census.gov/library/publications/2024/dec/c2020br-10.html), U.S. Census Bureau, report C2020BR-10.
[^8]: [Standard Country or Area Codes for Statistical Use (M49)](https://unstats.un.org/unsd/methodology/m49/), United Nations Statistics Division.
[^9]: [World Population Prospects 2024](https://population.un.org/wpp/), United Nations Department of Economic and Social Affairs, Population Division, mid-2024 estimates.
