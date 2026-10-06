#!/usr/bin/env python3
"""Shared escaped rendering helpers for the weekly and creative catalog."""
from pathlib import Path
import base64,json,html,mimetypes
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parent
esc=lambda value:html.escape(str(value or ''),quote=True)
def text(value):
 if isinstance(value,list): return '；'.join(map(str,value))
 if isinstance(value,dict): return '；'.join(f'{k}：{v}' for k,v in value.items())
 return str(value or '')
def v(obj,*keys,default=''):
 for k in keys:
  if obj.get(k) is not None and obj.get(k)!='':return text(obj[k])
 return default

def sources(item):
 ss=item.get('sources',[])
 if not ss and item.get('url'):ss=[{'label':'查看原作 / 原文','url':item['url']}]
 parts=[]
 for i,s in enumerate(ss):
  if isinstance(s,str):s={'url':s,'label':f'来源 {i+1}'}
  url=s.get('url','')
  if url.startswith(('https://','http://')):parts.append(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(s.get("label",s.get("title",f"来源 {i+1}")))}</a>')
 return '<div class="sources">'+''.join(parts)+'</div>'

def factline(item):
 date=v(item,'date','originalDate','publishedAt',default='未确认')
 first=v(item,'firstSeen',default='2026-10-06')
 updated=v(item,'lastVerified','verifiedAt',default='2026-10-06')
 original_updated=v(item,'originalUpdated','updated')
 extra=f' · 原文更新：{esc(original_updated)}' if original_updated and original_updated!=date else ''
 return f'<div class="facts">原文日期：{esc(date)}{extra}<br>首次收录：{esc(first)} · 最新核验：{esc(updated)}</div>'

def detail(label,content,css=''):
 return f'<p class="detail-line {css}"><strong>{esc(label)}：</strong>{esc(text(content))}</p>' if content else ''

def news_card(item):
 return f'''<article class="news-card" id="{esc(item.get('id',''))}"><div class="card-top"><span class="pill">{esc(v(item,'category',default='教育动态'))}</span><span>{esc(v(item,'date',default='日期待核验'))}</span></div><h3>{esc(v(item,'title'))}</h3><p class="lead">{esc(v(item,'summary','what'))}</p><p class="all-source-label">{esc(v(item,'freshness'))} · {esc(v(item,'evidenceLevel'))}</p>{detail('为什么值得看',v(item,'why','significance'))}{detail('边界与限制',v(item,'limits','limitations'))}{detail('可以怎么用',v(item,'application','education'),'application')}{sources(item)}{factline(item)}</article>'''

def x_card(item):
 return f'''<article class="x-card"><div class="card-top"><span class="pill neutral">{esc(v(item,'person','name','category',default='人物动态'))}</span><span>{esc(v(item,'date',default='日期待核验'))}</span></div><h3>{esc(v(item,'title'))}</h3><p>{esc(v(item,'summary','what'))}</p>{detail('观察',v(item,'why','application'))}{detail('一手交叉核对',v(item,'primaryFactCheck'))}<p class="metrics">{esc(v(item,'metrics','heat',default='未取得可复核的浏览量、点赞和转发指标；不据此判断热度。'))}</p>{sources(item)}{factline(item)}</article>'''

def image_markup(item):
 im=item.get('image') or {}
 if isinstance(im,str):im={'url':im}
 p=im.get('localPath') or im.get('path')
 uri=''
 if p:
  path=Path(p)
  if not path.is_absolute():path=ROOT/path
  if path.exists():
   mime=mimetypes.guess_type(path)[0] or 'image/jpeg'
   uri='data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
 if not uri and (im.get('url') or '').startswith('data:'):uri=im['url']
 if not uri:
  return '<div class="evidence-gap"><strong>查看原作效果</strong><span>'+esc(im.get('evidenceNote','本版不内嵌此图，请打开原作页面查看。'))+'</span><a href="'+esc(im.get('sourcePage',''))+'" target="_blank" rel="noopener noreferrer">打开作品来源 ↗</a></div>'
 alt=im.get('alt') or item.get('title','案例效果图')
 caption=im.get('credit') or im.get('evidenceNote') or '原作公开演示图；图像版权归原作者或原平台。'
 if '动图' in im.get('evidenceNote','') or 'GIF' in im.get('evidenceNote',''):caption+=' · 原作动图的静态帧'
 u=im.get('sourceUrl') or im.get('source_url') or im.get('sourcePage') or im.get('url') or ''
 img=f'<img src="{uri}" alt="{esc(alt)}" loading="lazy" decoding="async" width="960" height="600">'
 if u.startswith(('https://','http://')):img=f'<a href="{esc(u)}" target="_blank" rel="noopener noreferrer" aria-label="打开{esc(item.get("title",""))}图片来源">{img}</a>'
 license_note = (' · <a href="'+esc(im['licenseUrl'])+'" target="_blank" rel="noopener noreferrer">'+esc(im['licenseName'])+'</a>') if im.get('licenseUrl') else ''
 change_note = (' · '+esc(im['changes'])) if im.get('changes') else ''
 rights_note = (' · '+esc(im['rightsStatus'])) if im.get('rightsStatus') and not im.get('licenseUrl') else ''
 return f'<figure class="figure">{img}<figcaption>{esc(caption)}{license_note}{change_note}{rights_note}</figcaption></figure>'

def creative_card(item,i):
 tags=item.get('tags',[])
 if isinstance(tags,str):tags=[tags]
 tags=list(dict.fromkeys([v(item,'category',default='灵感')]+tags))
 return f'''<article class="creative-card" id="{esc(item.get('id','idea-'+str(i)))}" data-tags="{esc('|'.join(tags))}">{image_markup(item)}<div class="creative-body"><span class="creative-number">{i:02d}</span><span class="pill neutral">{esc(v(item,'category',default='灵感库'))}</span><h3>{esc(v(item,'title'))}</h3><p class="freshness">{esc(v(item,'freshness',default='灵感库收录'))} · {esc(v(item,'date',default='原始日期未确认'))}</p><p>{esc(v(item,'summary','play'))}</p>{detail('玩法',v(item,'play') if v(item,'play')!=v(item,'summary') else '')}<p class="tools"><strong>所需工具</strong> · {esc(v(item,'tools',default='见原作链接'))}</p><details><summary>复现思路与教育迁移</summary><p><strong>复现建议 · 编辑构想</strong>{esc(v(item,'reproduce','reproduction',default='先查看原作与使用条件，再用自己的素材尝试同类创作。'))}</p><p><strong>教育迁移 · 编辑构想</strong>{esc(v(item,'education','application',default='先小范围试用，再评估是否适合学习目标。'))}</p>{detail('使用边界',v(item,'limits','limitations'))}{detail('日期说明',v(item,'dateNote'))}{factline(item)}</details>{sources(item)}</div></article>'''
