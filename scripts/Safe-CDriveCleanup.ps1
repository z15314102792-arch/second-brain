#requires -Version 5.1

<#
.SYNOPSIS
    C 盘保守清理工具。版本：v1.3

.DESCRIPTION
    默认只扫描并预览，不删除任何文件。
    仅处理明确列入白名单、能够由系统或软件重新生成的临时文件和缓存。
    不删除整个目录，不处理文档、聊天记录、剪映草稿、浏览器账号数据、
    Windows Installer、WinSxS、更新数据库、驱动、注册表或系统还原点。

.PARAMETER Execute
    实际删除。没有此参数时永远只预览。

.PARAMETER MinAgeDays
    仅处理至少多少天未修改的文件，默认 7 天。

.PARAMETER IncludeBrowserCaches
    包含 Chrome 和 Edge 的网页、代码、图形缓存；浏览器运行时自动跳过。

.PARAMETER IncludeAppCaches
    包含剪映、飞书、豆包和 VS Code 的可再生缓存；相关软件运行时自动跳过。

.PARAMETER IncludeRetiredCopies
    包含已迁移到 D 盘的 C 盘旧副本。仅删除在 D 盘找到同路径、同字节数文件的副本。
    这是一次性项目，不应放入定时任务。

.PARAMETER IncludeRecycleBin
    包含回收站。默认不包含，因为回收站中的文件可能仍需恢复。

.PARAMETER Yes
    配合 -Execute 跳过输入 CLEAN 的二次确认。建议仅由已审阅的自动化调用。

.EXAMPLE
    .\Safe-CDriveCleanup.ps1
    只预览基础安全项目。

.EXAMPLE
    .\Safe-CDriveCleanup.ps1 -IncludeBrowserCaches -IncludeAppCaches
    预览基础项目和软件缓存，仍不删除。

.EXAMPLE
    .\Safe-CDriveCleanup.ps1 -Execute
    执行基础安全清理，删除前要求输入 CLEAN。
#>

[CmdletBinding()]
param(
    [switch]$Execute,
    [ValidateRange(1, 3650)]
    [int]$MinAgeDays = 7,
    [switch]$IncludeBrowserCaches,
    [switch]$IncludeAppCaches,
    [switch]$IncludeRetiredCopies,
    [switch]$IncludeRecycleBin,
    [switch]$Yes
)

$ErrorActionPreference = 'Continue'
$script:Cutoff = (Get-Date).AddDays(-$MinAgeDays)
$script:DeletedBytes = [int64]0
$script:DeletedFiles = 0
$script:FailedFiles = 0

function Test-IsAdministrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PathInsideRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    try {
        $fullPath = [IO.Path]::GetFullPath($Path)
        $fullRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\') + '\'
        return $fullPath.StartsWith($fullRoot, [StringComparison]::OrdinalIgnoreCase)
    }
    catch {
        return $false
    }
}

function Test-ProcessRunning {
    param([string[]]$Names)

    foreach ($name in $Names) {
        if (Get-Process -Name $name -ErrorAction SilentlyContinue) {
            return $true
        }
    }
    return $false
}

function Get-SafeFiles {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [string]$Filter = '*',
        [switch]$IgnoreAge
    )

    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return @()
    }

    return @(
        Get-ChildItem -LiteralPath $Root -Filter $Filter -Recurse -File -Force -ErrorAction SilentlyContinue |
            Where-Object {
                (Test-PathInsideRoot -Path $_.FullName -Root $Root) -and
                -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -and
                ($IgnoreAge -or $_.LastWriteTime -lt $script:Cutoff)
            }
    )
}

function Add-Target {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.ArrayList]$List,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Root,
        [string]$Filter = '*',
        [string[]]$BlockProcesses = @(),
        [switch]$RequiresAdmin
    )

    [void]$List.Add([pscustomobject]@{
        Name = $Name
        Root = $Root
        Filter = $Filter
        BlockProcesses = $BlockProcesses
        RequiresAdmin = [bool]$RequiresAdmin
    })
}

function Add-ChromiumProfileCaches {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.ArrayList]$List,
        [Parameter(Mandatory = $true)][string]$UserDataRoot,
        [Parameter(Mandatory = $true)][string]$ProductName,
        [Parameter(Mandatory = $true)][string[]]$BlockProcesses
    )

    if (-not (Test-Path -LiteralPath $UserDataRoot)) { return }

    Get-ChildItem -LiteralPath $UserDataRoot -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'Default' -or $_.Name -like 'Profile *' } |
        ForEach-Object {
            foreach ($cacheName in @('Cache', 'Code Cache', 'GPUCache')) {
                $cachePath = Join-Path $_.FullName $cacheName
                Add-Target -List $List -Name "$ProductName $($_.Name) $cacheName" `
                    -Root $cachePath -BlockProcesses $BlockProcesses
            }
        }
}

function Add-DiscoveredCaches {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.ArrayList]$List,
        [Parameter(Mandatory = $true)][string]$SearchRoot,
        [Parameter(Mandatory = $true)][string]$ProductName,
        [Parameter(Mandatory = $true)][string[]]$BlockProcesses
    )

    if (-not (Test-Path -LiteralPath $SearchRoot)) { return }

    Get-ChildItem -LiteralPath $SearchRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -in @('Cache', 'Code Cache', 'GPUCache') } |
        ForEach-Object {
            Add-Target -List $List -Name "$ProductName $($_.Name)" -Root $_.FullName `
                -BlockProcesses $BlockProcesses
        }
}

function Get-TargetPreview {
    param([pscustomobject]$Target, [bool]$IsAdmin)

    if ($Target.RequiresAdmin -and -not $IsAdmin) {
        return [pscustomobject]@{ Name = $Target.Name; Root = $Target.Root; Status = '跳过：需要管理员权限'; Files = 0; Bytes = 0 }
    }

    if ($Target.BlockProcesses.Count -gt 0 -and (Test-ProcessRunning $Target.BlockProcesses)) {
        return [pscustomobject]@{ Name = $Target.Name; Root = $Target.Root; Status = '跳过：相关软件正在运行'; Files = 0; Bytes = 0 }
    }

    $files = Get-SafeFiles -Root $Target.Root -Filter $Target.Filter
    $bytes = [int64](($files | Measure-Object Length -Sum).Sum)
    return [pscustomobject]@{
        Name = $Target.Name
        Root = $Target.Root
        Status = if ($files.Count -gt 0) { '可处理' } else { '没有符合条件的文件' }
        Files = $files.Count
        Bytes = $bytes
        FileList = $files
    }
}

function Remove-PreviewFiles {
    param([pscustomobject]$Preview)

    foreach ($file in @($Preview.FileList)) {
        if (-not (Test-PathInsideRoot -Path $file.FullName -Root $Preview.Root)) {
            $script:FailedFiles++
            continue
        }

        try {
            Remove-Item -LiteralPath $file.FullName -Force -ErrorAction Stop
            $script:DeletedBytes += $file.Length
            $script:DeletedFiles++
        }
        catch {
            $script:FailedFiles++
        }
    }
}

function Get-MirroredFiles {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Target
    )

    if (-not (Test-Path -LiteralPath $Source -PathType Container)) { return @() }
    if (-not (Test-Path -LiteralPath $Target -PathType Container)) { return @() }

    $targetLengths = @{}
    Get-ChildItem -LiteralPath $Target -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) } |
        ForEach-Object {
            $targetRelative = $_.FullName.Substring($Target.Length).TrimStart('\')
            $targetLengths[$targetRelative] = [int64]$_.Length
        }

    $matched = New-Object System.Collections.ArrayList
    $sourceFiles = @(
        Get-ChildItem -LiteralPath $Source -Recurse -File -Force -ErrorAction SilentlyContinue |
            Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) }
    )
    foreach ($sourceFile in $sourceFiles) {
        $relative = $sourceFile.FullName.Substring($Source.Length).TrimStart('\')
        if ($targetLengths.ContainsKey($relative) -and
            $targetLengths[$relative] -eq $sourceFile.Length) {
            [void]$matched.Add($sourceFile)
        }
    }
    return @($matched)
}

$isAdmin = Test-IsAdministrator
$targets = New-Object System.Collections.ArrayList

# 基础项目：只处理超过保留天数的可再生文件。
Add-Target -List $targets -Name '用户临时文件' -Root $env:TEMP
Add-Target -List $targets -Name 'Windows 临时文件' -Root 'C:\Windows\Temp' -RequiresAdmin
Add-Target -List $targets -Name '用户崩溃转储' -Root "$env:LOCALAPPDATA\CrashDumps"
Add-Target -List $targets -Name 'Windows 错误报告队列' -Root "$env:ProgramData\Microsoft\Windows\WER\ReportQueue"
Add-Target -List $targets -Name 'Windows 错误报告归档' -Root "$env:ProgramData\Microsoft\Windows\WER\ReportArchive"
Add-Target -List $targets -Name 'DirectX 着色器缓存' -Root "$env:LOCALAPPDATA\D3DSCache"
Add-Target -List $targets -Name '资源管理器缩略图缓存' `
    -Root "$env:LOCALAPPDATA\Microsoft\Windows\Explorer" -Filter 'thumbcache_*.db' `
    -BlockProcesses @('explorer')

if ($IncludeBrowserCaches) {
    Add-ChromiumProfileCaches -List $targets `
        -UserDataRoot "$env:LOCALAPPDATA\Google\Chrome\User Data" `
        -ProductName 'Chrome' -BlockProcesses @('chrome')
    Add-ChromiumProfileCaches -List $targets `
        -UserDataRoot "$env:LOCALAPPDATA\Microsoft\Edge\User Data" `
        -ProductName 'Edge' -BlockProcesses @('msedge')
}

if ($IncludeAppCaches) {
    Add-Target -List $targets -Name '剪映缓存' `
        -Root "$env:LOCALAPPDATA\JianyingPro\User Data\Cache" `
        -BlockProcesses @('JianyingPro')
    Add-ChromiumProfileCaches -List $targets `
        -UserDataRoot "$env:LOCALAPPDATA\Doubao\User Data" `
        -ProductName '豆包' -BlockProcesses @('Doubao')
    Add-DiscoveredCaches -List $targets `
        -SearchRoot "$env:APPDATA\LarkShell\aha\users" `
        -ProductName '飞书' -BlockProcesses @('Feishu', 'Lark')
    Add-Target -List $targets -Name 'VS Code 网页缓存' `
        -Root "$env:APPDATA\Code\Cache" -BlockProcesses @('Code')
    Add-Target -List $targets -Name 'VS Code 图形缓存' `
        -Root "$env:APPDATA\Code\GPUCache" -BlockProcesses @('Code')
}

$previews = @($targets | ForEach-Object { Get-TargetPreview -Target $_ -IsAdmin $isAdmin })
$previewBytes = [int64](($previews | Measure-Object Bytes -Sum).Sum)

Write-Host ''
Write-Host 'C 盘安全清理预览（版本 v1.3）' -ForegroundColor Cyan
Write-Host "模式：$(if ($Execute) { '执行' } else { '只预览，不删除' })；保留期：$MinAgeDays 天"
$previews |
    Select-Object Name, Status, Files, @{Name = 'GB'; Expression = { [math]::Round($_.Bytes / 1GB, 3) } }, Root |
    Format-Table -AutoSize
Write-Host ("本轮基础/缓存候选：{0:N3} GB" -f ($previewBytes / 1GB))

$retiredPreviews = @()
if ($IncludeRetiredCopies) {
    $retiredDefinitions = @(
        [pscustomobject]@{ Name = '旧 Ollama 模型'; Source = "$env:USERPROFILE\.ollama\models"; Target = 'D:\AIData\Ollama'; Setting = 'OLLAMA_MODELS'; Expected = 'D:\AIData\Ollama'; Block = @('ollama') },
        [pscustomobject]@{ Name = '旧 ModelScope 缓存'; Source = "$env:USERPROFILE\.cache\modelscope"; Target = 'D:\AIData\ModelScope'; Setting = 'MODELSCOPE_CACHE'; Expected = 'D:\AIData\ModelScope'; Block = @() },
        [pscustomobject]@{ Name = '旧 npm 缓存'; Source = "$env:LOCALAPPDATA\npm-cache"; Target = 'D:\DevCache\npm'; Setting = 'NPM_CONFIG_CACHE'; Expected = 'D:\DevCache\npm'; Block = @('npm') },
        [pscustomobject]@{ Name = '旧 pip 缓存'; Source = "$env:LOCALAPPDATA\pip\Cache"; Target = 'D:\DevCache\pip\cache'; Setting = 'PIP_CACHE_DIR'; Expected = 'D:\DevCache\pip'; Block = @() },
        [pscustomobject]@{ Name = '旧 pnpm 存储'; Source = "$env:LOCALAPPDATA\pnpm\store"; Target = 'D:\DevCache\pnpm-store'; Setting = $null; Expected = $null; Block = @('pnpm') }
    )

    foreach ($definition in $retiredDefinitions) {
        $settingOk = $true
        if ($definition.Setting) {
            $actual = [Environment]::GetEnvironmentVariable($definition.Setting, 'User')
            $settingOk = [string]::Equals($actual, $definition.Expected, [StringComparison]::OrdinalIgnoreCase)
        }
        if ($definition.Name -eq '旧 pnpm 存储') {
            $pnpmPath = (& pnpm config get store-dir 2>$null | Select-Object -First 1)
            $settingOk = [string]::Equals($pnpmPath, 'D:\DevCache\pnpm-store', [StringComparison]::OrdinalIgnoreCase)
        }

        if (-not $settingOk) {
            $retiredPreviews += [pscustomobject]@{ Name = $definition.Name; Status = '跳过：新路径设置未通过验证'; Files = 0; Bytes = 0; Root = $definition.Source }
            continue
        }
        if ($definition.Block.Count -gt 0 -and (Test-ProcessRunning $definition.Block)) {
            $retiredPreviews += [pscustomobject]@{ Name = $definition.Name; Status = '跳过：相关软件正在运行'; Files = 0; Bytes = 0; Root = $definition.Source }
            continue
        }

        $mirrored = @(Get-MirroredFiles -Source $definition.Source -Target $definition.Target)
        $bytes = [int64](($mirrored | Measure-Object Length -Sum).Sum)
        $retiredPreviews += [pscustomobject]@{
            Name = $definition.Name
            Status = '仅列出已在 D 盘找到同字节副本的文件'
            Files = $mirrored.Count
            Bytes = $bytes
            Root = $definition.Source
            FileList = $mirrored
        }
    }

    Write-Host ''
    Write-Host '一次性旧副本候选' -ForegroundColor Yellow
    $retiredPreviews |
        Select-Object Name, Status, Files, @{Name = 'GB'; Expression = { [math]::Round($_.Bytes / 1GB, 3) } }, Root |
        Format-Table -AutoSize
    $retiredBytes = [int64](($retiredPreviews | Measure-Object Bytes -Sum).Sum)
    Write-Host ("一次性旧副本候选：{0:N3} GB" -f ($retiredBytes / 1GB))
}

if ($IncludeRecycleBin) {
    Write-Warning '已选择回收站。清空后不能通过回收站恢复，且它不属于固定自动清理项目。'
}

if (-not $Execute) {
    Write-Host ''
    Write-Host '预览结束：没有删除任何文件。要实际执行必须显式添加 -Execute。' -ForegroundColor Green
    exit 0
}

if (-not $Yes) {
    $answer = Read-Host '即将永久删除上述白名单文件。请输入 CLEAN 继续'
    if ($answer -cne 'CLEAN') {
        Write-Host '已取消，没有删除任何文件。' -ForegroundColor Yellow
        exit 0
    }
}

$freeBefore = (Get-PSDrive -Name C).Free
foreach ($preview in $previews) {
    if ($preview.Status -eq '可处理') {
        Remove-PreviewFiles -Preview $preview
    }
}
foreach ($preview in $retiredPreviews) {
    if ($preview.FileList) {
        Remove-PreviewFiles -Preview $preview
    }
}

if ($IncludeRecycleBin) {
    try {
        Clear-RecycleBin -DriveLetter C -Force -ErrorAction Stop
    }
    catch {
        Write-Warning "回收站未能清空：$($_.Exception.Message)"
    }
}

$freeAfter = (Get-PSDrive -Name C).Free
Write-Host ''
Write-Host '清理完成' -ForegroundColor Green
Write-Host ("成功删除：{0} 个文件" -f $script:DeletedFiles)
Write-Host ("跳过或失败：{0} 个文件" -f $script:FailedFiles)
Write-Host ("按文件大小统计：{0:N3} GB" -f ($script:DeletedBytes / 1GB))
Write-Host ("C 盘实际增加：{0:N3} GB" -f (($freeAfter - $freeBefore) / 1GB))
