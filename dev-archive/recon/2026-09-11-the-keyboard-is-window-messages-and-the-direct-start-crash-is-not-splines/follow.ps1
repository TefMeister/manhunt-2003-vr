param(
  [Parameter(Mandatory=$true)][double]$X2, [Parameter(Mandatory=$true)][double]$Y2, [double]$Z2 = 0,
  [switch]$Doors, [double]$Tol = 1.3, [switch]$Run
)
# Follows an A* route over the level's own AI path graph (the reader's route.py
# over mapAI.grf) from the player's current POS to (X2, Y2, Z2), one waypoint at
# a time with nav.ps1. Stops at the first waypoint it cannot reach.
$dir = Split-Path $MyInvocation.MyCommand.Path
$log = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_proxy_log.txt"
$route = "D:\claude video game stuff\github-backups\staging\manhunt-2003-vr\offline-analysis\route.py"
& "$dir\send.ps1" -Lines "POS" -SettleMs 250 | Out-Null
$l = (Select-String -Path $log -Pattern '  POS player map=' | Select-Object -Last 1).Line
if ($l -notmatch 'map=\(([-\d.]+), ([-\d.]+), ([-\d.]+)\)') { "POS unreadable"; return }
$x1 = $matches[1]; $y1 = $matches[2]; $z1 = $matches[3]
$args2 = @($route, $x1, $y1, $X2, $Y2, "--z1", $z1, "--z2", $Z2)
if ($Doors) { $args2 += "--doors" }
$out = & python @args2 2>&1
$wps = @()
foreach ($line in $out) {
  if ("$line" -match '^\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+#(\d+)\s*(.*)$') {
    $wps += [pscustomobject]@{ x = [double]$matches[1]; y = [double]$matches[2]; z = [double]$matches[3]; id = $matches[4]; tag = $matches[5].Trim() }
  }
}
"route from ($x1, $y1, $z1): $($wps.Count) waypoints"
($out | Select-String 'route ' | Select-Object -Last 1)
$i = 0
foreach ($w in $wps) {
  $i++
  $navArgs = @{ X = $w.x; Y = $w.y; Tol = $Tol; MaxSteps = 14 }
  if ($Run) { $navArgs.Run = $true }
  $r = & "$dir\nav.ps1" @navArgs
  $lastLine = $r | Select-Object -Last 1
  if ("$lastLine" -match 'STUCK|unreadable') {
    "STOPPED at waypoint $i/$($wps.Count) #$($w.id) ($($w.x), $($w.y), $($w.z)) $($w.tag): $lastLine"
    ($r | Select-Object -Last 2 | Select-Object -First 1)
    return
  }
}
& "$dir\send.ps1" -Lines "POS $X2 $Y2" -SettleMs 250 | Out-Null
(Select-String -Path $log -Pattern '  POS player map=' | Select-Object -Last 1).Line
"ROUTE DONE"
