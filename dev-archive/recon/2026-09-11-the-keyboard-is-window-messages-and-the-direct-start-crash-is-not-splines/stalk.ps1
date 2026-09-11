param([Parameter(Mandatory=$true)][string]$Name, [double]$Reach = 1.3, [int]$MaxSteps = 20, [double]$MaxTurn = 25, [int]$HoldMs = 1500)
# Sneaks up behind hunter $Name using HUNTERS (his position, facing, and
# whether we are BEHIND him), turning at most $MaxTurn deg per step, one
# screenshot per step; when within $Reach and behind him, holds the attack
# button (left mouse) for $HoldMs to start an execution.
$dir = Split-Path $MyInvocation.MyCommand.Path
$log = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_proxy_log.txt"
function Norm([double]$a) { while ($a -gt 180) { $a -= 360 }; while ($a -le -180) { $a += 360 }; return $a }
for ($i = 1; $i -le $MaxSteps; $i++) {
  & "$dir\send.ps1" -Lines "POS;HUNTERS" -SettleMs 300 | Out-Null
  $pl = (Select-String -Path $log -Pattern '  POS player map=' | Select-Object -Last 1).Line
  $hl = (Select-String -Path $log -Pattern ("HUNTERS A {0} " -f $Name) | Select-Object -Last 1).Line
  if ($pl -notmatch 'yaw=([-\d.]+)') { "POS unreadable"; break }; $yaw = [double]$matches[1]
  if ($hl -notmatch 'health=([-\d.]+) state=(\S+)\s+player: ([\d.]+) m away.*?(BEHIND|IN FRONT|to his side).*?bearing to him ([-\d.]+)') { "hunter line unreadable: $hl"; break }
  $hp = [double]$matches[1]; $st = $matches[2]; $dist = [double]$matches[3]; $rel = $matches[4]; $bear = [double]$matches[5]
  $turn = Norm ($bear - $yaw)
  "step {0}: {1} {2:N1} m, {3}, health {4}, state {5}, turn {6:N0}" -f $i, $Name, $dist, $rel, $hp, $st, $turn
  & "$dir\drive.ps1" -Action shot -Out (Join-Path $dir ("stalk-{0:D2}.png" -f $i))
  if ($hp -le 0 -or $hl -match 'DEAD') { "HE IS DOWN"; break }
  $stp = [Math]::Max(-$MaxTurn, [Math]::Min($MaxTurn, $turn))
  $counts = [int][Math]::Round(-$stp / 0.343)
  if ([Math]::Abs($counts) -ge 3) { & "$dir\send.ps1" -Lines "M $counts 0 200" -SettleMs 100 | Out-Null }
  if ($dist -le $Reach -and [Math]::Abs($turn) -le 30) {
    "IN REACH ($rel) -- holding attack $HoldMs ms"
    & "$dir\send.ps1" -Lines "MB 0 $HoldMs" -SettleMs 1500 | Out-Null
    & "$dir\drive.ps1" -Action shot -Out (Join-Path $dir ("stalk-{0:D2}-exec.png" -f $i))
    continue
  }
  $ms = if ($dist -gt 4) { 1200 } else { 500 }
  & "$dir\keymsg.ps1" -Vk 0x57 -Scan 0x11 -HoldMs $ms -Via post -WithCtrl | Out-Null
}
