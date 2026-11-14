# Out-Anthropic · GitHub Pages 部署与验收

本目录是可直接合并至 `https://github.com/AndyAwake/Out-Anthropic` 的独立静态网站升级包。当前部署结果以仓库 Actions 和实际网站为准。

## 合并规则

1. 将本目录的 `index.html`、`assets/`、`robots.txt`、`sitemap.xml` 以及对应的证据/网站说明 Markdown、`.nojekyll` 文件 上传到 **Out-Anthropic 仓库根目录**。保留仓库中现有 `README.md`、`GUIDE.md`、LICENSE 和其他原文件。
2. 在仓库 `Settings → Pages` 选择 `Deploy from a branch`、`main`、`/(root)` 并保存。若你已有自定义部署流程，请先检查而不是覆盖。
3. 等 GitHub Pages 构建完成，访问 `https://andyawake.github.io/Out-Anthropic/`。这是**预期地址**，在实际启用 Pages 前不能宣称生效。
4. 逐项验证手机端首屏、3 个导航入口、PDF 下载、公司官网、复制微信号和源码链接；Out 站另验证迁移计划生成、Markdown 下载、清单保存；Free 站另验证任务选择器和资源筛选。
5. 实际网站开放后，再提交 sitemap 至搜索站长工具；如果启用了定制域名，修正 canonical、OG 和 sitemap 地址。

## 视觉与 SEO

- 单页静态网站，无构建依赖；黑白编辑风；手机端适配；中文标题、描述、Open Graph、结构化数据、Sitemap。
- PDF 收录本次 `HANDBOOK.md` **完整正文**；专项迁移、平替矩阵、模板和资源索引仍以网站 / Markdown 文件为准。
- 外部模型政策与政治新闻时间敏感，修改 `EVIDENCE` 或工具推荐前务必重新核对发布日期与原始来源。
- 官网角色严格区分：公司官网 https://www.a6no1.cn/；个人官网 https://metaver.vip/；微信 AIPMAndy。

## 线上验收

启用 Pages 后，以实际 URL、PDF 和页面交互验证结果为准；单独上传文件不代表部署已完成。

## README 导流入口

网站上线并实际验收通过后，可把 `README-INSERT.md` 提供的导航片段手动合并进仓库现有 `README.md` 顶部；不要在未上线时称网站已可访问。
