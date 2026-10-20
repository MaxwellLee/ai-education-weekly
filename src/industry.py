"""Issue-scoped industry reporting; entity and financial scope are explicit."""
import json
import render_helpers as H
E=H.esc

def render_industry(issue,root):
 path=root/'data/industry'/f'{issue["id"]}.json'
 if not path.exists():
  return '<section class="section" id="industry"><p class="section-kicker">INDUSTRY / GLOBAL FIELDNOTES</p><h2>行业动态</h2><p>本栏目自第002期增补建档；第001期未编写行业条目，不将新资料补写成历史新闻。</p><a href="#issue=002&amp;page=industry">查看第002期行业建档 →</a></section>'
 data=json.loads(path.read_text())
 def card(x):
  first=x.get('firstIssueId','002'); collected=x.get('firstCollected','2026-10-12')
  dates=H.detail('资料日期',x['sourceDate'])+H.detail('项目阶段',x['stage'])
  model=H.detail('谁付费 · 怎样收费',x['businessModel'])+H.detail('价格与成本',x['pricingCosts'])
  finance='<div class="industry-finance"><h4>财务观察 · 先看口径</h4>'+''.join('<p>'+E(f)+'</p>' for f in x['financials'])+'<p class="industry-boundary">'+E(x['financialBoundary'])+'</p></div>'
  cross=''.join('<p><a href="'+E(y['url'])+'">'+E(y['label'])+'</a></p>' for y in x.get('crosslinks',[]))
  return '<article class="industry-card" id="'+E(x['id'])+'" tabindex="-1"><p class="section-kicker">'+E(x['region'])+' / '+E(x['entity'])+'</p><h3>'+E(x['title'])+'</h3><p>'+E(x['summary'])+'</p>'+H.detail('服务对象',x['audience'])+H.detail('交付方式',x.get('delivery',''))+dates+H.detail('相对上期',x.get('changeSinceLastIssue',''))+H.detail('本轮核验范围',x.get('verificationNote',''))+'<details><summary>产品进展、商业模式与财务依据</summary>'+H.detail('功能与进展',x['progress'])+model+finance+H.detail('证据边界',x['limits'])+H.sources(x)+'</details><p class="industry-followup"><strong>继续跟踪 · 编辑判断：</strong>'+E(x['followup'])+'</p>'+cross+'<p class="criteria-note">首次收录：<a href="#issue='+E(first)+'&amp;page=industry">'+E(first)+'期 · '+E(collected)+'</a><br>条目核验：'+E(x.get('lastVerified',x.get('checkedAt',data['verifiedAt'])))+'</p></article>'
 body='<section class="section" id="industry"><div class="section-head"><div><p class="section-kicker">INDUSTRY / GLOBAL FIELDNOTES</p><h2>行业动态</h2></div><p class="section-note">看具体产品与项目，也看谁付费、钱从哪来。</p></div><p class="scope-note">第'+E(issue['id'])+'期行业观察 · 核验 '+E(data['verifiedAt'])+'。本期窗口为 '+E(issue['window']['start'])+' 至 '+E(issue['window']['end'])+'；建档日期不改变原文日期。</p><p>'+E(data['coverageNote'])+'</p><div class="note-box">财务读法：集团 ≠ 教育板块 ≠ 单一AI产品。营收、利润、融资与现金流不能混用；没有披露就保留空白，不把亏损直接称作现金消耗。</div>'
 body+='<nav class="industry-index" aria-label="行业机构索引">'+''.join('<a href="#issue='+E(issue['id'])+'&amp;page=industry&amp;focus='+E(x['id'])+'">'+E(x['shortName'])+'</a>' for x in data['items'])+'</nav>'
 if issue['id']=='003':
  body+='<aside class="note-box"><h3>10月20日补充 · 灵动与四个同类参照</h3><p>不是同质化排名：灵动侧重体验课到三级课程及机构开课；艾绘侧重绘本与学校创作；盛通侧重科技教育与软硬件；AIScratch侧重图形化编程、AI与硬件项目；创造栗侧重学校软硬件方案及师训。此为公开产品定位的编辑分析，不表示任何产品已实测或效果更好。</p><p>共同核验清单：签约主体、最终课程、教师独立开课能力、作品可编辑与导出、每班调用成本、未成年人数据处理、退款退出与机构持续使用。先比较完整交付闭环，再比较功能数量。</p></aside>'
 if data.get('courseComparison'):
  body+='<section class="industry-course-compare" aria-label="具体在售课程速览"><h3>具体在售课程 · 交付与收费速览</h3><p class="criteria-note">报价核验日期见各卡；未重新核验的报价保留历史日期。不同币种、课时、支持方式与套餐范围不能直接按总价排高低。所有报价均非利润，促销与可用班期可能变化。</p><div class="industry-grid">'
  for c in data['courseComparison']:
   body+='<article class="industry-compare-card"><h4><a href="#issue='+E(issue['id'])+'&amp;page=industry&amp;focus='+E(c['id'])+'">'+E(c['name'])+'</a></h4>'+H.detail('交付',c['delivery'])+H.detail('价格',c['price'])+H.detail('付费模式',c['model'])+H.detail('报价核验日期',c.get('verifiedAt',c.get('checkedAt','2026-10-12（历史核验，未更新）')))+'</article>'
  body+='</div></section>'
 for key,title,note in [('current','观察窗口内动态','至少有一项可核验来源或事件在本期窗口内；历史财务背景仍单独标日期。'),('baseline','历史背景与现行产品 · 持续跟踪','以下为历史资料或未标发布日期的现行课程、产品页面，不计作本周新发布。以后只在出现新证据时更新。')]:
  items=[x for x in data['items'] if x['freshness']==key]
  body+='<h3 class="shenzhen-group-title">'+title+' <span class="pill neutral">'+str(len(items))+' 个样本</span></h3><p class="criteria-note">'+note+'</p>'
  body+='<div class="industry-grid">'+''.join(card(x) for x in items)+'</div>' if items else '<p class="changes-baseline">本期未核验到窗口内可收录新动态；不把历史产品或财报包装成新消息。</p>'
 if data.get('pending'):
  body+='<aside class="industry-pending"><h3>补充核验事项 · 保留证据边界</h3>'+''.join('<p><strong>'+E(x['name'])+'</strong>：'+E(x['note'])+'</p>' for x in data['pending'])+'</aside>'
 return body+'<p class="criteria-note">公司官网、投资者关系资料和机构年报可确认其披露内容，不能单独证明教学成效。样本不构成投资建议或产品推荐。</p></section>'
