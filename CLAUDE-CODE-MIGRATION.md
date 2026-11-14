# Claude Code 专项迁移：项目、规则、Skills、MCP 与会话

> 适用：正在用 Claude Code（终端 / IDE / 本地桌面）的人，想迁到 Codex、Gemini CLI、WorkBuddy 或其他合法可用的执行环境。
> 本文是手工操作与验收手册，不提供偷取令牌、绕过地区限制或跨服务注入私人资料的方法。2026-11-14 核对官方文档；版本升级时复查。

## 先说结论：源码最容易搬，执行环境最容易漏

成功标准不是新工具「看上去还记得我」，而是它拿到同一份源码和任务卡后，能在明确权限、可控费用和相同验收条件下完成工作。

| Claude Code 内的资产 | 迁移操作 | 风险与验收 |
| --- | --- | --- |
| Git 仓库、未提交改动 | `git status` 审核；私有仓库或受控磁盘备份 | 确认未提交改动、分支、子模块和 LFS 都没有遗漏 |
| `CLAUDE.md` 与说明文件 | 先整理成无供应商依赖的 `PORTABLE-PROJECT.md`；再按目标写 `AGENTS.md` / `GEMINI.md` | 规则层级、加载时机和权限不同，不能简单改文件名就假设生效 |
| `.claude/skills/` 等技能文件 | 检查授权与 `SKILL.md`；复制可公开/自有技能；逐一运行测试 | 工具调用、路径和脚本运行环境可能不同 |
| `.claude/settings.json` 与 Hooks | 提取**行为需求**和检查逻辑，按新工具配置重写 | Claude 专用事件、权限表达式不能保证一对一迁移 |
| MCP 服务连接 | 记录服务名称、用途、scope、环境变量名称；在新客户端重新接入 | 不复制访问令牌；重做最小权限授权和读写测试 |
| 会话与已讨论的决策 | 在交互式 Claude Code 用 `/export` 导出当前会话；另写人工审核过的项目交接卡 | 聊天不是完整源码，也不保证新工具支持导入 |
| 定时任务、远端部署、云凭据 | 逐项检查触发器、负责人、部署配置、接入权限 | 新旧任务同时运行可能重复发信、扣费或写入 |

## 第 0 步：先给项目打一个可恢复的快照

仅在**你有权限**的项目根目录执行以下只读命令：

```bash
git status --short
git branch --show-current
git log -1 --format='%h %cs %s'
git remote -v
```

把输出记录在私有 `migration-notes.md`。`git remote -v` 可能显示带令牌的 URL，分享前务必删掉敏感部分。检查是否还有未提交改动、子模块、Git LFS、`.gitignore` 排除但业务实际依赖的文件。

备份时分开三层：**可公开源码**、**受保护业务文件**、**密钥与凭据**。不要把三个目录一股脑推送到公开 GitHub；`.env`、OAuth Token、API Key、Cookies 等只在安全渠道重新配置。

## 第 1 步：将项目指令从工具专用文件抽离

推荐一个中立层：`PORTABLE-PROJECT.md`，先写清项目目标、架构、边界、命令、验收、失败处理和来源。然后按目标工具准备轻量适配：

- Claude Code：保留 `CLAUDE.md`，引用中立层。
- Codex：使用 `AGENTS.md`（或当前版本官方支持的约定）；使用前确认工具读取了文件。
- Gemini CLI：使用 `GEMINI.md`，可以引用项目内的独立说明文件。
- WorkBuddy：在工作目录/任务说明中指定该中立层，并核对模型及工具权限；不要假设它自动按 Claude 文件名加载。

本仓库提供 [通用项目说明模板](templates/PORTABLE-PROJECT.md)、[Codex 适配参考](templates/AGENTS.md)、[Gemini CLI 适配参考](templates/GEMINI.md)。它们是示例，不代表跨产品执行行为完全一致。

## 第 2 步：Skills / Agents / MCP 不是「整个目录复制完就能工作」

**Skills**：先确认输入、输出、依赖工具和资源文件。将可合法复用的 `SKILL.md` 放入目标工具官方支持的位置，检查它是否真的加载，并只用公开或自有样例测试。

**Subagents / Agent Teams**：将角色定义为「研究、执行、审查」和明确的交接格式，而不是复制一段隐形思考过程。新工作台若没有同名子代理功能，可先用三份任务卡串行实现。

**MCP**：MCP 是协议层，但每个客户端的权限、确认弹窗、配置格式可能不同。先跑只读查询，再测试任何需要写入的动作；记下服务版本和 OAuth 权限，绝不公开密钥。

**Hooks**：先明确触发时机、退出条件、失败处理，再用新工具支持的机制实现。没有对应机制时用 `npm test` / `pytest` 或人工门禁替代，不因“能导入 JSON”就标记迁移成功。

## 第 3 步：先迁一个真的能跑的任务

从最小且可审计的任务开始。例如：

1. Claude Code 的既有 Git 仓库里有一个「移动端按钮偏小」的问题。
2. 在迁移目标中打开**同一份源码**，给它一张独立任务卡：只修改目标组件、不新增付费依赖、列出文件变更、运行测试并提供截图。
3. 核查版本、路由、启动命令、截图、差异、测试结果，以及是否超出允许修改范围。
4. 记录迁移差异：工具找不到文件、MCP 权限缺失、脚本依赖不兼容、Hook 未执行、模型不支持工具调用。
5. 只有在这些项通过后，才把此任务标为「迁移验证通过」。

## 第 4 步：不要丢的证据

```
project-portable/
  README.md                      # 原项目的启动/使用说明
  PORTABLE-PROJECT.md            # 中立规则、架构与验收
  AGENTS.md                      # Codex 适配（如使用）
  GEMINI.md                      # Gemini CLI 适配（如使用）
  skills/                        # 仅收录有授权的可迁移技能
  evidence/restore-report.md     # 迁移回放与失败记录
  .gitignore                     # 不提交凭据/私有记录
```

### 官方参考

- [Claude Code：设置文件及优先级](https://code.claude.com/docs/en/settings)
- [Claude Code：交互命令 `/export`](https://code.claude.com/docs/zh-CN/commands)
- [OpenAI：Codex AGENTS.md 工程实践](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)
- [Gemini CLI：GEMINI.md 上下文文件](https://geminicli.com/docs/cli/gemini-md/)
- [WorkBuddy：模型配置与后端切换](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Model)

**备注：** Claude Code 使用许可和平台支持条件以官方当日规则为准。迁移指的是合法持有的数据、自己创建的工作流程及具备重用权限的材料，不包括复制模型权重或提取未授权的系统提示词。
