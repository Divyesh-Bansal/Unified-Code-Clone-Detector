param (
    [Parameter(Mandatory=$true, HelpMessage="Enter the test folder name/path")]
    [string]$TargetFolder
)

# Check if the folder exists
if (-Not (Test-Path $TargetFolder)) {
    Write-Error "The specified folder '$TargetFolder' does not exist."
    exit 1
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Starting Hybrid Code Clone Detection Tool" -ForegroundColor Cyan
Write-Host " Target Folder : $TargetFolder" -ForegroundColor Cyan
Write-Host " Output File   : final_result.txt" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Initializing environment and loading files..." -ForegroundColor Yellow

# Measure time taken
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

# Run the python tool. 
# It already prints "Analyzing source files" and progress to the terminal.
python -m my_tool $TargetFolder --output final_result.txt --mode file

$stopwatch.Stop()
$elapsed = $stopwatch.Elapsed.ToString("hh\:mm\:ss\.ff")

Write-Host "`n[2/2] Processing finished!" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Analysis Complete!" -ForegroundColor Green
Write-Host " Time Elapsed : $elapsed" -ForegroundColor Cyan
Write-Host " Results successfully saved to: final_result.txt" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
