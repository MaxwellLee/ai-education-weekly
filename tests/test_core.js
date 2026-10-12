const assert=require('node:assert/strict'),fs=require('fs'),path=require('path'),S=path.resolve(__dirname,'../src'),C=require(S+'/core.js');
const m=JSON.parse(fs.readFileSync(S+'/data/issues.json')),items=JSON.parse(fs.readFileSync(S+'/data/ideas.json')).items;
let s=C.createState(m);assert.equal(s.issueId,m.latestIssueId);assert.equal(C.matchingIdeas(items,s).length,items.length);
for(let i=0;i<m.issues.length;i++){const id=m.issues[i].id;s=C.selectIssue(s,id,m);assert.deepEqual(C.neighbors(m,id),{previous:m.issues[i-1]?.id||null,next:m.issues[i+1]?.id||null});s.filters.scope='issue';assert.equal(C.matchingIdeas(items,s).length,items.filter(x=>x.firstIssue===id).length);for(const page of C.pages){s.page=page;assert.equal(C.fromHash(C.hashFor(s),m).page,page)}}
assert.throws(()=>C.selectIssue(s,'invalid-issue',m));s=C.createState(m);s.issueId='001';s.page='shenzhen';s.view='library';s.filters.query='故事 & 音乐';assert.deepEqual(C.fromHash(C.hashFor(s),m),s);
s.filters=C.emptyFilters();s.filters.query='nothing-matches-8129172';assert.equal(C.matchingIdeas(items,s).length,0);
s=C.selectIssue(s,m.latestIssueId,m);assert.equal(s.view,'library');assert.equal(s.page,'shenzhen');assert.deepEqual(s.filters,C.emptyFilters());assert.equal(C.matchingIdeas(items,s).length,items.length);
assert.equal(C.fromHash('#issue=invalid&page=bad',m).issueId,m.latestIssueId);assert.equal(C.fromHash('#issue=invalid&page=bad',m).page,'preview');
console.log('PASS: all real issue navigation, cumulative and per-issue scopes, invalid routes, Unicode hash/filter round trips, historical return state.');
