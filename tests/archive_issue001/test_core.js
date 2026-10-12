const assert=require('node:assert/strict'),fs=require('fs'),path=require('path');
const S=(fs.existsSync(path.resolve(__dirname,'../data'))?path.resolve(__dirname,'..'):path.resolve(__dirname,'../src')),C=require(S+'/core.js');
const manifest=JSON.parse(fs.readFileSync(S+'/data/issues.json'));
const items=JSON.parse(fs.readFileSync(S+'/data/ideas.json')).items;
let s=C.createState(manifest);
assert.equal(s.issueId,'001');assert.equal(C.matchingIdeas(items,s).length,15);
assert.deepEqual(C.neighbors(manifest,'001'),{previous:null,next:null});
assert.throws(()=>C.selectIssue(s,'002',manifest));
// Two isolated fixture issues, never copied into the deliverable or production manifest.
const fixtureManifest={latestIssueId:'fixture-b',issues:[...manifest.issues,{id:'fixture-a'},{id:'fixture-b'}]};
const fixtureItems=[...items,{id:'fixture-new-a',title:'A',firstIssue:'fixture-a',categories:['Agent自动化'],educationLevels:['小学教育','高等教育'],audienceTypes:[],scopeTags:['跨学段'],difficultyGroup:'进阶'},{id:'fixture-new-b',title:'B',firstIssue:'fixture-b',categories:['图像设计'],educationLevels:[],audienceTypes:[],scopeTags:['未限定'],difficultyGroup:'入门'}];
const immutable=JSON.stringify(fixtureItems);
s=C.createState(fixtureManifest);assert.equal(C.matchingIdeas(fixtureItems,s).length,17);
s.filters.scope='issue';assert.deepEqual(C.matchingIdeas(fixtureItems,s).map(i=>i.id),['fixture-new-b']);
s=C.selectIssue(s,'001',fixtureManifest);assert.equal(s.filters.scope,'all');assert.equal(C.matchingIdeas(fixtureItems,s).length,17);
s.filters.scope='issue';assert.equal(C.matchingIdeas(fixtureItems,s).length,15);
s=C.selectIssue(s,'fixture-a',fixtureManifest);s.filters.scope='issue';assert.deepEqual(C.matchingIdeas(fixtureItems,s).map(i=>i.id),['fixture-new-a']);
s.filters.educationLevels=['小学教育','高等教育'];assert.equal(C.matchingIdeas(fixtureItems,s).length,1);
s.filters.categories=['故事视频'];assert.equal(C.matchingIdeas(fixtureItems,s).length,0);
s=C.selectIssue(s,'fixture-b',fixtureManifest);assert.deepEqual(s.filters,C.emptyFilters());assert.equal(C.matchingIdeas(fixtureItems,s).length,17);
s.filters.scopeTags=['未限定'];assert.deepEqual(C.matchingIdeas(fixtureItems,s).map(i=>i.id),['fixture-new-b']);
s.filters=C.emptyFilters();s.filters.query='this cannot match 8921837213';assert.equal(C.matchingIdeas(fixtureItems,s).length,0);
s.filters=C.emptyFilters();assert.equal(C.matchingIdeas(fixtureItems,s).length,17);
assert.deepEqual(C.neighbors(fixtureManifest,'fixture-a'),{previous:'001',next:'fixture-b'});assert.deepEqual(C.neighbors(fixtureManifest,'fixture-b'),{previous:'fixture-a',next:null});
assert.equal(JSON.stringify(fixtureItems),immutable);
for(const level of ['学前教育','小学教育','初中教育','高中阶段教育','高等教育']){s=C.createState(manifest);s.filters.educationLevels=[level];assert(C.matchingIdeas(items,s).length>0)}
console.log('PASS: real single issue, two unpublished fixture issues, shared catalog persistence, navigation, new-only scope, reset, multi-stage OR, cross-dimension AND, no-result, no data mutation.');
for(const page of C.pages){s=C.createState(manifest);s.page=page;assert.equal(C.fromHash(C.hashFor(s),manifest).page,page);}
s=C.createState(manifest);s.page='people';s.view='library';s.filters.educationLevels=['小学教育','高等教育'];s.filters.query='故事 & 音乐';s.filters.scope='issue';assert.deepEqual(C.fromHash(C.hashFor(s),manifest),s);
assert.equal(C.fromHash('#issue=nonexistent&page=bad',manifest).issueId,'001');assert.equal(C.fromHash('#issue=nonexistent&page=bad',manifest).page,'preview');
s=C.createState(fixtureManifest);s.page='people';s.view='library';s=C.selectIssue(s,'001',fixtureManifest);assert.equal(s.view,'library');assert.equal(s.page,'people');assert.equal(C.matchingIdeas(fixtureItems,s).length,17);
console.log('PASS: hash routes, direct links, malformed routes, Unicode filter round-trip and return page retention.');
