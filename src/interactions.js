(()=>{
 'use strict';
 const C=window.WeeklyCore;
 const data=JSON.parse(document.getElementById('app-data').textContent),manifest=data.manifest,ideas=data.ideas;
 let state=C.fromHash(window.location.hash,manifest),renderedIssue=null,rememberedFilters=C.emptyFilters();
 const $=s=>document.querySelector(s),$$=s=>Array.from(document.querySelectorAll(s));
 const pageLabels={preview:'本期预览',education:'AI教育前沿',people:'公众人物言论',shenzhen:'深圳专题',updates:'更新须知'};
 function applyFilters(){
  const visible=new Set(C.matchingIdeas(ideas,state).map(x=>x.id));
  $$('.creative-card').forEach(card=>{card.hidden=!visible.has(card.dataset.ideaId);});
  $$('.facet').forEach(b=>b.setAttribute('aria-pressed',String(state.filters[b.dataset.dimension].includes(b.dataset.value))));
  $$('.scope-button').forEach(b=>b.setAttribute('aria-pressed',String(state.filters.scope===b.dataset.scope)));
  $('#idea-query').value=state.filters.query;$('#difficulty').value=state.filters.difficulty;
  const base=state.filters.scope==='issue'?ideas.filter(x=>x.firstIssue===state.issueId).length:ideas.length;
  $('#result-count').textContent=`显示 ${visible.size} / ${base} 个案例 · 累计总库 ${ideas.length} 个`;
  $('#empty-filter').hidden=visible.size>0;
  $('#scope-hint').textContent=state.filters.scope==='issue'?`第 ${state.issueId} 期首次收录；条目详情采用累计库的最新记录。`:`全部历年收录 · 截至 ${data.asOf}，共 ${ideas.length} 个。切换期刊不会缩减此库。`;
 }
 function render(scroll=false){
  const issue=manifest.issues.find(x=>x.id===state.issueId),isLibrary=state.view==='library';
  if(renderedIssue!==state.issueId){$('#issue-content').replaceChildren(document.getElementById('issue-template-'+state.issueId).content.cloneNode(true));renderedIssue=state.issueId;}
  $('#weekly-panel').hidden=isLibrary;$('#library-panel').hidden=!isLibrary;
  $('#weekly-navigation').hidden=isLibrary;$('#issue-toolbar').hidden=isLibrary;
  $$('[data-weekly-page]').forEach(page=>{page.hidden=page.dataset.weeklyPage!==state.page;});
  $$('.nav [data-page]').forEach(a=>{const on=a.dataset.page===state.page;a.classList.toggle('active',on);if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');a.href=C.hashFor({...state,view:'weekly',page:a.dataset.page,focus:''});});
  $('#issue-select').value=state.issueId;
  $('#issue-label').textContent=isLibrary?`全部创意 · 资料截至 ${data.asOf}`:`第 ${state.issueId} 期 · ${issue.date}`;
  $('#footer-issue').textContent=isLibrary?`累计库截至 ${data.asOf} · 返回第 ${state.issueId} 期`:`当前第 ${state.issueId} 期 · ${pageLabels[state.page]}`;
  document.title=isLibrary?'全部创意 · AI 教育与灵感周刊':`${pageLabels[state.page]} · 第 ${state.issueId} 期 · AI 教育与灵感周刊`;
  $('#return-weekly').textContent=`← 返回第 ${state.issueId} 期 · ${pageLabels[state.page]}`;
  $('#return-weekly').href=C.hashFor({...state,view:'weekly',focus:''});
  $('#open-library').href=C.hashFor({...state,view:'library',focus:''});
  $('#open-library').classList.toggle('current',isLibrary);
  if(isLibrary)$('#open-library').setAttribute('aria-current','page');else $('#open-library').removeAttribute('aria-current');
  const n=C.neighbors(manifest,state.issueId);
  $('#previous-issue').disabled=!n.previous;$('#next-issue').disabled=!n.next;$('#latest-issue').disabled=state.issueId===manifest.latestIssueId;
  $('#current-new-label').textContent=`第 ${state.issueId} 期新增`;
  applyFilters();
  $('#issue-status').textContent=isLibrary?`已打开独立累计创意库，共 ${ideas.length} 个案例。`:`第 ${state.issueId} 期，${pageLabels[state.page]}。`;
  if(scroll){
   const focus=state.focus?document.getElementById(state.focus):null;
   const destination=focus||document.getElementById(isLibrary?'library-panel':'page-'+state.page);
   destination?.scrollIntoView({block:'start'});
   if(focus){focus.setAttribute('tabindex','-1');focus.focus({preventScroll:true});}
  }
 }
 function navigate(next,replace=false,scroll=true){
  state=next;const hash=C.hashFor(state);
  if(window.location.hash!==hash)window.history[replace?'replaceState':'pushState'](null,'',hash);
  render(scroll);
 }
 function selectIssue(id){rememberedFilters=C.emptyFilters();navigate(C.selectIssue(state,id,manifest));}
 function changeFilters(){rememberedFilters=JSON.parse(JSON.stringify(state.filters));navigate(state,true,false);}
 $('#issue-select').addEventListener('change',e=>selectIssue(e.target.value));
 $('#previous-issue').addEventListener('click',()=>{const id=C.neighbors(manifest,state.issueId).previous;if(id)selectIssue(id);});
 $('#next-issue').addEventListener('click',()=>{const id=C.neighbors(manifest,state.issueId).next;if(id)selectIssue(id);});
 $('#latest-issue').addEventListener('click',()=>selectIssue(manifest.latestIssueId));
 document.addEventListener('click',event=>{
  const target=event.target.closest('button,a');if(!target||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||event.button>0)return;
  if(target.dataset.page){event.preventDefault();navigate({...state,view:'weekly',page:target.dataset.page,focus:target.dataset.focus||''});}
  if(target.dataset.openLibrary!==undefined){event.preventDefault();if(state.view==='library')return;navigate({...state,view:'library',focus:'',filters:JSON.parse(JSON.stringify(rememberedFilters))});}
  if(target.dataset.returnWeekly!==undefined){event.preventDefault();rememberedFilters=JSON.parse(JSON.stringify(state.filters));navigate({...state,view:'weekly',focus:''});}
  if(target.dataset.scrollTop!==undefined){event.preventDefault();document.getElementById('top').scrollIntoView({block:'start'});}
 });
 $$('.facet').forEach(b=>b.addEventListener('click',()=>{const key=b.dataset.dimension;state.filters[key]=C.toggleValue(state.filters[key],b.dataset.value);changeFilters();}));
 $$('.scope-button').forEach(b=>b.addEventListener('click',()=>{state.filters.scope=b.dataset.scope;changeFilters();}));
 $('#idea-query').addEventListener('input',e=>{state.filters.query=e.target.value;changeFilters();});
 $('#difficulty').addEventListener('change',e=>{state.filters.difficulty=e.target.value;changeFilters();});
 $('#reset-filters').addEventListener('click',()=>{state.filters=C.emptyFilters();changeFilters();});
 function restoreRoute(){state=C.fromHash(window.location.hash,manifest);rememberedFilters=JSON.parse(JSON.stringify(state.filters));render(true);}
 window.addEventListener('popstate',restoreRoute);window.addEventListener('hashchange',restoreRoute);
 navigate(state,true,false);
})();
