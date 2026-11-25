import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 675
BG = (244, 241, 234)
INK = (34, 34, 34)
SUB = (110, 104, 96)
ACCENT = (150, 60, 45)

SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Medium.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANS_M = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"

NO_START = set("、。，．・：；？！ー」』）】〕…‥ぁぃぅぇぉっゃゅょァィゥェォッャュョ")
NO_END = set("「『（【〔")
BREAK_AFTER = set("、。」』をはがのにでともへやて")
NO_LEAD = set("にをはがのでともへやてだ")


def wrap(text, font, max_w, draw):
    lines = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if draw.textlength(line + ch, font=font) <= max_w:
                line += ch
                continue
            # prefer breaking right after punctuation or a particle
            for back in range(0, 7):
                pos = len(line) - back
                if pos <= 0:
                    break
                nxt = (line[pos:] + ch)[0]
                if line[pos - 1] in BREAK_AFTER and nxt not in NO_START and nxt not in NO_LEAD:
                    ch = line[pos:] + ch
                    line = line[:pos]
                    break
            else:
                if ch in NO_START and line:
                    ch = line[-1] + ch
                    line = line[:-1]
                if line and line[-1] in NO_END:
                    ch = line[-1] + ch
                    line = line[:-1]
            lines.append(line)
            line = ch
        lines.append(line)
    return lines


def make(quote, title, out):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    left, right = 110, W - 110
    max_w = right - left

    # size the quote to fit
    for size in (52, 48, 44, 40, 36, 32):
        qf = ImageFont.truetype(SERIF, size)
        lines = wrap(quote, qf, max_w, d)
        lh = int(size * 1.7)
        if len(lines) * lh <= 330:
            break

    # opening mark
    mark = ImageFont.truetype(SERIF, 120)
    d.text((left - 12, 40), "“", font=mark, fill=ACCENT)

    block_h = len(lines) * lh
    y = 150 + (330 - block_h) // 2
    for ln in lines:
        d.text((left, y), ln, font=qf, fill=INK)
        y += lh

    # footer
    d.line([(left, 540), (left + 60, 540)], fill=ACCENT, width=3)
    tf = ImageFont.truetype(SANS_M, 26)
    t_lines = wrap("note「" + title + "」", tf, max_w - 260, d)
    d.text((left, 562), t_lines[0] + ("…" if len(t_lines) > 1 else ""), font=tf, fill=SUB)
    af = ImageFont.truetype(SANS, 24)
    author = "並木 将仁"
    aw = d.textlength(author, font=af)
    d.text((right - aw, 564), author, font=af, fill=SUB)

    img.save(out, "PNG", optimize=True)


if __name__ == "__main__":
    make(sys.argv[1], sys.argv[2], sys.argv[3])
