$pids = Get-Content -Path "../pid.txt"
foreach ($p in $pids) {
    Stop-Process -Force  $p
}

$pids = Get-Content -Path "../main_pid.txt"
foreach ($p in $pids) {
    Stop-Process -Force  $p
}
