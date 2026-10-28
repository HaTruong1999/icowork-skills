#!/usr/bin/env python3
"""report.json -> HTML (khổ slide 16:9) theo assets/template.html.

Thường được gọi qua `report.py build`. Hàm chính:
  validate(report)            -> danh sách lỗi (chuỗi tiếng Việt, có đường dẫn tới chỗ sai)
  render(report, skill_dir)   -> chuỗi HTML hoàn chỉnh (font nhúng base64, mở offline được)

Định dạng chữ trong mọi trường văn bản: **đậm**, xuống dòng bằng \\n. Không viết thẻ HTML.
"""
import base64
import html
import json
import re
from pathlib import Path

# ---------------------------------------------------------------- lược đồ

TONES = {
    "stat": {"default", "primary", "warn", "dark", "accent", "highlight"},
    "panel": {"light", "warn", "danger", "dark"},
    "category": {"primary", "dark"},
    "text": {"accent", "highlight", "default"},
}
BADGE_TONES = {"done", "todo", "eval", "doing", "neutral"}

# loại khối -> (trường bắt buộc, trường tùy chọn)
BLOCKS = {
    "stat": ({"value", "label"}, {"tone", "grow"}),
    "split": ({"parts"}, {"title", "note", "grow"}),
    "numlist": ({"items"}, {"title", "grow"}),
    "category": ({"title", "rows"}, {"sub", "total", "tone", "grow"}),
    "progress": ({"value", "percent"}, {"label", "caption", "grow"}),
    "panel": ({"title"}, {"bullets", "text", "tone", "grow"}),
    "status_table": ({"rows"}, {"title", "grow"}),
    "status_list": ({"items"}, {"title", "grow"}),
    "steps": ({"items"}, {"title", "grow"}),
    "text": ({"text"}, {"title", "tone", "grow"}),
    "table": ({"columns", "rows"}, {"title", "num_cols", "grow"}),
    "bars": ({"items"}, {"title", "label_width", "grow"}),
    "stack": ({"blocks"}, {"grow"}),
}
SLIDE_FIELDS = {
    "cover": ({"title"}, {"type", "kicker", "subtitle", "date", "agenda"}),
    "section": ({"title"}, {"type", "kicker", "subtitle"}),
    "content": ({"title", "rows"}, {"type", "kicker", "lead", "next", "note", "dark"}),
}
THEME_KEYS = {"navy", "navy-2", "primary", "sky", "sky-soft", "warn", "highlight", "bg", "card",
              "line", "text", "muted", "next-bg", "font"}


TONE_FIX = {  # tone sai -> tone gần nghĩa nhất của loại khối đó
    "panel": {"primary": "light", "accent": "light", "highlight": "warn", "default": "light", "info": "light",
              "success": "light", "error": "danger", "red": "danger", "orange": "warn", "blue": "dark", "navy": "dark"},
    "stat": {"light": "default", "danger": "warn", "dark": "dark", "info": "primary", "blue": "primary",
             "orange": "highlight", "success": "default"},
    "text": {"warn": "highlight", "primary": "accent", "light": "default", "dark": "default", "danger": "highlight"},
    "category": {"light": "primary", "warn": "primary", "accent": "primary", "default": "primary", "navy": "dark"},
}


def autofix(rep):
    """Tự sửa lỗi cấu trúc vô hại (tone sai, số cols lệch số khối). Trả về danh sách mô tả đã sửa."""
    fixed = []

    def blk(b, where):
        if not isinstance(b, dict):
            return
        t, tone = b.get("type"), b.get("tone")
        if t in TONES and tone and tone not in TONES[t]:
            new = TONE_FIX.get(t, {}).get(tone) or sorted(TONES[t])[0]
            b["tone"] = new
            fixed.append(f"{where} ({t}): tone '{tone}' → '{new}'")
        for k, sub in enumerate(b.get("blocks") or [] if t == "stack" else [], 1):
            blk(sub, f"{where} > khối {k}")

    for i, s in enumerate(rep.get("slides") or [], 1):
        if not isinstance(s, dict):
            continue
        for r, row in enumerate(s.get("rows") or [], 1):
            if not isinstance(row, dict) or not isinstance(row.get("blocks"), list):
                continue
            n = len(row["blocks"])
            if row.get("cols") is not None and (not isinstance(row["cols"], list) or len(row["cols"]) != n):
                fixed.append(f"slide {i} > row {r}: cols {row['cols']} → {[1] * n} (bằng số khối)")
                row["cols"] = [1] * n
            for k, b in enumerate(row["blocks"], 1):
                blk(b, f"slide {i} > row {r} > khối {k}")
    return fixed


def find_unbalanced_bold(obj, path="report"):
    """Tìm chuỗi có số lần '**' lẻ (mở đậm nhưng quên đóng, hoặc ngược lại)."""
    bad = []
    if isinstance(obj, str):
        if obj.count("**") % 2:
            bad.append((path, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            bad += find_unbalanced_bold(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            bad += find_unbalanced_bold(v, f"{path}[{i}]")
    return bad


def validate(rep):
    err = []
    if not isinstance(rep, dict):
        return ["Gốc của report.json phải là một object { ... }"]
    meta = rep.get("meta")
    if not isinstance(meta, dict) or not meta.get("title"):
        err.append("Thiếu meta.title (tên báo cáo).")
    slides = rep.get("slides")
    if not isinstance(slides, list) or not slides:
        return err + ["Thiếu danh sách slides (mảng không rỗng)."]
    leftovers = sorted({m for m in re.findall(r"«[^»]{0,40}»?", json.dumps(rep, ensure_ascii=False))})
    if leftovers:
        err.append(f"Còn {len(leftovers)} chữ mẫu «…» chưa thay bằng nội dung thật, vd: {', '.join(leftovers[:5])}")
    bold_bad = find_unbalanced_bold(rep)
    if bold_bad:
        samples = "; ".join(f"{p}: \"{t[:60]}\"" for p, t in bold_bad[:5])
        err.append(f"Có {len(bold_bad)} chỗ dùng ** không khớp cặp (thiếu ** đóng hoặc thừa ** mở): {samples}")
    for k in (rep.get("theme") or {}):
        if k not in THEME_KEYS:
            err.append(f"theme.{k}: không có biến này. Dùng: {', '.join(sorted(THEME_KEYS))}")
    for i, s in enumerate(slides, 1):
        where = f"slide {i}"
        if not isinstance(s, dict):
            err.append(f"{where}: phải là object.")
            continue
        typ = s.get("type", "content")
        if typ not in SLIDE_FIELDS:
            err.append(f"{where}: type '{typ}' không hợp lệ (cover | section | content).")
            continue
        req, opt = SLIDE_FIELDS[typ]
        for f in req - set(s):
            err.append(f"{where}: thiếu trường '{f}'.")
        for f in set(s) - req - opt:
            err.append(f"{where}: trường lạ '{f}' (slide {typ} chỉ có: {', '.join(sorted(req | opt))}).")
        if typ == "content":
            note = s.get("note")
            if note is not None and not (isinstance(note, str) or (isinstance(note, dict) and "text" in note)):
                err.append(f"{where}.note: là chuỗi hoặc {{\"label\": \"Ghi chú\", \"text\": \"...\"}}.")
            rows = s.get("rows")
            if not isinstance(rows, list):
                continue
            for r, row in enumerate(rows, 1):
                w = f"{where} > row {r}"
                if not isinstance(row, dict) or not isinstance(row.get("blocks"), list) or not row["blocks"]:
                    err.append(f"{w}: phải là {{\"cols\": [1,1], \"blocks\": [...]}} với blocks không rỗng.")
                    continue
                cols = row.get("cols") or [1] * len(row["blocks"])
                if len(cols) != len(row["blocks"]):
                    err.append(f"{w}: cols có {len(cols)} số nhưng có {len(row['blocks'])} khối – phải bằng nhau.")
                for f in set(row) - {"cols", "blocks", "grow"}:
                    err.append(f"{w}: trường lạ '{f}' (row chỉ có cols, blocks, grow).")
                for b, blk in enumerate(row["blocks"], 1):
                    check_block(blk, f"{w} > khối {b}", err)
        if typ == "cover":
            for a, it in enumerate(s.get("agenda") or [], 1):
                if not isinstance(it, dict) or "text" not in it:
                    err.append(f"{where} > agenda {a}: cần {{\"num\": \"01\", \"text\": \"...\"}}.")
    if not err:
        err += check_sections(slides)
    return err


def check_sections(slides):
    """Kicker dạng '0i / 0N · TÊN PHẦN': N thống nhất, đủ phần 1..N theo thứ tự; mục lục bìa khớp số phần."""
    err, secs, total = [], [], set()
    for i, s in enumerate(slides, 1):
        m = re.match(r"\s*(\d{1,2})\s*/\s*(\d{1,2})\s*·?\s*([^·]*)", str(s.get("kicker") or ""))
        if m:
            k, n = int(m.group(1)), int(m.group(2))
            total.add(n)
            if not secs or secs[-1][0] != k:
                secs.append((k, i, m.group(3).strip()))
    if not secs:
        return err
    if len(total) > 1:
        err.append(f"Kicker đánh số phần không thống nhất: có cả {', '.join(f'/ {n:02d}' for n in sorted(total))}.")
        return err
    n = total.pop()
    order = [k for k, _, _ in secs]
    if order == list(range(1, len(order) + 1)) and len(order) < n:
        err.append(f"Kicker ghi “/ {n:02d}” nhưng báo cáo chỉ có {len(order)} phần (01 → {len(order):02d}). "
                   f"Đổi mẫu số ở MỌI kicker thành “/ {len(order):02d}”. Slide tổng hợp nền tối KHÔNG đánh số "
                   f"(kicker: THÔNG ĐIỆP TỔNG HỢP TRÌNH LÃNH ĐẠO).")
    elif order != list(range(1, n + 1)):
        err.append(f"Kicker đánh số phần phải đi lần lượt 01 → {n:02d}, mỗi phần liền nhau; hiện là: "
                   + ", ".join(f"{k:02d} (slide {i})" for k, i, _ in secs) + ".")
    cover = next((s for s in slides if s.get("type") == "cover"), None)
    agenda = (cover or {}).get("agenda") or []
    has_summary = any(s.get("dark") and not re.match(r"\s*\d{1,2}\s*/", str(s.get("kicker") or "")) for s in slides)
    if agenda and len(agenda) not in (n, n + (1 if has_summary else 0)):
        want = [f"{k:02d} {name.title() if name.isupper() else name}" for k, _, name in secs]
        if has_summary:
            want.append(f"{n + 1:02d} <slide tổng hợp, vd Thông điệp, kiến nghị>")
        err.append(f"Mục lục bìa có {len(agenda)} mục nhưng báo cáo có {n} phần"
                   + (" + 1 slide tổng hợp" if has_summary else "")
                   + f". Sửa agenda theo đúng các phần: {'; '.join(want)}.")
    elif agenda:
        stop = {"và", "&", "các", "của", "cho", "với", "the", "chi", "tiết"}
        words = lambda t: {w for w in re.findall(r"[0-9a-zà-ỹđ]+", str(t).lower()) if w not in stop}
        for (k, i, name), item in zip(secs, agenda):
            if name and not (words(name) & words(item.get("text", ""))):
                err.append(f"Mục lục mục {k:02d} “{item.get('text')}” không khớp phần {k:02d} “{name}” "
                           f"(kicker slide {i}). Mục lục phải theo đúng tên và thứ tự các phần.")
    return err


def check_block(blk, w, err):
    if not isinstance(blk, dict) or blk.get("type") not in BLOCKS:
        t = blk.get("type") if isinstance(blk, dict) else blk
        err.append(f"{w}: type '{t}' không hợp lệ. Dùng: {', '.join(BLOCKS)}.")
        return
    t = blk["type"]
    w = f"{w} ({t})"
    req, opt = BLOCKS[t]
    for f in req - set(blk):
        err.append(f"{w}: thiếu trường '{f}'.")
    for f in set(blk) - req - opt - {"type"}:
        err.append(f"{w}: trường lạ '{f}' (chỉ có: {', '.join(sorted(req | opt))}).")
    tone = blk.get("tone")
    if tone and t in TONES and tone not in TONES[t]:
        err.append(f"{w}: tone '{tone}' không hợp lệ ({' | '.join(sorted(TONES[t]))}).")
    if t == "stack":
        for b, sub in enumerate(blk.get("blocks") or [], 1):
            if isinstance(sub, dict) and sub.get("type") == "stack":
                err.append(f"{w} > khối {b}: không lồng stack trong stack.")
            else:
                check_block(sub, f"{w} > khối {b}", err)
    if t == "split":
        for p, part in enumerate(blk.get("parts") or [], 1):
            if not isinstance(part, dict) or not {"value", "label", "weight"} <= set(part):
                err.append(f"{w} > part {p}: cần value, label, weight (số), desc (tùy chọn).")
    if t == "numlist":
        for p, it in enumerate(blk.get("items") or [], 1):
            if not isinstance(it, dict) or not {"value", "text"} <= set(it):
                err.append(f"{w} > item {p}: cần value, text (tone 'warn' tùy chọn).")
    if t == "category":
        for p, it in enumerate(blk.get("rows") or [], 1):
            if not isinstance(it, dict) or not {"label", "value"} <= set(it):
                err.append(f"{w} > row {p}: cần label, value.")
    if t in ("status_table",):
        for p, it in enumerate(blk.get("rows") or [], 1):
            if not isinstance(it, dict) or not {"item", "status", "desc"} <= set(it):
                err.append(f"{w} > row {p}: cần item, status, desc (tone tùy chọn).")
    if t == "status_list":
        for p, it in enumerate(blk.get("items") or [], 1):
            if not isinstance(it, dict) or not {"status", "text"} <= set(it):
                err.append(f"{w} > item {p}: cần status, text.")
    if t == "bars":
        for p, it in enumerate(blk.get("items") or [], 1):
            if not isinstance(it, dict) or not {"label", "value", "percent"} <= set(it):
                err.append(f"{w} > item {p}: cần label, value (chữ hiển thị), percent (số 0-100).")
            elif not isinstance(it["percent"], (int, float)) or not (0 <= it["percent"] <= 100):
                err.append(f"{w} > item {p}: percent phải là số 0-100 đã tính sẵn (vd 23.0 cho 23%), không phải số thô cần chia.")
        lw = blk.get("label_width")
        if lw is not None and not re.fullmatch(r"\d+(\.\d+)?(px|%|ch|em|rem)", str(lw)):
            err.append(f"{w}: label_width phải là độ dài CSS (vd \"90px\"), không phải tên nhãn.")
    if t == "table":
        ncol = len(blk.get("columns") or [])
        for p, r in enumerate(blk.get("rows") or [], 1):
            if not isinstance(r, list) or len(r) != ncol:
                err.append(f"{w} > dòng {p}: phải là mảng {ncol} ô (bằng số columns).")
    if t == "progress" and not isinstance(blk.get("percent"), (int, float)):
        err.append(f"{w}: percent phải là số (vd 33.33), value là chữ hiển thị (vd \"33,33%\").")
    if t == "panel" and not (blk.get("bullets") or blk.get("text")):
        err.append(f"{w}: cần bullets (mảng) hoặc text.")


# ---------------------------------------------------------------- dựng HTML

def fmt(s):
    """Escape HTML, rồi **đậm** -> <strong>, \\n -> <br>."""
    s = html.escape(str(s if s is not None else ""), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s.replace("\n", "<br>")


def badge_tone(status, tone=None):
    if tone in BADGE_TONES:
        return tone
    s = (status or "").lower()
    if "chưa" in s or "trễ" in s or "chậm" in s or "vướng" in s:
        return "todo"
    if s.startswith("hoàn thành") or s.startswith("đã ") or s == "xong":
        return "done"
    if "đánh giá" in s or "xem xét" in s or "chờ" in s:
        return "eval"
    if s.startswith("đang"):
        return "doing"
    return "neutral"


def cls(*names):
    return " ".join(n for n in names if n)


def title_html(b):
    return f'<div class="blk-title">{fmt(b["title"])}</div>' if b.get("title") else ""


def block_html(b):
    t = b["type"]
    grow = "grow" if b.get("grow") else ""
    tone = b.get("tone")
    name = f'{t}: {b.get("title") or b.get("label") or b.get("value") or ""}'[:60]
    attr = f'data-name="{html.escape(name)}"'
    if t == "stack":
        inner = "".join(block_html(x) for x in b["blocks"])
        return f'<div class="{cls("stack", grow)}">{inner}</div>'
    if t == "stat":
        return (f'<div class="{cls("blk card stat", tone and "t-" + tone, grow)}" {attr}>'
                f'<div class="v">{fmt(b["value"])}</div><div class="l">{fmt(b["label"])}</div></div>')
    if t == "split":
        parts = b["parts"]
        total = sum(float(p["weight"]) for p in parts) or 1
        segs = "".join(f'<div class="seg" style="flex:{float(p["weight"]) / total:.4f} 1 0">'
                       f'{fmt(p["value"])} {fmt(p["label"])}</div>' for p in parts)
        colw = " ".join(f'minmax(0,{max(float(p["weight"]) / total, 0.3):.3f}fr)' for p in parts)
        descs = "".join(f'<div>{fmt(p.get("desc", ""))}</div>' for p in parts)
        foot = f'<div class="foot">{fmt(b["note"])}</div>' if b.get("note") else ""
        return (f'<div class="{cls("blk card split", grow)}" {attr}>{title_html(b)}<div class="bar">{segs}</div>'
                f'<div class="descs" style="grid-template-columns:{colw}">{descs}</div>{foot}</div>')
    if t == "numlist":
        its = "".join(f'<div class="it"><span class="{cls("n", it.get("tone"))}">{fmt(it["value"])}</span>'
                      f'<span class="t">{fmt(it["text"])}</span></div>' for it in b["items"])
        return f'<div class="{cls("blk card numlist", grow)}" {attr}>{title_html(b)}<div class="items">{its}</div></div>'
    if t == "category":
        rows = "".join(f'<div class="r"><span>{fmt(r["label"])}</span><span class="val">{fmt(r["value"])}</span></div>'
                       for r in b["rows"])
        sub = f'<div class="s">{fmt(b["sub"])}</div>' if b.get("sub") else ""
        tot = f'<div class="tot">{fmt(b["total"])}</div>' if b.get("total") else ""
        return (f'<div class="{cls("blk category", "t-" + (tone or "primary"), grow)}" {attr}>'
                f'<div class="hd"><div><div class="t">{fmt(b["title"])}</div>{sub}</div>{tot}</div>'
                f'<div class="bd">{rows}</div></div>')
    if t == "progress":
        pct = max(0.0, min(100.0, float(b["percent"])))
        lb = f'<div class="lb">{fmt(b["label"])}</div>' if b.get("label") else ""
        cap = f'<div class="cap">{fmt(b["caption"])}</div>' if b.get("caption") else ""
        return (f'<div class="{cls("blk card progress", grow)}" {attr}>{lb}<div class="v">{fmt(b["value"])}</div>'
                f'<div class="track"><div class="fill" style="width:{pct:.2f}%"></div></div>{cap}</div>')
    if t == "panel":
        body = ""
        if b.get("text"):
            body += f'<p>{fmt(b["text"])}</p>'
        if b.get("bullets"):
            body += '<ul class="bul">' + "".join(f"<li>{fmt(x)}</li>" for x in b["bullets"]) + "</ul>"
        return (f'<div class="{cls("blk card panel", "t-" + (tone or "light"), grow)}" {attr}>'
                f'{title_html(b)}{body}</div>')
    if t == "status_table":
        rows = "".join(f'<div class="r"><div class="it">{fmt(r["item"])}</div>'
                       f'<div class="st"><span class="badge {badge_tone(r["status"], r.get("tone"))}">{fmt(r["status"])}</span></div>'
                       f'<div class="ds"><span>{fmt(r["desc"])}</span></div></div>' for r in b["rows"])
        return f'<div class="{cls("blk card status_table", grow)}" {attr}>{title_html(b)}<div class="grid">{rows}</div></div>'
    if t == "status_list":
        its = "".join(f'<div class="it"><span class="badge {badge_tone(it["status"], it.get("tone"))}">'
                      f'{fmt(it["status"])}</span><div class="tx">{fmt(it["text"])}</div></div>' for it in b["items"])
        return f'<div class="{cls("blk card status_list", grow)}" {attr}>{title_html(b)}{its}</div>'
    if t == "steps":
        its = "".join(f"<li><b>{k}</b><span>{fmt(x)}</span></li>" for k, x in enumerate(b["items"], 1))
        return f'<div class="{cls("blk card steps", grow)}" {attr}>{title_html(b)}<ol>{its}</ol></div>'
    if t == "text":
        return (f'<div class="{cls("blk text", tone and "t-" + tone, grow)}" {attr}>{title_html(b)}'
                f'<p>{fmt(b["text"])}</p></div>')
    if t == "table":
        nums = set(b.get("num_cols") or [])
        th = "".join(f'<th class="{"num" if k in nums else ""}">{fmt(c)}</th>' for k, c in enumerate(b["columns"]))
        trs = "".join("<tr>" + "".join(f'<td class="{"num" if k in nums else ""}">{fmt(c)}</td>'
                                       for k, c in enumerate(r)) + "</tr>" for r in b["rows"])
        return (f'<div class="{cls("blk card table", grow)}" {attr}>{title_html(b)}'
                f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
    if t == "bars":
        its = "".join(f'<div class="it"><span class="lb">{fmt(it["label"])}</span><div class="tr">'
                      f'<div class="{cls("fl", it.get("tone"))}" style="width:{max(0.0, min(100.0, float(it["percent"]))):.2f}%">'
                      f'</div></div><span class="vl">{fmt(it["value"])}</span></div>' for it in b["items"])
        lw = f' style="--lw:{b["label_width"]}"' if b.get("label_width") else ""
        return f'<div class="{cls("blk card bars", grow)}" {attr}{lw}>{title_html(b)}{its}</div>'
    raise ValueError(t)


def slide_html(s):
    typ = s.get("type", "content")
    kicker = f'<div class="kicker">{fmt(s["kicker"])}</div>' if s.get("kicker") else ""
    if typ == "cover":
        sub = f'<div class="sub">{fmt(s["subtitle"])}</div>' if s.get("subtitle") else ""
        date = f'<div class="date">{fmt(s["date"])}</div>' if s.get("date") else ""
        ag = ""
        if s.get("agenda"):
            items = "".join(f'<div class="{cls("ag", "gap" if a.get("gap") else "")}"><div class="n">{fmt(a.get("num", ""))}</div>'
                            f'<div class="t">{fmt(a["text"])}</div></div>' for a in s["agenda"])
            ag = f'<div class="agenda">{items}</div>'
        return (f'<section class="slide cover"><div class="left">{kicker}<h1>{fmt(s["title"])}</h1>'
                f'{sub}{date}</div>{ag}</section>')
    if typ == "section":
        sub = f'<div class="lead">{fmt(s["subtitle"])}</div>' if s.get("subtitle") else ""
        return (f'<section class="slide dark" style="justify-content:center">{kicker}'
                f'<div class="title" style="font-size:48px">{fmt(s["title"])}</div>{sub}</section>')
    lead = f'<div class="lead">{fmt(s["lead"])}</div>' if s.get("lead") else ""
    rows = []
    # Không hàng nào ghi "grow" -> hàng cuối tự giãn cho kín slide (ghi "grow": false để tắt)
    auto = len(s["rows"]) - 1 if not any("grow" in r for r in s["rows"]) else -1
    for k, row in enumerate(s["rows"]):
        cols = row.get("cols") or [1] * len(row["blocks"])
        tpl = " ".join(f"minmax(0,{float(c):g}fr)" for c in cols)
        inner = "".join(block_html(b) for b in row["blocks"])
        rows.append(f'<div class="{cls("row", "grow" if row.get("grow") or k == auto else "")}" '
                    f'style="grid-template-columns:{tpl}">{inner}</div>')
    nxt = f'<div class="next"><b>Tiếp theo →</b><span>{fmt(s["next"])}</span></div>' if s.get("next") else ""
    note = ""
    if s.get("note"):
        n = s["note"]
        if isinstance(n, dict):
            lab = f'<b>{fmt(n["label"])}:</b> ' if n.get("label") else ""
            note = f'<div class="note">{lab}{fmt(n["text"])}</div>'
        else:
            note = f'<div class="note">{fmt(n)}</div>'
    dark = " dark" if s.get("dark") else ""
    return (f'<section class="slide{dark}">{kicker}<div class="title">{fmt(s["title"])}</div>{lead}'
            f'<div class="rows">{"".join(rows)}</div>{nxt}{note}</section>')


def fonts_css(font_dir):
    weights = {"Regular": 400, "Bold": 700}  # template chỉ dùng 2 độ đậm
    out = []
    for name, w in weights.items():
        f = Path(font_dir) / f"BeVietnamPro-{name}.ttf"
        if f.exists():
            b64 = base64.b64encode(f.read_bytes()).decode()
            out.append(f'@font-face{{font-family:"Be Vietnam Pro";font-weight:{w};font-style:normal;'
                       f'src:url(data:font/ttf;base64,{b64}) format("truetype")}}')
    return "\n".join(out)


def render(rep, skill_dir):
    skill_dir = Path(skill_dir)
    tpl = (skill_dir / "assets" / "template.html").read_text(encoding="utf-8")
    theme = rep.get("theme") or {}
    theme_css = (":root{" + ";".join(f"--{k}:{v}" for k, v in theme.items()) + "}") if theme else ""
    meta = rep.get("meta", {})
    slides = "\n".join(slide_html(s) for s in rep["slides"])
    return (tpl.replace("{{FONTS}}", fonts_css(skill_dir / "assets" / "fonts"))
               .replace("{{THEME}}", theme_css)
               .replace("{{TITLE}}", html.escape(meta.get("title", "Báo cáo")))
               .replace("{{AUTHOR}}", html.escape(meta.get("author", "")))
               .replace("{{SLIDES}}", slides))
