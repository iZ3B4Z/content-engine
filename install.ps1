# Content Engine installer (Windows). Usage: powershell -File install.ps1 [<parent-dir>]
param([string]$Parent = "")
$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/iZ3B4Z/content-engine"
$Dest = Join-Path $HOME ".claude/skills/content-engine"
$Src  = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
if (Test-Path (Join-Path $Src "scripts/common.py")) {
  Copy-Item -Recurse -Force (Join-Path $Src "scripts"),(Join-Path $Src "skills") $Dest
} else {
  $tmp = New-Item -ItemType Directory -Path (Join-Path $env:TEMP ([guid]::NewGuid()))
  git clone --depth 1 $RepoUrl (Join-Path $tmp "ce")
  Copy-Item -Recurse -Force (Join-Path $tmp "ce/scripts"),(Join-Path $tmp "ce/skills") $Dest
}
if ($Parent -ne "") { python3 (Join-Path $Dest "scripts/init_repo.py") $Parent }
Write-Host "Done."
