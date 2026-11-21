#!/usr/bin/env python3
"""Static HTML image-alt preflight. Detects omissions, not image semantic truth or SEO ranking."""
from html.parser import HTMLParser
import argparse,json,sys
class AuditParser(HTMLParser):
 def __init__(self): super().__init__(convert_charrefs=True);self.imgs=[];self.headings=[];self.langs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img': self.imgs.append(a)
  if tag in ('h1','h2','h3'): self.headings.append(tag)
  if tag=='html':self.langs.append(a.get('lang'))
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
def evaluate(html):
 p=AuditParser();p.feed(html)
 errors=[];warnings=[]
 for i,img in enumerate(p.imgs):
  if 'alt' not in img:errors.append(f'img[{i}] missing alt attribute: {img.get("src", "<no src>")}')
  elif img.get('alt') and img.get('aria-hidden')=='true':warnings.append(f'img[{i}] nonempty alt under aria-hidden: possible contradictory semantics')
  elif not img.get('alt') and img.get('role')=='img': warnings.append(f'img[{i}] empty alt but role=img: inspect intent')
 if p.headings.count('h1')>1:warnings.append('multiple H1 elements detected in standalone HTML; inspect host page hierarchy')
 if p.langs and not p.langs[0]:warnings.append('html has no lang; host template may supply lang in embedded mode')
 return {'status':'STRUCTURAL_ALT_PASS_NOT_SEMANTIC_VERIFICATION' if not errors else 'FAIL',
 'img_count':len(p.imgs),'nonempty_alt_count':sum(bool(a.get('alt')) for a in p.imgs),'empty_alt_count':sum('alt' in a and not a['alt'] for a in p.imgs),
 'errors':errors,'warnings':warnings,
 'limits':'Cannot verify alt factual quality, CSS-background semantics, hidden DOM, indexability, GEO or actual host canonical/hreflang.'}
def main():
 a=argparse.ArgumentParser();a.add_argument('html');o=a.parse_args()
 res=evaluate(open(o.html,encoding='utf-8').read());print(json.dumps(res,ensure_ascii=False,indent=2));return 0 if not res['errors'] else 2
if __name__=='__main__':sys.exit(main())
