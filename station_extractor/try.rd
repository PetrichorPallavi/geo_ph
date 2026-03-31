a code to be pasted in terminal to show busy terminal;)


$files = @(
"system_update.pkg",
"security_patch.bin",
"database_backup.sql"
)

foreach ($file in $files) {

    Write-Host "[*] Downloading $file"

    for ($i=1; $i -le 100; $i++) {
        Write-Host -NoNewline "`r$file $i%"
        Start-Sleep -Seconds 2
    }

    Write-Host "`r$file 100% [COMPLETE]"
    Start-Sleep -Minutes 1
}