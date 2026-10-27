import fs from 'fs';
import * as topo from 'topojson-client';
const lines = f => fs.readFileSync(f,'utf8').split('\n').filter(l=>l.trim()&&!l.startsWith('#'));
const F = lines('figures.txt').map((l,i)=>{const p=l.split('|'); if(p.length!==13) throw new Error('bad line '+l);
 return {id:i,n:p[0],s:+p[1],e:+p[2],c:p[3],t:p[4],r:p[5],l:p[6],p:p[7],la:+p[8],lo:+p[9],w:+p[10],a:p[11],k:p[12]}});
const T = lines('temples.txt').map((l,i)=>{const p=l.split('|'); if(p.length!==7) throw new Error('bad '+l);
 return {n:p[0],d:p[1],g:p[2],p:p[3],la:+p[4],lo:+p[5],k:p[6]}});
let bad=[];
const names=new Set();
for(const f of F){ if(names.has(f.n)) bad.push('dup '+f.n); names.add(f.n);
 if(!(f.s<=f.e)) bad.push('dates '+f.n); if(f.la<5||f.la>38||f.lo<60||f.lo>98) bad.push('coord '+f.n);
 if(!'SG AC BH YO RF MA AY MU'.split(' ').includes(f.c)) bad.push('cat '+f.n); if(!'HTL'.includes(f.a)) bad.push('att '+f.n);}
for(const t of T){ if(t.la<5||t.la>38||t.lo<60||t.lo>98) bad.push('tcoord '+t.n);}
console.log('figures',F.length,'temples',T.length,'women',F.filter(f=>f.w).length,'issues',bad);
const cats={}; F.forEach(f=>cats[f.c]=(cats[f.c]||0)+1); console.log(cats, 'range', Math.min(...F.map(f=>f.s)), Math.max(...F.map(f=>f.e)));
// basemap
const w = JSON.parse(fs.readFileSync('wa/package/countries-50m.json','utf8'));
const keep = new Set(['356','586','050','524','064','144','104','004','156','364','762','462','418','764','795','860','116','704','784','512']);
const fc = topo.feature(w, w.objects.countries);
const r = x=>Math.round(x*100)/100;
const round = c => typeof c[0]==='number' ? [r(c[0]),r(c[1])] : c.map(round);
const L = JSON.parse(fs.readFileSync('wa/package/land-50m.json','utf8'));
const land = topo.feature(L, L.objects.land);
const inBox = ring => ring.some(([x,y])=>x>55&&x<110&&y>0&&y<45);
const polys=[]; for(const f of land.features){ const g=f.geometry; const ps=g.type==='Polygon'?[g.coordinates]:g.coordinates; for(const p of ps) if(inBox(p[0])) polys.push(round(p)); }
const feats=[{type:'Feature',properties:{},geometry:{type:'MultiPolygon',coordinates:polys}}];
fs.writeFileSync('data.js', 'const FIG='+JSON.stringify(F)+';\nconst TEM='+JSON.stringify(T)+';\nconst BASE='+JSON.stringify({type:'FeatureCollection',features:feats})+';\n');
console.log('data.js KB', (fs.statSync('data.js').size/1024).toFixed(0));
