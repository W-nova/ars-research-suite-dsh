---
name: ars-research-suite
description: 学术研究套件（ARS 改造版）：按提示词自动选择一个研究工作流，覆盖研究问题收敛、文献与系统综述、论文大纲/初稿/返修、模拟同行评审、端到端研究流水线、实验方案与统计解读。所有引用、统计数据与期刊政策均核查来源；无法核实的条目明确标注"[未验证]"，不编造。
whenToUse: 用户要求写论文、开题、文献综述、系统综述/PRISMA、模拟审稿、返修/Rebuttal、引用核查、期刊政策查询、实验方案或统计解读时。
metadata:
  version: "0.1.0"
  adapted_from: "ARS-Codex academic-research-suite v3.22.0"
---

# ARS 学术研究套件（DSH 版）

把学术研究做成一条固定链路：**选一个工作流 → 读它的规则 → 只加载当前阶段需要的角色卡/参考 → 分阶段产出 → 交付前过证据核查**。

## 0. 证据纪律（最高优先级，覆盖任何流程）

适用于引用文献、统计数据、期刊/会议政策，以及方法学断言。

1. 每条外部可核验的声明都要有来源，并登记在交付物末尾的《证据核查表》。
2. 核验工具：`web_search` 找线索，`web_fetch` 打开原始页面；优先 DOI、出版社/期刊官网、官方文档、原始数据集。
3. 状态只有四种：`已核实` / `部分核实` / `未验证` / `与来源冲突`。
4. 无法核实 → 正文原处标 `[未验证]`，核查表登记原因；**绝不补全**作者、年份、卷期、页码、DOI。
5. 检索不到 ≠ 不存在：写"未验证"，不写"错误/不存在"。
6. 用户提供的材料可以直接引用，但来源栏写"用户提供，未独立核验"。
7. 与已核实来源冲突 → 标 `与来源冲突`，并在正文显式提示差异。
8. 期刊/会议政策（分区、影响因子、字数、格式、AI 披露要求）必须落到官方页面；聚合站只作线索。
9. 统计数字必须能追到一手来源；转引要写"转引自"。
10. 不编造参考文献、DOI、统计结果、审稿意见或期刊政策。宁可少写一条，也不虚构。
11. 单轮外部检索预算 ≤ 8 次（`web_search`/`web_fetch` 合计）；超出预算的条目直接标 `未验证` 并说明。

交付前必须运行 `scripts/verify_checklist.py <交付文件>`；有违规先修再交付。

## 1. 路由：一次只选一个工作流

| 用户意图 | 读这个文件 | 默认模式 |
|---|---|---|
| 选题收敛、文献综述、系统综述（PRISMA）、Meta 分析、事实核查 | `workflows/deep-research.md` | full / lit-review / socratic / systematic-review / fact-check |
| 论文大纲、初稿、摘要、修改、引用格式、AI 披露、格式转换、审稿回复审计 | `workflows/academic-paper.md` | plan / outline-only / draft / revision / … |
| 模拟审稿、编辑决定信、方法学专项、返修后再审 | `workflows/paper-reviewer.md` | full / quick / methodology / re-review |
| 端到端（选题→投稿）、完整性核查 | `workflows/pipeline.md` | 分阶段流水线 |
| 实验方案、人类研究协议、统计解读、可重复性 | `workflows/experiment-design.md` | plan / protocol / stats / reproducibility |

### 别名快捷方式

用户写 `/ars-plan` 或纯文本 `ars-plan` 都算显式指令：剥掉别名 token，按表进入对应模式。

| 别名 | 模式 | 目标文件 |
|---|---|---|
| ars-plan | academic-paper · plan | workflows/academic-paper.md |
| ars-outline | academic-paper · outline-only | 同上 |
| ars-abstract | academic-paper · abstract-only | 同上 |
| ars-lit-review | academic-paper · lit-review（写作内的综述章） | 同上 |
| ars-3w | deep-research · three-way-scan | workflows/deep-research.md |
| ars-citation-check | academic-paper · citation-check | 同上 |
| ars-revision | academic-paper · revision | workflows/academic-paper.md |
| ars-revision-coach | academic-paper · revision-coach | 同上 |
| ars-reviewer | paper-reviewer · full | workflows/paper-reviewer.md |
| ars-full | pipeline | workflows/pipeline.md |
| ars-disclosure | academic-paper · disclosure | workflows/academic-paper.md |
| ars-format-convert | academic-paper · format-convert | 同上 |
| ars-rebuttal-audit | academic-paper · rebuttal-audit | 同上 |

### 路由判定顺序（严格按序）

1. 别名命中 → 直接进该模式，不再追问。
2. **宽泛选题 override（优先级最高）**：用户说"想写论文/开题/有个题目/研究方向"，但没给明确研究问题 → 进 `deep-research` 的 `socratic`，先收敛 RQ，**不产出大纲、不写初稿、不做完整流水线**。
3. 单阶段明确请求（"帮我写摘要""审一下这篇""核一下引用"）→ 直接进对应模式。
4. 一次给了跨阶段材料（如初稿 + 审稿意见）→ 先澄清一句，不自动猜。
5. 既没材料也没明确请求 → 问 1–3 个关键问题；问题要具体，不要发问卷。
6. 只有**新请求**才路由；同一会话的续跑、压缩恢复、用户补充材料都沿用已选工作流，不重新判定。切换工作流必须用户确认。

### 歧义处理

- 一次最多问 3 个问题，放在一条消息里。
- 只问决定"路由/产出"所必需的：研究问题、材料在哪、目标期刊或学科、语言与格式。
- 用户不回答也能推进时，先给最小可用产出，并在开头写明假设。

## 2. 加载顺序（省上下文）

1. 只读选中的 `workflows/<x>.md`。
2. 按该文件"需要的角色/参考"小节，只读当前阶段用到的 `agents/*.md`、`references/*.md`。
3. 不要预加载其它工作流，不要一次读全部 references；模板只在要产出该文件时读。

## 3. 分阶段产出

长流程每条回复开头四行：

```
工作流: <name> · 模式: <mode>
阶段: <n/总数> <阶段名>
本次产出: <这一个产物>
下一关卡: <需要用户确认什么>
```

- 到关卡就停，等确认；用户说"一路跑完"可以不逐段停，但证据核查关卡与投稿前关卡仍必须停。
- 每阶段只做一件事：不要同一条回复里又出大纲又出全文。
- 用户中途插话 → 先处理插话，再回到原阶段。

## 4. DSH 运行时映射

| 原先的写法 | 在本环境里 |
|---|---|
| Read / Glob / Grep | `read` / `glob` / `grep` |
| WebSearch | `web_search`；打开页面用 `web_fetch` |
| Bash(python) | `pwsh` 调 python；优先 `load_workspace_dependencies` 给出的内置 python |
| Write / Edit | `write` / `edit` |
| Agent Team / Task tool | 默认**内联扮演**角色卡；只有用户明确要"并行/多角色独立评审"时才用 `subagent` / Agent Teams，并说明独立性限制 |
| `/ars-*` 斜杠命令 | 不存在；用纯文本 `ars-*` 触发上面的别名表 |
| Claude hooks / 写保护 | 不存在；写文件前先说清楚要改哪个文件 |
| Pandoc / LaTeX | 用 `office` 系列 skill 出 DOCX/PDF；没有 LaTeX 环境时不要承诺编译 PDF |

## 5. 输出默认

- 语言跟随用户（用户写简体就简体），不强制繁体。
- 引用默认 APA 7；用户指定则从其指定（IEEE / Chicago / MLA / Vancouver / GB/T 7714）。
- 事实、推断、建议分开写；推断标"推断"，建议标"建议"。
- 不确定就写不确定；不要用"研究表明"给没有来源的话撑腰。

## 6. 资源索引

- `workflows/`：deep-research、academic-paper、paper-reviewer、pipeline、experiment-design
- `agents/`：socratic-mentor、research-question、citation-auditor、synthesis、draft-writer、methodology-reviewer、domain-reviewer、devils-advocate、editor-in-chief、revision-coach
- `references/`：verification-protocol、evidence-levels、ai-failure-modes、review-rubric、citation-formats、journal-policy、writing-quality
- `templates/`：research-brief、literature-matrix、review-report、decision-letter、revision-roadmap、evidence-table
- `scripts/`：`verify_checklist.py`（交付前跑，检查证据核查表与未验证标注）
