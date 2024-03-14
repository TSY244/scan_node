$main_pid = Get-Content -Path "../main_pid.txt"

while ($true) {
    $ret = tasklist.exe | findstr.exe $main_pid
    if ($ret -eq "") {
        $main_pid = Get-Content -Path "../main_pid.txt"
        if ($main_pid -ne "1") {
            Write-Host "server kill the main process"
            exit
        }
        Start-Process -FilePath "python" -ArgumentList "../main.py"
        start-sleep 60
        $main_pid = Get-Content -Path "../main_pid.txt"
    } 
    else {
        Write-Host "Main process is running"
    }
    Start-Sleep 60
}