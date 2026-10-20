"""Issue-scoped Shenzhen coverage. Never recycle a prior issue as fresh news."""
import json
import render_helpers as H

def render_shenzhen(issue, root):
 path=root/'data/shenzhen'/f'{issue["id"]}.json'
 if not path.exists():
  return '<section class="section"><p class="section-kicker">SHENZHEN / LOCAL FIELDNOTES</p><h2>深圳专题</h2><p>本期尚无已核验的深圳专题条目；未沿用旧期动态。</p></section>'
 data=json.loads(path.read_text());E=H.esc
 def card(x):
  labels=' · '.join(x['districts'])+' / '+x['type']+' / '+x['stage']
  details=''.join(H.detail(label,x[key]) for label,key in [('学校与机构','organizations'),('人物与企业','peopleCompanies'),('发生了什么','summary'),('为什么值得关注 · 编辑判断','relevance'),('证据边界','limits')])
  follow=x.get('followUp',{})
  if follow.get('firstIssueId') and follow['firstIssueId']!=issue['id']:
   details+=H.detail('相对上期',follow.get('change',''))+'<p><a href="#issue='+E(follow['firstIssueId'])+'&amp;page=shenzhen&amp;focus='+E(follow['firstItemId'])+'">首次收录：第 '+E(follow['firstIssueId'])+' 期</a></p>'
  if x.get('priorIssue'):details+='<p><a href="#issue='+E(x['priorIssue'])+'&amp;page=shenzhen&amp;focus='+E(x['priorItemId'])+'">首次收录与旧基线：第 '+E(x['priorIssue'])+' 期</a></p>'
  return f'<article class="shenzhen-card" id="{E(x["id"])}" tabindex="-1"><p class="section-kicker">{E(labels)}</p><h3>{E(x["title"])}</h3><p class="criteria-note">原文发布日期：{E(x["publishedDate"])}<br>事件时间：{E(x["eventDate"])}<br>收录核验：{E(data["verifiedAt"])}</p>{details}{H.sources(x)}</article>'
 body=f'<section class="section" id="shenzhen"><div class="section-head"><div><p class="section-kicker">SHENZHEN / LOCAL FIELDNOTES</p><h2>深圳专题</h2></div><p class="section-note">区、校、项目、人物与企业的本地观察</p></div><p class="scope-note">专题增补核验：{E(data["verifiedAt"])}。沿用本期观察窗口 {E(issue["window"]["start"])} 至 {E(issue["window"]["end"])}；增补时间不改变原期刊日期。</p><p>{E(data["coverageNote"])}</p>'
 for key,title,note in [('current','观察窗口内动态','按原文发布日期进入本期；事件发生时间另外标注。'),('baseline','历史背景 · 项目追踪','以下资料早于观察窗口，仅为追踪项目与机构建立基线，不计作本周新闻。')]:
  items=[x for x in data['items'] if x['freshness']==key]
  body+=f'<h3 class="shenzhen-group-title">{title} <span class="pill neutral">{len(items)} 条</span></h3><p class="criteria-note">{note}</p>'
  body+='<div class="shenzhen-grid">'+''.join(card(x) for x in items)+'</div>' if items else '<p class="changes-baseline">本期未核验到可收录条目。</p>'
 return body+'<p class="criteria-note">覆盖情况是本期已核验样本，不代表全市完整清单。项目公布、签约、试点与正式运行分开描述；校方或企业自述不等于独立教育成效证据。下一期继续查新，没有新证据不重复包装旧闻。</p></section>'
