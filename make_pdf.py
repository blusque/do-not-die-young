# -*- coding: utf-8 -*-
"""把 build.py 生成的 index.html 渲染成 PDF，一次出两个版本。

    full    —— 展开每一条建议的「来源」文献；
    simple  —— 来源保持收起，只留「来源（N 条文献）」这一行，体积小很多。

用无头 Chrome 的 --print-to-pdf 渲染：调用的是 index.html 自带的 @media print
样式（会隐藏顶栏、左侧目录、回到顶部按钮）。

用法：
    python make_pdf.py index.html -o dist
    python make_pdf.py index.html -o dist --paper Letter
    python make_pdf.py index.html -o dist --chrome "/path/to/chrome"
    python make_pdf.py index.html -o dist --prefix 高性价比人生指南

Chrome 位置依次从 --chrome、环境变量 CHROME_PATH / CHROME、PATH 上的
google-chrome / chromium / msedge，以及 Windows 常见安装路径里找。
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DETAILS = '<details class="src">'
DETAILS_OPEN = '<details class="src" open>'


def parse_args():
    ap = argparse.ArgumentParser(description="把单文件阅读页渲染成 simple / full 两个 PDF")
    ap.add_argument("html", help="输入 HTML（build.py 生成的 index.html）")
    ap.add_argument("-o", "--out", default="dist", help="输出目录（默认 dist）")
    ap.add_argument("--chrome", default=None, help="Chrome/Chromium 可执行文件路径")
    ap.add_argument("--paper", default="A4",
                    help="纸张尺寸，如 A4、Letter；传 default 表示用浏览器默认（默认 A4）")
    ap.add_argument("--prefix", default="how-to-live-better", help="输出文件名前缀")
    return ap.parse_args()


def find_chrome(explicit):
    if explicit:
        return explicit
    for var in ("CHROME_PATH", "CHROME"):
        v = os.environ.get(var)
        if v and Path(v).exists():
            return v
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    for c in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if Path(c).exists():
            return c
    raise SystemExit("找不到 Chrome/Chromium，请用 --chrome 指定，或设置 CHROME_PATH。")


def inject(html, css):
    """把一段 CSS 插到 </head> 之前（没有 head 就放最前面）。"""
    if not css:
        return html
    tag = "<style>%s</style>" % css
    if "</head>" in html:
        return html.replace("</head>", tag + "</head>", 1)
    return tag + html


def render(chrome, html_path, pdf_path):
    """调用无头 Chrome 把 html_path 打成 pdf_path。"""
    profile = Path(tempfile.mkdtemp(prefix="hltb-chrome-"))
    args = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=20000",
        "--user-data-dir=" + str(profile),
        "--print-to-pdf=" + str(pdf_path),
        html_path.resolve().as_uri(),
    ]
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.stderr.write(p.stdout or "")
        sys.stderr.write(p.stderr or "")
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise SystemExit("Chrome 渲染失败：%s" % pdf_path)
    shutil.rmtree(profile, ignore_errors=True)


def main():
    a = parse_args()
    chrome = find_chrome(a.chrome)
    html = Path(a.html).read_text(encoding="utf-8")

    outdir = Path(a.out)
    if not outdir.is_absolute():
        outdir = Path.cwd() / outdir
    outdir.mkdir(parents=True, exist_ok=True)

    n = html.count(DETAILS)
    page_css = "" if a.paper.lower() in ("default", "none", "") else "@page{size:%s;margin:12mm}" % a.paper

    # full：把每个 <details class="src"> 打开；simple：保持收起，并强制不显示来源正文
    variants = {
        "full": (html.replace(DETAILS, DETAILS_OPEN), page_css),
        "simple": (html, page_css + '.src .sbody{display:none!important}'),
    }

    print("Chrome: %s" % chrome)
    print("来源条目: %d ｜ 纸张: %s" % (n, a.paper))

    tmpdir = Path(tempfile.mkdtemp(prefix="hltb-html-"))
    for name, (doc, css) in variants.items():
        tmp_html = tmpdir / ("%s.html" % name)
        tmp_html.write_text(inject(doc, css), encoding="utf-8")
        pdf = outdir / ("%s-%s.pdf" % (a.prefix, name))
        render(chrome, tmp_html, pdf)
        print("输出：%s  (%.1f MB)" % (pdf, pdf.stat().st_size / 1048576))

    shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
