#!/usr/bin/env bash
# 安装到 DSH 的 skills 目录。
#
# 用法:
#   ./install/install.sh              # 用户级 ~/.dsh/skills（所有工作区可用）
#   ./install/install.sh --project    # 当前工作区 .dsh/skills（仅本项目）
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET=""
PROJECT=0

for arg in "$@"; do
  case "$arg" in
    --project) PROJECT=1 ;;
    -h|--help) echo "用法: $0 [--project] [目标目录]"; exit 0 ;;
    *) TARGET="$arg" ;;
  esac
done

if [ -z "$TARGET" ]; then
  if [ "$PROJECT" = "1" ]; then
    TARGET="$PWD/.dsh/skills/ars-research-suite"
  else
    TARGET="$HOME/.dsh/skills/ars-research-suite"
  fi
fi

if [ -e "$TARGET" ]; then
  echo "目标已存在: $TARGET"
  echo "请先移走或删除后再安装。"
  exit 1
fi

mkdir -p "$TARGET"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude '.git' --exclude '.github' "$REPO/" "$TARGET/"
else
  cp -R "$REPO/." "$TARGET/"
  rm -rf "$TARGET/.git" "$TARGET/.github"
fi

echo "已安装到: $TARGET"
echo "在 DSH 新会话中应能看到 skill: ars-research-suite（或输入 /ars-research-suite）"
echo "自检: python3 \"$TARGET/scripts/selftest.py\""
