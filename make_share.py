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
for sid in ["checklist-sec", "entry-sec", "jp-sec"]:
    a = s.index('<section id="%s"' % sid)
    b = s.index("</section>", a) + len("</section>")
    print("section", sid, b - a)
    s = s[:a] + s[b:]

# 2. 拿掉分頁按鈕
for tab in ["check", "jp"]:
    pat = re.compile(r'\s*<button class="tab-btn"[^>]*data-tab="%s"[^>]*>[^<]*</button>' % tab)
    assert len(pat.findall(s)) == 1, tab
    s = pat.sub("", s)

# 3. JS：預算區塊與準備清單區塊
a = s.index("const incomeRows=["); b = s.index("];", a) + 2
print("js incomeRows", b - a); s = s[:a] + "const incomeRows=[];" + s[b:]
a = s.index("/* ===== 準備清單")
b = s.index("window.resetCheck=resetCheck;") + len("window.resetCheck=resetCheck;")
print("js check", b - a); s = s[:a] + s[b:]

# 3b. 費用分頁：只移除「已收款」
a = s.index('<h3 style="margin:22px 0 8px;font-size:15px">💰 已收款</h3>')
b = s.index('<div class="small" style="margin-top:8px">標「已訂」者', a)
print("cut 已收款", b - a); s = s[:a] + s[b:]
old = "<br><b>已收款</b>與支出連動：差額為正代表還有剩，為負代表要自己再補。"
assert s.count(old) == 1; s = s.replace(old, "")

# 3c. JS 裡殘留的已收款函式與差額計算
NL = chr(10)
a = s.index("/* ===== 已收款 ===== */"); b = s.index("function calcBudget()")
print("js 已收款 funcs", b - a); s = s[:a] + s[b:]
a = s.index("let totalIn=0;"); b = s.index(NL + "  }" + NL + "  defaultRows", a)
print("js 差額", b - a); s = s[:a].rstrip() + NL + s[b:]
s = s.replace("incomeRows.forEach(r=>addInRow(r[0],r[1]));", "")
s = s.replace("const incomeRows=[];", "")

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
