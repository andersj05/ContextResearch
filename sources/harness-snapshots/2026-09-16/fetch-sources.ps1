param([string]$Harness)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$repos = @{
  codex = @{ repo='openai/codex'; sha='da18000cae9884ab45f83b2d07fbd5a220a1de39'; patterns=@('^codex-rs/core/src/compact[^/]*\.rs$', '^codex-rs/core/src/context_manager/(history|normalize)\.rs$', '^codex-rs/core/src/state/auto_compact_window\.rs$', '^codex-rs/core/src/codex\.rs$', '^codex-rs/(models-manager/models\.json|models-manager/src/model_info\.rs|protocol/src/openai_models\.rs)$', '^codex-rs/utils/output-truncation/src/lib\.rs$', '^codex-rs/prompts/templates/compact/', '^codex-rs/core/src/(exec|unified_exec)') }
  pi = @{ repo='earendil-works/pi'; sha='bdee230f1ea4beec1972c54716433ced691a92b5'; patterns=@('^packages/coding-agent/docs/compaction\.md$', '^packages/coding-agent/src/core/(compaction/|tools/(truncate|bash|read|grep)\.ts$|settings-manager\.ts$|agent-session\.ts$)', '^packages/agent/src/harness/(compaction/|utils/truncate\.ts$)', '^packages/coding-agent/examples/extensions/custom-compaction\.ts$') }
  omp = @{ repo='can1357/oh-my-pi'; sha='60c9a115b2e8decc0f75825459362d14188a8bc0'; patterns=@('^docs/(compaction|tools/context-notes|tools/new-context)\.md$', '^packages/agent/src/(compaction/|append-only-context\.ts$)', '^packages/coding-agent/src/(session/(compaction-methods|context-notes)\.ts$|config/settings-schema\.ts$|tools/(output-meta|terminal-output)\.ts$)', '^packages/snapcompact/README\.md$', '^crates/pi-builtins/src/truncate\.rs$') }
}
$spec = $repos[$Harness]
$tree = Get-Content -Raw -LiteralPath (Join-Path $root "$Harness-tree.json") | ConvertFrom-Json
$pattern = $spec.patterns -join '|'
$paths = @($tree.tree | Where-Object { $_.type -eq 'blob' -and $_.path -match $pattern -and $_.path -notmatch '(tests?/|snapshots/)' } | Select-Object -ExpandProperty path)
$paths | ForEach-Object -Parallel {
  $spec = $using:spec
  $dest = Join-Path (Join-Path $using:root $using:Harness) $_
  New-Item -ItemType Directory -Path (Split-Path $dest) -Force | Out-Null
  $content = gh api "repos/$($spec.repo)/contents/$($_)?ref=$($spec.sha)" -H 'Accept: application/vnd.github.raw+json'
  if ($LASTEXITCODE -ne 0) { throw "Failed to fetch $_" }
  $content | Set-Content -LiteralPath $dest -Encoding utf8
} -ThrottleLimit 6
@{harness=$Harness; repository=$spec.repo; commit=$spec.sha; files=$paths.Count} | ConvertTo-Json -Compress
