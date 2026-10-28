#!/usr/bin/env python3
"""Dựng bộ slide HTML từ tệp nội dung JSON (cho hệ thống chạy được Python).

Dùng:  python3 dung-slide.py <noi-dung.json> [-o ra.html] [--bo-qua-loi]
Chỉ cần Python 3. Không chạy được Python thì mở Tao-slide-VNPT-AI.html,
bấm ⋯ › Dán nội dung từ AI: kết quả giống hệt.

- Kiểm nội dung trước (kiem-slide.py). Còn lỗi thì dừng, trừ khi thêm --bo-qua-loi.
- Thay khối nội dung trong Tao-slide-VNPT-AI.html bằng tệp JSON, ghi ra MỘT tệp HTML tự chạy.
"""
import argparse, json, os, re, runpy, sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def an_toan(o):
    return json.dumps(o, ensure_ascii=False, indent=2).replace('</', '<\\/').replace('<!--', '<\\!--')


def main():
    ap = argparse.ArgumentParser(description='Dựng slide HTML từ nội dung JSON')
    ap.add_argument('noi_dung'); ap.add_argument('-o', '--ra'); ap.add_argument('--bo-qua-loi', action='store_true')
    a = ap.parse_args()
    deck = json.load(open(a.noi_dung, encoding='utf-8'))
    k = runpy.run_path(os.path.join(GOC, 'cong-cu', 'kiem-slide.py'), run_name='thu_vien')
    ds = k['kiem'](deck)
    for x in ds: print(('LỖI  ' if x['muc'] == 'loi' else 'NHẮC ') + x['ma'] + ' · ' + x['vi_tri'] + ' · ' + x['y'])
    loi = [x for x in ds if x['muc'] == 'loi']
    if loi and not a.bo_qua_loi:
        print(f'\nChưa dựng: còn {len(loi)} lỗi. Sửa nội dung rồi chạy lại.'); sys.exit(1)
    khung = open(os.path.join(GOC, 'Tao-slide-VNPT-AI.html'), encoding='utf-8').read()
    html = re.sub(r'(<script type="application/json" id="deck">)[\s\S]*?(</script>)', lambda m: m.group(1) + an_toan(deck) + m.group(2), khung, count=1)
    ten = (deck.get('meta') or {}).get('ten'); ten = ten.get('vi') if isinstance(ten, dict) else ten
    html = re.sub(r'<title>.*?</title>', '<title>' + str(ten or 'Slide VNPT AI').replace('<', '') + '</title>', html, count=1)
    ra = a.ra or os.path.splitext(a.noi_dung)[0] + '.html'
    open(ra, 'w', encoding='utf-8').write(html)
    print(f'\nĐã dựng: {ra} ({len(html) // 1024} KB, {len(deck["slides"])} slide)')


if __name__ == '__main__':
    main()
