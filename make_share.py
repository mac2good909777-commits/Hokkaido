# 由正本「北海道Vanlife行程.html」產生對外分享版（拿掉費用、準備清單、筆記，以及訂單編號與金額）
import os, re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root, "北海道Vanlife行程.html")
out_dir = os.path.join(root, "share-site")
s = open(src, encoding="utf-8").read()

def cut(s, start_pat, end_pat, label, end_inclusive=True):
    a = s.index(start_pat)
    b = s.index(end_pat, a)
    if end_inclusive: b += len(end_pat)
    print("cut", label, b - a)
    return s[:a] + s[b:]

# 1. 拿掉整個分頁的 section
for sid in ["budget-sec", "checklist-sec", "entry-sec", "jp-sec"]:
    a = s.index('<section id="%s"' % sid)
    b = s.index("</section>", a) + len("</section>")
    print("section", sid, b - a)
    s = s[:a] + s[b:]

# 2. 拿掉分頁按鈕
for tab in ["check", "budget", "jp"]:
    pat = re.compile(r'\s*<button class="tab-btn"[^>]*data-tab="%s"[^>]*>[^<]*</button>' % tab)
    assert len(pat.findall(s)) == 1, tab
    s = pat.sub("", s)

# 3. JS：預算區塊與準備清單區塊
a = s.index("const defaultRows")
a = s.rfind("\n", 0, s.rfind("/*", 0, a)) + 1 if s.rfind("/*", 0, a) > a - 400 else s.rfind("\n", 0, a) + 1
b = s.index("renderJ2T();", s.index("incomeRows.forEach")) + len("renderJ2T();")
print("js budget", b - a); s = s[:a] + s[b:]
a = s.index("/* ===== 準備清單")
b = s.index("window.resetCheck=resetCheck;") + len("window.resetCheck=resetCheck;")
print("js check", b - a); s = s[:a] + s[b:]

# 4. 私人資訊
s = re.sub(r'<tr><th[^>]*>(?:車資|房價)</th>.*?</tr>\s*', "", s, flags=re.S)
s = s.replace("・<b>TWD 27,435</b>", "")
s = re.sub(r'<div class="kpi"><div class="k">總車資</div>.*?</div></div>\s*', "", s, count=1, flags=re.S)
s = s.replace("✅ 已訂 — 預約號碼 99932053400", "✅ 已訂")
s = re.sub(r'\s*<div class="ok"><b>已投保旅平險</b>[^<]*</div>', "", s)
a = s.index('<h3 style="margin:16px 0 8px;font-size:15px">季節價')
b = s.index("</table>", a); b = s.index("</div>", b) + len("</div>")
print("cut 季節價", b - a); s = s[:a] + s[b:]

# 5. 行前倒數（含取消期限、訂位狀態）的 JS 與提示
i = s.index("getElementById('deadline')")
a = s.rfind("(function", 0, i); b = s.index("})();", i) + 5
print("js deadline", b - a); s = s[:a] + s[b:]
s = s.replace('<br><span class="small">訂單註明「飯店隨機安排房型」</span>', "")
def j2t(m):
    p = [int(x) for x in m.group(1).split("-")]
    return "–".join("¥{:,}".format(x) for x in p)
s = re.sub(r'<span class="j2t" data-jpy="([\d\-]+)"></span>', j2t, s)
s = s.replace('<title>', '<title>', 1)


# 6. GA4（對外頁面必帶）
ga = open(os.path.expanduser("~/.claude/skills/ga4-tracking/assets/ga4.html"), encoding="utf-8").read()
s = s.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + chr(10) + ga, 1)
assert "G-H5VLHW8761" in s

os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(s)
dst = os.path.join(out_dir, "photos")
os.makedirs(dst, exist_ok=True)
shutil.copytree(os.path.join(root, "photos"), dst, dirs_exist_ok=True)
print("wrote", len(s))
