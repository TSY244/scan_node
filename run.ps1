
while ($true) {
    $main_pid = Get-Content -Path "main_pid.txt"
    $ret = tasklist.exe | findstr.exe $main_pid
    if ($ret -eq "" -or $null -eq $ret) {
        $main_pid = Get-Content -Path "main_pid.txt"
        if ($main_pid -eq "1") {
            Write-Host "server kill the main process"
            exit
        }
        Start-Process -FilePath "ScanNodeVenv/Scripts/python.exe" -ArgumentList "/main.py"
        start-sleep 60
        $main_pid = Get-Content -Path "main_pid.txt"
        Write-Host "Main process is running with pid: $main_pid"
    } 
    else {
        Write-Host "Main process is running"
    }
    Start-Sleep 5
}