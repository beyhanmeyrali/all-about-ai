# CrewAI Docker Runner
# Run CrewAI scripts in a Docker container to avoid Windows build issues

param(
    [Parameter(Mandatory=$false)]
    [string]$Script = "00_crew_basics.py"
)

Write-Host "🐳 Running CrewAI script in Docker container..." -ForegroundColor Cyan
Write-Host "Script: $Script" -ForegroundColor Yellow

# Build the Docker image if it doesn't exist
$imageName = "crewai-runner"
$imageExists = docker images -q $imageName

if (-not $imageExists) {
    Write-Host "`n📦 Building Docker image (first time only)..." -ForegroundColor Cyan
    docker build -t $imageName .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
        exit 1
    }
}

# Run the script
Write-Host "`n🚀 Executing script..." -ForegroundColor Cyan
docker run --rm `
    --add-host=host.docker.internal:host-gateway `
    -v "${PWD}:/app" `
    $imageName python $Script

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Script completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Script failed with exit code $LASTEXITCODE" -ForegroundColor Red
}
