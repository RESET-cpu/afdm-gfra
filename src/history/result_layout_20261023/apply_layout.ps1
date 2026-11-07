$ErrorActionPreference = 'Stop'
$workspaceRoot = 'D:\afdm-gfra'
$recordRoot = Join-Path $workspaceRoot 'paper\docs\result_layout_20261023'
$layout = Get-Content -LiteralPath (Join-Path $recordRoot 'PLAN.json') -Raw | ConvertFrom-Json
$journal = [System.Collections.Generic.List[object]]::new()

function Safe-WorkspacePath([string]$value) {
    $absolute = [System.IO.Path]::GetFullPath($value)
    $prefix = $workspaceRoot.TrimEnd('\') + '\'
    if (-not $absolute.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path outside workspace: $absolute"
    }
    return $absolute
}

function Save-Journal {
    $journal | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $recordRoot 'OPERATIONS.json') -Encoding utf8
}

foreach ($move in $layout.moves) {
    $source = Safe-WorkspacePath $move.source
    $destination = Safe-WorkspacePath $move.destination
    $item = Get-Item -LiteralPath $source -Force
    if (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "Expected an original directory: $source"
    }
    if (Test-Path -LiteralPath $destination) { throw "Destination already exists: $destination" }
    if ($destination.StartsWith($source.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Cannot move directory into itself: $source"
    }
}

foreach ($name in $layout.experiments) {
    foreach ($kind in @('data', 'figures')) {
        $directory = Safe-WorkspacePath (Join-Path $workspaceRoot "result\$name\$kind")
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
}
New-Item -ItemType Directory -Path (Safe-WorkspacePath $layout.archive) | Out-Null

foreach ($move in $layout.moves) {
    # Validate both absolute endpoints immediately before the native move.
    $source = Safe-WorkspacePath $move.source
    $destination = Safe-WorkspacePath $move.destination
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $destination
    try {
        New-Item -ItemType Junction -Path $source -Target $destination | Out-Null
    } catch {
        if (-not (Test-Path -LiteralPath $source)) {
            $rollbackFrom = Safe-WorkspacePath $destination
            $rollbackTo = Safe-WorkspacePath $source
            Move-Item -LiteralPath $rollbackFrom -Destination $rollbackTo
        }
        throw
    }
    if ($move.hidden_compatibility) {
        $item = Get-Item -LiteralPath $source -Force
        $item.Attributes = $item.Attributes -bor [IO.FileAttributes]::Hidden
    }
    $journal.Add([ordered]@{action='move_with_compatibility_junction'; source=$source; destination=$destination; utc=[DateTime]::UtcNow.ToString('o')})
    Save-Journal
    if (($journal.Count % 20) -eq 0) { Write-Output "Organized $($journal.Count) directories" }
}

foreach ($value in $layout.protected_original_directories) {
    $path = Safe-WorkspacePath $value
    $item = Get-Item -LiteralPath $path -Force
    $item.Attributes = $item.Attributes -bor [IO.FileAttributes]::Hidden
    $journal.Add([ordered]@{action='keep_in_place_hidden_compatibility'; path=$path; utc=[DateTime]::UtcNow.ToString('o')})
}

foreach ($link in $layout.data_links) {
    $path = Safe-WorkspacePath $link.path
    $target = Safe-WorkspacePath $link.target
    if (-not (Test-Path -LiteralPath $target -PathType Container)) { throw "Missing data target: $target" }
    if (Test-Path -LiteralPath $path) { throw "Data entry already exists: $path" }
    New-Item -ItemType Directory -Path (Split-Path -Parent $path) -Force | Out-Null
    New-Item -ItemType Junction -Path $path -Target $target | Out-Null
    $item = Get-Item -LiteralPath $path -Force
    $item.Attributes = $item.Attributes -band (-bnot [IO.FileAttributes]::Hidden)
    $journal.Add([ordered]@{action='data_junction'; path=$path; target=$target; status=$link.status})
}
Save-Journal
$visible = @(Get-ChildItem -LiteralPath (Join-Path $workspaceRoot 'result') -Directory | Select-Object -ExpandProperty Name)
if (@(Compare-Object ($layout.experiments | Sort-Object) ($visible | Sort-Object)).Count -ne 0) {
    throw "Visible result directory differs from the eight-experiment plan."
}
Write-Output "Completed: eight visible experiment directories; $($layout.data_links.Count) data entries; original paths preserved."
