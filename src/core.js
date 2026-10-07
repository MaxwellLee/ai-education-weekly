/* Pure state operations: five weekly pages and one independent cumulative library. */
(function(root){
 'use strict';
 const pages=['preview','education','people','shenzhen','updates'];
 const dimensions=['categories','educationLevels','audienceTypes','scopeTags'];
 const emptyFilters=()=>({scope:'all',categories:[],educationLevels:[],audienceTypes:[],scopeTags:[],difficulty:'all',query:''});
 function createState(manifest){return {issueId:manifest.latestIssueId,view:'weekly',page:'preview',focus:'',filters:emptyFilters()};}
 function selectIssue(state,id,manifest){if(!manifest.issues.some(x=>x.id===id))throw new Error('Unknown issue');return {...state,issueId:id,focus:'',filters:emptyFilters()};}
 function toggleValue(list,value){return list.includes(value)?list.filter(x=>x!==value):[...list,value];}
 function matchingIdeas(items,state){
  const f=state.filters,query=f.query.trim().toLocaleLowerCase();
  return items.filter(item=>{
   if(f.scope==='issue'&&item.firstIssue!==state.issueId)return false;
   for(const key of dimensions)if(f[key].length&&!f[key].some(v=>(item[key]||[]).includes(v)))return false;
   if(f.difficulty!=='all'&&item.difficultyGroup!==f.difficulty)return false;
   if(query&&!JSON.stringify([item.title,item.summary,item.tools,item.uses,...(item.categories||[])]).toLocaleLowerCase().includes(query))return false;
   return true;
  });
 }
 function neighbors(manifest,id){const index=manifest.issues.findIndex(x=>x.id===id);return {previous:manifest.issues[index-1]?.id||null,next:manifest.issues[index+1]?.id||null};}
 function hashFor(state){
  const p=new URLSearchParams({issue:state.issueId,page:state.page});
  if(state.view==='library'){
   p.set('view','library');
   const f=state.filters;if(f.scope==='issue')p.set('scope','issue');
   for(const key of dimensions)for(const v of f[key])p.append(key,v);
   if(f.difficulty!=='all')p.set('difficulty',f.difficulty);
   if(f.query)p.set('q',f.query);
  }else if(state.focus)p.set('focus',state.focus);
  return '#'+p.toString();
 }
 function fromHash(hash,manifest){
  const s=createState(manifest),p=new URLSearchParams(hash.replace(/^#/,''));
  if(manifest.issues.some(x=>x.id===p.get('issue')))s.issueId=p.get('issue');
  if(pages.includes(p.get('page')))s.page=p.get('page');
  if(p.get('view')==='library'){
   s.view='library';s.filters.scope=p.get('scope')==='issue'?'issue':'all';
   for(const key of dimensions)s.filters[key]=Array.from(new Set(p.getAll(key)));
   if(['入门','进阶','分层'].includes(p.get('difficulty')))s.filters.difficulty=p.get('difficulty');
   s.filters.query=p.get('q')||'';
  }else{s.focus=p.get('focus')||'';}
  return s;
 }
 const api={pages,emptyFilters,createState,selectIssue,toggleValue,matchingIdeas,neighbors,hashFor,fromHash};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.WeeklyCore=api;
})(typeof window==='undefined'?globalThis:window);
