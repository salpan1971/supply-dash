#!/usr/bin/env python3
"""data/market.json 으로 검색엔진이 읽는 '오늘의 수급 요약' 글과 sitemap.xml 을 만든다.
index.html 안 <!--SEO-START--> ~ <!--SEO-END--> 사이만 바꾼다."""
import json, re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://cash.d-star27.com/'
d = json.loads((ROOT / 'data' / 'market.json').read_text(encoding='utf-8'))
e = html.escape


def amt(v):
    a = abs(round(v))
    if a >= 10000:
        jo, eok = divmod(a, 10000)
        return f'{jo}조 {eok:,}억' if eok else f'{jo}조'
    return f'{a:,}억'


def flow(name, v):
    return f'{name} {amt(v)} {"순매수" if v >= 0 else "순매도"}'


y, m, dd = d['date'].split('-')
date_ko = f'{int(y)}년 {int(m)}월 {int(dd)}일'
short = f'{int(m)}/{int(dd)}'
parts = []
for mk in ('코스피', '코스닥'):
    k = d.get('mk', {}).get(mk)
    if k and k.get('d1'):
        ind, fgn, ins = k['d1']
        parts.append(f'{mk} ' + ', '.join([flow('외국인', fgn), flow('기관', ins), flow('개인', ind)]))
P = d['periods']['1']
top = []
if P['f_buy']:
    top.append(f"외국인 순매수 1위 {P['f_buy'][0][1]}")
if P['i_buy']:
    top.append(f"기관 순매수 1위 {P['i_buy'][0][1]}")
oneline = f'{short} 수급 · ' + ' / '.join(parts) + (' · ' + ', '.join(top) if top else '') + f' ({SITE})'


def rank(title, rows, idx):
    lis = ''.join(f'<li>{e(r[1])} {amt(r[idx])}</li>' for r in rows[:5])
    return f'<h3>{title}</h3><ol>{lis}</ol>'


lu = [r[1] for r in d.get('limitup', {}).get('items', [])][:12]
block = f'''<!--SEO-START-->
  <section class="seo-summary" id="seo-summary" data-tab="market" aria-label="오늘의 수급 요약">
    <h2>{date_ko} 코스피·코스닥 수급 요약</h2>
    <p id="seo-oneline">{e(oneline)}</p>
    {rank('외국인 순매수 상위 5', P['f_buy'], 2)}{rank('외국인 순매도 상위 5', P['f_sell'], 2)}{rank('기관 순매수 상위 5', P['i_buy'], 3)}{rank('기관 순매도 상위 5', P['i_sell'], 3)}
    {('<h3>오늘 상한가 종목</h3><p>' + e(', '.join(lu)) + '</p>') if lu else ''}
    <p>코스피200과 코스닥 시가총액 상위 종목을 기준으로 집계한 참고 자료이며 거래소 전체 집계와 다릅니다. 투자 권유가 아닙니다.</p>
  </section>
  <!--SEO-END-->'''

p = ROOT / 'index.html'
s = p.read_text(encoding='utf-8')
if '<!--SEO-START-->' in s:
    s = re.sub(r'<!--SEO-START-->.*?<!--SEO-END-->', lambda _: block, s, flags=re.S)
else:
    anchor = '  <p class="note disc">'
    assert anchor in s, 'anchor not found'
    s = s.replace(anchor, '  ' + block + '\n\n' + anchor, 1)
p.write_text(s, encoding='utf-8')

(ROOT / 'sitemap.xml').write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE}</loc><lastmod>{d["date"]}</lastmod><changefreq>daily</changefreq></url>\n</urlset>\n',
    encoding='utf-8')
rb = ROOT / 'robots.txt'
t = rb.read_text(encoding='utf-8')
if 'Sitemap:' not in t:
    rb.write_text(t.rstrip('\n') + f'\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
print('ok', oneline)
