# Find and Fit Skills

**先找现成的，再只改你需要的。** 一个帮助 AI 为真实需求寻找、检查和适配现有 Skill / 开源工具的轻量 Skill。

Find existing agent skills, check them against your constraints, and adapt only the missing piece.

## 为什么做这个

搜索到一个热门仓库，不代表它能在你的电脑上解决问题。本项目把发现候选和验证适配分开：读取实际 SKILL.md，记录版本与证据，检查平台、离线要求、费用、许可证，然后给出「直接用 / 少量适配 / 独立工具 / 没有合适候选」的结论。

适合这样问：

- “帮我找一个在 Windows 上离线转写日语录音的 Skill，没有 GPU。”
- “找能批量提取 PDF 表格的工具，扫描件也要处理，先别安装。”
- “我想把已有 Skill 改成适合自己的工作流程，先检查哪些能力已经具备。”

## 安装到 Codex

需要 Git；可选辅助脚本需要 Python 3.10+，仅用标准库，无 pip 依赖、无 API 付费要求。搜索公开 GitHub 需要联网。Skill 的推理依赖你使用的 AI 客户端及其额度。

```text
git clone https://github.com/BLacxDx/find-and-fit-skills.git
```

将 `skills/find-and-fit` 文件夹复制到 Codex 的 skills 目录（默认 `~/.codex/skills/`；配置了 CODEX_HOME 时用其 `skills/` 子目录）。Windows PowerShell 默认目录示例：

```powershell
Copy-Item -Recurse ./find-and-fit-skills/skills/find-and-fit "$env:USERPROFILE/.codex/skills/"
```

已有同名目录时先比较，避免覆盖自己的修改。新会话中输入：

```text
用 $find-and-fit 找一个满足以下要求的 Skill：Windows、无需付费 API、批量处理 PDF。先比较，不安装。
```

Skill 保持默认自动发现；实际是否触发由宿主决定，也可以显式调用。其他支持 SKILL.md 的客户端可按其安装方式使用；目前没有逐个验证。

## 单独使用搜索助手

在仓库根目录运行：

```text
python skills/find-and-fit/scripts/discover.py search "pdf translation skill in:readme" --limit 3
python skills/find-and-fit/scripts/discover.py inspect vercel-labs/skills --skill-path skills/find-skills/SKILL.md
```

输出 JSON 包括检索时间、仓库信息、许可证元数据、SKILL.md 路径和固定到提交的文件链接。默认最多读取三个 Skill 和一个根目录 README；大文件跳过，截断/未读取情况明确列出。源码作为 `untrusted_content` 返回，脚本不执行候选内容，不安装软件，不创建 PR。

GitHub 仓库搜索不是完整的 Skill 索引；中文关键词可能漏检，AI 应结合英文检索或可用的网页/注册表搜索。请求超时或限流时返回非零退出码，不能当作「没有结果」。脚本不读取本机凭证，使用匿名公开 API；频繁使用会触发限流。不要把私人资料放进查询词。

## 与现有方案的关系

[Vercel find-skills](https://github.com/vercel-labs/skills/tree/main/skills/find-skills) 已经提供发现与安装流程，本项目不声称首创 Skill 搜索。这里的重点是用户约束、提交固定的源码证据、未知项和最小适配测试；可搭配已有发现工具使用，而非替代它们。

目前是小型首版：没有完整安全审计能力、自动语义排名、安装器或自动改写器。适配实现由宿主 AI 在用户授权范围内完成。没有受控实验能证明它比不启用 Skill 更好，也不保证任何资助申请资格。

## 验证和贡献

```text
python -m unittest discover -s tests -v
```

六个离线回归测试覆盖检索不完整、未知许可证、提交固定、内容不执行、下载大小、参数和缺失文件。真实仓库检查见 [验证记录](examples/validation.md)。这些是功能冒烟测试，不是独立会话的能力提升评测。

欢迎提交带输入、预期行为、实际结果的 issue。改代码时运行上述测试；新增搜索源请保持只读、可限制请求量，并保留证据来源和失败信息。

MIT License。代码与文档使用 AI 辅助编写，当前维护者：BLacxDx。
