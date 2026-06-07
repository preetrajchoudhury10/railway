# Run this script ONCE as Administrator to schedule daily job hunting
$taskName = "GenAIJobHunter"
$scriptPath = "$PSScriptRoot\run_hunter.bat"

# Create daily trigger at 9:00 AM (repeat every 6 hours)
$trigger = New-JobTrigger -Daily -At "09:00AM" -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration ([TimeSpan]::MaxValue)

# Register the task
Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action (New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`"") -RunLevel Highest -User $env:USERNAME -Force

Write-Host "Scheduled task '$taskName' created! Runs daily at 9 AM, repeating every 6 hours." -ForegroundColor Green
Write-Host "Jobs will appear on your desktop as Windows notifications." -ForegroundColor Yellow
