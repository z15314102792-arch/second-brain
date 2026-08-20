param(
  [Parameter(Mandatory=$true)][string]$Source,
  [string]$Transcript,
  [string]$Review,
  [ValidateSet('copy','reencode')][string]$RenderMode = 'reencode',
  [switch]$AutoHook,
  [switch]$Subtitles,
  [switch]$BurnSubtitles,
  [switch]$Render,
  [switch]$Jianying,
  [switch]$Effects,
  [string]$DeployDir,
  [switch]$NoAi,
  [string]$FunAsrPy = 'C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe',
  [string]$JianyingPy = 'C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
  $fallback = 'C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe'
  if (Test-Path $fallback) { $py = Get-Item $fallback } else { throw '找不到 Python。请安装 Python 3.10+，或把 Python 加入 PATH。' }
}

$editDir = Join-Path (Split-Path -Parent $Source) 'edit'
New-Item -ItemType Directory -Force -Path $editDir | Out-Null

if (-not $Transcript) {
  $Transcript = Join-Path $editDir 'transcript.raw.json'
  $transcriber = Join-Path $root 'scripts\transcribe.py'
  & $py.Source $transcriber '--source' $Source '--output' $Transcript '--funasr-py' $FunAsrPy
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$analyzer = Join-Path $root 'scripts\analyze_transcript.py'
$args = @($analyzer, '--source', $Source, '--transcript', $Transcript, '--edit-dir', $editDir)
if ($Review) { $args += @('--review', $Review) }
if ($NoAi) { $args += @('--no-ai') }
& $py.Source @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($AutoHook) {
  $hooker = Join-Path $root 'scripts\apply_hook.py'
  & $py.Source $hooker '--edl' (Join-Path $editDir 'edl.json') '--hooks' (Join-Path $editDir 'hook_candidates.json') '--output' (Join-Path $editDir 'edl.json')
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Subtitles -or $BurnSubtitles) {
  $subtitleBuilder = Join-Path $root 'scripts\build_subtitles.py'
  & $py.Source $subtitleBuilder '--transcript' (Join-Path $editDir 'transcript.normalized.json') '--edl' (Join-Path $editDir 'edl.json') '--srt' (Join-Path $editDir 'master.srt') '--ass' (Join-Path $editDir 'master.ass')
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Render) {
  $renderer = Join-Path $root 'scripts\render_from_edl.py'
  & $py.Source $renderer '--edl' (Join-Path $editDir 'edl.json') '--output' (Join-Path $editDir 'preview.mp4') '--mode' $RenderMode
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($BurnSubtitles) {
  if (-not $Render) { throw '-BurnSubtitles 需要同时指定 -Render。' }
  $burner = Join-Path $root 'scripts\burn_subtitles.py'
  $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
  if (-not $ffmpeg) { throw '找不到 ffmpeg，无法烧录字幕。' }
  & $py.Source $burner '--input' (Join-Path $editDir 'preview.mp4') '--ass' (Join-Path $editDir 'master.ass') '--output' (Join-Path $editDir 'final.mp4') '--ffmpeg' $ffmpeg.Source
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Jianying) {
  $exporter = Join-Path $root 'scripts\export_jianying.py'
  $ffprobe = Join-Path $root 'runtime\ffmpeg\bin\ffprobe.exe'
  $exportArgs = @($exporter, '--edl', (Join-Path $editDir 'edl.json'), '--srt', (Join-Path $editDir 'master.srt'), '--draft-dir', (Join-Path $editDir 'jianying_draft'), '--draft-name', '口播自动剪辑', '--ffprobe', $ffprobe)
  if ($Effects) {
    # 特效/音效：先合成音效素材（幂等），再按重点句规划位置，最后导出时写入草稿
    $ffmpeg = Join-Path $root 'runtime\ffmpeg\bin\ffmpeg.exe'
    & $JianyingPy (Join-Path $root 'scripts\gen_sfx.py') '--out' (Join-Path $root 'runtime\sfx') '--ffmpeg' $ffmpeg
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $JianyingPy (Join-Path $root 'scripts\plan_effects.py') '--edl' (Join-Path $editDir 'edl.json') '--transcript' (Join-Path $editDir 'transcript.normalized.json') '--sfx-dir' (Join-Path $root 'runtime\sfx') '--output' (Join-Path $editDir 'effects.json')
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $exportArgs += @('--effects', (Join-Path $editDir 'effects.json'))
  }
  if ($DeployDir) { $exportArgs += @('--deploy-dir', $DeployDir) }
  & $JianyingPy @exportArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Output "完成：$editDir"
