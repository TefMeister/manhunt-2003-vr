param([string]$Prefix = "seq", [int]$Count = 6, [int]$EverySec = 10)
# Take a screenshot every N seconds; stop early if the game dies or crashes.
$s = Split-Path $MyInvocation.MyCommand.Path
$log = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_proxy_log.txt"
for ($i = 1; $i -le $Count; $i++) {
  Start-Sleep -Seconds $EverySec
  if (-not (Get-Process manhunt -ErrorAction SilentlyContinue)) { "process gone"; break }
  if (Select-String -Path $log -Pattern '=== CRASH|table FULL' -Quiet) { "log reports crash/FULL"; break }
  $f = "{0}-{1:D2}.png" -f $Prefix, $i
  & "$s\drive.ps1" -Action shot -Out (Join-Path $s $f)
  "$f at $(Get-Date -Format HH:mm:ss)"
}
