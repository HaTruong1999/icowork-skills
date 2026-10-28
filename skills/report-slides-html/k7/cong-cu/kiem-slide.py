#!/usr/bin/env python3
"""Kiểm tệp nội dung slide (JSON) theo quy tắc của 12 mẫu. Chỉ cần Python 3.

Dùng:  python3 kiem-slide.py <noi-dung.json> [--json]

Mã kiểm (giống hàm K7.kiem() trong trang HTML, thêm phần cấu trúc):
  C1 cấu trúc tệp (meta, slides)      C2 thiếu trường bắt buộc của mẫu
  M1 mẫu không có trong bộ            M2 chữ dài hơn giới hạn của ô
  M3 thiếu bản tiếng Anh              M4 số mục ngoài khoảng cho phép
  M5 slide có số liệu chưa ghi nguồn  M6 chưa có lời thoại
  M8 icon không có trong thư viện     M9 ảnh dùng chung không tồn tại
  M10 đánh dấu *nhấn mạnh* sai (lẻ dấu *, hoặc quá 1 cụm trong tiêu đề)
Mức: "loi" phải sửa trước khi dựng; "nhac" nên sửa (M3, M6).
M7 (chữ tràn khung khi hiển thị) chỉ kiểm được trong trình duyệt: mở HTML, chạy K7.kiem().
"""
import json, os, re, sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QT = json.load(open(os.path.join(GOC, 'khung', 'quy-tac-mau.json'), encoding='utf-8'))
_html = open(os.path.join(GOC, 'Tao-slide-VNPT-AI.html'), encoding='utf-8').read()
ANH = set(json.loads(re.search(r'<script type="application/json" id="assets">([\s\S]*?)</script>', _html).group(1)).keys())
MAU, GH_CHUNG, ICON = QT['mau'], QT['gioiHanChung'], QT['icon']

# trường bắt buộc theo mẫu
BAT_BUOC = {
    'bia': ['tieuDe', 'phu', 'dong'], 'muc-luc': ['tieuDe', 'muc'], 'chuong': ['so', 'tieuDe'],
    'so-lieu': ['dauMuc', 'tieuDe', 'so'], 'van-de': ['dauMuc', 'tieuDe', 'vanDe', 'giaiPhap'],
    'the': ['dauMuc', 'tieuDe', 'the'], 'bang': ['dauMuc', 'tieuDe', 'cot', 'hang'],
    'lop': ['dauMuc', 'tieuDe', 'lop'], 'anh': ['dauMuc', 'tieuDe', 'anh', 'vung', 'chuGiai'],
    'hinh-so': ['dauMuc', 'tieuDe', 'anh', 'so'], 'lo-trinh': ['dauMuc', 'tieuDe', 'buoc'],
    'cam-on': ['tieuDe', 'lienHe'],
}
CO_SO_LIEU = {'so-lieu', 'hinh-so', 'van-de'}
BO_QUA = re.compile(r'(^|\.)(src|mau|x|y|w|h|logo|icon|nen|noi|soMuc)(\.|$)')


def chu(v, lg):
    if v is None: return ''
    if isinstance(v, dict): return v.get(lg) or v.get('vi') or ''
    return str(v)


def gioi_han(mau, p):
    g = MAU.get(mau, MAU['the']).get('gh', {})
    sao = re.sub(r'\.\d+(?=\.|$)', '.*', p)
    if p in g: return g[p]
    if sao in g: return g[sao]
    k2 = re.sub(r'\.\d+$', '.*', p)
    if k2 in g: return g[k2]
    return GH_CHUNG.get(p, 0)


def la_chu(v):
    return isinstance(v, str) or (isinstance(v, dict) and ('vi' in v or 'en' in v) and not any(isinstance(x, (dict, list)) for x in v.values()))


def duyet(o, p=''):
    if la_chu(o):
        yield p, o; return
    if isinstance(o, dict):
        for k, v in o.items(): yield from duyet(v, f'{p}.{k}' if p else k)
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from duyet(v, f'{p}.{i}' if p else str(i))


def lay(o, p):
    for k in p.split('.'):
        if o is None: return None
        o = o[int(k)] if isinstance(o, list) and k.isdigit() and int(k) < len(o) else (o.get(k) if isinstance(o, dict) else None)
    return o


def kiem(deck):
    ds = []
    def them(muc, ma, vi_tri, y): ds.append({'muc': muc, 'ma': ma, 'vi_tri': vi_tri, 'y': y})
    if not isinstance(deck, dict) or not isinstance(deck.get('slides'), list) or not deck['slides']:
        them('loi', 'C1', 'tệp', 'Cần có "meta" và mảng "slides" không rỗng'); return ds
    if not isinstance(deck.get('meta'), dict) or not deck['meta'].get('ten'):
        them('loi', 'C1', 'meta', 'Cần "meta.ten" (tên bộ slide)')
    for i, s in enumerate(deck['slides'], 1):
        vt = f'slide {i}'
        m = s.get('mau')
        if m not in MAU:
            them('loi', 'M1', vt, f'Mẫu "{m}" không có trong bộ (chọn một trong: {", ".join(MAU)})'); continue
        for f in BAT_BUOC[m]:
            if lay(s, f) in (None, '', [], {}): them('loi', 'C2', vt, f'Mẫu "{m}" cần trường "{f}"')
        for p, v in duyet(s):
            if BO_QUA.search(p) or p == 'mau': continue
            for lg in (('vi', 'en') if isinstance(v, dict) else ('vi',)):
                t = chu(v, lg); n = len(t.replace('*', '')); g = gioi_han(m, p)
                if g and n > g: them('loi', 'M2', f'{vt} · {p} · {lg}', f'Dài {n}/{g} ký tự')
                if t.count('*') % 2: them('loi', 'M10', f'{vt} · {p} · {lg}', 'Dấu * bị lẻ: nhấn mạnh viết *cụm từ*')
            if isinstance(v, str) and v.strip() and p not in ('so', 'doiTac') and not re.fullmatch(r'[\d\s.,+%×x<>≥≤~–\-/:]+', v) and not p.endswith('.so') and not p.endswith('.ma') and not p.endswith('.gt'):
                them('nhac', 'M3', f'{vt} · {p}', 'Chưa có bản tiếng Anh (viết {"vi": "…", "en": "…"})')
            elif isinstance(v, dict) and v.get('vi') and not v.get('en'):
                them('nhac', 'M3', f'{vt} · {p}', 'Chưa có bản tiếng Anh')
        td = chu(s.get('tieuDe'), 'vi')
        if td.count('*') > 2: them('loi', 'M10', f'{vt} · tieuDe', 'Tiêu đề chỉ nhấn mạnh tối đa 1 cụm')
        for k, (lo, hi) in MAU[m].get('ds', {}).items():
            n = len(lay(s, k) or [])
            if n < lo or n > hi: them('loi', 'M4', f'{vt} · {k}', f'{n} mục, mẫu cần {lo}–{hi}')
        if m == 'anh' and len(s.get('vung') or []) != len(s.get('chuGiai') or []):
            them('loi', 'M4', f'{vt} · vung', 'Số vùng trên ảnh phải bằng số dòng chú giải')
        if m in CO_SO_LIEU and not chu(s.get('nguon'), 'vi'):
            them('loi', 'M5', vt, 'Slide có số liệu nhưng chưa ghi nguồn ("nguon")')
        if not chu(s.get('loiThoai'), 'vi'):
            them('nhac', 'M6', vt, 'Chưa có lời thoại ("loiThoai")')
        for f in ('the', 'so', 'buoc'):
            for k, t in enumerate(s.get(f) if isinstance(s.get(f), list) else []):
                if isinstance(t, dict) and t.get('icon') and t['icon'] not in ICON:
                    them('loi', 'M8', f'{vt} · {f}.{k}.icon', f'Icon "{t["icon"]}" không có trong thư viện')
        for src in re.findall(r'"asset:([^"]+)"', json.dumps(s, ensure_ascii=False)):
            if src not in ANH: them('loi', 'M9', vt, f'Ảnh "asset:{src}" không có trong ảnh dùng chung')
        if s.get('nen') and s['nen'] not in ANH: them('loi', 'M9', vt, f'Nền "{s["nen"]}" không có trong ảnh dùng chung')
    return ds


def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    deck = json.load(open(sys.argv[1], encoding='utf-8'))
    ds = kiem(deck)
    if '--json' in sys.argv:
        print(json.dumps(ds, ensure_ascii=False, indent=1))
    else:
        for x in ds: print(('LỖI  ' if x['muc'] == 'loi' else 'NHẮC ') + x['ma'] + ' · ' + x['vi_tri'] + ' · ' + x['y'])
        loi = sum(1 for x in ds if x['muc'] == 'loi'); nhac = len(ds) - loi
        print(f'\nKẾT QUẢ: {len(deck.get("slides", []))} slide · {loi} lỗi · {nhac} nhắc' + (' · ĐẠT' if not loi else ''))
    sys.exit(1 if any(x['muc'] == 'loi' for x in ds) else 0)


if __name__ == '__main__':
    main()
