---
name: ai-pulse
description: >
  📡 AI Pulse —— 用于收集、筛选并整合 AI 综合资讯的简报技能，覆盖 AI 产品发布、开源趋势、行业新闻与播客更新。
  当用户要求“帮我整理一份 AI 资讯”“汇总今日 AI 新闻”“做一份 AI 简报”“盘点最近的 AI 动态”等相关内容时，必须使用此技能。
  也可由 cronjob 触发，用于生成固定时段的 AI 资讯简报。



---

# 📡 AI Pulse（ai-pulse）

这是一份综合性的 AI 资讯简报，结合了产品发布、开源趋势和精选新闻。

## 语言区域

最终输出应使用用户偏好的语言，即 `zh-CN` 简体中文。

## 工作流总览

按顺序执行以下步骤。凡是可能的地方，都应并行使用 `web_fetch` 调用，以尽量降低延迟。

### 抓取结果解包与定向解析

`web_fetch` 的转存文件有时不是网页正文，而是把正文放在 `result` 字段中的单行包装文本，其中换行显示为 `\n` 等转义序列。遇到这种形态时，先完成解包，再解析内容：

1. 先检查文件外层结构；若正文位于包装层的 `result` 字段，使用与包装格式匹配的解析方式提取该字段，并将转义序列解码为真实文本。优先使用 JSON 等结构化解析，避免手工替换导致 Unicode 乱码。
2. 解码前不要依赖物理行号读取正文，也不要在 `grep_search` 的正则中写入字面换行；此时文件可能只有一行，按行范围读取会为空，含字面换行的正则也可能被工具拒绝。
3. 解码后按稳定结构划分完整条目：Product Hunt 以 `<entry>...</entry>` 为边界，GitHub Trending 以 `## [owner / repo](/owner/repo)` 标题及下一个同级标题为边界。新闻、博客和播客同样优先使用标题、条目标签或卡片边界。
4. 从每个完整条目内提取字段并校验名称、链接、描述和指标是否属于同一条目。不要用固定字符长度截取标题后的宽泛片段，因为相邻条目可能被拼接，造成描述、语言或 Star 数错位。
5. 若稳定结构缺失，降级为逐项核对标题与链接的一致性；无法可靠归属的字段留空或注明未获取，不跨条目猜测补齐。

---

### 步骤 1：获取 Product Hunt 数据（聚焦 AI，Top 3–5）

目标：从今天的 Product Hunt 排行榜中获取**前 3–5 个与 AI 相关的产品**。

1. 对 `https://www.producthunt.com/feed` 执行 `web_fetch`（其中月份和日期 M、D 不带前导零）。
2. 从排行榜中选出**前 3–5 个与 AI 相关的产品**（AI 工具、LLM 封装、ML 基础设施、AI Agent、AIGC 等）。如果排行榜中少于 3 个 AI 产品，则用综合排名靠前的非 AI 产品补足，并注明它们并非 AI 产品。
3. 对每个产品收集以下信息：
   - 产品名称
   - 一句简介（tagline）
   - 点赞数（如果可获取）
   - 产品页面直链：`https://www.producthunt.com/posts/{slug}`
4. 写一句简短的个人点评，说明它为何重要或有何值得关注之处。

---

### 步骤 2：获取 GitHub Trending 数据（Top 10）

目标：使用 `github-trending` Skill 获取 GitHub Trending **前 10 个仓库**（daily，默认语言筛选）。

1. 必须先加载并使用 `github-trending` Skill 获取 Trending 仓库数据，不再直接在本步骤中通过 `web_fetch` 抓取 `https://github.com/trending?since=daily`。
2. 按 `github-trending` Skill 的推荐方式获取 daily、默认语言筛选的 Trending 仓库列表，并取**前 10 个**仓库。
3. 每个仓库需包含：
   - 完整名称（`owner/repo`）
   - 描述
   - 主要语言
   - 总 Star 数
   - 今日新增 Star 数
4. 链接格式：`https://github.com/{owner}/{repo}`。
5. 如适用，可补充一句说明其与用户兴趣（AI agents、TypeScript、Python、LangChain、医疗科技等）的相关性。

---

### 步骤 3：获取新闻、AI 博客、播客

这是编辑性最强的一步。需要从多个来源收集内容，并控制信息密度：3a、3b、3c 每一项数量控制在 **3–5 条**，步骤 3 总数不要超过 **15 条**。少一些也比为了凑数而灌水更好。

#### 3a：AI 资讯

1. 从以下渠道获取**近一天**的 AI 资讯，内容需要和 AI 行业相关，包含大模型、Agent、AI 产品、AI 公司等相关领域：
   - [Anthropic News](https://www.anthropic.com/news)
   - [OpenAI News](https://openai.com/zh-Hans-CN/news/)
   - [Google Blog](https://blog.google/innovation-and-ai/)
   - [MIT Technology Review](https://www.technologyreview.com)
   - [Import AI](https://importai.substack.com)
   - [The Batch](https://www.deeplearning.ai/the-batch)
   - [TLDR AI](https://tldr.tech/ai)
   - [The Rundown AI](https://www.therundown.ai)
   - [Hacker News](https://news.ycombinator.com)
   - [机器之心](https://www.jiqizhixin.com)
   - [量子位](https://www.qbitai.com)
   - [AI Now Institute](https://ainnow.com)
   - [InfoQ 中文站](https://www.infoq.cn)
   - [雷峰网](https://www.leiphone.com)
2. 优先选择对 AI 从业者有实质影响的内容，例如模型发布、Agent 进展、AI 产品发布、AI 公司融资或组织变化、开源生态、监管政策、基础设施和评测基准。
3. 每条内容包含标题、来源、发布时间、直链和 1–2 句中文摘要。
4. 按重要性和时效性筛选 **3–5 条**；如果没有足够重要的新闻，可以少于 3 条。

#### 3b：AI 博客

1. 从以下博客网站拉取**近 2 天**的 AI 相关文章，并按照发布时间从新到旧排列：
   - [OpenAI Blog](https://openai.com/blog)
   - [Anthropic Engineering Blog](https://www.anthropic.com/engineering)
   - [Google AI Blog](https://ai.googleblog.com)
   - [DeepMind Blog](https://deepmind.google/discover/blog)
   - [Hugging Face Blog](https://huggingface.co/blog)
   - [Meta AI Blog](https://ai.meta.com/blog)
   - [LangChain Blog](https://blog.langchain.com)
   - [Towards Data Science](https://towardsdatascience.com)
   - [daily.dev — AI 专栏](https://daily.dev/blog)
   - [Medium](https://medium.com)
   - [通义千问 Qwen Blog](https://qwen.ai/blog)
   - [深度求索 DeepSeek Blog](https://deepseek.com/blog)
   - [月之暗面 Moonshot Blog](https://moonshot.cn/blog)
   - [字节跳动 AI Lab](https://ailab.bytedance.com/publications)
2. 优先选择模型发布、工程实践、AI Agent、开源工具、评测、产品能力、研究应用等对 AI 从业者有实质参考价值的文章。
3. 每条内容包含文章标题、来源、发布时间、直链和 1–2 句中文摘要。
4. 最终筛选 **3–5 条**；如果近 2 天内没有足够高质量内容，可以少于 3 条。

#### 3c：获取播客

1. 对以下播客执行 `web_fetch`，查看是否有更新：
   - [硅谷101](https://www.xiaoyuzhoufm.com/podcast/5e5c52c9418a84a04625e6cc)
   - [罗永浩的十字路口](https://www.xiaoyuzhoufm.com/podcast/68981df29e7bcd326eb91d88)
   - [十字路口 Crossing](https://www.xiaoyuzhoufm.com/podcast/60502e253c92d4f62c2a9577)
   - [晚点聊](https://www.xiaoyuzhoufm.com/podcast/61933ace1b4320461e91fd55)
   - [elsewhere别处发生](https://www.xiaoyuzhoufm.com/podcast/68ff657d9c745a6e69da8fcf)

2. 只选择最近 48 小时内有更新的播客。
3. 最终筛选 **3–5 条**；如果最近 48 小时内没有足够更新，可以少于 3 条或跳过该子章节。

---

### 步骤 4：检查是否与近期 Pulse 重复

在组装最终输出之前：

1. 使用 `conversation_search`，查询 `Pulse`，检索最近的 Pulse 简报。
2. 将你收集到的 AI 资讯、AI 博客和播客更新与这些近期输出进行比较。
3. 删除所有重复内容。如果某条内容是对之前事件的实质性更新，则可以保留，并加注类似“🔄 进展更新”的说明。

---

### 步骤 5：组装输出

使用以下模板。所有章节标题、产品名称、仓库名称、AI 资讯标题、AI 博客标题和播客标题都**必须直接加超链接**，不要额外添加“sources”章节。

语言要求：正文使用中文（全角标点：，、：！？。）；产品名、仓库名和技术术语保留英文。

```markdown
# 📡 Pulse | {YYYY年M月D日}

## Product Hunts

- **[Product Name](https://www.producthunt.com/posts/slug)** {upvotes if available}
简短介绍与点评（简体中文）。

- **[Product Name](URL)**
...

(5-10 items)

---

## GitHub Trending

- **[owner/repo](https://github.com/owner/repo)** ⭐ {total stars} (+{today})
Description。{Language}。简短点评（简体中文）。

- **[owner/repo](URL)** ⭐ ...
...

(5 items)

---

## AI News

- **[Headline](URL)**
来源与发布时间。1–2 sentence summary（简体中文）。

- **[Headline](URL)**
...

(3–5 items, or fewer if there are not enough important AI news items)

---

## AI Blogs

- **[Article Title](URL)**
来源与发布时间。1–2 sentence summary（简体中文）。

- **[Article Title](URL)**
...

(3–5 items, ordered by publish time, newest first)

---

## Podcasts (If exists updates)

- **[Podcast Name](URL)**
简短介绍与点评（简体中文）。

- **[Podcast Name](URL)**
...

(3–5 items, or fewer if there are not enough updates)
```

### 格式规则

- **标题层级**：顶级标题使用 `#`，章节使用 `##`，单项内容使用列表。这种结构适合映射到飞书 / Word 导出。
- **链接**：每个产品、仓库、AI 资讯、AI 博客和播客标题都**必须**在其自身标题中带可点击链接。不要把 URL 放在脚注或“sources”区块中。
- **简洁性**：每条内容的点评最多 1–2 句话。整份 Pulse 应当能在 2 分钟内快速浏览完。
- **禁止灌水**：如果某个章节没有值得写的内容，就写一句类似“今天暂无重要 AI 资讯”，不要强行填充。
- **中文标点**：所有中文正文必须使用全角标点（，。：！？、）。
- **不要使用引用或 `` 标签**：Pulse 是一份简报，不是研究报告。来源归因通过标题中的超链接来完成。
- **不要重复**：同一天内不要纳入重复 AI 资讯、AI 博客或播客更新。