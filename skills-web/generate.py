#!/usr/bin/env python3
"""Generate self-contained index.html with all lesson content embedded."""
import json, re

with open("/tmp/lessons_data.json", "r") as f:
    lessons = json.load(f)

# Escape for JS template literal
def js_escape(s):
    return s.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

BUOI_NAMES = {
    1: 'Buổi 1: Cấu Trúc Tài Chính Toàn Cầu',
    2: 'Buổi 2: Bài Học Từ Các Quốc Gia',
    3: 'Buổi 3: Chiến Lược Việt Nam',
    4: 'Buổi 4: Đầu Tư Thực Chiến'
}
BUOI_ICONS = {1: '📘', 2: '🌏', 3: '🇻🇳', 4: '💰'}
BUOI_COLORS = {1: '#2b6cb0', 2: '#2f855a', 3: '#c53030', 4: '#b7791f'}

# Build lessons JS array
lessons_js = json.dumps(lessons, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Khóa Học Vĩ Mô | Vinalink Skills</title>
<meta name="description" content="Khóa học Kinh tế Vĩ mô - Hiểu dòng tiền, chu kỳ kinh tế và chiến lược đầu tư. Vinalink Academy.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"><\/script>
<style>
:root {{
  --primary: #1a365d;
  --primary-light: #2b6cb0;
  --accent: #ed8936;
  --bg: #f7fafc;
  --text: #2d3748;
  --text-light: #718096;
  --border: #e2e8f0;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }}

.hero {{
  background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 50%, #3182ce 100%);
  color: white; padding: 2.5rem 1.5rem 2rem; text-align: center;
  position: relative; overflow: hidden;
}}
.hero::before {{
  content:'';position:absolute;inset:0;
  background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none'%3E%3Cg fill='%23fff' fill-opacity='.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}}
.hero-content {{ position:relative; z-index:1; max-width:800px; margin:0 auto; }}
.hero .brand {{ font-size:0.8rem; text-transform:uppercase; letter-spacing:3px; opacity:0.8; margin-bottom:0.5rem; }}
.hero .brand a {{ color:white; text-decoration:none; }}
.hero h1 {{ font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:800; margin-bottom:0.6rem; }}
.hero .subtitle {{ font-size:1rem; opacity:0.9; max-width:550px; margin:0 auto 1.2rem; }}
.hero .stats {{ display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; }}
.hero .stat-num {{ font-size:1.6rem; font-weight:800; }}
.hero .stat-label {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; opacity:0.7; }}

.nav-bar {{
  background:white; border-bottom:1px solid var(--border); padding:0.6rem 1rem;
  position:sticky; top:0; z-index:100; box-shadow:0 1px 3px rgba(0,0,0,0.08);
}}
.nav-inner {{ max-width:1100px; margin:0 auto; display:flex; gap:0.4rem; flex-wrap:wrap; justify-content:center; }}
.nav-btn {{
  padding:0.45rem 0.9rem; border:1px solid var(--border); border-radius:8px;
  background:white; cursor:pointer; font-size:0.82rem; font-weight:500; color:var(--text); transition:all 0.2s;
}}
.nav-btn:hover,.nav-btn.active {{ background:var(--primary); color:white; border-color:var(--primary); }}

.container {{ max-width:1100px; margin:0 auto; padding:1.5rem; display:flex; gap:1.5rem; }}
.sidebar {{ width:260px; flex-shrink:0; position:sticky; top:75px; height:fit-content; max-height:calc(100vh - 90px); overflow-y:auto; }}
.main-content {{ flex:1; min-width:0; }}

.toc {{ background:white; border-radius:12px; padding:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.06); border:1px solid var(--border); }}
.toc h3 {{ font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; color:var(--text-light); margin-bottom:0.8rem; }}
.toc-section {{ margin-bottom:0.8rem; }}
.toc-section-title {{
  font-weight:600; font-size:0.82rem; color:var(--primary); padding:0.35rem 0; cursor:pointer;
}}
.toc-item {{
  display:block; padding:0.3rem 0 0.3rem 1.2rem; font-size:0.78rem; color:var(--text-light);
  cursor:pointer; border-left:2px solid transparent; transition:all 0.15s; text-decoration:none;
}}
.toc-item:hover {{ color:var(--primary); border-left-color:var(--primary); }}
.toc-item.active {{ color:var(--primary); font-weight:600; border-left-color:var(--accent); }}

.card-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }}
.lesson-card {{
  background:white; border-radius:12px; padding:1.1rem; border:1px solid var(--border);
  cursor:pointer; transition:all 0.2s; box-shadow:0 1px 3px rgba(0,0,0,0.04);
}}
.lesson-card:hover {{ transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.1); border-color:var(--primary-light); }}
.lesson-card .badge {{
  display:inline-block; font-size:0.68rem; font-weight:600; padding:0.15rem 0.5rem;
  border-radius:20px; background:#ebf4ff; color:var(--primary-light); margin-bottom:0.4rem;
}}
.lesson-card h3 {{ font-size:0.95rem; font-weight:600; margin-bottom:0.3rem; }}
.lesson-card p {{ font-size:0.8rem; color:var(--text-light); line-height:1.5; }}

.article {{ background:white; border-radius:12px; padding:2rem 2.5rem; border:1px solid var(--border); box-shadow:0 1px 3px rgba(0,0,0,0.06); }}
.article .back-btn {{
  display:inline-flex; align-items:center; gap:0.3rem; font-size:0.85rem;
  color:var(--primary-light); cursor:pointer; margin-bottom:1.2rem; font-weight:500;
}}
.article .back-btn:hover {{ color:var(--accent); }}
.article h1 {{ font-family:'Playfair Display',serif; font-size:1.8rem; margin-bottom:1rem; color:var(--primary); }}
.article h2 {{ font-size:1.2rem; margin:1.5rem 0 0.7rem; padding-bottom:0.3rem; border-bottom:2px solid var(--border); color:var(--primary); }}
.article h3 {{ font-size:1.05rem; margin:1.2rem 0 0.5rem; color:var(--primary-light); }}
.article p {{ margin-bottom:0.7rem; }}
.article ul,.article ol {{ margin:0.4rem 0 0.8rem 1.5rem; }}
.article li {{ margin-bottom:0.25rem; }}
.article table {{ width:100%; border-collapse:collapse; margin:0.8rem 0; font-size:0.85rem; }}
.article th {{ background:var(--primary); color:white; padding:0.5rem 0.7rem; text-align:left; }}
.article td {{ padding:0.45rem 0.7rem; border-bottom:1px solid var(--border); }}
.article tr:hover td {{ background:#f7fafc; }}
.article strong {{ color:var(--primary); }}
.article blockquote {{ border-left:3px solid var(--accent); padding:0.4rem 1rem; margin:0.8rem 0; background:#fffaf0; border-radius:0 8px 8px 0; }}

.lesson-nav {{
  display:flex; justify-content:space-between; margin-top:2rem; padding-top:1rem; border-top:1px solid var(--border);
}}
.lesson-nav a {{
  padding:0.5rem 1rem; border-radius:8px; background:#ebf4ff; color:var(--primary-light);
  text-decoration:none; font-size:0.85rem; font-weight:500; cursor:pointer;
}}
.lesson-nav a:hover {{ background:var(--primary); color:white; }}

.footer {{ text-align:center; padding:1.5rem; color:var(--text-light); font-size:0.78rem; border-top:1px solid var(--border); margin-top:2rem; }}
.footer a {{ color:var(--primary-light); text-decoration:none; }}

@media(max-width:768px) {{
  .sidebar {{ display:none; }}
  .container {{ padding:1rem; }}
  .article {{ padding:1.2rem; }}
  .hero h1 {{ font-size:1.6rem; }}
  .card-grid {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-content">
    <div class="brand"><a href="https://vinalink.edu.vn" target="_blank">Vinalink Academy</a></div>
    <h1>📚 Khóa Học Vĩ Mô</h1>
    <p class="subtitle">Hiểu vĩ mô để không bị "xén lông cừu" — Nắm bắt dòng tiền, chu kỳ kinh tế và chiến lược đầu tư thông minh</p>
    <div class="stats">
      <div class="stat"><div class="stat-num">4</div><div class="stat-label">Buổi học</div></div>
      <div class="stat"><div class="stat-num">17</div><div class="stat-label">Bài giảng</div></div>
      <div class="stat"><div class="stat-num">3h+</div><div class="stat-label">Nội dung</div></div>
    </div>
  </div>
</div>

<nav class="nav-bar">
  <div class="nav-inner">
    <button class="nav-btn active" onclick="showOverview()">🏠 Tổng quan</button>
    <button class="nav-btn" onclick="showBuoi(1)">📘 Buổi 1</button>
    <button class="nav-btn" onclick="showBuoi(2)">🌏 Buổi 2</button>
    <button class="nav-btn" onclick="showBuoi(3)">🇻🇳 Buổi 3</button>
    <button class="nav-btn" onclick="showBuoi(4)">💰 Buổi 4</button>
  </div>
</nav>

<div class="container">
  <aside class="sidebar">
    <div class="toc">
      <h3>📑 Mục lục</h3>
      <div id="toc-content"></div>
    </div>
  </aside>
  <div class="main-content" id="main"></div>
</div>

<div class="footer">
  <p>🎓 <strong>Khóa Học Vĩ Mô</strong> — <a href="https://vinalink.edu.vn" target="_blank">Vinalink Academy</a></p>
  <p style="margin-top:0.3rem">© 2025 Vinalink. Nội dung mang tính giáo dục và tham khảo.</p>
</div>

<script>
const LESSONS = {lessons_js};
const BUOI = {{1:'Buổi 1: Cấu Trúc Tài Chính Toàn Cầu',2:'Buổi 2: Bài Học Từ Các Quốc Gia',3:'Buổi 3: Chiến Lược Việt Nam',4:'Buổi 4: Đầu Tư Thực Chiến'}};
const ICONS = {{1:'📘',2:'🌏',3:'🇻🇳',4:'💰'}};

function buildTOC() {{
  let h='';
  for(let b=1;b<=4;b++) {{
    const items=LESSONS.filter(l=>l.buoi===b);
    h+=`<div class="toc-section"><div class="toc-section-title" onclick="showBuoi(${{b}})">${{ICONS[b]}} ${{BUOI[b]}}</div>`;
    items.forEach((l,i)=>{{
      h+=`<a class="toc-item" data-b="${{b}}" data-i="${{l.idx}}" onclick="showLesson(${{b}},${{l.idx}})">${{l.idx}}. ${{l.title}}</a>`;
    }});
    h+='</div>';
  }}
  document.getElementById('toc-content').innerHTML=h;
}}

function setNav(n){{ document.querySelectorAll('.nav-btn').forEach((b,i)=>b.classList.toggle('active',i===n)); }}
function setToc(b,idx){{ document.querySelectorAll('.toc-item').forEach(a=>a.classList.toggle('active',+a.dataset.b===b&&+a.dataset.i===idx)); }}

function showOverview() {{
  setNav(0); setToc(0,0);
  let h='<div class="card-grid">';
  LESSONS.forEach(l=>{{
    h+=`<div class="lesson-card" onclick="showLesson(${{l.buoi}},${{l.idx}})">
      <span class="badge">${{ICONS[l.buoi]}} Buổi ${{l.buoi}} — Phần ${{l.idx}}</span>
      <h3>${{l.title}}</h3><p>${{l.desc}}</p></div>`;
  }});
  h+='</div>';
  document.getElementById('main').innerHTML=h;
}}

function showBuoi(b) {{
  setNav(b); setToc(0,0);
  const items=LESSONS.filter(l=>l.buoi===b);
  let h=`<h2 style="font-family:'Playfair Display',serif;color:var(--primary);margin-bottom:1rem">${{ICONS[b]}} ${{BUOI[b]}}</h2><div class="card-grid">`;
  items.forEach(l=>{{
    h+=`<div class="lesson-card" onclick="showLesson(${{l.buoi}},${{l.idx}})">
      <span class="badge">Phần ${{l.idx}}</span>
      <h3>${{l.title}}</h3><p>${{l.desc}}</p></div>`;
  }});
  h+='</div>';
  document.getElementById('main').innerHTML=h;
}}

function showLesson(b,idx) {{
  const lesson=LESSONS.find(l=>l.buoi===b&&l.idx===idx);
  if(!lesson) return;
  setNav(b); setToc(b,idx);

  const rendered=marked.parse(lesson.content);

  // Find prev/next
  const allIdx=LESSONS.indexOf(lesson);
  const prev=allIdx>0?LESSONS[allIdx-1]:null;
  const next=allIdx<LESSONS.length-1?LESSONS[allIdx+1]:null;

  let nav='<div class="lesson-nav">';
  if(prev) nav+=`<a onclick="showLesson(${{prev.buoi}},${{prev.idx}})">← ${{prev.title}}</a>`; else nav+='<span></span>';
  if(next) nav+=`<a onclick="showLesson(${{next.buoi}},${{next.idx}})">${{next.title}} →</a>`; else nav+='<span></span>';
  nav+='</div>';

  document.getElementById('main').innerHTML=`
    <div class="article">
      <div class="back-btn" onclick="showBuoi(${{b}})">← Quay lại ${{BUOI[b]}}</div>
      <h1>${{lesson.title}}</h1>
      ${{rendered}}
      ${{nav}}
    </div>`;
  window.scrollTo({{top:0,behavior:'smooth'}});
}}

buildTOC();
showOverview();
<\/script>
</body>
</html>'''

out = "/home/openclaw/.openclaw/workspace-main/khoa-hoc-vi-mo/skills-web/index.html"
with open(out, "w") as f:
    f.write(html)
print(f"Written {len(html):,} bytes to {out}")
