(()=>{'use strict';
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>Array.from(r.querySelectorAll(s));
const menu=$('#menu-button'),nav=$('#top-nav');if(menu&&nav){menu.addEventListener('click',()=>{const open=nav.classList.toggle('is-open');menu.setAttribute('aria-expanded',String(open))});$$('a',nav).forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('is-open');menu.setAttribute('aria-expanded','false')}))}
$$('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const val=b.getAttribute('data-copy');let ok=false;try{await navigator.clipboard.writeText(val);ok=true}catch(e){try{const t=document.createElement('textarea');t.value=val;t.style.position='fixed';t.style.top='-1000px';document.body.append(t);t.select();ok=document.execCommand('copy');t.remove()}catch(err){}}const old=b.dataset.oldLabel||b.textContent;b.dataset.oldLabel=old;b.textContent=ok?'已复制 ✓':'手动复制: '+val;window.setTimeout(()=>b.textContent=old,2000)}));
const checks=$$('input[data-check]');if(checks.length){const key='andyawake-guide-'+($('body').dataset.project||'guide')+'-v3';let saved=[];try{saved=JSON.parse(localStorage.getItem(key)||'[]');if(!Array.isArray(saved))saved=[]}catch(e){}checks.forEach(c=>c.checked=saved.includes(c.value));const update=()=>{const count=checks.filter(c=>c.checked).length;const v=$('#progress-value'),bar=$('#progress-fill');if(v)v.textContent=count+' / '+checks.length+' 项';if(bar)bar.style.width=(count/checks.length*100)+'%';try{localStorage.setItem(key,JSON.stringify(checks.filter(c=>c.checked).map(c=>c.value)))}catch(e){}};checks.forEach(c=>c.addEventListener('change',update));update();const reset=$('#reset-checks');if(reset)reset.addEventListener('click',()=>{checks.forEach(c=>c.checked=false);update()})}
const buttons=$$('[data-filter]');if(buttons.length){const cards=$$('[data-category]');buttons.forEach(b=>b.addEventListener('click',()=>{const cat=b.dataset.filter;buttons.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));cards.forEach(c=>{c.hidden=cat!=='all'&&c.dataset.category!==cat})}))}
const anchors=$$('.toc a[href^="#"]');if(anchors.length&&'IntersectionObserver'in window){const sections=anchors.map(a=>$(a.getAttribute('href'))).filter(Boolean);const obs=new IntersectionObserver(es=>{es.filter(e=>e.isIntersecting).forEach(e=>{anchors.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+e.target.id))})},{rootMargin:'-100px 0px -70% 0px'});sections.forEach(el=>obs.observe(el))}
})();

// Interactive helpers work entirely on-device. No fetch/XHR, account access, or uploaded files.
(() => {
  'use strict';
  const source = document.getElementById('migration-source');
  const target = document.getElementById('migration-target');
  const generate = document.getElementById('generate-plan');
  const download = document.getElementById('download-plan');
  const result = document.getElementById('migration-result');
  const out = document.getElementById('plan-output');
  let latestPlan = '';
  const sourceNames = {
    web: 'Claude 聊天 / 网页端',
    projects: 'Claude Projects / 记忆',
    code: 'Claude Code / Agent',
    api: 'Claude API / 自动化'
  };
  const sourceDetails = {
    web: [
      '在 Claude 网页或桌面端 Settings → Privacy 中申请 Export data；手机 App 不能直接发起',
      '保存官方 ZIP 原件并标记下载时间，确认压缩包能解压；导出链接可能过期',
      '找回自己上传的原始图片、PDF 和 Word；官方聊天导出不包含原上传附件',
      '选一段真正影响工作的聊天，整理目标、来源、决策与成品为独立文件'
    ],
    projects: [
      '按项目列出名称、Projects instructions、知识文件和你仍有权保留的附件',
      '按官方可见的 Memory 入口导出或复制记忆，并删去不必要的隐私资料',
      '为每个 P0 项目保存 PROJECT-HANDOFF.md，说明进度、原料、约束和验收',
      '留存可编辑原稿、最终成品和版本；不期待新服务自动读懂整个项目历史'
    ],
    code: [
      '在自己的仓库运行 git status --short，查未提交代码、分支、依赖、子模块',
      '保存 CLAUDE.md、项目说明、自有 Skills、MCP 服务名称与权限、Hooks 行为定义',
      '在 Claude Code 交互会话使用 /export 保存需要的会话；不要把令牌或认证文件推到公开仓库',
      '生成 PORTABLE-PROJECT.md 中立项目上下文，为目标 Agent 建立适配规则',
      '完成一次真实源码修改和测试，核验文件 diff、运行与新工具权限'
    ],
    api: [
      '备份自己拥有的应用源码、API 合约、模型标识与调用位置',
      '记录合法可复用的提示词、输入输出 JSON 样例、重试策略和故障处理',
      '另行安全管理凭据；不要把 API Key 或客户请求记录放入公开仓库',
      '用脱敏公开样例测试替代 API 的工具调用、输出格式、实际计费和限流',
      '设置灰度和回滚条件，检查原自动化是否仍在运行以免重复执行'
    ]
  };
  const targetDetails = {
    codex: '目标 Codex：准备 AGENTS.md / 项目规则，并在允许的环境里读取同一 Git 仓库；只按文件 diff、测试和实物交付判定。',
    workbuddy: '目标 WorkBuddy：指定单独的任务文件夹、核对模型选择及实际后端，明确本地文件与写入权限；在结果区检查导出的真实文件。',
    chatgpt: '目标 ChatGPT：以人工审核后的项目交接卡、资料及本次任务开始；不要假设 Claude 官方导出 ZIP 能完整自动导入。',
    gemini: '目标 Gemini：若用 Gemini CLI，维护 GEMINI.md 并用 /memory show 核查实际加载；网页版需要按当前实际支持的入口分别操作。',
    domestic: '目标 Kimi / 豆包：用项目交接卡和有权使用的原料从一个小任务开始；先确认当地账号、文件功能与费用。',
    selfhost: '目标本地/自托管：先核对硬件、模型许可证、数据路径、工具权限和日志；本地执行不等于天然零成本或绝对安全。'
  };
  const enumItems = lines => lines.map((x,i)=>`${i+1}. ${x}`).join('\n');
  if (source && target && generate && download && result && out) {
    const build = () => {
      const s=source.value, t=target.value;
      latestPlan = [
        '# 我的 Claude 迁移执行计划',
        '',
        `- 来源：${sourceNames[s]}`,
        `- 目标：${target.options[target.selectedIndex].text}`,
        `- 计划生成：${new Date().toLocaleDateString('zh-CN')}`,
        '- 状态：待人工执行 / 待恢复验收',
        '',
        '## A. 优先保住自己的资料',
        enumItems(sourceDetails[s]),
        '',
        '## B. 迁入目标工具',
        targetDetails[t],
        '',
        '## C. 一项真实任务的验收',
        '- [ ] 原料只来自自己有权使用的文件，敏感信息已脱敏',
        '- [ ] 原压缩包/源码/可编辑成品均能独立打开',
        '- [ ] 在目标工具完成相同的 P0 任务',
        '- [ ] 核对关键事实、文件格式、运行结果和权限',
        '- [ ] 记录实际工具模型、费用、返工和失败缺口',
        '',
        '## D. 安全与边界',
        '- 不把 API Key、Cookie、私有客户资料提交到公开仓库。',
        '- 聊天导出不等于附件、Projects、Skills、MCP 和账号权限已完整迁移。',
        '- 原平台与新平台导入/导出能力不同；没有逐项复核的部分标记「未验证」。',
        '',
        '继续阅读：https://github.com/AndyAwake/Out-Anthropic',
        '专项迁移：https://github.com/AndyAwake/Out-Anthropic/blob/main/CLAUDE-CODE-MIGRATION.md',
        '按任务选工具：https://github.com/AndyAwake/Free-Anthropic',
      ].join('\n');
      out.textContent=latestPlan;
      result.hidden=false;
      download.disabled=false;
    };
    generate.addEventListener('click',build);
    [source,target].forEach(el=>el.addEventListener('change',()=>{result.hidden=true;download.disabled=true;}));
    download.addEventListener('click',()=>{
      if (!latestPlan || download.disabled) return;
      const file=new Blob([latestPlan],{type:'text/markdown;charset=utf-8'});
      const url=URL.createObjectURL(file), a=document.createElement('a');
      a.href=url; a.download='Claude-迁移执行计划.md'; a.style.display='none';
      document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
  }
  const task=document.getElementById('tool-task');
  const priority=document.getElementById('tool-priority');
  const suggest=document.getElementById('suggest-tool');
  const suggestion=document.getElementById('suggestion-result');
  const suggestionTitle=document.getElementById('suggestion-title');
  const suggestionBody=document.getElementById('suggestion-body');
  const suggestionCaveat=document.getElementById('suggestion-caveat');
  const rules={
    writing:['写作与日常对话：从已有可用账户试起','先尝试当前地区可用的 Kimi / 豆包等助手；在官方支持条件下也可以用 ChatGPT / Gemini 同题试做。留下一篇带来源的 Markdown。','核对原文事实、品牌语气和是否能带走可编辑文本。'],
    knowledge:['Projects / 知识库：先迁项目交接卡','先做一份人工清理过的项目说明、来源索引和附件清单，再选支持该文件类型的 Kimi / WorkBuddy 或其他合法可用工具。','部分工具的 Projects、记忆、权限规则并不兼容；不能把「上传成功」当成「工作恢复」。'],
    coding:['Claude Code：以源码和工程任务为中心','Codex、WorkBuddy 或经验证的编程工作台都可作为首轮候选；保留 Git 仓库、可移植上下文、Skills 清单，用一次小功能/回归测试比较。','CLAUDE.md、Hooks、MCP、认证与订阅不保证直接互通；请看专项迁移教程。'],
    automation:['Agent / MCP / 自动化：先审查权限','优先考虑能显示实际模型、操作日志和写入授权的工作台或自管 Agent 流程；WorkBuddy 官方说明支持 MCP、Skills 和模型选择。','写操作必须授权；检查新旧任务是否重复触发，不以「模型答复成功」替代运行验收。'],
    docs:['文档、表格：验收可编辑文件','用支持本地文件的 Kimi / WorkBuddy 或当前账号已拥有的办公工具做一份公开示例；保留 Word/Markdown/CSV/XLSX 原稿。','数值、公式、来源和文件实际打开情况比一次生成的外观更重要。'],
    private:['私有/离线需求：先明确数据边界','先调查组织合规要求；在硬件、许可证和能力满足时试本地模型，或选择获批准的企业工作台。','本地运行也有硬件、电力、维护、更新与泄露风险；无任何方案可无条件保证安全。']
  };
  const risks={
    easy:'优先确保能登录、能输入、能输出。最简单的方案不一定具备自动化和批量接口。',
    portable:'把原料、规则、源码、模板和最终文件存在自己控制的位置，最好另做恢复演练。',
    private:'特别核查实际模型服务方、授权范围、日志与数据保留条款，不把客户端品牌当成数据流向证明。',
    cost:'用三次同类任务记录订阅摊销、API、人工改稿、托管与重复执行成本，未知项写「待测」。'
  };
  if(task && priority && suggest && suggestion && suggestionTitle && suggestionBody && suggestionCaveat){
    suggest.addEventListener('click',()=>{
      const [title,detail,caveat]=rules[task.value];
      suggestionTitle.textContent=title;
      suggestionBody.textContent=detail;
      suggestionCaveat.textContent='关键边界：'+caveat+' '+risks[priority.value];
      suggestion.hidden=false;
    });
    [task,priority].forEach(el=>el.addEventListener('change',()=>{suggestion.hidden=true;}));
  }
})();
