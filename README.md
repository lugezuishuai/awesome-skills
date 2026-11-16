# Awesome Skills

个人维护的 Agent Skills 集合，覆盖 AI 资讯、文章排版、代码质量、开源趋势与文档处理。每个 skill 都包含独立的 `SKILL.md`，以及执行任务需要的脚本、参考资料或模板，可通过 [`skills` CLI](https://github.com/vercel-labs/skills) 安装到 Codex、Claude Code 等支持的智能体。

## Skills

| Skill | 用途 | 使用示例 |
| --- | --- | --- |
| [ai-pulse](skills/ai-pulse/SKILL.md) | 汇总 AI 产品、GitHub Trending、行业新闻、博客和播客，生成中文资讯简报。 | 帮我整理今天的 AI 资讯简报。 |
| [article-to-html](skills/article-to-html/SKILL.md) | 将 Markdown 或对话中的文章排版为单文件 HTML，支持内联 SVG 和可选交互。 | 把这篇文章做成论文风格的单页 HTML。 |
| [clean-code-principles](skills/clean-code-principles/SKILL.md) | 提供命名、函数拆分、条件简化、模块组织和重构指导，适用于多种语言。 | 按整洁代码原则重构这个模块，保持现有行为。 |
| [github-trending](skills/github-trending/SKILL.md) | 获取 GitHub Trending 仓库数据，提供页面解析和 GitHub Search API 备选方案。 | 获取今天 GitHub Trending 的前 10 个仓库。 |
| [pdf-watermark-remover](skills/pdf-watermark-remover/SKILL.md) | 移除有权修改的 PDF 中显式标记的水印，保留原文档并检查输出页面。 | 删除这份 PDF 的水印，保留正文、图片和排版。 |
| [resume-builder](skills/resume-builder/SKILL.md) | 用固定海军蓝模板生成中文技术简历，支持 HTML、DOCX、PDF。 | 根据这些经历生成一份中文技术简历 PDF。 |

## 安装

需要 Node.js 22.20+ 和 npm，并能访问 GitHub 与 npm registry。安装参数详见 [skills CLI 文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-add)。

### 交互选择

在目标项目目录中运行，按提示选择 skill 和智能体：

```bash
npx skills add lugezuishuai/awesome-skills
```

只查看可安装的 skills：

```bash
npx skills add lugezuishuai/awesome-skills --list
```

### 指定 skill 和智能体

例如，将 `article-to-html` 安装到当前项目的 Codex：

```bash
npx skills add lugezuishuai/awesome-skills --skill article-to-html --agent codex -y
```

`ai-pulse` 会调用 `github-trending`，请一起安装：

```bash
npx skills add lugezuishuai/awesome-skills --skill ai-pulse github-trending --agent codex -y
```

安装全部 skills 到当前项目的 Codex：

```bash
npx skills add lugezuishuai/awesome-skills --skill '*' --agent codex -y
```

将 `--agent codex` 替换为 `--agent claude-code` 可安装到 Claude Code；也可以传入多个智能体名称。加上 `-g` 可全局安装，让其他项目使用：

```bash
npx skills add lugezuishuai/awesome-skills --skill '*' --agent codex -g -y
```

### 验证安装

```bash
# 查看当前项目中安装到 Codex 的 skills
npx skills list --agent codex

# 查看全局安装结果
npx skills list -g --agent codex
```

列表中应出现所选 skill。默认的项目级 Codex 安装目录为 `.agents/skills/<skill-name>/`；全局安装目录为 `~/.agents/skills/<skill-name>/`。安装后，由智能体加载对应 `SKILL.md` 并按其中的说明执行任务。

## 使用依赖

安装 skill 会复制或链接说明和资源文件；执行任务所需的工具依赖按各 skill 的说明准备。

| Skill | 执行时需要 |
| --- | --- |
| `ai-pulse` | 网络搜索／网页抓取能力、`github-trending` skill；近期简报去重步骤使用会话检索能力。 |
| `article-to-html` | 本地文件读写能力；浏览器用于查看生成的 HTML。模板不依赖远程字体、图片或 CDN。 |
| `clean-code-principles` | 待修改项目的代码读写和验证工具，无独立运行依赖。 |
| `github-trending` | 网络访问；使用 TypeScript 页面解析示例时需要 `cheerio`，GitHub Search API 方案可配置 `GITHUB_TOKEN`。 |
| `pdf-watermark-remover` | Python 3、`pypdf`，以及 Poppler 的 `pdfinfo`、`pdftoppm` 等 PDF 检查和渲染工具。 |
| `resume-builder` | Python 3.8+；脚本按输出格式准备 `python-docx`／`weasyprint`，PDF 还需 Pango 等系统库及中文字体。HTML 模式无额外 Python 包依赖。 |

## 仓库结构

`skills/` 下按 skill 名称平铺，不增加分类目录。单个 skill 内仍保留其需要的资源层级。

```text
awesome-skills/
├── README.md
├── AGENTS.md
└── skills/
    ├── ai-pulse/
    ├── article-to-html/
    ├── clean-code-principles/
    ├── github-trending/
    ├── pdf-watermark-remover/
    └── resume-builder/
```

每个目录必须包含 `SKILL.md`，可按需附带 `scripts/`、`references/`、`assets/`、`examples/` 或 `evals/`。添加或维护 skill 时，请遵循 [AGENTS.md](AGENTS.md)，同步更新上方目录、依赖与安装说明。

## 来源与许可

首批六个 skills 从维护者本地的 `~/.agents/skills/` 对应目录复制，保留原有说明、脚本、示例及许可证。仓库的目录说明与安装文档参考了 [agentara/skills](https://github.com/agentara/skills) 和 [anthropics/skills](https://github.com/anthropics/skills)，并采用本仓库要求的平铺结构。Skill 格式参考 [Agent Skills 规范](https://agentskills.io/specification)。

各 skill 的许可与归属以其目录内的文件为准；[resume-builder](skills/resume-builder/LICENSE) 附带 MIT 许可证。本仓库未为其他未声明许可的 skill 统一授予新许可证。
