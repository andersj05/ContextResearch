[CmdletBinding()]
param(
    [string]$Manifest = "catalog/paper-downloads.csv",
    [string]$OutputDirectory = "papers/academic",
    [string]$Category,
    [switch]$ForceRefresh
)

$ErrorActionPreference = "Stop"

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$manifestPath = (Resolve-Path (Join-Path $repositoryRoot $Manifest)).Path
$outputPath = Join-Path $repositoryRoot $OutputDirectory
$inventoryPath = Join-Path $repositoryRoot "catalog/pdf-inventory.csv"
$failurePath = Join-Path $repositoryRoot "catalog/pdf-download-failures.csv"

New-Item -ItemType Directory -Force -Path $outputPath | Out-Null

$rows = @(Import-Csv -LiteralPath $manifestPath)
if ($Category) {
    $rows = @($rows | Where-Object { $_.category -eq $Category })
}

if ($rows.Count -eq 0) {
    throw "No manifest rows matched the requested category '$Category'."
}

$pdfInfoCommand = Get-Command pdfinfo.exe -ErrorAction SilentlyContinue
$existingInventory = @()
if (Test-Path -LiteralPath $inventoryPath) {
    $existingInventory = @(Import-Csv -LiteralPath $inventoryPath)
}
$inventoryById = @{}
foreach ($item in $existingInventory) {
    $inventoryById[$item.source_id] = $item
}

$failures = [System.Collections.Generic.List[object]]::new()
$index = 0
foreach ($row in $rows) {
    $index += 1
    $destination = Join-Path $outputPath ($row.source_id + ".pdf")
    $relativePath = "papers/academic/" + $row.source_id + ".pdf"
    $needsDownload = $ForceRefresh -or -not (Test-Path -LiteralPath $destination)

    Write-Host ("[{0}/{1}] {2}" -f $index, $rows.Count, $row.source_id)

    try {
        if ($needsDownload) {
            $partial = $destination + ".part"
            if (Test-Path -LiteralPath $partial) {
                Remove-Item -LiteralPath $partial -Force
            }

            & curl.exe -L --fail --silent --show-error --retry 2 --retry-delay 2 `
                --connect-timeout 20 --max-time 240 `
                --user-agent "HarnessResearch/1.0 (academic corpus; contact via repository)" `
                --output $partial $row.pdf_url
            if ($LASTEXITCODE -ne 0) {
                throw "curl exited with code $LASTEXITCODE"
            }

            $stream = [System.IO.File]::OpenRead($partial)
            try {
                $header = New-Object byte[] 5
                $read = $stream.Read($header, 0, 5)
            }
            finally {
                $stream.Dispose()
            }
            $signature = [System.Text.Encoding]::ASCII.GetString($header, 0, $read)
            if ($signature -ne "%PDF-") {
                throw "Downloaded response is not a PDF (signature '$signature')"
            }

            Move-Item -LiteralPath $partial -Destination $destination -Force
        }

        $file = Get-Item -LiteralPath $destination
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash.ToLowerInvariant()
        $pages = ""
        $encrypted = ""
        if ($pdfInfoCommand) {
            $infoLines = @(& $pdfInfoCommand.Source $destination 2>&1)
            if ($LASTEXITCODE -ne 0) {
                throw "pdfinfo could not parse the downloaded file"
            }
            foreach ($line in $infoLines) {
                if ($line -match '^Pages:\s+(\d+)') { $pages = $Matches[1] }
                if ($line -match '^Encrypted:\s+(\S+)') { $encrypted = $Matches[1] }
            }
        }

        $inventoryById[$row.source_id] = [pscustomobject]@{
            source_id = $row.source_id
            category = $row.category
            title = $row.title
            publication_status = $row.publication_status
            landing_url = $row.landing_url
            pdf_url = $row.pdf_url
            pdf_path = $relativePath
            bytes = $file.Length
            pages = $pages
            encrypted = $encrypted
            sha256 = $hash
            accessed = (Get-Date).ToString("yyyy-MM-dd")
            fetch_status = if ($needsDownload) { "downloaded" } else { "verified-existing" }
        }
    }
    catch {
        if (Test-Path -LiteralPath ($destination + ".part")) {
            Remove-Item -LiteralPath ($destination + ".part") -Force
        }
        $failures.Add([pscustomobject]@{
            source_id = $row.source_id
            pdf_url = $row.pdf_url
            attempted = (Get-Date).ToString("s")
            error = $_.Exception.Message
        })
        Write-Warning ("Failed {0}: {1}" -f $row.source_id, $_.Exception.Message)
    }
}

@($inventoryById.Values | Sort-Object category, source_id) |
    Export-Csv -LiteralPath $inventoryPath -NoTypeInformation -Encoding utf8

if ($failures.Count -gt 0) {
    $failures | Export-Csv -LiteralPath $failurePath -NoTypeInformation -Encoding utf8
    Write-Warning ("{0} download(s) failed; see {1}" -f $failures.Count, $failurePath)
}
elseif (Test-Path -LiteralPath $failurePath) {
    Remove-Item -LiteralPath $failurePath -Force
}

Write-Host ("Inventory now contains {0} verified PDF(s)." -f $inventoryById.Count)
