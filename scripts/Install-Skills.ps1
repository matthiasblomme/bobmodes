# Install-Skills.ps1 - install the modes in this repo as Claude Code skills.
#
# The Bob counterpart is Import-BobModes.ps1, which merges the .bobmodes definitions into a
# project's .bob/custom_modes.yaml. This script is the Claude Code side: it links each mode
# folder into ~/.claude/skills, where skills are discovered.
#
# Why a junction rather than a copy: Claude Code takes the invocable skill identifier from
# the FOLDER NAME under ~/.claude/skills, not from the SKILL.md frontmatter. Linking keeps
# one copy of the truth, so a git pull updates the installed skills with no second step, and
# it makes the folder name the same string as the declared name by construction.
#
# Phase 1 validates that equality across every mode and REFUSES TO INSTALL ANYTHING if any
# of them disagree. A folder whose name differs from its frontmatter means you type one name
# while the docs describe another.
#
# Skills from other sources are never touched: real directories that are not ours and
# junctions pointing outside this repo are left alone, and a real directory that shadows one
# of ours is moved to ~/.claude/skills-backup rather than deleted.
#
# Usage:
#   .\scripts\Install-Skills.ps1 -WhatIf    # preview, changes nothing
#   .\scripts\Install-Skills.ps1            # install / refresh
#   .\scripts\Install-Skills.ps1 -Prune     # also remove leftovers from a renamed mode
#
# Windows only (it creates NTFS junctions). On macOS / Linux, copy the folders manually -
# see the root README.

[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [switch]$Prune
)

$ErrorActionPreference = 'Stop'
$repoRoot  = Split-Path -Parent $PSScriptRoot
$skillsDir = Join-Path $env:USERPROFILE '.claude\skills'
$backupDir = Join-Path $env:USERPROFILE '.claude\skills-backup'
# Trailing separator matters: without it a sibling directory whose name merely starts with
# this one (bobmodes2) would be mistaken for ours.
$repoPrefix = $repoRoot.TrimEnd('\') + '\'

# The modes live under bobmodes/. Anything with a SKILL.md there is a skill.
$skillRoots = @('bobmodes')

function Get-FrontmatterName {
    param([string]$SkillMd)
    foreach ($line in Get-Content $SkillMd -TotalCount 20) {
        if ($line -match '^name:\s*(.+?)\s*$') { return $Matches[1] }
    }
    return $null
}

function Get-BobmodesSlug {
    param([string]$Bobmodes)
    foreach ($line in Get-Content $Bobmodes -TotalCount 40) {
        if ($line -match '^\s*-?\s*slug:\s*(.+?)\s*$') { return $Matches[1] }
    }
    return $null
}

# --- Phase 1: discover and validate -----------------------------------------

$desired = @{}
$problems = @()

foreach ($root in $skillRoots) {
    $rootPath = Join-Path $repoRoot $root
    if (-not (Test-Path $rootPath)) { continue }
    Get-ChildItem $rootPath -Recurse -Directory -Force |
        Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
        ForEach-Object {
            $folder   = $_.Name
            $declared = Get-FrontmatterName (Join-Path $_.FullName 'SKILL.md')

            if (-not $declared) {
                $problems += "$folder : SKILL.md has no 'name:' in its frontmatter"
            } elseif ($declared -ne $folder) {
                $problems += "$folder : folder name vs SKILL.md name: '$declared'"
            }

            $bobmodes = Join-Path $_.FullName '.bobmodes'
            if (Test-Path $bobmodes) {
                $slug = Get-BobmodesSlug $bobmodes
                if ($slug -and $slug -ne $folder) {
                    $problems += "$folder : folder name vs .bobmodes slug: '$slug'"
                }
            }

            if ($desired.ContainsKey($folder)) {
                $problems += "$folder : duplicate skill name (also at $($desired[$folder]))"
            } else {
                $desired[$folder] = $_.FullName
            }
        }
}

if ($problems.Count -gt 0) {
    Write-Host ''
    Write-Host 'Name drift detected - nothing was installed:' -ForegroundColor Red
    $problems | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host ''
    Write-Host 'Folder name, SKILL.md name: and .bobmodes slug: must be identical.'
    exit 1
}

if ($desired.Count -eq 0) { Write-Host "No skills found under $($skillRoots -join ', ')."; exit 1 }
Write-Host "Validated $($desired.Count) skills - folder name, frontmatter name and slug agree."

# --- Phase 2: classify what is already installed ----------------------------
# A dangling junction is invisible to Test-Path (it resolves the target, which is gone) while
# the directory entry still exists and still blocks mklink. So enumerate the parent and read
# the reparse data instead of testing the path.

if (-not (Test-Path $skillsDir)) {
    if ($PSCmdlet.ShouldProcess($skillsDir, 'create skills directory')) {
        New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null
    }
}

$existing = @{}
Get-ChildItem $skillsDir -Force -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $existing[$_.Name] = $_
}

$actions = New-Object System.Collections.Generic.List[object]
function Add-Action {
    param($Name, $Action, $Detail)
    $actions.Add([pscustomobject]@{ Name = $Name; Action = $Action; Detail = $Detail })
}

foreach ($name in $desired.Keys | Sort-Object) {
    $source = $desired[$name]

    if (-not $existing.ContainsKey($name)) {
        Add-Action $name 'Create' $source
        continue
    }

    $entry      = $existing[$name]
    $isJunction = [bool]($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)

    if ($isJunction) {
        $target = $entry.Target
        if ($target) { $target = $target.TrimEnd('\') }
        if ($target -eq $source.TrimEnd('\')) {
            Add-Action $name 'Unchanged' $target
        } elseif ($target -and $target.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            Add-Action $name 'Recreate' "was -> $target"
        } else {
            Add-Action $name 'Skip-Foreign' "junction points outside the repo -> $target"
        }
    } else {
        # A real directory. Only replace it if it is a copy of one of OUR skills - decided by
        # reading its frontmatter, never by comparing folder names, because a stale copy can
        # sit under a differently-spelled folder than the name it declares.
        $itsSkillMd = Join-Path $entry.FullName 'SKILL.md'
        $itsName = if (Test-Path $itsSkillMd) { Get-FrontmatterName $itsSkillMd } else { $null }
        if ($itsName -and $desired.ContainsKey($itsName)) {
            Add-Action $name 'Replace' "existing copy (declares '$itsName') -> backed up"
        } else {
            Add-Action $name 'Skip-Foreign' 'real directory, not one of ours'
        }
    }
}

# Leftovers under a name we no longer use: a junction into this repo whose mode was renamed,
# or a real copy of one of our skills sitting under its old folder name.
foreach ($name in $existing.Keys | Sort-Object) {
    if ($desired.ContainsKey($name)) { continue }
    $entry      = $existing[$name]
    $isJunction = [bool]($entry.Attributes -band [IO.FileAttributes]::ReparsePoint)

    if ($isJunction) {
        $target = $entry.Target
        if ($target -and $target.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            if ($Prune) { Add-Action $name 'Prune' "stale junction -> $target" }
            else        { Add-Action $name 'Stale' 'points into the repo but no such skill; re-run with -Prune' }
        }
        continue
    }

    $itsSkillMd = Join-Path $entry.FullName 'SKILL.md'
    if (-not (Test-Path $itsSkillMd)) { continue }
    $itsName = Get-FrontmatterName $itsSkillMd
    if ($itsName -and $desired.ContainsKey($itsName)) {
        Add-Action $name 'Backup-Stale' "copy declaring '$itsName' under an old folder name"
    }
}

# --- Phase 3: apply ---------------------------------------------------------

foreach ($a in $actions) {
    $link = Join-Path $skillsDir $a.Name
    switch ($a.Action) {
        'Create' {
            if ($PSCmdlet.ShouldProcess($link, 'create junction')) {
                cmd /c mklink /J "$link" "$($desired[$a.Name])" | Out-Null
            }
        }
        'Recreate' {
            if ($PSCmdlet.ShouldProcess($link, 'recreate junction')) {
                cmd /c rmdir "$link" | Out-Null
                cmd /c mklink /J "$link" "$($desired[$a.Name])" | Out-Null
            }
        }
        'Replace' {
            if ($PSCmdlet.ShouldProcess($link, 'back up real directory and junction')) {
                if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }
                $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                # Move OUT of the skills directory - a backup left in place would itself be
                # discovered as a skill.
                Move-Item -Path $link -Destination (Join-Path $backupDir "$($a.Name)-$stamp") -Force
                cmd /c mklink /J "$link" "$($desired[$a.Name])" | Out-Null
            }
        }
        'Prune' {
            if ($PSCmdlet.ShouldProcess($link, 'remove stale junction')) {
                # cmd /c rmdir removes the link only. Remove-Item -Recurse has historically
                # followed junctions and deleted the target's contents.
                cmd /c rmdir "$link" | Out-Null
            }
        }
        'Backup-Stale' {
            if ($PSCmdlet.ShouldProcess($link, 'move stale copy out of the skills directory')) {
                if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }
                $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
                Move-Item -Path $link -Destination (Join-Path $backupDir "$($a.Name)-$stamp") -Force
            }
        }
    }
}

# --- Phase 4: report --------------------------------------------------------

Write-Host ''
$actions | Sort-Object Action, Name | Format-Table -AutoSize Name, Action, Detail

$summary = $actions | Group-Object Action | ForEach-Object { "$($_.Name)=$($_.Count)" }
Write-Host ("Summary: " + ($summary -join ', '))

$conflicts = @($actions | Where-Object { $_.Action -eq 'Skip-Foreign' -and $desired.ContainsKey($_.Name) })
if ($conflicts.Count -gt 0) {
    Write-Host ''
    Write-Host "$($conflicts.Count) skill(s) could not be installed - another entry occupies the name:" -ForegroundColor Yellow
    $conflicts | ForEach-Object { Write-Host "  $($_.Name): $($_.Detail)" -ForegroundColor Yellow }
    exit 1
}

$stale = @($actions | Where-Object { $_.Action -eq 'Stale' })
if ($stale.Count -gt 0) {
    Write-Host ''
    Write-Host "$($stale.Count) stale junction(s) left in place. Re-run with -Prune to remove them." -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Start a new Claude Code session to pick up the changes (skills are enumerated at session start).'
