# Test all CrewAI scripts
$scripts = @(
    "00_crew_basics.py",
    "01_simple_crew.py",
    "03_hierarchical_crew.py",
    "04_tools_in_crew.py",
    "05_memory_crew.py",
    "06_delegation.py",
    "07_production_crew.py"
)

$env:PYTHONUTF8=1
$python = "D:\workspace\all-about-ai\ai-agents\02-agent-frameworks\crewai\.venv_new\Scripts\python.exe"

foreach ($script in $scripts) {
    Write-Host "`n`n========================================" -ForegroundColor Cyan
    Write-Host "Testing: $script" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    & $python $script
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ $script PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n❌ $script FAILED (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}
