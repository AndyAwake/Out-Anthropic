#!/usr/bin/env python3
"""Build AndyAwake standalone editorial GitHub Pages and printable full handbook.
Run inside the repository root: python scripts/build.py
Requires: pip install mistune weasyprint (PDF optional).
"""
from pathlib import Path
import re, html, json, shutil, os
from datetime import date
from urllib.parse import quote
import mistune

ROOT=Path(__file__).resolve().parents[1]
NAME=ROOT.name
if NAME not in ('Anti-Anthropic','Out-Anthropic','Free-Anthropic'):
    raise SystemExit('Copy this script to one of the three repository scripts/ folders first.')
CONFIG={
 'Anti-Anthropic': {
  'index':'03', 'theme':'METHODS / PORTABILITY / SOURCE EVIDENCE', 'title':'学会好方法，<br><em>不被工具绑住。</em>',
  'deck':'Claude Code 的项目指令、Skills、MCP 与 Agent 工作流，哪些值得学、如何变成自己的能力？政策争议保留证据与讨论，不妨碍你立即行动。',
  'note':'先学能带走的能力，再看供应商风险。公开证据、作者观点和未证实信息严格区分；不针对任何民族。',
  'statement':'已公开的政策值得审查；没有独立证据的指控，不应被写成已经证实的结论。',
  'widget_title':'企业 AI 供应商风险自查',
  'widget_note':'这张清单只保存在你本机浏览器，不读取账号和文件。',
  'checks':['列出业务中正在使用的 AI 软件与模型','核对账号、实体与实际所在地对应的支持政策','明确客户数据、存储位置和访问控制','为核心任务准备独立备份和替代方案','用同一任务完成一次可复核的替代演练'],
  'resources':[('原仓库完整攻略','research','https://github.com/AndyAwake/Anti-Anthropic/blob/main/GUIDE.md','政策分析与行动方法'),('数据控制详解','practice','https://github.com/AndyAwake/Anti-Anthropic/blob/main/DATA-CONTROL.md','robots、WAF 与权限边界'),('政治活动研究','research','https://github.com/AndyAwake/Anti-Anthropic/blob/main/POLITICS.md','公开政治资金及政策过程'),('证据档案','research','EVIDENCE-2026.md','事实与推测的分界'),('Claude 能力可移植指南','practice','PORTABLE-CLAUDE.md','规则、Skills、MCP、Hooks 到跨工具资产'),('学习资源地图','research','RESOURCE-ATLAS.md','精选官方文档与 Andy 原创开源项目'),('Claude Code / Agent 实战研究库','practice','https://github.com/AIPMAndy/anthropic-claude-code-agent-handbook','作者既有 Claude Code 系统化资料'),('供应商审计 CSV','template','templates/vendor-audit.csv','记录模型、数据与恢复风险'),('政策观察 CSV','template','templates/policy-watch.csv','长期跟踪原始链接与变化')],
  'adjacent':['Out-Anthropic','Free-Anthropic']
 },
 'Out-Anthropic':{
  'index':'01', 'theme':'CLAUDE / CLAUDE CODE / SAFE MIGRATION', 'title':'Claude 迁移，<br><em>不用从零开始。</em>',
  'deck':'聊天、Projects、记忆、原始附件、Claude Code 的源码与 Skills：先生成属于你的迁移路线，再逐项备份、迁出、恢复与验证。',
  'note':'官方导出不一定包含你上传过的原始文件；每一步都配有核验，避免“下载了但恢复不了”。',
  'statement':'一个文件下载成功，不代表一次迁移完成；必须能从独立副本恢复并继续真实工作。',
  'widget_title':'七步数据迁移进度',
  'widget_note':'勾选状态保存在当前设备浏览器，不上传任何资料。',
  'checks':['申请官方导出并保存未修改的原件','建立七类资产清单，按项目整理','单独保存并清理记忆和长期偏好','为 P0 项目填写交接卡','补齐原始上传文件、可编辑成品与源码','在替代工具中重做一个相同的真实任务','从独立副本恢复并记录差异与缺口'],
  'resources':[('原仓库七步教程','research','https://github.com/AndyAwake/Out-Anthropic/blob/main/GUIDE.md','账号角色与导出操作'),('原仓库恢复清单','practice','https://github.com/AndyAwake/Out-Anthropic/blob/main/RESTORE.md','验证资料与业务连续性'),('迁移资产台账 CSV','template','templates/migration-inventory.csv','七类资料逐项登记'),('项目交接卡 Markdown','template','templates/PROJECT-HANDOFF.md','目标、版本、依赖与验收'),('恢复测试报告','template','templates/restore-report.md','逐项记录真实恢复结果'),('Claude 官方导出说明','research','https://support.claude.com/en/articles/9450526-export-your-claude-data','账户与权限最新说明'),('Claude Code 专项迁移','practice','CLAUDE-CODE-MIGRATION.md','源码、会话、CLAUDE.md、Skills、MCP、Hooks'),('通用项目上下文','template','templates/PORTABLE-PROJECT.md','跨工具共有项目目标、限制与验收'),('Codex 适配模板','template','templates/AGENTS.md','通用工程约束'),('Gemini CLI 适配模板','template','templates/GEMINI.md','上下文导入示例'),('本地迁移计划模板','template','templates/MIGRATION-PLAN.md','七类资产登记与单任务回放')],
  'adjacent':['Anti-Anthropic','Free-Anthropic']
 },
 'Free-Anthropic':{
  'index':'02','theme':'FIND YOUR ALTERNATIVE / KEEP YOUR RESULTS','title':'换一个 AI，<br><em>工作照样继续。</em>',
  'deck':'从 Claude 用户熟悉的任务出发：写作、Projects、Claude Code、文档、Agent 和 API。按实际可用性、交付效果与成本找到新工作台。',
  'note':'Free 代表选择自由，不代表所有产品免费。所有“建议先试”均不等于当前账号已通过实测。',
  'statement':'决定工具价值的，不是一段惊艳回答，而是你能不能把真实任务按标准交付并且下次复用。',
  'widget_title':'一次高质量同题测试',
  'widget_note':'完成以下动作再判断工具是否真的适合你。',
  'checks':['定义一个真实任务和可验证输出格式','准备许可清晰的公开或自有原料','记录实际模型与可见计费信息','生成并保存可编辑成果','人工复查事实、格式、运行情况与版权','记录耗时/成本，使用备用工具同题对照'],
  'resources':[('原仓库五类任务工作流','practice','https://github.com/AndyAwake/Free-Anthropic/blob/main/WORKFLOWS.md','相同原料与验收基准'),('开源与许可项目目录','research','https://github.com/AndyAwake/Free-Anthropic/blob/main/OPEN-SOURCE.md','工具、许可证与上手条件'),('真实评测记录 CSV','template','templates/task-evaluation.csv','成本、模型和返工时间'),('任务需求卡 Markdown','template','templates/brief-template.md','模板化定义输入与输出'),('Andy Video Skill','practice','https://github.com/AIPMAndy/Andy-Video-Skill','真实 UI 视频工作方法'),('Claude 平替任务矩阵','practice','ALTERNATIVE-MATRIX.md','不同 Claude 场景的候选方案与限制'),('跨模型工作流卡','template','templates/WORKFLOW-CARD.md','记录输入、输出、验收、成本与回放'),('Claude Code / Agent 学习库','research','https://github.com/AIPMAndy/anthropic-claude-code-agent-handbook','作者已有系统化开源资料'),('FreeDocs','practice','https://github.com/AIPMAndy/FreeDocs','可迁移文档项目')],
  'adjacent':['Anti-Anthropic','Out-Anthropic']
 }
}[NAME]

mdtxt=(ROOT/'HANDBOOK.md').read_text(encoding='utf8')
markdown=mistune.create_markdown(escape=True,plugins=['table','strikethrough','url','task_lists'])
content=markdown(mdtxt)
headings=re.findall(r'^##\s+(.+?)\s*$',mdtxt,re.M)
idx=iter(range(1,500))
def heading(m):
    n=next(idx)
    return f'<h2 id="chapter-{n:02d}">{m.group(1)}</h2>'
content=re.sub(r'<h2>(.*?)</h2>',heading,content)
# Retain first source h1 only in PDF, avoid duplicate in web landing.
content=re.sub(r'^<h1>.*?</h1>\n?', '', content,count=1,flags=re.S)
# Make markdown tables overflow safely in mobile reader.
content=re.sub(r'(<table>.*?</table>)',lambda m:'<div class="table-scroller">'+m.group(1)+'</div>',content,flags=re.S)

s=lambda v:html.escape(v,quote=True)
toc=''.join(f'<a href="#chapter-{i:02d}">{s(h)}</a>' for i,h in enumerate(headings,1))
checkhtml=''.join(f'<label class="check-item"><input type="checkbox" data-check value="item-{i}"><span>{s(c)}</span></label>' for i,c in enumerate(CONFIG['checks'],1))
filterbuttons=''.join(f'<button type="button" data-filter="{id}" aria-pressed="{str(i==0).lower()}">{label}</button>' for i,(id,label) in enumerate([('all','全部'),('research','证据'),('practice','实操'),('template','模板')]))
resourcecards=''.join(f'<div class="resource-card" data-category="{group}"><h3>{s(title)}</h3><p>{s(desc)}</p><a href="{url}"'+(' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else '')+'>打开资源 ↗</a></div>' for title,group,url,desc in CONFIG['resources'])
url=f'https://andyawake.github.io/{NAME}/'
# Main journey is always migration first, then alternatives, then portable skills.
journey=[
 ('Out-Anthropic','01','先备份迁出','对话、Projects、Code、文件、恢复验证'),
 ('Free-Anthropic','02','再找可用平替','按工作任务与真实验收匹配工具'),
 ('Anti-Anthropic','03','把优秀方法留下','Skills、MCP、Agent、公开证据与独立性')]
def make_journey_card(name,num,label,desc):
 current = ' current' if name==NAME else ''
 current_attr = ' aria-current="step"' if name==NAME else ''
 return f'<a class="journey-card{current}" href="https://andyawake.github.io/{name}/"{current_attr}><span class="journey-n">{num}</span><strong>{label}</strong><small>{desc}</small><span class="journey-arrow">↗</span></a>'
journey_html=''.join(make_journey_card(*item) for item in journey)
primary={'Anti-Anthropic':('学习可移植方法','PORTABLE-CLAUDE.md'),'Out-Anthropic':('开始生成迁移路线','#route-planner'),'Free-Anthropic':('按任务找平替','#tool-finder')}[NAME]
second={'Anti-Anthropic':('进入迁移教程','https://andyawake.github.io/Out-Anthropic/'),'Out-Anthropic':('查看平替工具','https://andyawake.github.io/Free-Anthropic/'),'Free-Anthropic':('下载完整手册','assets/guide.pdf')}[NAME]
helper_widget=''
if NAME=='Out-Anthropic':
 helper_widget='''<section class="route-box" id="route-planner" aria-labelledby="planner-heading"><div class="route-head"><div><p class="overline">START HERE / CHOOSE YOUR PATH</p><h2 id="planner-heading">我的 Claude 资料，怎么搬？</h2><p>选择你的来源和目标工具，生成一份可下载的迁移计划。<strong>全部在浏览器本地处理，不会读取或上传私人资料。</strong></p></div><span class="route-tag">无需登录</span></div><div class="route-form"><label for="migration-source">你现在主要使用什么？<select id="migration-source"><option value="web">Claude 聊天 / 网页版</option><option value="projects">Claude Projects / 记忆</option><option value="code">Claude Code / Agent</option><option value="api">Claude API / 自动化</option></select></label><label for="migration-target">准备迁往哪里？<select id="migration-target"><option value="codex">Codex / 代码 Agent</option><option value="workbuddy">WorkBuddy / 国内工作台</option><option value="chatgpt">ChatGPT / 普通聊天</option><option value="gemini">Gemini / Gemini CLI</option><option value="domestic">Kimi / 豆包等国内助手</option><option value="selfhost">本地模型 / 自托管工具</option></select></label></div><div class="route-actions"><button class="button button-primary" id="generate-plan" type="button">生成我的迁移步骤</button><button class="button button-light" id="download-plan" type="button" disabled>下载 Markdown 计划</button></div><div class="route-result" id="migration-result" aria-live="polite" hidden><h3>你的迁移执行卡</h3><pre id="plan-output"></pre></div><p class="route-privacy">官方导出需你自己在 Claude 中完成。此生成器不接收账号、文件或 API Key，也不是聊天数据自动转换器。</p></section>'''
elif NAME=='Free-Anthropic':
 helper_widget='''<section class="route-box" id="tool-finder" aria-labelledby="finder-heading"><div class="route-head"><div><p class="overline">TASK FIRST / ZERO HYPE</p><h2 id="finder-heading">你现在用 Claude 做什么？</h2><p>按任务筛出值得先试的一条路线。没有绝对排名，实际能力、费用和账号地区要在工具里核验。</p></div><span class="route-tag">1 分钟筛选</span></div><div class="route-form"><label for="tool-task">选择任务类型<select id="tool-task"><option value="writing">日常聊天 / 写作</option><option value="knowledge">Projects / 资料整理</option><option value="coding">Claude Code / 网站与代码</option><option value="automation">Agent / MCP / 自动化</option><option value="docs">PDF / 表格 / 办公文件</option><option value="private">离线 / 私有数据</option></select></label><label for="tool-priority">你最看重什么？<select id="tool-priority"><option value="easy">立即可开始、学习成本低</option><option value="portable">源码和文件可带走</option><option value="private">权限、数据可控</option><option value="cost">总成本可量化</option></select></label></div><div class="route-actions"><button class="button button-primary" id="suggest-tool" type="button">查看我的候选路线</button><a class="button button-light" href="ALTERNATIVE-MATRIX.md">对照完整矩阵 ↗</a></div><div class="route-result" id="suggestion-result" aria-live="polite" hidden><h3 id="suggestion-title"></h3><p id="suggestion-body"></p><p id="suggestion-caveat" class="caveat"></p><a href="templates/WORKFLOW-CARD.md">下载同题验收模板 ↗</a></div></section>'''
else:
 helper_widget='''<section class="route-box method-intro" id="methods" aria-labelledby="method-heading"><p class="overline">WHAT TO KEEP / NOT WHAT TO BUY</p><h2 id="method-heading">Claude 值得学习的，是这四类可携带能力。</h2><div class="method-grid"><div><span>01</span><strong>上下文工程</strong><p>项目目标、约束和记忆写进自有文件。</p></div><div><span>02</span><strong>Skills 与 Agent</strong><p>沉淀可复用技能和角色交接，不依赖聊天窗口。</p></div><div><span>03</span><strong>MCP 与自动化</strong><p>权限最小化、服务可替换、凭据不公开。</p></div><div><span>04</span><strong>测试与恢复</strong><p>用真实文件、测试和人工审核证明效果。</p></div></div><a href="PORTABLE-CLAUDE.md">阅读可移植能力手册 ↗</a><span class="method-sep">/</span><a href="RESOURCE-ATLAS.md">查看学习资料地图 ↗</a></section>'''

side=(''.join(f'<a href="https://andyawake.github.io/{slug}/">{slug} ↗</a>' for slug in CONFIG['adjacent']))
jsonld=json.dumps({'@context':'https://schema.org','@type':'TechArticle','headline':re.sub('<.*?>','',CONFIG['title']),'inLanguage':'zh-CN','dateModified':'2026-11-14','author':{'@type':'Person','name':'AI 酋长 Andy'},'publisher':{'@type':'Organization','name':'星觉科技','url':'https://www.a6no1.cn/'},'mainEntityOfPage':url},ensure_ascii=False)
PAGE=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="theme-color" content="#ffffff"><title>{s(NAME)} · {s(re.sub('<.*?>','',CONFIG['title']))} | AndyAwake</title><meta name="description" content="{s(CONFIG['deck'])}"><meta name="author" content="AI 酋长 Andy / 星觉科技"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{s(NAME)} | AndyAwake"><meta property="og:description" content="{s(CONFIG['deck'])}"><meta property="og:url" content="{url}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script type="application/ld+json">{jsonld}</script></head>
<body data-project="{NAME}"><a class="skip-link" href="#main-content">跳转正文</a><header class="topbar"><div class="shell topbar-inner"><a class="brand" href="https://github.com/AndyAwake"><span class="brand-logo" aria-hidden="true">AW</span>ANDYAWAKE<span class="brand-sub">/ 星觉科技</span></a><button class="mobile-menu" id="menu-button" aria-expanded="false" aria-controls="top-nav">菜单 ☰</button><nav class="topnav" id="top-nav" aria-label="主导航"><a href="https://andyawake.github.io/Out-Anthropic/" {'aria-current="page"' if NAME=='Out-Anthropic' else ''}>01 · 迁出 Claude</a><a href="https://andyawake.github.io/Free-Anthropic/" {'aria-current="page"' if NAME=='Free-Anthropic' else ''}>02 · 找可用平替</a><a href="https://andyawake.github.io/Anti-Anthropic/" {'aria-current="page"' if NAME=='Anti-Anthropic' else ''}>03 · 学优秀方法</a><a href="https://github.com/AndyAwake/{NAME}">源码 ↗</a></nav></div></header>
<section class="hero" id="start"><div class="shell hero-grid"><div><span class="overline">FIELD GUIDE {CONFIG['index']} / {s(CONFIG['theme'])}</span><h1>{CONFIG['title']}</h1><p class="deck">{s(CONFIG['deck'])}</p><div class="actionset"><a class="button button-primary" href="{primary[1]}">{primary[0]} ↘</a><a class="button button-light" href="{second[1]}">{second[0]} ↗</a><a class="button button-light" href="assets/guide.pdf" download>PDF 全文 ↓</a></div></div><div class="hero-aside"><div class="big-number">{len(headings):02d}</div><p>全文章节 / DEEP DIVE</p><hr><div class="aside-meta"><div><b>资料类型</b>　开源知识手册</div><div><b>核查日期</b>　2026.11.14</div><div><b>版本</b>　4.0 · 用户优先</div><div><b>读者</b>　普通用户 / 团队 / 创业者</div></div></div></div></section>
<div class="note-strip"><div class="shell"><b>编辑原则 / EDITORIAL RULE</b><span>{s(CONFIG['note'])}</span></div></div>
<div class="shell journey-wrap" aria-label="三步阅读路线"><p class="journey-overline">YOUR ROUTE / 从 Claude 出发，最终把能力留在自己手里</p><div class="journey-grid">{journey_html}</div></div><div class="tabline"><div class="shell"><a href="#main-content">章节正文</a><a href="#quickcheck">快速自查</a><a href="#resources">文档与模板</a><a href="#about-author">关于作者</a><a href="assets/guide.pdf">PDF 全文 ↓</a></div></div>
<div class="shell layout" id="main-content"><aside class="toc" aria-label="章节目录"><p>CHAPTERS / 内容索引</p>{toc}</aside>
<div class="bodycolumn">{helper_widget}<div class="mobile-toc"><details><summary>打开 {len(headings)} 章阅读目录 ↓</summary>{toc}</details></div><div class="ux-widget" id="quickcheck"><p class="overline">YOUR WORK / LIVE CHECKLIST</p><h2>{s(CONFIG['widget_title'])}</h2><p>{s(CONFIG['widget_note'])}</p><div class="progress-label" id="progress-value" aria-live="polite">0 / {len(CONFIG['checks'])} 项</div><div class="progress-rail" aria-hidden="true"><div class="progress-fill" id="progress-fill"></div></div><div class="check-items">{checkhtml}</div><div style="margin-top:13px"><button class="subtle-btn" id="reset-checks">重置清单</button></div></div><article class="article" aria-label="手册全文">{content}</article><section class="ux-widget" id="resources"><p class="overline">DOWNLOADS / ACTIONABLE FILES</p><h2>文档与可编辑模板</h2><p>所有手册和模板都可直接获取，无需留手机号或加微信。</p><div class="category-pills" aria-label="筛选资源">{filterbuttons}</div>{resourcecards}</section></div>
<aside class="inline-tools"><div class="right-block"><h3>OPEN EDITION</h3><p>本版完整内容以 HTML 和可编辑 Markdown 发布，并提供全文 PDF。</p><a href="assets/guide.pdf">↓ 完整 PDF</a><a href="HANDBOOK.md">↗ Markdown</a></div><div class="right-block"><h3>FIND A CHAPTER</h3><p>先看快速自查，再按目录查原始来源和真实动作。</p><button class="copy-link" data-copy="{url}">复制本页链接</button></div><div class="right-block"><h3>RELATED GUIDES</h3>{side}</div></aside></div>
<section class="shell brand-block" id="about-author"><div><span class="chapter-kicker">BY ANDYAWAKE / FROM PRACTICE</span><h2>方法公开，<br>真正的价值在于交付。</h2><p>作者长期从事 B 端 AI 产品、内容与开源实践。把学习资料整理成可执行的迁移方案、Skills、工具选择矩阵与真实工作流；客户与私密资料不会进入公开仓库。开源教程可以独立使用，商务联系只是可选入口。</p></div><div class="brand-meta"><div class="row"><span>公司 · 星觉科技</span><a href="https://www.a6no1.cn/">www.a6no1.cn ↗</a></div><div class="row"><span>作者 · AI 酋长 Andy</span><a href="https://metaver.vip/">metaver.vip ↗</a></div><div class="row"><span>商务微信</span><div><b>AIPMAndy</b>　<button data-copy="AIPMAndy">复制</button></div></div><p style="color:#8d918c;font-size:11px;line-height:1.9">开源内容无需付费。咨询服务可选，需求、价格和交付范围另行约定。</p></div></section>
<footer class="foot"><div class="shell"><span>© 2026 AndyAwake · V4.0 · 2026-11-14 · 资料可带走，方法可复用</span><div class="footer-cross"><a href="https://www.a6no1.cn/">公司官网</a><a href="https://metaver.vip/">个人官网</a><a href="https://github.com/AndyAwake/{NAME}">源码</a></div></div></footer><script defer src="assets/app.js"></script></body></html>'''
(ROOT/'index.html').write_text(PAGE,encoding='utf8')

# Print-book is not a short marketing brochure: same complete manuscript as HTML.
tocrows=''.join(f'<div class="toc-line"><span>{s(h)}</span><span>{i:02d}</span></div>' for i,h in enumerate(headings,1))
printcss='''
@page{size:A4;margin:21mm 18mm 21mm 18mm;@top-left{content:"ANDYAWAKE · OPEN FIELD GUIDE";font-family:"Noto Sans CJK SC";font-size:8px;color:#a0a3a0;letter-spacing:.11em}@top-right{content:"2026 / 11 / 14";font-family:"Noto Sans CJK SC";font-size:8px;color:#a0a3a0}@bottom-left{content:"ANDYAWAKE · 开源迁移与工作流手册";font-family:"Noto Sans CJK SC";font-size:8px;color:#888d89}@bottom-right{content:counter(page);font-family:"Noto Sans CJK SC";font-size:9px;color:#777}}
@page:first{@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}html{font-family:"Noto Sans CJK SC",sans-serif;color:#161918;background:#fff}body{margin:0;font-size:10.5pt;line-height:1.85}a{color:#225674;text-decoration:none}p,li{orphans:3;widows:3}p{margin:0 0 9pt;color:#363c3a}strong{font-weight:700;color:#161817}.cover{height:250mm;position:relative;page-break-after:always}.cover-top{border-top:1.5px solid #222;padding-top:12mm;font-size:9pt;letter-spacing:.13em;color:#666}.cover-num{font-family:serif;font-size:118pt;color:#e4e5e2;position:absolute;top:44mm;right:0;line-height:1}.cover-title{position:absolute;top:75mm;left:0;right:0;font-family:"Noto Serif CJK SC",serif;font-size:29pt;letter-spacing:-.06em;line-height:1.42;font-weight:650}.cover-sub{position:absolute;top:132mm;left:0;right:0;color:#5f6663;font-size:12pt;max-width:140mm;line-height:2}.cover-bottom{position:absolute;bottom:21mm;left:0;right:0;border-top:1px solid #d5d7d2;padding-top:8mm;display:flex;justify-content:space-between;color:#616965;font-size:9pt}.small{font-size:9pt;color:#747974}.chapter-toc{page-break-after:always}.chapter-toc h1{font-family:"Noto Serif CJK SC",serif;font-size:23pt;margin:12mm 0 6mm}.toc-line{display:flex;justify-content:space-between;gap:10mm;border-bottom:1px solid #e3e5e1;font-size:10pt;padding:2.6mm 0}.toc-line span:last-child{font-family:Georgia,serif;color:#9b9f99}.toc-intro{color:#646b68;font-size:9pt;line-height:1.8;margin:5mm 0 11mm}.pdf-content h2{font-family:"Noto Serif CJK SC",serif;color:#111;letter-spacing:-.03em;font-size:17pt;line-height:1.38;font-weight:660;border-top:1px solid #d5d8d3;padding-top:8mm;margin:13mm 0 5mm;break-after:avoid}.pdf-content h2:first-child{margin-top:0}.pdf-content h3{font-size:12.5pt;margin:6mm 0 3mm;break-after:avoid}.pdf-content p,.pdf-content li{font-size:10pt;line-height:1.9}.pdf-content ul,.pdf-content ol{padding-left:7mm;margin:3mm 0 6mm}.pdf-content li{margin:1.4mm 0}.pdf-content blockquote{border-left:2px solid #b8bcb5;background:#f8f9f7;padding:3mm 4mm;margin:5mm 0}.pdf-content blockquote p{color:#5c625d;font-size:9pt;margin:0}.pdf-content pre{font-family:"Noto Sans Mono CJK SC",monospace;font-size:8pt;line-height:1.58;white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f7f5;border:1px solid #e0e3df;padding:4mm;margin:4mm 0 7mm}code{font-family:"Noto Sans Mono CJK SC",monospace;font-size:8.5pt;overflow-wrap:anywhere}.pdf-content table{width:100%;border-collapse:collapse;margin:4mm 0 7mm;font-size:8pt;table-layout:fixed}.pdf-content th{background:#f4f5f2;border-top:1px solid #d7dad6;color:#343a37;text-align:left;padding:2.2mm 1.5mm;overflow-wrap:anywhere}.pdf-content td{border-bottom:1px solid #e4e6e3;padding:2mm 1.5mm;vertical-align:top;overflow-wrap:anywhere}.table-scroller{max-width:100%}.table-scroller table{break-inside:auto}.table-scroller tr{break-inside:avoid}.last-note{margin-top:9mm;padding:5mm 0;border-top:1px solid #ddd;font-size:9pt;color:#696f6b}
'''
if NAME=='Anti-Anthropic':
    # Keep the source index from spilling alone onto an otherwise empty 11th page.
    printcss += '.pdf-content p,.pdf-content li{line-height:1.78;font-size:9.7pt}.pdf-content h2{margin:10mm 0 4.5mm;padding-top:7mm}.pdf-content ol,.pdf-content ul{margin-bottom:4mm}'
cover_title=re.sub('<br>',' ',re.sub('<.*?>','',CONFIG['title']))
# For PDF retain whole text with full content; the initial blockquote in text carries editorial note.
PDFHTML=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{printcss}</style></head><body><section class="cover"><div class="cover-top">ANDYAWAKE　/　{CONFIG['theme']}</div><div class="cover-num">{CONFIG['index']}</div><div class="cover-title">{s(cover_title)}<p style="font-family:'Noto Sans CJK SC';font-size:11pt;font-weight:400;letter-spacing:0;color:#919894;margin-top:7mm">{NAME} · 全文可打印编辑版</p></div><div class="cover-sub">{s(CONFIG['deck'])}</div><div class="cover-bottom"><span>AI 酋长 Andy / 星觉科技<br>公开研究 · 方法 · 模板</span><span>2026.11.14 · V4.0<br>公司：www.a6no1.cn · 微信 AIPMAndy</span></div></section><section class="chapter-toc"><p class="overline">CONTENTS</p><h1>阅读目录</h1><p class="toc-intro">这份 PDF 收录网站的完整章节，不是缩写版导读。查阅动态规则和价格，请以原始来源与最新官方公告为准。所有示例均区分真实个人经验、教学演示和未验证结果。</p>{tocrows}<div class="last-note">开源：github.com/AndyAwake/{NAME}<br>公司：www.a6no1.cn · 作者：metaver.vip · 微信：AIPMAndy</div></section><main class="pdf-content">{content}</main></body></html>'''
(ROOT/'assets').mkdir(exist_ok=True)
(ROOT/'assets/guide-print.html').write_text(PDFHTML,encoding='utf8')
try:
    from weasyprint import HTML
    HTML(string=PDFHTML,base_url=str(ROOT)).write_pdf(str(ROOT/'assets/guide.pdf'))
    print(NAME, 'PDF done')
except ImportError:
    print(NAME, 'HTML done (pip install weasyprint to rebuild PDF)')
print(NAME,'chapters',len(headings),'HTML',len(PAGE),'manuscript',len(mdtxt))
