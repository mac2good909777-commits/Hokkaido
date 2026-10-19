# 由正本「北海道Vanlife行程.html」產生對外分享版。
# 10 個分頁全留；只拿掉：已收款（贊助金、叔叔嬸嬸姑姑旅費、差額）、
# 以及能直接查到訂位／保單的編號（訂單編號、預約號碼、PIN、進件編號、銷帳編號）、行前倒數提示。
import os, re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(root, "北海道Vanlife行程.html")
out_dir = os.path.join(root, "share-site")
s = open(src, encoding="utf-8").read()
NL = chr(10)

def sub1(old, new, label):
    global s
    n = s.count(old)
    assert n >= 1, ("missing", label)
    s = s.replace(old, new)
    print("replace", label, n)

# 1. 費用分頁：只移除「已收款」
a = s.index('<h3 style="margin:22px 0 8px;font-size:15px">💰 已收款</h3>')
b = s.index('<div class="small" style="margin-top:8px">標「已訂」者', a)
print("cut 已收款", b - a); s = s[:a] + s[b:]
sub1("<br><b>已收款</b>與支出連動：差額為正代表還有剩，為負代表要自己再補。", "", "已收款說明")

# 2. 費用分頁 JS：已收款資料、函式、差額計算
a = s.index("const incomeRows=["); b = s.index("];", a) + 2
s = s[:a] + s[b:]
a = s.index("/* ===== 已收款 ===== */"); b = s.index("function calcBudget()")
s = s[:a] + s[b:]
a = s.index("let totalIn=0;"); b = s.index(NL + "  }" + NL + "  defaultRows", a)
s = s[:a].rstrip() + NL + s[b:]
sub1("incomeRows.forEach(r=>addInRow(r[0],r[1]));", "", "incomeRows 呼叫")

# 3. 行前倒數（含取消期限、訂位狀態）的 JS
i = s.index("getElementById('deadline')")
a = s.rfind("(function", 0, i); b = s.index("})();", i) + 5
print("js deadline", b - a); s = s[:a] + s[b:]

# 4. 能直接查到訂位／保單的編號
sub1("✅ 已訂 — 預約號碼 99932053400", "✅ 已訂", "預約號碼(交通住宿)")
sub1("✅ 已訂 99932053400", "✅ 已訂", "預約號碼(準備清單)")
sub1("✅ 已訂</span>　訂單 1616333771093225", "✅ 已訂</span>", "訂單(準備清單)")
sub1("訂單編號 <b>1616333771093225</b>・PIN 6485<br>　", "", "訂單編號+PIN(筆記)")
sub1("預約號碼 <b>99932053400</b>・總額", "總額", "預約號碼+總額(筆記)")
sub1("預約號碼 <b>99932053400</b><br>　", "", "預約號碼(筆記)")
sub1("予約番号：1616333771093225", "予約番号：（予約確認メールのとおり）", "日語小卡預約號")
sub1("訂單編號 1616333771093225。", "訂單編號請看訂房確認信。", "日語小卡中文")
sub1("進件編號 <b>2610001371675740</b>　／　銷帳編號 60952771307997<br>", "", "保單編號")
left = re.findall(r"\d{9,}", re.sub(r"<[^>]+>|[A-Za-z0-9_\-]{9,}", " ", s))
print("remaining 9+ digit runs:", left[:10])

# 5. GA4（對外頁面必帶）
ga = open(os.path.expanduser("~/.claude/skills/ga4-tracking/assets/ga4.html"), encoding="utf-8").read()
s = s.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">' + NL + ga, 1)
assert "G-H5VLHW8761" in s

os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(s)
dst = os.path.join(out_dir, "photos")
os.makedirs(dst, exist_ok=True)
shutil.copytree(os.path.join(root, "photos"), dst, dirs_exist_ok=True)
print("wrote", len(s))
