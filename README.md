# ARS Research Suite · DSH 版

> 给 [DeepSeek Harness (DSH)](https://github.com/deepseek-ai) 用的学术研究技能套件：**按提示词自动选工作流 → 只加载当前阶段的规则 → 分阶段产出 → 交付前过证据核查**。

本仓库把 ARS-Codex 的 `academic-research-suite` 改造成 DSH 原生 skill：保留工作流、角色卡、核查原则与自动路由，去掉 Codex/Claude 专属机制（slash command 注册、hooks、插件市场、多 agent 自动编排）。全部文本为新写，不 vendor 上游文件。

- 5 个工作流：deep-research / academic-paper / paper-reviewer / pipeline / experiment-design
- 10 张角色卡：socratic-mentor、research-question、citation-auditor、synthesis、draft-writer、methodology-reviewer、domain-reviewer、devils-advocate、editor-in-chief、revision-coach
- 7 份参考：来源核查协议、证据等级、AI 失败模式、评审量表、引用格式、期刊政策、写作质量
- 6 个模板 + 1 个确定性检查脚本
- 体积约 65 KB / 30 个文件（上游约 16 MB / 2600 个文件），加载时只读 `SKILL.md`

## 特性

- **自动路由**：用户只说需求，skill 按意图选一个工作流；`ars-*` 别名可直达模式。
- **宽泛选题 override**：只给题目、没给研究问题 → 先走 Socratic 收敛，不产出大纲。
- **证据纪律**：所有引用、统计、期刊政策必须核查来源；核不了的标 `[未验证]`，不补全 DOI/卷期/页码。
- **可验证**：交付前跑 `scripts/verify_checklist.py`，检查证据核查表结构与状态词。
- **无外部依赖**：核心是 Markdown 提示词；检查脚本只用 Python 标准库。

## 安装

DSH 会扫描这些目录（按优先级）：`<项目>/.dsh/skills` → `<项目>/.agents/skills` → 自定义目录 → `~/.dsh/skills` → `~/.agents/skills`。
**跨工作区通用**请装到 `~/.dsh/skills`。

### 方式 A：git clone（推荐，便于升级）

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.dsh\skills" | Out-Null
git clone https://github.com/W-nova/ars-research-suite-dsh.git "$env:USERPROFILE\.dsh\skills\ars-research-suite"
```

macOS / Linux：

```bash
mkdir -p ~/.dsh/skills
git clone https://github.com/W-nova/ars-research-suite-dsh.git ~/.dsh/skills/ars-research-suite
```

升级：

```powershell
cd "$env:USERPROFILE\.dsh\skills\ars-research-suite"; git pull
```

> 部署目录名可以随意，DSH 以 `SKILL.md` 里的 `name` 字段为准；建议就叫 `ars-research-suite`。

### 方式 B：下载 ZIP + 安装脚本

```powershell
# 用户级（所有工作区可用）
.\install\install.ps1

# 项目级（仅当前工作区）
.\install\install.ps1 -Project
```

```bash
# 用户级
./install/install.sh

# 项目级
./install/install.sh --project
```

### 验证安装

```powershell
python scripts/selftest.py
```

然后在 DSH 新会话的技能目录里应看到 `ars-research-suite`，或直接输入 `/ars-research-suite`。

> DSH 会监听 skill 目录，新装/修改通常不需要重启；若目录里没出现，检查 `SKILL.md` 是否在第一行有正确的 YAML frontmatter。

## 使用

**自然语言**（推荐）：

```
帮我写一篇关于 AI 治理的论文大纲
评审这篇论文，重点方法学和引用完整性
帮我把这 20 条引用核一遍
```

**显式调用**：先 `/ars-research-suite` 载入路由器，再按需说明。

**别名**（纯文本即可，DSH 不注册斜杠命令）：

| 别名 | 进入 |
|---|---|
| `ars-plan` / `ars-outline` / `ars-abstract` | 论文计划 / 大纲 / 摘要 |
| `ars-lit-review` | 论文内的文献综述章 |
| `ars-3w` | 三路文献扫描 |
| `ars-citation-check` | 引用逐条核查 |
| `ars-revision` / `ars-revision-coach` | 按审稿意见修改 / 修改路线图 |
| `ars-reviewer` | 完整模拟评审（3 审稿人 + 魔鬼代言人 + 决定信） |
| `ars-disclosure` | 目标 venue 的 AI 使用披露 |
| `ars-format-convert` | 引用格式转换（APA/IEEE/Chicago/MLA/Vancouver/GB-T 7714） |
| `ars-rebuttal-audit` | 审稿回复信审计 |
| `ars-full` | 端到端流水线 |

## 目录结构

```text
.
├── SKILL.md                  # 入口：证据纪律 + 路由表 + DSH 映射
├── workflows/                # 5 个工作流
│   ├── deep-research.md
│   ├── academic-paper.md
│   ├── paper-reviewer.md
│   ├── pipeline.md
│   └── experiment-design.md
├── agents/                   # 10 张角色卡（角色/输入/输出契约/禁止/证据要求）
├── references/               # 核查协议、证据等级、失败模式、量表、格式、政策、写作质量
├── templates/                # 研究简报、文献矩阵、审稿报告、决定信、修改路线图、证据核查表
├── scripts/
│   ├── verify_checklist.py   # 交付前检查证据核查表（仅标准库）
│   └── selftest.py           # 仓库/安装自检
├── install/                  # install.ps1 / install.sh
└── .github/workflows/selftest.yml
```

## 证据纪律（核心规则）

1. 引用、统计、期刊政策必须核查来源，并登记到交付物末尾的《证据核查表》。
2. 状态只有四种：`已核实` / `部分核实` / `未验证` / `与来源冲突`。
3. 核不了 → 正文标 `[未验证]`，**绝不**补全作者、卷期、页码、DOI。
4. 检索不到 ≠ 不存在；写"未验证"，不写"错误"。
5. 期刊政策必须落到官方页面；影响因子/分区没有官网页就不写数值。
6. 单轮外部检索预算 ≤ 8 次；超出的标未验证。

交付前运行：

```powershell
python scripts/verify_checklist.py <交付文件.md>
# 可选：--out report.txt  --json
```

退出码 0 = 通过；1 = 有违规（状态词非法 / 已核实但无来源 / 出现"凭记忆"等）。

## 与上游 ARS-Codex 的差异

| 上游 | 本仓库 |
|---|---|
| 47 KB 单文件 router + 2600 文件 vendored 内容 | 5.5 KB router + 按需加载的 30 个文件 |
| Claude/Codex slash command、hooks、插件市场 | 只用 DSH 的 `skill` 工具与纯文本别名 |
| 13/12/7 个 agent 自动组队 | 10 张角色卡内联扮演；需要并行时才用 DSH subagent/Agent Teams |
| 0–100 分评审 | 定性档位（Reject/Major/Minor/Accept），不编造分数与校准数据 |
| 繁体中文默认 | 跟随用户语言 |

## 自检与 CI

```powershell
python scripts/selftest.py
```

检查：frontmatter 的 `name`/`description`、kebab-case、必备目录、`SKILL.md` 与各 workflow 引用的文件是否存在。CI（`.github/workflows/selftest.yml`）在每次 push 时跑同一脚本。

## 许可与致谢

- 本仓库文本以 **CC BY-NC 4.0** 发布（非商业使用，需署名）。见 [`LICENSE`](LICENSE)。
- 结构与工作流思路改编自 **Academic Research Skills**（作者 Cheng-I Wu，[Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)，CC BY-NC 4.0）及其 Codex 发行版 `academic-research-suite`。详见 [`NOTICE.md`](NOTICE.md)。
- 本仓库不是上游官方发行版，也未获得其背书；`academic-research-suite` 名称归上游项目所有。
- 未包含任何外部 API key；联网核查依赖运行环境的 `web_search` / `web_fetch`。

## 常见问题

**Q：装好但技能列表里没有？**
A：确认路径是 `<skill 根>/ars-research-suite/SKILL.md`（只扫一层目录），frontmatter 以 `---` 开头且含 `name`、`description`；`name` 必须是 kebab-case。

**Q：`python` 找不到？**
A：Windows 上 `python` 可能是 Microsoft Store 占位符。用 DSH 内置解释器（`load_workspace_dependencies` 返回的路径），或 Git Bash 里的 python。

**Q：控制台中文乱码？**
A：PowerShell 默认 GBK。脚本支持 `--out report.txt`，或先 `$env:PYTHONIOENCODING='utf-8'`。

**Q：能直接用完整 6 阶段流水线吗？**
A：可以，但小模型（如 deepseek-flash）上不划算。建议先用 `ars-reviewer`、`ars-citation-check`、`ars-lit-review` 单模式。
