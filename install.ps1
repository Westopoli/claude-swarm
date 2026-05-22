# claude-swarm installer for Windows (PowerShell)
# Copies skills into ~/.claude/skills/ so Claude Code picks them up.
#
# Usage (run from PowerShell):
#   irm https://raw.githubusercontent.com/Westopoli/claude-swarm/main/install.ps1 | iex
#
# Or, after cloning the repo:
#   .\install.ps1

$ErrorActionPreference = "Stop"

$REPO_URL = "https://github.com/Westopoli/claude-swarm"
$SKILLS_DIR = Join-Path $env:USERPROFILE ".claude\skills"
$SKILLS = @("swarm", "swarm-review", "swarm-merge", "swarm-shared")

Write-Host "claude-swarm -- installing to $SKILLS_DIR"
New-Item -ItemType Directory -Force -Path $SKILLS_DIR | Out-Null

# Determine source: local checkout or fresh clone.
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (Test-Path (Join-Path $SCRIPT_DIR "skills")) {
    $SRC = Join-Path $SCRIPT_DIR "skills"
    Write-Host "  source: local checkout ($SRC)"
} else {
    $TMP = Join-Path $env:TEMP "claude-swarm-install-$([System.IO.Path]::GetRandomFileName())"
    Write-Host "  source: cloning $REPO_URL to temp dir"
    git clone --depth 1 $REPO_URL $TMP 2>$null
    $SRC = Join-Path $TMP "skills"
}

foreach ($skill in $SKILLS) {
    $dest = Join-Path $SKILLS_DIR $skill
    if (Test-Path $dest) {
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        $backup = "${dest}.bak.$timestamp"
        Write-Host "  ${skill}: existing install found, backing up to $(Split-Path -Leaf $backup)"
        Move-Item $dest $backup
    }
    Copy-Item -Recurse (Join-Path $SRC $skill) $dest
    Write-Host "  ${skill}: installed"
}

if ($TMP) { Remove-Item -Recurse -Force $TMP -ErrorAction SilentlyContinue }

Write-Host ""
Write-Host "Done. Restart Claude Code, then try:"
Write-Host "  /swarm"
Write-Host "  /swarm-review"
Write-Host "  /swarm-merge"
