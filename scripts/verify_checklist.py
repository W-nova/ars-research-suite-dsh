#!/usr/bin/env python3
"""检查交付物的证据核查表与未验证标注。

用法:
    python verify_checklist.py <deliverable.md> [--json]

退出码: 0 = 通过, 1 = 有违规, 2 = 参数/文件错误
只用标准库，不联网。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Windows 控制台默认可能是 GBK，统一按 UTF-8 输出，避免中文乱码。
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ALLOWED_STATUS = {"已核实", "部分核实", "未验证", "与来源冲突"}
SOURCE_OK = re.compile(r"https?://|doi\.org|10\.\d{4,}|用户提供|用户材料|用户数据", re.I)
DATE_OK = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}")
FABRICATION_HINT = re.compile(r"记忆|模型推测|凭印象|据说|大概是")
UNVERIFIED_MARK = re.compile(r"\[未验证\]")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def heading_level(line: str) -> int:
    m = HEADING.match(line)
    return len(m.group(1)) if m else 0


def find_section(lines: list[str], keyword: str) -> tuple[int, int] | None:
    """返回 [start, end) 行区间；start 是标题行。"""
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and keyword in m.group(2):
            level = len(m.group(1))
            end = len(lines)
            for j in range(i + 1, len(lines)):
                mj = HEADING.match(lines[j])
                if mj and len(mj.group(1)) <= level:
                    end = j
                    break
            return i, end
    return None


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_table(section: list[str]) -> tuple[list[str], list[list[str]], list[int]]:
    """返回 (header, rows, row_line_numbers)。row_line_numbers 是相对 section 的索引。"""
    table_lines = [(i, ln) for i, ln in enumerate(section) if ln.lstrip().startswith("|")]
    if len(table_lines) < 2:
        return [], [], []
    header = split_row(table_lines[0][1])
    body: list[list[str]] = []
    row_ids: list[int] = []
    for i, (idx, ln) in enumerate(table_lines[1:]):
        cells = split_row(ln)
        if all(c.strip("-: ") == "" for c in cells):
            continue
        body.append(cells)
        row_ids.append(idx)
    return header, body, row_ids


def column_index(header: list[str], keys: list[str]) -> int | None:
    for i, name in enumerate(header):
        low = name.lower().replace(" ", "")
        for key in keys:
            if key.lower() in low:
                return i
    return None


def cell(row: list[str], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return row[idx].strip()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("用法: python verify_checklist.py <deliverable.md> [--json]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    as_json = "--json" in argv[2:]
    if not path.is_file():
        print(f"错误: 找不到文件 {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()

    errors: list[str] = []
    warnings: list[str] = []
    stats = {"rows": 0, "已核实": 0, "部分核实": 0, "未验证": 0, "与来源冲突": 0}

    section = find_section(lines, "证据核查")
    table_found = False
    if section is None:
        errors.append("缺少《证据核查》小节：交付物末尾必须有该节（见 templates/evidence-table.md）")
    else:
        start, end = section
        header, rows, _ = parse_table(lines[start:end])
        if not header:
            errors.append("《证据核查》小节里没有表格")
        else:
            table_found = True
            i_id = column_index(header, ["id"])
            i_claim = column_index(header, ["声明", "条目", "claim"])
            i_type = column_index(header, ["类型", "type"])
            i_src = column_index(header, ["来源", "source"])
            i_date = column_index(header, ["日期", "date"])
            i_status = column_index(header, ["状态", "status"])
            i_note = column_index(header, ["备注", "note"])

            if i_status is None:
                errors.append("证据核查表缺《状态》列")
            if i_src is None:
                errors.append("证据核查表缺《来源》列")
            if i_claim is None:
                errors.append("证据核查表缺《声明/条目》列")

            for n, row in enumerate(rows, start=1):
                stats["rows"] += 1
                rid = cell(row, i_id) or f"第{n}行"
                status = cell(row, i_status).strip("*` ")
                source = cell(row, i_src)
                date = cell(row, i_date)
                note = cell(row, i_note)
                claim = cell(row, i_claim)

                if i_status is not None and status not in ALLOWED_STATUS:
                    errors.append(f"{rid}: 状态“{status}”不合法（只允许 已核实/部分核实/未验证/与来源冲突）")
                    continue
                if status:
                    stats[status] += 1
                if i_claim is not None and not claim:
                    warnings.append(f"{rid}: 声明列为空")

                if status in {"已核实", "部分核实"}:
                    if not SOURCE_OK.search(source):
                        errors.append(f"{rid}: 状态为“{status}”但来源不是可解析链接或用户材料（来源=“{source}”）")
                    if i_date is not None and not DATE_OK.search(date):
                        errors.append(f"{rid}: 状态为“{status}”但核验日期缺失/格式不对（应为 YYYY-MM-DD）")
                if status == "未验证" and not (note or source):
                    warnings.append(f"{rid}: 标为未验证但没写原因（备注/来源都空）")

                joined = " ".join(row)
                if FABRICATION_HINT.search(joined):
                    errors.append(f"{rid}: 来源/备注里出现“{FABRICATION_HINT.search(joined).group(0)}”，疑似凭记忆或推测")

    if stats["未验证"] and find_section(lines, "未验证清单") is None:
        warnings.append("有未验证条目，但缺少《未验证清单》小节（建议逐条列原因与下一步）")

    marks = [
        (i + 1, ln.strip())
        for i, ln in enumerate(lines)
        if UNVERIFIED_MARK.search(ln) and not ln.lstrip().startswith("|")
    ]
    ref_section = find_section(lines, "参考文献")
    ref_count = 0
    if ref_section:
        s, e = ref_section
        ref_count = sum(1 for ln in lines[s + 1 : e] if re.match(r"^\s*(\[|-|\d+\.)\s*\S", ln))

    result = {
        "file": str(path),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
        "in_text_unverified_marks": len(marks),
        "reference_entries": ref_count,
    }

    out_path: str | None = None
    if "--out" in argv:
        idx = argv.index("--out")
        if idx + 1 < len(argv):
            out_path = argv[idx + 1]

    if as_json:
        rendered = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        buf = [f"文件: {result['file']}"]
        buf.append(
            f"证据核查: {stats['rows']} 行 | 已核实 {stats['已核实']} | 部分核实 {stats['部分核实']} "
            f"| 未验证 {stats['未验证']} | 与来源冲突 {stats['与来源冲突']}"
        )
        buf.append(f"正文 [未验证] 标记: {len(marks)} 处 | 参考文献条目: {ref_count} 条")
        buf.extend(f"警告: {w}" for w in warnings)
        buf.extend(f"错误: {e}" for e in errors)
        buf.append("结论: " + ("通过" if not errors else f"不通过（{len(errors)} 个错误）"))
        rendered = "\n".join(buf)

    if out_path:
        Path(out_path).write_text(rendered + "\n", encoding="utf-8")
        print(f"报告已写入: {out_path}")
    else:
        print(rendered)

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
