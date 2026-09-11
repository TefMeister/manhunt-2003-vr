param([Parameter(Mandatory=$true)][string]$Lines, [string]$Shot = "", [int]$SettleMs = 600)
# Queue lines into the proxy's input script file, wait until the proxy has
# consumed it, let it play out, then optionally capture a screenshot.
# Lines are separated by ';'.
$g = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_input.txt"
$body = ($Lines -split ';' | ForEach-Object { $_.Trim() }) -join "`r`n"
Set-Content -Path $g -Value $body -Encoding ASCII
$t = Get-Date
while ((Test-Path $g) -and ((Get-Date) - $t).TotalSeconds -lt 10) { Start-Sleep -Milliseconds 100 }
if (Test-Path $g) { "NOT CONSUMED after 10 s" } else { "consumed after $([int]((Get-Date) - $t).TotalMilliseconds) ms" }
# crude wait for the scripted durations to play out
$ms = 0
foreach ($l in ($Lines -split ';')) {
  $p = $l.Trim() -split '\s+'
  switch ($p[0]) {
    'M'    { if ($p.Count -ge 4) { $ms += [int]$p[3] } else { $ms += 200 } }
    'MB'   { $ms += [int]$p[2]; if ($p.Count -ge 4) { $ms += [int]$p[3] } }
    'K'    { $ms += [int]$p[2]; if ($p.Count -ge 4) { $ms += [int]$p[3] } }
    'WAIT' { $ms += [int]$p[1] }
  }
}
Start-Sleep -Milliseconds ($ms + $SettleMs)
if ($Shot) {
  $s = Split-Path $MyInvocation.MyCommand.Path
  & "$s\drive.ps1" -Action shot -Out (Join-Path $s $Shot)
  "shot $Shot at $(Get-Date -Format HH:mm:ss)"
}
