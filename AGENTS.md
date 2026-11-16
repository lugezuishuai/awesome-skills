# 仓库维护指南

本仓库维护可通过 `npx skills add` 安装的 Agent Skills。主要产物是 skill 指令及其配套资源。

## 目录约定

```text
skills/<skill-name>/SKILL.md
skills/<skill-name>/scripts/       # 按需提供
skills/<skill-name>/references/    # 按需提供
skills/<skill-name>/assets/        # 按需提供
skills/<skill-name>/examples/      # 按需提供
skills/<skill-name>/evals/         # 按需提供
```

- `skills/` 的直接子目录就是 skill；保持平铺，不添加 `productivity/`、`engineering/` 等分类层级。
- 文件夹名称使用小写字母、数字和连字符，与 `SKILL.md` 中的 `name` 一致。
- 将脚本、模板和参考资料保留在所属 skill 中，以相对路径引用，保证单独安装后仍然完整可用。
- 只有实际需要时才添加资源目录；不为每个 skill 强制创建相同的空目录。

## Skill 格式

`SKILL.md` 必须以有效的 YAML frontmatter 开头：

```yaml
---
name: example-skill
description: 说明这个 skill 做什么，以及用户在什么情况下应使用它。
---
```

- `name` 和 `description` 为必填的非空字符串；命名和可选字段遵循 [Agent Skills 规范](https://agentskills.io/specification)。
- 正文写明工作流、需要的工具、输入输出和必要的验证方式。较长的参考内容放进 `references/` 并提供入口链接。
- 保留有效的可选元数据，例如 `compatibility`、`license`、`metadata`，不要为了适配过旧的校验器删除它们。
- 复制已有 skill 时保留其正文、配套资源、来源说明和许可证。改动行为时应有明确需求，避免顺带重写。
- 不写入维护者机器的绝对路径、凭据、真实个人资料或任务生成物；示例数据使用虚构信息。

## 文档同步

添加、删除、重命名或改变 skill 能力时，同步维护根目录 `README.md` 中的 skill 列表、相对链接、使用依赖与安装示例。仓库使用根目录统一索引，无需增加分类 README。

`ai-pulse` 依赖 `github-trending`，相关安装示例应包含两者。其他工具依赖按各 skill 的当前说明记录。

## 验证

提交前检查以下内容：

1. 每个直接子目录都包含 `SKILL.md`，名称与 frontmatter 一致，YAML 可解析，引用的配套资源存在。
2. 从其他目录导入时核对文件清单和内容，避免遗漏脚本、模板、隐藏配置或许可证；不导入缓存和生成物。
3. 用 CLI 检查本地发现结果，并确认 README 中的列表一致：

   ```bash
   npx skills add . --list
   ```

4. 修改可执行脚本时运行与改动相符的检查。仅复制文件时优先验证内容一致性和安装完整性。
5. 检查 `git diff --check` 和 `git status --short`，只提交当前任务涉及的文件。

当任务包含发布及安装验证时，在推送成功后从远端安装，使用独立临时目录完成项目级验证：

```bash
SKILLS_VERIFY_DIR="$(mktemp -d)"
cd "$SKILLS_VERIFY_DIR"
npx skills add lugezuishuai/awesome-skills --skill '*' --agent codex --copy -y
npx skills list --agent codex
```

检查 `.agents/skills/` 中的 skill 清单和配套文件是否与发布内容一致。区分“安装成功”和“各 skill 的实际任务已运行验证”，不要将前者描述为后者。

发布范围以用户要求为准。验证产物留在临时目录，不提交安装生成的 `.agents/` 或 `skills-lock.json`；结束前再次检查仓库状态。
