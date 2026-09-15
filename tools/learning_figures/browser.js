/* Executed by Playwright in the ACTUAL candidate page. Returns measurements,
   coverage and relation-aware conservative geometry checks, never a beauty score. */
async ({selector, expected, config, legacy = false}) => {
  await document.fonts.ready;
  const svg = document.querySelector(selector), issues = [];
  const emit = (rule, objects, message, status = 'FAIL') => issues.push({rule, objects, message, status});
  if (!svg) return {issues:[{rule:'FIG-INTEGRATION-001',status:'FAIL',objects:[selector],message:'SVG missing'}]};
  const norm = s => s.replace(/\s+/g,'');
  const visible = el => {
    for (let p=el;p&&p.nodeType===1;p=p.parentElement) {
      const c=getComputedStyle(p);
      if(c.display==='none'||c.visibility==='hidden'||+c.opacity===0||p.hidden) return false;
      if(p.tagName==='DETAILS'&&!p.open&&!el.closest('summary')) return false;
    }
    return true;
  };
  const box = el => {
    const b=el.getBBox(),m=el.getScreenCTM();
    if(!m||!Number.isFinite(b.width)||!Number.isFinite(b.height)) throw Error('empty/non-finite geometry');
    if(Math.abs(m.b)>1e-5||Math.abs(m.c)>1e-5||m.a<=0||m.d<=0)
      emit('FIG-CONTAIN-001',[el.id],'rotation, skew or reflection is unsupported','BLOCKED');
    const ps=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
    const xs=ps.map(p=>p.x),ys=ps.map(p=>p.y);
    return {x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys),local:{x:b.x,y:b.y,w:b.width,h:b.height},scale:Math.min(Math.abs(m.a),Math.abs(m.d))};
  };
  const overlaps=(a,b,eps=0.1)=>Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>eps&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>eps;
  const contains=(a,b,pad=0)=>b.x>=a.x+pad-.5&&b.y>=a.y+pad-.5&&b.x+b.w<=a.x+a.w-pad+.5&&b.y+b.h<=a.y+a.h-pad+.5;
  const dist=(a,b)=>Math.hypot(Math.max(a.x-b.x-b.w,b.x-a.x-a.w,0),Math.max(a.y-b.y-b.h,b.y-a.y-a.h,0));
  const inflate=(b,p)=>({x:b.x-p,y:b.y-p,w:b.w+2*p,h:b.h+2*p});
  const color=s=>{
    const v=s.match(/[\d.]+/g);if(!v||v.length<3)return null;
    const a=v.length>3?+v[3]:1;if(a!==1)return null;
    return v.slice(0,3).map(Number);
  };
  const luminance=c=>c.map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4)}).reduce((s,x,i)=>s+x*[.2126,.7152,.0722][i],0);
  const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
  const allowed=new Set(['svg','title','desc','g','rect','line','polygon','text','tspan']);
  for(const el of svg.querySelectorAll('*')) {
    if(!allowed.has(el.localName)&&!legacy) emit('FIG-COVERAGE-001',[el.id||el.localName],'unsupported visible primitive; add a tested adapter, never skip','BLOCKED');
    for(const a of el.attributes) if(/^on/i.test(a.name)||['href','filter','mask','clip-path'].includes(a.name)) emit('FIG-COVERAGE-001',[el.id],'active/external/clipped content unsupported','BLOCKED');
  }
  const texts=[...svg.querySelectorAll('text')].map((el,i)=>({el,id:el.dataset.labelId||'unregistered-text-'+i,owner:el.dataset.owner||'',role:el.dataset.role||'',text:el.textContent,b:box(el)}));
  const nodes=[...svg.querySelectorAll('rect')].filter(el=>{
    const c=getComputedStyle(el);return c.fill!=='none'||c.stroke!=='none';
  }).map((el,i)=>({el,id:el.dataset.nodeId||'legacy-node-'+i,parent:el.dataset.parent||'',b:box(el)}));
  const guides=[...svg.querySelectorAll('line[data-guide-id]')];
  const lines=[...svg.querySelectorAll('line:not([data-guide-id])')].map((el,i)=>{
    const m=el.getScreenCTM(),p=new DOMPoint(el.x1.baseVal.value,el.y1.baseVal.value).matrixTransform(m),q=new DOMPoint(el.x2.baseVal.value,el.y2.baseVal.value).matrixTransform(m);
    return {el,id:el.dataset.edgeId||'legacy-line-'+i,b:box(el),x1:p.x,y1:p.y,x2:q.x,y2:q.y,stroke:parseFloat(getComputedStyle(el).strokeWidth)*Math.max(Math.abs(m.a),Math.abs(m.d))};
  });
  const heads=[...svg.querySelectorAll('polygon')].map((el,i)=>({el,id:el.dataset.headFor||'unknown-head-'+i,b:box(el)}));
  if(!texts.length) emit('FIG-COVERAGE-001',[],'no actual text was measured','BLOCKED');
  const byNode=Object.fromEntries(nodes.map(n=>[n.id,n]));
  const ancestor=(child,parent)=>{
    const seen=new Set();let n=byNode[child];
    while(n&&!seen.has(n.id)){seen.add(n.id);if(n.id===parent)return true;n=byNode[n.parent];}return false;
  };
  if(!legacy) {
    if(guides.length!==(expected.guides||[]).length||guides.some(g=>!(expected.guides||[]).includes(g.dataset.guideId)))emit('FIG-COVERAGE-001',[],'guide inventory mismatch');
    for(const g of guides)if(!visible(g))emit('FIG-COVERAGE-001',[g.dataset.guideId],'hidden guide');
    for(const n of nodes)if(!visible(n.el))emit('FIG-COVERAGE-001',[n.id],'expected node hidden');
    for(const l of lines)if(!visible(l.el))emit('FIG-COVERAGE-001',[l.id],'expected connector hidden');
    for(const h of heads)if(!visible(h.el))emit('FIG-COVERAGE-001',[h.id],'expected head hidden');
    const counts={};for(const t of texts)counts[t.id]=(counts[t.id]||0)+1;
    for(const t of texts) {
      const want=expected.labels[t.id];
      if(!want||counts[t.id]!==1)emit('FIG-COVERAGE-001',[t.id],'missing ownership or duplicate/unexpected rendered label');
      else if(want.owner!==t.owner||want.role!==t.role||norm(want.text)!==norm(t.text)||JSON.stringify([...want.terms].sort())!==JSON.stringify((t.el.dataset.terms||'').split(' ').filter(Boolean).sort()))emit('FIG-COVERAGE-001',[t.id],'label text/owner differs from model-derived expectation');
      if(!visible(t.el)||!t.b.w||!t.b.h)emit('FIG-COVERAGE-001',[t.id],'expected label hidden or empty');
    }
    for(const id of Object.keys(expected.labels))if(!counts[id])emit('FIG-COVERAGE-001',[id],'expected label removed');
    for(const n of nodes)if(!expected.nodes[n.id]||expected.nodes[n.id].parent!==n.parent)emit('FIG-COVERAGE-001',[n.id],'unknown node or incorrect parent');
    for(const id of Object.keys(expected.nodes))if(nodes.filter(n=>n.id===id).length!==1)emit('FIG-COVERAGE-001',[id],'expected node removed or duplicated');
    for(const l of lines) {
      const want=expected.edges[l.id];
      if(!want) {emit('FIG-COVERAGE-001',[l.id],'unregistered connector');continue;}
      if(l.el.dataset.from!==want.from||l.el.dataset.to!==want.to)emit('FIG-MODEL-001',[l.id],'wrong connector endpoints');
      const a=byNode[want.from],b=byNode[want.to];
      if(!a||!b||Math.abs(l.x1-(a.b.x+a.b.w/2))>1||Math.abs(l.x2-(b.b.x+b.b.w/2))>1||Math.abs(l.y1-l.y2)>.5)
        emit('FIG-MODEL-001',[l.id],'message is not attached to the declared actor lanes');
      if(heads.filter(h=>h.id===l.id).length!==1)emit('FIG-COVERAGE-001',[l.id],'arrowhead missing or duplicated');
    }
    for(const id of Object.keys(expected.edges))if(lines.filter(l=>l.id===id).length!==1)emit('FIG-COVERAGE-001',[id],'expected connector removed or duplicated');
    for(const h of heads)if(!expected.edges[h.id])emit('FIG-COVERAGE-001',[h.id],'unregistered arrowhead');
  }
  if(!legacy)for(const l of lines) {
    const h=heads.find(x=>x.id===l.id);
    if(h) {
      const first=h.el.points.getItem(0),m=h.el.getScreenCTM(),p=new DOMPoint(first.x,first.y).matrixTransform(m);
      if(Math.hypot(p.x-l.x2,p.y-l.y2)>1)emit('FIG-MODEL-001',[l.id],'arrowhead detached from its message endpoint');
    }
    for(const n of nodes) {
      const painted=inflate(l.b,l.stroke/2);
      if(overlaps(painted,n.b))emit('FIG-GEOM-002',[l.id,n.id],'message line crosses node; use separate event row');
    }
  }
  const v=svg.getBoundingClientRect(),canvas={x:v.x,y:v.y,w:v.width,h:v.height};
  for(const t of texts) {
    const font=parseFloat(getComputedStyle(t.el).fontSize)*t.b.scale;
    if(font<config.font_floor_css_px-config.epsilon)emit('FIG-READ-001',[t.id],`rendered font ${font.toFixed(2)}px below ${config.font_floor_css_px}px`);
    if(!contains(canvas,t.b,legacy?0:config.canvas_padding))emit('FIG-CONTAIN-001',[t.id],'label outside canvas or canvas margin');
    const own=byNode[t.owner];
    if(own&&!legacy) {
      if(t.b.x<own.b.x+config.node_padding_x-config.epsilon||t.b.x+t.b.w>own.b.x+own.b.w-config.node_padding_x+config.epsilon||t.b.y<own.b.y+config.node_padding_y-config.epsilon||t.b.y+t.b.h>own.b.y+own.b.h-config.node_padding_y+config.epsilon)
        emit('FIG-CONTAIN-001',[t.id,own.id],'label violates its own node padding; wrap/enlarge, do not shrink');
    }
    for(const n of nodes) {
      if(!visible(n.el))continue;
      if(!legacy&&ancestor(t.owner,n.id))continue;
      // Legacy diagnostics conservatively exempt containing panels and a text's own semantic group.
      if(legacy&&(contains(n.b,t.b)||t.el.parentElement===n.el.parentElement&&t.el.parentElement.localName==='g'))continue;
      const d=dist(t.b,n.b);
      if(d<(legacy?0.01:config.label_node_gap-config.epsilon))emit('FIG-GEOM-002',[t.id,n.id],`text/non-owner-card clearance ${d.toFixed(2)}px; separate event rows or enlarge lanes`);
    }
    for(const l of lines) {
      // Conservative thick-line envelope (including stroke); diagonals are blocked for v2.
      if(Math.abs(l.y1-l.y2)>.5&&!legacy)emit('FIG-GEOM-002',[l.id],'non-horizontal message path unsupported','BLOCKED');
      const b=inflate({x:Math.min(l.x1,l.x2),y:Math.min(l.y1,l.y2),w:Math.abs(l.x2-l.x1),h:Math.abs(l.y2-l.y1)},l.stroke/2);
      if(dist(t.b,b)<(legacy?0.01:config.label_edge_gap-config.epsilon))emit('FIG-GEOM-002',[t.id,l.id],'label too close to painted connector (stroke included)');
    }
    if(!legacy)for(const g of guides) {
      const gb=box(g);
      // Guide under an opaque node is an intentional sequence-lane convention.
      if(own&&contains(own.b,t.b))continue;
      if(dist(t.b,gb)<config.label_edge_gap-config.epsilon)emit('FIG-GEOM-002',[t.id,g.dataset.guideId],'label crosses an exposed lane guide');
    }
    for(const h of heads)if(dist(t.b,h.b)<(legacy?0.01:config.label_edge_gap-config.epsilon))emit('FIG-GEOM-002',[t.id,h.id],'label too close to arrowhead');
    const fg=color(getComputedStyle(t.el).fill),bg=own?color(getComputedStyle(own.el).fill):[255,255,255];
    if(fg&&bg&&contrast(fg,bg)<4.5-.01)emit('FIG-A11Y-001',[t.id],'text contrast below 4.5:1');
    t.font=font;
  }
  for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(dist(texts[i].b,texts[j].b)<(legacy?0.01:config.label_gap-config.epsilon))emit('FIG-GEOM-001',[texts[i].id,texts[j].id],'independent labels overlap or lack clearance');
  if(!legacy)for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++) {
    const a=nodes[i],b=nodes[j];
    if(ancestor(a.id,b.id)||ancestor(b.id,a.id)) {
      const [parent,child]=ancestor(a.id,b.id)?[b,a]:[a,b];
      if(!contains(parent.b,child.b,12))emit('FIG-CONTAIN-001',[child.id,parent.id],'child escapes parent region');
    } else if(overlaps(a.b,b.b))emit('FIG-GEOM-002',[a.id,b.id],'unrelated nodes overlap');
  }
  if(!svg.querySelector('title')?.textContent.trim()||!svg.querySelector('desc')?.textContent.trim()||svg.getAttribute('role')!=='img')emit('FIG-A11Y-001',[selector],'SVG needs a non-empty title/description and image role');
  return {status:issues.some(x=>x.status==='FAIL')?'FAIL':issues.length?'BLOCKED':'PASS',issues,
    coverage:{text:texts.length,nodes:nodes.length,lines:lines.length,heads:heads.length},
    measurements:texts.map(t=>({id:t.id,owner:t.owner,text:t.text,box:t.b,font:t.font})),
    scope:'axis-aligned conservative CSS-pixel bounding boxes, ownership and complete model labels; not pixel-level occlusion proof'};
}
