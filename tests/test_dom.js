const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),path=require('path');
const ROOT=(fs.existsSync(path.resolve(__dirname,'../data'))?path.resolve(__dirname,'..'):path.resolve(__dirname,'../src')),raw=JSON.parse(fs.readFileSync(__dirname+'/dom.json'));
class El{
 constructor(o={}){Object.assign(this,o);this.dataset=o.dataset||{};this.listeners={};this.attrs=o.attrs||{};this.hidden='hidden' in this.attrs;this.value='';this.textContent='';this.classes=new Set();this.classList={toggle:(v,b)=>b?this.classes.add(v):this.classes.delete(v)};}
 setAttribute(k,v){this.attrs[k]=v}removeAttribute(k){delete this.attrs[k]}addEventListener(k,cb){this.listeners[k]=cb}scrollIntoView(){this.scrolled=true}focus(){this.focused=true}replaceChildren(c){this.content=c}closest(){return this}
 trigger(type,event={}){this.listeners[type]?.({target:this,preventDefault(){},...event})}
}
function setup(input=raw,initial=''){
 const lists={'.facet':input.facets.map(x=>new El(x)),'.scope-button':input.scope.map(x=>new El(x)),'.nav [data-page]':input.nav.map(x=>new El(x)),'[data-weekly-page]':input.pages.map(x=>new El(x)),'.creative-card':input.cards.map(x=>new El(x))};
 const ids={};for(const id of input.ids)ids[id]=new El({id});for(const list of Object.values(lists))for(const e of list)if(e.id)ids[e.id]=e;
 ids['app-data'].textContent=JSON.stringify(input.app);
 for(const issue of input.app.manifest.issues){ids['issue-template-'+issue.id]=new El();ids['issue-template-'+issue.id].content={cloneNode(){return {issue:issue.id}}};}
 const docListeners={},winListeners={};const document={querySelector(s){return ids[s.slice(1)]},querySelectorAll(s){return lists[s]||[]},getElementById(s){return ids[s]},addEventListener(k,cb){docListeners[k]=cb}};
 let position=0;const stack=[initial],win={location:{hash:initial},addEventListener(k,cb){winListeners[k]=cb;}};
 win.history={pushState(o,t,hash){stack.splice(position+1);stack.push(hash);position++;win.location.hash=hash},replaceState(o,t,hash){stack[position]=hash;win.location.hash=hash},back(){if(position){win.location.hash=stack[--position];winListeners.popstate();}},forward(){if(position<stack.length-1){win.location.hash=stack[++position];winListeners.popstate();}}};
 const context={window:win,document,Set,JSON,URLSearchParams};vm.runInNewContext(fs.readFileSync(ROOT+'/core.js','utf8'),context);vm.runInNewContext(fs.readFileSync(ROOT+'/interactions.js','utf8'),context);
 return {ids,lists,win,document,visible:()=>lists['.creative-card'].filter(x=>!x.hidden).length,click:(e)=>docListeners.click({target:e,preventDefault(){}}),hash(hash){win.location.hash=hash;winListeners.hashchange();}};
}
let h=setup(),{ids,lists,win}=h; const count=raw.cards.length,latest=raw.app.manifest.latestIssueId;
assert.equal(h.visible(),count);assert.equal(ids['weekly-panel'].hidden,false);assert.equal(ids['library-panel'].hidden,true);assert.equal(ids['latest-issue'].disabled,true);assert.equal(win.location.hash,'#issue='+latest+'&page=preview');
for(const a of lists['.nav [data-page]']){h.click(a);assert.equal(lists['[data-weekly-page]'].filter(x=>!x.hidden).length,1);assert.equal(lists['[data-weekly-page]'].find(x=>!x.hidden).dataset.weeklyPage,a.dataset.page);}
ids['previous-issue'].trigger('click');assert.equal(ids['issue-content'].content.issue,'001');assert.equal(ids['previous-issue'].disabled,true);assert.equal(ids['next-issue'].disabled,false);
h.click(lists['.nav [data-page]'].find(x=>x.dataset.page==='shenzhen'));h.click(new El({dataset:{openLibrary:''}}));assert.equal(ids['library-panel'].hidden,false);assert.equal(ids['weekly-navigation'].hidden,true);assert.equal(h.visible(),count);assert.match(ids['return-weekly'].textContent,/001.*深圳专题/);
lists['.scope-button'].find(x=>x.dataset.scope==='issue').trigger('click');assert.equal(h.visible(),raw.app.ideas.filter(x=>x.firstIssue==='001').length);
h.click(new El({dataset:{returnWeekly:''}}));assert.equal(ids['issue-content'].content.issue,'001');assert.equal(lists['[data-weekly-page]'].find(x=>!x.hidden).dataset.weeklyPage,'shenzhen');
win.history.back();assert.equal(ids['library-panel'].hidden,false);win.history.forward();assert.equal(ids['weekly-panel'].hidden,false);
ids['next-issue'].trigger('click');assert.equal(ids['issue-content'].content.issue,latest);assert.equal(h.visible(),count);ids['previous-issue'].trigger('click');ids['latest-issue'].trigger('click');assert.equal(ids['issue-content'].content.issue,latest);
h.click(new El({dataset:{openLibrary:''}}));lists['.scope-button'].find(x=>x.dataset.scope==='issue').trigger('click');assert.equal(h.visible(),raw.app.ideas.filter(x=>x.firstIssue===latest).length);
ids['idea-query'].value='nothing-matches-71918833';ids['idea-query'].trigger('input');assert.equal(h.visible(),0);assert.equal(ids['empty-filter'].hidden,false);ids['reset-filters'].trigger('click');assert.equal(h.visible(),count);
h.hash('#issue=001&page=updates&view=library');assert.match(ids['return-weekly'].textContent,/001.*更新须知/);h.click(new El({dataset:{returnWeekly:''}}));assert.equal(ids['issue-content'].content.issue,'001');assert.equal(lists['[data-weekly-page]'].find(x=>!x.hidden).dataset.weeklyPage,'updates');
console.log('PASS: actual production controller in synthetic DOM; real 001/002 snapshots, six tabs, previous/next/latest, independent cumulative library, new scopes, empty/reset, history, historical issue/page return. Real-browser layout is separate.');
