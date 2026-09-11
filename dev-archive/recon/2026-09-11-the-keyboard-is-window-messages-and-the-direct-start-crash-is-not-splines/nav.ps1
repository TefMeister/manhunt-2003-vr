param(
  [Parameter(Mandatory=$true)][double]$X,
  [Parameter(Mandatory=$true)][double]$Y,
  [double]$Tol = 1.5,
  [int]$MaxSteps = 25,
  [double]$DegPerCount = 0.343,   # measured 2026-09-11: +100 mouse X counts = yaw -34.3 deg
  [double]$WalkSpeed = 2.2,       # measured 2026-09-11: ~2.2 map units/s walking
  [switch]$Run
)
# Steers Manhunt's player to map point (X, Y) using the proxy's POS command
# (player map position + yaw, read from memory) and posted W key-downs.
# Yaw convention (pos.c): 0 along +X, 90 along +Y, counter-clockwise positive.
$dir = Split-Path $MyInvocation.MyCommand.Path
$log = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_proxy_log.txt"
function Pos {
  & "$dir\send.ps1" -Lines "POS" -SettleMs 250 | Out-Null
  $l = (Select-String -Path $log -Pattern '  POS player map=' | Select-Object -Last 1).Line
  if ($l -match 'map=\(([-\d.]+), ([-\d.]+), ([-\d.]+)\) yaw=([-\d.]+)') {
    return @{ x = [double]$matches[1]; y = [double]$matches[2]; z = [double]$matches[3]; yaw = [double]$matches[4] }
  }
  return $null
}
function Norm([double]$a) { while ($a -gt 180) { $a -= 360 }; while ($a -le -180) { $a += 360 }; return $a }
$last = $null; $stuck = 0
for ($i = 1; $i -le $MaxSteps; $i++) {
  $p = Pos
  if (-not $p) { "step $i : POS unreadable"; break }
  $dx = $X - $p.x; $dy = $Y - $p.y; $dist = [Math]::Sqrt($dx*$dx + $dy*$dy)
  $bear = [Math]::Atan2($dy, $dx) * 180 / [Math]::PI
  $turn = Norm ($bear - $p.yaw)
  "step {0}: at ({1:N1}, {2:N1}, {3:N1}) yaw {4:N0}  -> target {5:N1} m, bearing {6:N0}, turn {7:N0}" -f $i, $p.x, $p.y, $p.z, $p.yaw, $dist, $bear, $turn
  if ($dist -le $Tol) { "ARRIVED"; break }
  if ($last) {
    $moved = [Math]::Sqrt([Math]::Pow($p.x - $last.x, 2) + [Math]::Pow($p.y - $last.y, 2))
    if ($moved -lt 0.4) { $stuck++ } else { $stuck = 0 }
    if ($stuck -ge 2) { "STUCK (moved $([Math]::Round($moved,2)) m twice)"; break }
  }
  $last = $p
  $counts = [int][Math]::Round(-$turn / $DegPerCount)
  if ([Math]::Abs($counts) -ge 3) { & "$dir\send.ps1" -Lines "M $counts 0 250" -SettleMs 150 | Out-Null }
  $secs = [Math]::Min($dist / $WalkSpeed, 3.0)
  if ([Math]::Abs($turn) -gt 60) { $secs = [Math]::Min($secs, 0.8) }
  $ms = [int]([Math]::Max($secs, 0.4) * 1000)
  if ($Run) { & "$dir\keymsg.ps1" -Vk 0x57 -Scan 0x11 -HoldMs $ms -Via post -WithShift | Out-Null }
  else      { & "$dir\keymsg.ps1" -Vk 0x57 -Scan 0x11 -HoldMs $ms -Via post | Out-Null }
}
