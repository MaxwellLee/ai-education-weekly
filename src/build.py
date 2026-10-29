#!/usr/bin/env python3
"""Build a static weekly with independent issue snapshots and one shared catalog."""
from pathlib import Path
import json,html,argparse
import render_helpers as H
from shenzhen import render_shenzhen
from industry import render_industry
ROOT=Path(__file__).resolve().parent
E=H.esc

def tags(values):return '<div class="tag-list">'+''.join(f'<span class="pill neutral">{E(v)}</span>' for v in dict.fromkeys(values) if v)+'</div>'
def section(kicker,title,body,note='',id=''):
 return f'<section class="section" id="{E(id)}"><div class="section-head"><div><p class="section-kicker">{E(kicker)}</p><h2>{E(title)}</h2></div><p class="section-note">{E(note)}</p></div>{body}</section>'
def news(item):
 out=H.news_card(item)
 extra=tags(item.get('educationLevels',[])+item.get('audienceTypes',[])+item.get('scopeTags',[]))
 if item.get('region'):extra+=H.detail('地区',item['region'])
 if item.get('ageRestriction'):extra+=H.detail('来源明示年龄条件',item['ageRestriction'])
 return out.replace('</h3>','</h3>'+extra,1)
def portrait(profile):
 im=profile['portrait'];p=im.get('path');name=profile['name']
 if not p:
  return '<a class="portrait-placeholder" href="'+E(im['sourcePage'])+'" target="_blank" rel="noopener noreferrer" aria-label="'+E(name)+'的官方人物页面"><span>官方人物页<br>查看肖像 ↗</span></a>'
 path=(H.ROOT/p).resolve()
 assert path.is_relative_to(H.ROOT.resolve()) and path.is_file(),('Invalid portrait path',p)
 import base64,mimetypes
 uri='data:'+(mimetypes.guess_type(path)[0] or 'image/jpeg')+';base64,'+base64.b64encode(path.read_bytes()).decode()
 return f'<a class="portrait-link" href="{E(im["sourcePage"])}" target="_blank" rel="noopener noreferrer" aria-label="{E(name)}的照片来源"><img class="portrait" src="{uri}" alt="{E(im["alt"])}" loading="lazy" decoding="async" width="88" height="104"></a>'

def person(item,profile,evidence_updates=()):
 item=dict(item)
 applied=[u for u in evidence_updates if u["itemId"]==item["id"]]
 for update in applied:item.update(update["after"])
 name=H.v(item,'name','person');date=H.v(item,'date','publishedAt','originalDate',default='日期未确认')
 ss=item.get('sources',[])
 if not ss and item.get('source_url'):ss=[{'label':'人物原始发言 / 官方发布','url':item['source_url']}]
 q=dict(item,sources=ss)
 platform=H.v(item,'platform',default='公开一手来源')
 contributions=''.join(f'<li><strong class="contribution-title">{E(c.get("title","代表成果"))}</strong><p>{E(c["text"])}</p>{H.sources({"sources":c.get("sources") or [c["source"]]})}<p class="contribution-boundary">{E(c.get("evidenceNote",""))}</p></li>' for c in profile['contributions'])
 bio=''.join(f'<span>{E(sentence)}</span>' for sentence in profile['bio'])
 profile_limits=''.join(f'<p class="profile-limit"><strong>资料边界：</strong>{E(note)}</p>' for note in profile.get('profileCaveats',[]))
 evidence_update_note=''.join(f'<p class="evidence-update-note">资料补核 {E(u["date"])}：任职与核验边界已用独立官方资料补充；原活动报道及原期快照保留。详见本卡人物资料来源。</p>' for u in applied)
 im=profile['portrait']
 if item.get('first_seen_issue')=='001':evidence_update_note+='<p><a href="#issue=001&amp;page=people&amp;focus=person-dan-fitzpatrick">首次收录：第001期人物原文</a></p>'
 if im.get('path'):
  photo_credit=f'<p class="portrait-credit">照片：{E(im["credit"])} · <a href="{E(im["sourcePage"])}" target="_blank" rel="noopener noreferrer">来源</a></p>'
 else:
  photo_credit=f'<p class="portrait-credit">肖像来源说明：{E(im.get("missingReason") or im.get("evidenceNote") or "尚未取得可可靠核对身份的官方公开肖像，保留文字占位。")}</p>'
 profile_body=f'''<div class="person-profile" data-profile-id="{E(profile['id'])}"><div class="profile-heading">{portrait(profile)}<div><p class="profile-kicker">人物背景</p><h3 class="person-name">{E(name)}</h3><p class="person-identity">{E(profile['identity'])}</p></div></div><p class="person-bio">{bio}</p><p class="follow-reason"><strong>持续关注 · 编辑判断</strong>{E(profile['followReason'])}</p><details class="profile-details"><summary>代表成果与资料来源</summary><ol class="contribution-list">{contributions}</ol><p class="profile-source-label">简介与身份依据</p>{H.sources({'sources':profile['profileSources']})}{profile_limits}{photo_credit}<p class="portrait-rights">{E(im['rightsStatus'])}</p></details><p class="profile-updated">人物资料更新：<time datetime="{E(profile['profileUpdatedAt'])}">{E(profile['profileUpdatedAt'])}</time></p></div>'''
 return f'''<article class="x-card person-card" id="{E(item['id'])}" tabindex="-1">{profile_body}<div class="person-update"><div class="card-top"><span class="pill">本期动态</span><span>原文日期：{E(date)}</span></div><p class="role">{E(H.v(item,'role'))} · {E(platform)}</p><h4>{E(H.v(item,'title','headline'))}</h4><p>{E(H.v(item,'summary','what'))}</p>{H.detail('值得留意',H.v(item,'why','significance','analysis'))}{H.detail('事实与观点',H.v(item,'fact_vs_opinion','factOpinionBoundary'))}{H.detail('边界与限制',H.v(item,'caveat','limits','limitation'))}{H.detail('事件日期',H.v(item,'event_date') if item.get('event_date') and item['event_date']!=date else '')}<p class="all-source-label">{E(H.v(item,'freshness','timeLabel'))} · {E(H.v(item,'verification','evidenceLevel'))}</p>{H.sources(q)}{evidence_update_note}</div></article>'''

def creative(item,i):
 body=H.creative_card(item,i)
 body=body.replace(f'id="{E(item["id"])}"',f'id="idea-{E(item["id"])}" data-idea-id="{E(item["id"])}" tabindex="-1"',1)
 old=f'<span class="pill neutral">{E(H.v(item,"category",default="灵感库"))}</span>'
 body=body.replace(old,'',1)
 body=body.replace('</h3>','</h3>'+tags(item['categories'])+tags(item['educationLevels']+item['audienceTypes']+item.get('scopeTags',[])),1)
 body=body.replace('<details>',f'<p class="uses"><strong>用途</strong> · {E("；".join(item["uses"]))}<br><strong>难度</strong> · {E(item.get("difficulty","未标注"))}</p><p class="catalog-meta">首次收录：第 {E(item["firstIssue"])} 期 · {E(item["firstSeen"])}<br>原始日期：{E(item["originalDate"])}<br>资料更新：{E(item["updatedAt"])} · 最新核验：{E(item.get("lastVerified","未标注"))}</p><details>',1)
 body=body.replace('<summary>复现思路与教育迁移</summary>','<summary>复现思路、教育迁移与使用边界</summary><p>'+E(item['stageBasis'])+'</p>',1)
 return body

def distribution(items):
 """One count per article: multiple stages and cross-stage labels go in one bucket."""
 columns=['学前教育','小学教育','初中教育','高中阶段教育','高等教育','跨学段','未限定']
 rows={}
 for item in items:
  topic=item.get('category') or '未分类'
  stages=list(dict.fromkeys(item.get('educationLevels',[])))
  bucket='跨学段' if '跨学段' in item.get('scopeTags',[]) or len(stages)>1 else stages[0] if stages else '未限定'
  rows.setdefault(topic,{c:[] for c in columns})[bucket].append(item['id'])
 return columns,rows

def distribution_table(issue):
 items=issue['education']['items'];columns,rows=distribution(items)
 peak=max(len(ids) for row in rows.values() for ids in row.values())
 head='<tr><th scope="col">主题 / 学段</th>'+''.join(f'<th scope="col">{E(c)}</th>' for c in columns)+'<th scope="col">合计</th></tr>'
 body=''
 for topic,row in rows.items():
  body+=f'<tr><th scope="row">{E(topic)}</th>'
  for col in columns:
   ids=row[col];n=len(ids);shade=round(n/peak*4) if n else 0
   content=(f'<a href="#issue={E(issue["id"])}&amp;page=education&amp;focus={E(ids[0])}" data-page="education" data-focus="{E(ids[0])}" aria-label="{E(topic)}，{E(col)}，{n} 条，查看教育前沿">{n}</a>' if n else '<span>0</span>')
   body+=f'<td class="heat heat-{shade}" data-topic="{E(topic)}" data-stage="{E(col)}" data-count="{n}">{content}</td>'
  body+=f'<td class="row-total">{sum(map(len,row.values()))}</td></tr>'
 totals=[sum(len(row[c]) for row in rows.values()) for c in columns]
 foot='<tr><th scope="row">本期条目</th>'+''.join(f'<td>{n}</td>' for n in totals)+f'<td>{len(items)}</td></tr>'
 table=f'<div class="matrix-scroll" role="region" aria-label="本期关注分布表，可横向滚动" tabindex="0"><table class="attention-table"><caption class="sr-only">第 {E(issue["id"])} 期教育收录：按原有主题标签与单一学段桶统计，共 {len(items)} 条。</caption><thead>{head}</thead><tbody>{body}</tbody><tfoot>{foot}</tfoot></table></div>'
 return section('THIS ISSUE / COVERAGE','本期关注分布表',table+f'<p class="matrix-key"><span class="heat heat-0">0</span><span class="heat heat-2">少</span><span class="heat heat-4">多</span> 色深仅表示本期收录数量；点击非零数字可查看对应教育条目。</p><p class="criteria-note">统计本期 {len(items)} 条有来源的教育内容，含明确标注的背景资料。主题沿用条目分类；每条只计一次。多学段标签或“跨学段”统一计入跨学段列，不向各学段重复展开；无明确学段计入未限定。职业教育、成人与继续教育、教育工作者仍在条目中独立标注。</p><p class="criteria-note">这是本期选题分布，不代表全网热度或教育成效。当前只展示本期数量，不生成趋势与涨幅；0 表示本期未收录。</p>','主题 × 学段 · 数量由本期内容自动计算','distribution')

def experiments_section(issue,editorial):
 items={x['id']:x for x in issue['education']['items']};cards=''
 for n,item in enumerate(editorial['experiments'],1):
  refs=''.join(f'<a href="#issue={E(issue["id"])}&amp;page=education&amp;focus={E(ref)}" data-page="education" data-focus="{E(ref)}">依据：{E(items[ref]["title"])}</a>' for ref in item['sourceIds'])
  cards+=f'''<article class="experiment-card" id="{E(item['id'])}"><span class="experiment-number">0{n}</span><h3>{E(item['title'])}</h3><p class="experiment-meta"><strong>适用对象</strong>{E(item['audience'])}<br><strong>预计投入</strong>{E(item['estimatedMinutes'])}</p><p>{E(item['steps'])}</p><p class="verification-goal"><strong>验证目标</strong>{E(item['verificationGoal'])}</p><p class="experiment-status">{E(item['status'])}</p><div class="sources">{refs}</div></article>'''
 return section('THIS WEEK / SMALL TESTS','本周值得试的 3 件事','<div class="experiment-grid">'+cards+'</div><p class="criteria-note">以下为基于本期来源的编辑建议；时间为估计，未实测，也不会自动执行。仅使用已有授权的工具及公开、自编或获准材料，不上传学生个人信息；试验记录不等于学习成效证据。</p>','从一个小问题开始，先定验证目标，再决定是否继续。','experiments')

def changes_section(issue,editorial):
 changes=editorial['changes']
 if not changes['items']:
  headline="首期建立基线" if changes["status"]=="baseline" else "本期未核验到新增变化"
  body=f'''<div class="changes-baseline" data-changes-status="{E(changes['status'])}"><p><strong>{E(headline)}</strong></p><p>{E(changes['note'].replace('首期建立基线。','',1))}</p><a href="#issue={E(changes['baselineIssue'])}&amp;page=education">首次收录基线：第 {E(changes['baselineIssue'])} 期 · {E(changes['baselineDate'])}</a></div>'''
 else:
  body='<div class="change-list">'
  for c in changes['items']:
   body+=f'''<article class="change-card"><h3>{E(c['title'])}</h3><p><strong>上次</strong> · {E(c['previous'])}</p><p><strong>现在</strong> · {E(c['current'])}</p><p class="criteria-note">原文日期：{E(c['sourceDate'])} · 变化类型：{E(c['changeType'])}</p>{H.sources({'sources':c['sources']})}<p><a href="#issue={E(c['firstIssue'])}&amp;page=education&amp;focus={E(c['firstItemId'])}">首次收录：第 {E(c['firstIssue'])} 期</a> · <a href="#issue={E(c['previousIssue'])}&amp;page=education&amp;focus={E(c['previousItemId'])}">对照：第 {E(c['previousIssue'])} 期</a></p></article>'''
  body+='</div>'
 return section('SINCE LAST ISSUE','相比上次变了什么',body,'只记录有原文依据的变化，区分来源日期与收录日期。','changes')

def editorial_record(issue,editorial):
 logs=''.join(f'<li><strong>{E(log["date"])} · {E(log["version"])} · {E(log["type"])}</strong><span>{E(log["summary"])}</span></li>' for log in editorial['revisionLog'])
 corrections=editorial.get('factCorrections',[])
 correction_html='<p class="no-corrections">尚无事实更正记录。上面的版本修订不等于事实纠错；如后续发现错误，将保留原内容、更正内容、日期、原因及依据。</p>' if not corrections else '<ol>'+''.join(f'<li><strong>{E(c["date"])} · {E(c["itemId"])}</strong><p>原记录：{E(c["before"])}<br>更正：{E(c["after"])}<br>原因：{E(c["reason"])}</p>{H.sources({"sources":c["sources"]})}</li>' for c in corrections)+'</ol>'
 updates_html=''.join(f'<li><strong>{E(u["date"])} · {E(u["kind"])} · {E(u.get("name",u["itemId"]))}</strong><p>{E(u["reason"])}</p><p>原记录：{E(u["before"]["role"])}<br>补核后：{E(u["after"]["role"])}</p>{H.sources({"sources":u["sources"]})}</li>' for u in editorial.get('evidenceUpdates',[]))
 if updates_html:updates_html='<h3>证据补充</h3><ul class="evidence-updates">'+updates_html+'</ul>'
 body=f'''<div class="method"><div><h3>证据怎样区分</h3><ul class="evidence-types"><li><strong>官方公告</strong>可确认公布了什么；可用性、价格、交割或学习效果仍要看具体条件。</li><li><strong>研究结果</strong>保留样本、设计与限制；自报感受、相关性和前后差异不自动构成因果证据。</li><li><strong>人物观点与教师自述</strong>说明是谁的观察，不把个人经验写成普遍结论。简介与动态分别标日期。</li><li><strong>编辑建议 · 未实测</strong>包括本期三个尝试和创意迁移，提供待验证方向，不宣称已复现或有效。</li></ul><p>原始日期、事件日期、首次收录、资料更新与核验时间各自保留；历史条目不包装成本周新发布。</p><p>人物肖像及原作效果图随对应介绍与评论展示，保留出处、署名和许可核验状态。除单独注明的许可外，公开转载许可未确认；来源公开和署名不表示作者授权或背书。</p></div><div><h3>版本修订日志</h3><p>采集截止：{E(issue.get("cutoff",issue["date"]))}。期刊快照：第 {E(issue["id"])} 期，{E(issue["date"])}。人物资料另标核验日期。</p><ol class="revision-log">{logs}</ol>{updates_html}<h3>事实更正</h3>{correction_html}</div></div>'''
 return section('EDITORIAL RECORD','本期来源与修订',body,'版本增补、版式调整与事实更正分别记录。','method')

def snapshot(issue,requirements,profiles,editorial,root=ROOT):
 education=issue['education'];people=issue.get('publicFigures',[])
 sums=''
 for i,s in enumerate(education.get('summaries',[])[:5],1):
  if isinstance(s,str):s={'title':f'本期观察 {i}','summary':s}
  target=s.get('target') or (education['items'][i-1]['id'] if len(education['items'])>=i else 'education')
  sums+=f'<article class="summary-card"><span class="summary-number">{i:02d}</span><h3>{E(H.v(s,"title","headline"))}</h3><p>{E(H.v(s,"summary","body","text"))}</p><a href="#issue={E(issue["id"])}&amp;page=education&amp;focus={E(target.lstrip("#"))}" data-page="education" data-focus="{E(target.lstrip("#"))}">阅读全文 →</a></article>'
 preview=f'<section class="summary-section" id="digest"><div class="section-head"><div><p class="section-kicker">THE SHORT READ / 第 {E(issue["id"])} 期</p><h2>本期重点速览</h2></div><p class="section-note">{E(issue["date"])} · {len(education["items"])} 条教育观察 · {len(people)} 位公众人物</p></div><div class="three-grid">{sums}</div><p class="scope-note">观察窗口 {E(issue["window"]["start"])} 至 {E(issue["window"]["end"])}。窗口外的资料标为背景；收录时间不等于原作发布时间。</p></section>'+distribution_table(issue)+experiments_section(issue,editorial)+changes_section(issue,editorial)
 frontier=render_frontier(issue)
 figures=section('PEOPLE & SIGNALS','公众人物言论','<div class="x-grid">'+''.join(person(x,profiles[x['id']],editorial.get('evidenceUpdates',[])) for x in people)+'</div>',f'{len(people)} 位人物的背景、代表成果与具体公开动态。人物资料与本期动态分别标注日期；代表成果可展开查看，不把简介计作动态，不作无证据热度排名。','people')
 notes=section('HOW THIS WEEKLY WORKS','更新须知',requirements,'内容范围、保存方式与每周更新标准','updates')
 notes+=editorial_record(issue,editorial)
 return ''.join(f'<div class="weekly-page" id="page-{key}" data-weekly-page="{key}"'+('' if key=='preview' else ' hidden')+f'>{body}</div>' for key,body in [('preview',preview),('education',frontier),('people',figures),('shenzhen',render_shenzhen(issue,root)),('industry',render_industry(issue,root)),('updates',notes)])

def render_frontier(issue):
 items=issue['education']['items']
 if issue['id']=='001':
  body='<div class="news-grid">'+''.join(news(x) for x in items)+'</div>'
 else:
  groups=[('技术与研究','模型能力、学习科学与教育技术；保留具体研究及适用范围。'),('教学实践','课程、教师发展与教学应用；活动日程不等于完成或成效。'),('政策与评价','治理、安全、评价与政策；区分正式规则、倡议和研究评估。')]
  body='<nav class="education-group-nav" aria-label="教育前沿分类">'+''.join('<a href="#issue='+E(issue['id'])+'&amp;page=education&amp;focus=education-group-'+str(i)+'">'+E(name)+'</a>' for i,(name,_) in enumerate(groups))+'</nav>'
  for i,(name,note) in enumerate(groups):
   subset=[x for x in items if x['frontierCategory']==name]
   body+='<section class="education-group" id="education-group-'+str(i)+'" tabindex="-1"><h3>'+E(name)+' <span class="pill neutral">'+str(len(subset))+' 条</span></h3><p class="criteria-note">'+E(note)+'</p><div class="news-grid">'+''.join(news(x) for x in subset)+'</div></section>'
 return section('EDUCATION FRONTIER','AI 教育前沿',body,'技术与研究、教学实践、政策与评价。企业产品的商业模式与财务另见行业动态。','education')

def facet(label,dimension,values):
 return f'<fieldset class="filter-set"><legend>{E(label)} · 可多选</legend><div class="filter-row">'+''.join(f'<button type="button" class="filter facet" data-dimension="{E(dimension)}" data-value="{E(x)}" aria-pressed="false">{E(x)}</button>' for x in values)+'</div></fieldset>'

def build(root=ROOT):
 H.ROOT=root
 manifest=json.loads((root/'data/issues.json').read_text());catalog=json.loads((root/'data/ideas.json').read_text());ideas=catalog['items']
 issues=[json.loads((root/'data'/x['file']).read_text()) for x in manifest['issues']]
 assert len({x['id'] for x in ideas})==len(ideas),'Duplicate creative IDs'
 assert len({x['id'] for x in issues})==len(issues),'Duplicate issue IDs'
 assert manifest['latestIssueId'] in [x['id'] for x in issues]
 for x in issues:
  assert all(i in {j['id'] for j in ideas} for i in x.get('newIdeaIds',[]))
 latest=next(x for x in issues if x['id']==manifest['latestIssueId'])
 requirements=(root/'requirements-fragment.html').read_text()
 profile_data=json.loads((root/'data/people.json').read_text());profiles={p['id']:p for p in profile_data['items']}
 editorials=json.loads((root/'data/editorial.json').read_text())['issues']
 snapshots={x['id']:snapshot(x,requirements,profiles,editorials[x['id']],root) for x in issues}
 app={'manifest':manifest,'asOf':catalog['asOf'],'ideas':[{k:x.get(k) for k in ['id','title','summary','tools','uses','categories','educationLevels','audienceTypes','scopeTags','firstIssue','difficultyGroup']} for x in ideas]}
 app_json=json.dumps(app,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
 issue_options=''.join(f'<option value="{E(x["id"])}"'+(' selected' if x['id']==latest['id'] else '')+f'>第 {E(x["id"])} 期 · {E(x["date"])} · {E(x["title"])}</option>' for x in reversed(manifest['issues']))
 navigation=''.join(f'<a href="#issue={E(latest["id"])}&amp;page={key}" data-page="{key}"'+(' class="active" aria-current="page"' if key=='preview' else '')+f'>{label}</a>' for key,label in [('preview','本期预览'),('education','AI教育前沿'),('shenzhen','深圳专题'),('industry','行业动态'),('people','公众人物言论'),('updates','更新须知')])
 library=f'''<section class="catalog-head" id="creative"><div class="library-return-row"><a class="button" id="return-weekly" href="#issue={E(latest['id'])}&amp;page=preview" data-return-weekly>← 返回第 {E(latest['id'])} 期周报</a><span class="library-badge">独立累计库</span></div><div class="section-head"><div><p class="section-kicker">THE SHARED IDEA CABINET</p><h2>全部创意</h2></div><p class="section-note">{len(ideas)} 个去重案例 · {sum(bool(x.get('image',{}).get('localPath')) for x in ideas)} 张原作效果图。先看效果，再拆玩法；复现与教学迁移均为编辑建议。</p></div><p class="issue-note">资料截至 {E(catalog['asOf'])}。所有期刊共用这一累计库；切换期刊不会缩减全库。离线文件不会自动获取未来更新。</p><div class="catalog-controls"><div class="scope-row" role="group" aria-label="收录范围"><button type="button" class="scope-button" data-scope="all" aria-pressed="true">全部累计</button><button type="button" class="scope-button" data-scope="issue" aria-pressed="false" id="current-new-label">第 {E(latest['id'])} 期新增</button></div><p class="criteria-note" id="scope-hint"></p>{facet('玩法分类','categories',catalog['categoryOrder'])}{facet('教育阶段','educationLevels',catalog['educationLevelOrder'])}{facet('类型与对象','audienceTypes',catalog['audienceTypeOrder'])}{facet('适用范围','scopeTags',catalog['scopeTagOrder'])}<div class="search-row"><label for="idea-query">搜索标题、工具或用途<input id="idea-query" type="search" placeholder="例如：故事、音乐、Docker" autocomplete="off"></label><label for="difficulty">难度<select id="difficulty"><option value="all">全部难度</option><option>入门</option><option>进阶</option><option>分层</option></select></label><button type="button" id="reset-filters" class="button">清除全部筛选</button></div><p class="criteria-note">同组多选满足任一标签即可，不同组同时满足。学段是教学迁移建议，不是产品年龄许可；学前案例指教师准备或陪同演示。职业教育、成人与继续教育、教育工作者独立标注。</p></div><p class="result-count" id="result-count" aria-live="polite">显示 {len(ideas)} / {len(ideas)} 个案例</p><div class="creative-grid">{''.join(creative(x,i) for i,x in enumerate(ideas,1))}</div><p class="empty-filter" id="empty-filter" hidden>暂时没有符合这些条件的案例。试试减少标签，或清除全部筛选；累计创意不会因此删除。</p></section>'''
 html_doc=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="六页式AI教育周刊与独立累计创意库，保留公开来源与证据边界。"><title>AI 教育与灵感周刊 · 第 {E(latest['id'])} 期</title><style>{(root/'styles.css').read_text()}</style></head><body><a class="skip" href="#main">跳到正文</a><header class="wrap masthead" id="top"><div class="eyebrow"><span>FIELDNOTES / AI & EDUCATION</span><a id="open-library" class="library-shortcut" href="#issue={E(latest['id'])}&amp;page=preview&amp;view=library" data-open-library>全部创意 <span aria-hidden="true">↗</span></a></div><div class="brand"><h1><span>AI 教育</span><span>与灵感周刊</span></h1><span class="mark" aria-hidden="true">f.</span></div><p class="meta"><span id="issue-label">第 {E(latest['id'])} 期 · {E(latest['date'])}</span><span>资料截至 {E(catalog["asOf"])}</span><span class="edition">公开发布版 · 第004期 · 10月29日补发</span></p><div class="issue-toolbar" id="issue-toolbar"><label class="issue-picker" for="issue-select">选择期刊<select id="issue-select">{issue_options}</select></label><div class="issue-buttons"><button id="previous-issue" class="button" disabled>← 上一期</button><button id="next-issue" class="button" disabled>下一期 →</button><button id="latest-issue" class="button" disabled>回到最新一期</button></div></div><p class="sr-only" id="issue-status" aria-live="polite"></p></header><div class="nav-shell" id="weekly-navigation"><nav class="wrap nav" aria-label="周报页面">{navigation}</nav></div><main class="wrap" id="main"><noscript><p class="nojs">请启用浏览器 JavaScript 以使用六个页面、切期与独立创意库。当前显示最新一期预览。</p></noscript><div id="weekly-panel"><div id="issue-content">{snapshots[latest['id']]}</div></div><div id="library-panel" hidden>{library}</div></main><footer class="wrap footer"><div class="footer-inner"><p>AI 教育与灵感周刊 / <span id="footer-issue">当前第 {E(latest['id'])} 期</span></p><p>资料与图片来源见各条目 · <a href="#top" data-scroll-top>回到顶部</a></p></div></footer>{''.join(f'<template id="issue-template-{E(k)}">{v}</template>' for k,v in snapshots.items())}<script type="application/json" id="app-data">{app_json}</script><script>{(root/'core.js').read_text()}</script><script>{(root/'interactions.js').read_text()}</script></body></html>'''
 (root/'index.html').write_text(html_doc)
 print(json.dumps({'issues':len(issues),'education':len(latest['education']['items']),'people':len(latest.get('publicFigures',[])),'creative':len(ideas),'creativeImages':sum(bool(x.get('image',{}).get('localPath')) for x in ideas),'portraitImages':sum(bool(x['portrait'].get('path')) for x in profiles.values()),'embeddedImageElementsIncludingTemplates':html_doc.count('<img '),'bytes':len(html_doc.encode())},ensure_ascii=False))
 return html_doc
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args();build(args.root)
