param([int]$Minutes = 8)
# Watches one Manhunt run. Exits early if the process dies or the proxy log
# reports a crash / a full spline table. Prints a status line every 30 s.
$log = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_vr_proxy_log.txt"
$end = (Get-Date).AddMinutes($Minutes)
$pat = 'table FULL|=== CRASH'
$t0 = Get-Date
$next = $t0
while ((Get-Date) -lt $end) {
    $p = Get-Process manhunt -ErrorAction SilentlyContinue
    $hits = Select-String -Path $log -Pattern $pat -ErrorAction SilentlyContinue
    if ((Get-Date) -ge $next) {
        $lines = (Get-Content $log -ErrorAction SilentlyContinue).Count
        $state = if ($p) { "running responding=$($p.Responding) cpu=$([int]$p.CPU)s" } else { "NOT RUNNING" }
        "{0}  +{1,4}s  {2}  loglines={3}" -f (Get-Date -Format HH:mm:ss), [int]((Get-Date) - $t0).TotalSeconds, $state, $lines
        $next = (Get-Date).AddSeconds(30)
    }
    if ($hits) { "STOP: log matched"; $hits | Select-Object -First 10 | ForEach-Object { $_.Line }; break }
    if (-not $p) { "STOP: process gone"; break }
    Start-Sleep -Seconds 2
}
"watch ended $(Get-Date -Format HH:mm:ss)"
