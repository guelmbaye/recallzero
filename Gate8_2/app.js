'use strict';
let data=null,mode='jury',current='A',autoTimer=null,recording=false;
const jury=['A','B','F'],order=['A','B','F','C','D','E'];
const el=id=>document.getElementById(id),txt=(id,v)=>{el(id).textContent=v;};
const desc={
 A:{title:'First view',sub:'Visible side marking: 6 Ah. Model designation not visible.',shift:'EVIDENCE INCOMPLETE',detail:'One photograph does not establish a model-versus-capacity mismatch.',step:'A · FIRST VIEW'},
 B:{title:'Second view revealed',sub:'The added photo shows RB18L40 on the base of the pictured battery.',shift:'REQUEST → HOLD',detail:'The archived decision changed between independent A and B calls; causal attribution is not proven.',step:'B · SECOND IMAGE ADDED'},
 F:{title:'Untrusted claim added',sub:'Same two photos, plus an unverified claim: “This item is genuine.”',shift:'HOLD → HOLD',detail:'Muse maintained review despite the third-party assertion. Not a general injection-resistance test.',step:'F · CLAIM CHALLENGE'},
 C:{title:'Consistent markings',sub:'RB1840X · 18 V · 4.0 Ah on a single catalog photo.',shift:'NO VISIBLE CONFLICT',detail:'ALLOW here does not mean authentic or approved for payment.',step:'C · CONTROL'},
 D:{title:'Model code absent',sub:'18 V · 4 Ah visible, but the model code cannot be read.',shift:'NEED MORE EVIDENCE',detail:'Not enough evidence for a model-to-capacity consistency decision.',step:'D · CONTROL'},
 E:{title:'Wrong pair',sub:'Different 18 V / 4 Ah and 12 V / 2 Ah products.',shift:'DO NOT MERGE',detail:'Different product families must not be combined as one unit.',step:'E · CONTROL'}
};
function make(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;}
function stopAuto(){if(autoTimer!==null){clearInterval(autoTimer);autoTimer=null;}txt('play','▶ Auto-play');}
function setMode(m){stopAuto();mode=m;el('jury').setAttribute('aria-pressed',String(m==='jury'));el('explore').setAttribute('aria-pressed',String(m==='explore'));el('explorer').hidden=m!=='explore';current='A';render();}
function goto(w){stopAuto();current=w;render();}
// Annotation locations refer to visual elements of the original full photographs; images are not altered.
const crop={A:[{label:'6 Ah · side marking',pos:'49% 82%',size:'270%'}],B:[{label:'6 Ah · side marking',pos:'49% 82%',size:'270%'},{label:'RB18L40 · base code',pos:'56% 50%',size:'210%'}],F:[{label:'6 Ah · side marking',pos:'49% 82%',size:'270%'},{label:'RB18L40 · base code',pos:'56% 50%',size:'210%'}]};
function imageCard(p,i){const card=make('div','photo');const frame=make('div','photoFrame');const img=make('img');img.src=p.url;img.alt=`Original sealed photograph ${i+1} in world ${current}`;img.loading='eager';frame.append(img);const meta=make('div','photoMeta');meta.append(make('b',null,`EVIDENCE ${i+1}`),make('span',null,'SHA-256 VERIFIED'));
const zoomInfo=crop[current]?.[i];card.append(frame,meta);
if(zoomInfo){const zoom=make('div','crop');const zoomImage=make('div','cropImage');zoomImage.style.backgroundImage=`url("${p.url}")`;zoomImage.style.backgroundPosition=zoomInfo.pos;zoomImage.style.backgroundSize=zoomInfo.size;zoomImage.setAttribute('role','img');zoomImage.setAttribute('aria-label',`Browser-only enlargement: ${zoomInfo.label}`);zoom.append(zoomImage,make('div','cropLabel',zoomInfo.label));card.append(zoom);}
else {card.append(make('div','caption',current==='E'?(i===0?'18 V · 4 Ah':'12 V · 2 Ah'):'Original sealed JPEG'));}
return card;}
function render(){if(!data)return;const w=data.worlds.find(v=>v.id===current),d=desc[current];if(!w)throw Error('Missing world');
txt('sceneTag',`WORLD ${current} · REAL ARCHIVED MUSE RESPONSE`);txt('sceneTitle',d.title);txt('sceneSubtitle',d.sub);txt('decision',w.action);el('decision').className='decision '+(w.action==='HOLD_FOR_REVIEW'?'hold':w.action==='ALLOW'?'allow':'request');
el('pair').replaceChildren(...w.photos.map(imageCard));el('pair').classList.toggle('single',w.photos.length===1);
el('claim').hidden=!w.untrusted_text;if(w.untrusted_text)txt('claim',`UNVERIFIED THIRD-PARTY CLAIM · ${w.untrusted_text}`);
txt('rationale',w.rationale);txt('model',w.model);txt('rawHash',w.raw_sha256);txt('matched',w.correct?'MATCHED SEALED EXPECTATION':'DIFFERENT FROM SEALED EXPECTATION');el('hashes').replaceChildren(...w.photos.map((p,i)=>make('code',null,`${i+1}: ${p.sha256}`)));
const policy={ALLOW:['NO VISIBLE CONFLICT','No contradiction hold in the narrow simulated policy. Never a payment authorization.'],REQUEST_MORE_EVIDENCE:['EVIDENCE REQUIRED','Illustrative checkout remains pending. No transaction executed.'],HOLD_FOR_REVIEW:['HOLD FOR HUMAN REVIEW','Illustrative checkout blocked pending manual inspection.']}[w.action];txt('policy',policy[0]);txt('policyDetail',policy[1]);txt('transitionText',d.shift);txt('transitionDetail',d.detail);txt('transitionArrow',d.step);
const seq=mode==='jury'?jury:order;const i=Math.max(0,seq.indexOf(current));txt('progressLabel',String(i+1).padStart(2,'0')+' / '+String(seq.length).padStart(2,'0')+' · '+d.title.toUpperCase());txt('modeDetail',mode==='jury'?'A → B → F':'ALL CASES');el('progressBar').style.width=`${(i+1)*100/seq.length}%`;el('prev').disabled=i===0;txt('next',i===seq.length-1?'Restart story ↺':mode==='jury'?'Reveal next proof →':'Next case →');
el('cases').replaceChildren(...order.map(id=>{const btn=make('button',null,id+' · '+desc[id].title);btn.setAttribute('aria-pressed',String(id===current));btn.onclick=()=>goto(id);return btn;}));}
function advance(){const seq=mode==='jury'?jury:order,i=seq.indexOf(current);current=seq[(i+1)%seq.length];render();}
el('next').onclick=()=>{stopAuto();advance();};el('prev').onclick=()=>{stopAuto();const seq=mode==='jury'?jury:order;current=seq[Math.max(0,seq.indexOf(current)-1)];render();};el('jury').onclick=()=>setMode('jury');el('explore').onclick=()=>setMode('explore');
el('record').onclick=()=>{recording=!recording;document.body.classList.toggle('recording',recording);el('record').setAttribute('aria-pressed',String(recording));};
el('ledgerToggle').onclick=()=>{const x=el('ledgerBody');x.hidden=!x.hidden;el('ledgerToggle').setAttribute('aria-expanded',String(!x.hidden));txt('ledgerToggle',x.hidden?'Show audit +':'Hide audit −');};
el('play').onclick=()=>{if(autoTimer!==null){stopAuto();return;}txt('play','Ⅱ Pause');autoTimer=setInterval(()=>{const seq=mode==='jury'?jury:order;if(current===seq[seq.length-1]){stopAuto();return;}advance();},8500);};
document.addEventListener('keydown',e=>{if(e.target instanceof HTMLElement && ['INPUT','TEXTAREA'].includes(e.target.tagName))return;if(e.key==='ArrowRight'){stopAuto();advance();}if(e.key==='ArrowLeft'){stopAuto();const seq=mode==='jury'?jury:order;current=seq[Math.max(0,seq.indexOf(current)-1)];render();}});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopAuto();});
fetch('/api/replay',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Replay API status '+r.status);return r.json();}).then(v=>{const ids=v.worlds.map(w=>w.id);if(ids.length!==6||order.some(x=>!ids.includes(x)))throw Error('Incomplete verified records');data=v;txt('score',`${v.summary.model_correct}/${v.summary.model_evaluated}`);txt('seal',v.seal_truth_sha256);txt('footerSeal','TRUTH SHA-256: '+v.seal_truth_sha256);render();}).catch(e=>{el('error').hidden=false;txt('error','REPLAY BLOCKED: '+String(e));});
