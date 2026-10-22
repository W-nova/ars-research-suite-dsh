#!/usr/bin/env python3
"""仓库/安装自检：frontmatter、目录结构、被引用的资源文件是否都存在。

用法:
    python scripts/selftest.py

退出码: 0 通过, 1 有错误
仅使用标准库，不联网。
"""
from __future__ import annotations

import re
import sys
import py_compile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"
REQUIRED_DIRS = ["workflows", "agents", "references", "templates", "scripts"]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REF_RE = re.compile(r"`((?:workflows|agents|references|templates|scripts)/[A-Za-z0-9._/-]+)`")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not SKILL.is_file():
        print(f"错误: 缺少 {SKILL}")
        return 1

    skill_text = SKILL.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)

    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        errors.append("SKILL.md frontmatter 缺 name")
    elif not NAME_RE.match(name):
        errors.append(f"SKILL.md name 不是 kebab-case: {name}")
    if not desc:
        errors.append("SKILL.md frontmatter 缺 description")

    for d in REQUIRED_DIRS:
        if not (ROOT / d).is_dir():
            errors.append(f"缺目录: {d}/")

    # 所有 md 里以反引号引用的资源路径
    md_files = list(ROOT.glob("*.md")) + list(ROOT.glob("workflows/*.md")) + list(ROOT.glob("agents/*.md")) + list(ROOT.glob("references/*.md")) + list(ROOT.glob("templates/*.md"))
    missing: set[str] = set()
    referenced: set[str] = set()
    for md in md_files:
        for rel in REF_RE.findall(md.read_text(encoding="utf-8")):
            rel = rel.rstrip("/")
            referenced.add(rel)
            if not (ROOT / rel).exists():
                missing.add(f"{rel} (被 {md.relative_to(ROOT)} 引用)")
    for item in sorted(missing):
        errors.append(f"引用的文件不存在: {item}")

    # 孤立文件（存在但文件名从未出现在任何文档里）——只警告
    all_text = "\n".join(p.read_text(encoding="utf-8") for p in md_files)
    for d in ["workflows", "agents", "references", "templates"]:
        for f in sorted((ROOT / d).glob("*.md")):
            rel = f.relative_to(ROOT).as_posix()
            if rel in all_text or f.name in all_text or f.stem in all_text:
                continue
            warnings.append(f"未被引用（可能是孤立的）: {rel}")

    # 脚本可编译
    for py in sorted((ROOT / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(py), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"脚本语法错误: {py.name}: {exc.msg}")

    print(f"仓库: {ROOT}")
    print(f"skill: {name or '(缺失)'}")
    files = [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    print(f"文件数: {len(files)}")
    for w in warnings:
        print(f"警告: {w}")
    for e in errors:
        print(f"错误: {e}")
    print("结论: " + ("通过" if not errors else f"不通过（{len(errors)} 个错误）"))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
