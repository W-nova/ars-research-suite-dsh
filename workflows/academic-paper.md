# workflow: academic-paper（论文写作）

适用：大纲、初稿、摘要、修改、引用格式、AI 披露、格式转换、审稿回复审计。
不适用：整篇模拟评审 → `paper-reviewer.md`；选题未定 → 先回 `deep-research.md` 的 socratic。

需要的角色：`draft-writer`、`revision-coach`、`citation-auditor`、`synthesis`
需要的参考：`writing-quality.md`、`citation-formats.md`、`verification-protocol.md`、`journal-policy.md`
输出模板：`revision-roadmap.md`、`evidence-table.md`

## 模式

| 模式 | 触发 | 产出 |
|---|---|---|
| plan | `ars-plan`、"写作计划" | 章节架构 + 论证链 + 证据缺口 + 进度 |
| outline-only | `ars-outline` | 三级大纲，每节写"要证明什么" |
| draft | "写初稿/写某一节" | 指定章节正文（不是整篇） |
| abstract-only | `ars-abstract` | 结构化摘要（中英双语按需） |
| revision | `ars-revision`、附审稿意见 | 修订稿 + 改动说明 |
| revision-coach | `ars-revision-coach` | 审稿意见 → 可执行路线图 |
| citation-check | `ars-citation-check` | 引用逐条核查表 |
| format-convert | `ars-format-convert` | 引用格式转换（APA/IEEE/Chicago/MLA/Vancouver/GB/T 7714） |
| disclosure | `ars-disclosure` | 目标 venue 的 AI 使用披露声明 |
| rebuttal-audit | `ars-rebuttal-audit` | 回复信逐条对照审计 |
| lit-review | `ars-lit-review` | 论文内的文献综述章 |

## plan：四要素先说清

目标（期刊/会议/学位论文）+ 现有材料（数据、结果、文献矩阵）+ 本次产出 + 约束（篇幅、语言、格式、学科）。

产出必须包含：

1. 一句话论点（What I argue that…）
2. 章节树，每节标注：要证明什么 / 用什么证据 / 证据是否已有
3. **证据缺口清单**：缺哪类文献、缺哪个数据、缺哪个分析
4. 风险：最可能被审稿人打的三点

## draft：按段推进

1. 一次只写一节（默认先写引言或结论，看用户）。
2. 每个论断后面挂证据：`[E1]` 指向证据核查表；没有证据的写 `[CITE: 需要 X 类文献]`，**不要编一条引用**。
3. 结构优先于润色：先给"论点句 + 支撑句 + 反例处理"，再展开。
4. 写完一节跑一次自检（见 `writing-quality.md`）：有没有空泛断言、有没有"研究表明"却没有来源、有没有把相关性写成因果。
5. 章节之间的承诺要对账：引言说要做的事，方法/结果必须做到。

## 引用规则

- 正文引用与参考文献必须一一对应；多一条少一条都算错。
- 未核实的引用：正文标 `[未验证]`，参考文献条目保留但加注。
- 用户给的文献可以直接用，来源栏写"用户提供"。
- 转引必须写"转引自"，不要把二手当一手。
- 格式转换只改格式，不改内容；转换后抽样比对 10% 条目。

## revision：按审稿意见逐条

1. 先建映射表：意见编号 → 类型（事实/方法/写作/补充实验）→ 可行性 → 计划改动位置。
2. 不可行的意见要写"为什么不改 + 替代方案"，不要硬答应。
3. 改完逐条回填：改了哪里、怎么改、是否新增证据。
4. 不引入新问题：改动涉及的相邻章节要回归检查。

## disclosure：先核政策

1. 找 venue 官方 AI 政策页面（`journal-policy.md` 有核查步骤）。
2. 政策没找到 → 输出"未验证该 venue 政策"，给通用模板，并标注需人工确认。
3. 声明只描述事实：用了什么工具、用在哪一步、人工做了哪些判断。
4. 不写"未使用 AI"除非确实没用。

## rebuttal-audit

逐条检查回复信：是否覆盖全部意见、是否引用了修改后的具体位置、是否夸大承诺（承诺了未做的实验）、语气是否对抗。

## 关卡清单

- [ ] 论点句已确认
- [ ] 证据缺口清单已确认
- [ ] 每个论断有证据或 `[CITE]` 占位
- [ ] 引用与参考文献一一对应
- [ ] 交付前跑 `scripts/verify_checklist.py`
