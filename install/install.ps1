# 安装到 DSH 的 skills 目录。
#
# 用法:
#   .\install\install.ps1                 # 用户级 ~/.dsh/skills（所有工作区可用）
#   .\install\install.ps1 -Project        # 当前工作区 .dsh/skills（仅本项目）
#   .\install\install.ps1 -Force          # 已存在时先备份再覆盖
#   .\install\install.ps1 -Target D:\x\skills\ars-research-suite
[CmdletBinding()]
param(
    [string]$Target,
    [switch]$Project,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

if (-not $Target) {
    if ($Project) {
        $base = Join-Path (Get-Location).Path '.dsh\skills'
    } else {
        $base = Join-Path $env:USERPROFILE '.dsh\skills'
    }
    $Target = Join-Path $base 'ars-research-suite'
}

if (Test-Path $Target) {
    if (-not $Force) {
        throw "目标已存在: $Target`n如需覆盖请加 -Force（会先备份为 *.bak-<时间>）"
    }
    $backup = "$Target.bak-$([datetime]::Now.ToString('yyyyMMdd-HHmmss'))"
    Move-Item -LiteralPath $Target -Destination $backup
    Write-Host "已备份到: $backup"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
New-Item -ItemType Directory -Force -Path $Target | Out-Null
Get-ChildItem -LiteralPath $repo -Force |
    Where-Object { $_.Name -notin @('.git') } |
    ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $Target -Recurse -Force }

Write-Host "已安装到: $Target"
Write-Host "在 DSH 新会话中应能看到 skill: ars-research-suite（或输入 /ars-research-suite）"
Write-Host "自检: python `"$Target\scripts\selftest.py`""
