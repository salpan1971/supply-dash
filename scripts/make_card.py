#!/usr/bin/env python3
"""data/market.json 으로 블로그·오픈채팅·커뮤니티에 올릴 '오늘의 수급' 그림(promo/daily.png)과 글(promo/daily.txt)을 만든다.
그림 찍기는 GitHub Actions(.github/workflows/seo-summary.yml)가 playwright 로 합니다."""
import json, html, pathlib, sys

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


def cls(v):
    return 'pos' if v >= 0 else 'neg'


def sign(v):
    return '순매수' if v >= 0 else '순매도'


y, m, dd = d['date'].split('-')
date_ko = f'{int(y)}년 {int(m)}월 {int(dd)}일'
P = d['periods']['1']
rows = ''
text_lines = [f'[{int(m)}/{int(dd)} 코스피·코스닥 수급 요약]']
for mk in ('코스피', '코스닥'):
    k = d['mk'].get(mk)
    if not k or not k.get('d1'):
        continue
    ind, fgn, ins = k['d1']
    cells = ''.join(f'<div class="c"><span>{n}</span><b class="{cls(v)}">{amt(v)}</b><i>{sign(v)}</i></div>' for n, v in (('외국인', fgn), ('기관', ins), ('개인', ind)))
    rows += f'<div class="mk"><h3>{mk}</h3><div class="cs">{cells}</div></div>'
    text_lines.append(f'{mk}: 외국인 {amt(fgn)} {sign(fgn)}, 기관 {amt(ins)} {sign(ins)}, 개인 {amt(ind)} {sign(ind)}')


def top(title, lst, idx):
    li = ''.join(f'<li><span>{e(r[1])}</span><b>{amt(r[idx])}</b></li>' for r in lst[:3])
    return f'<div class="top"><h3>{title}</h3><ol>{li}</ol></div>'


for title, lst, idx in (('외국인 순매수', P['f_buy'], 2), ('기관 순매수', P['i_buy'], 3)):
    text_lines.append(f'{title} 상위: ' + ', '.join(f'{r[1]} {amt(r[idx])}' for r in lst[:3]))
text_lines += ['', f'자세히 보기: {SITE}', '※ 분석 종목 기준 참고 자료이며 투자 권유가 아닙니다. 투자 판단과 손익은 본인 책임입니다.']

page = f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap">
<style>
*{{box-sizing:border-box}}body{{margin:0;width:1080px;height:1350px;background:#0a0a0a;color:#fff;font-family:'Noto Sans KR',sans-serif;padding:64px;position:relative;overflow:hidden}}
.badge{{display:inline-block;background:#008254;border-radius:30px;padding:8px 22px;font-size:28px;font-weight:700}}
h1{{font-size:76px;margin:22px 0 4px;font-weight:900;letter-spacing:-2px}}.date{{font-size:32px;color:#98a09c;margin-bottom:34px}}
.mk{{margin-bottom:26px}}.mk h3{{font-size:34px;margin:0 0 10px;color:#ddfa88}}.cs{{display:flex;gap:16px}}.c{{flex:1;background:#151a18;border:1px solid #232a27;border-radius:14px;padding:16px 18px}}
.c span{{display:block;font-size:24px;color:#98a09c}}.c b{{display:block;font-size:38px;margin:4px 0}}.c i{{font-style:normal;font-size:22px;color:#98a09c}}.pos{{color:#ff6b6b}}.neg{{color:#6db0ff}}
.tops{{display:flex;gap:16px;margin-top:8px}}.top{{flex:1}}.top h3{{font-size:30px;margin:0 0 8px}}.top ol{{margin:0;padding:0;list-style:none}}
.top li{{display:flex;justify-content:space-between;font-size:28px;padding:10px 0;border-bottom:1px solid #232a27}}.top li b{{color:#ff6b6b;font-weight:700}}
.warn{{position:absolute;left:64px;right:64px;bottom:150px;background:#2b2108;border:2px solid #f0b429;border-left-width:10px;border-radius:12px;padding:18px 22px;font-size:26px;line-height:1.5;color:#ffe9a8}}
.warn b{{color:#ffd34d}}.url{{position:absolute;left:64px;bottom:64px;font-size:36px;font-weight:700;color:#ddfa88}}
img{{position:absolute;right:40px;bottom:0;height:140px}}
</style>
<span class="badge">코스피200 + 코스닥</span><h1>오늘의 수급</h1><div class="date">{date_ko} 기준</div>
{rows}<div class="tops">{top('외국인 순매수 TOP3', P['f_buy'], 2)}{top('기관 순매수 TOP3', P['i_buy'], 3)}</div>
<div class="warn"><b>⚠ 투자 유의</b> 분석 종목 기준 참고 자료이며 <b>매수·매도 추천이 아닙니다.</b> 투자 판단과 손익은 본인 책임입니다.</div>
<div class="url">cash.d-star27.com</div><img src="{(ROOT / 'img' / 'ggumbyeol-chart.png').as_uri()}">'''

out = ROOT / 'promo'
out.mkdir(exist_ok=True)
(out / 'daily.txt').write_text('\n'.join(text_lines) + '\n', encoding='utf-8')
(out / '_card.html').write_text(page, encoding='utf-8')

print('ok: promo/_card.html 과 promo/daily.txt 을 만들었습니다. 그림은 아래 명령으로 찍습니다.')
print('npx playwright screenshot --viewport-size=1080,1350 --wait-for-timeout=2500 promo/_card.html promo/daily.png')
