# manhunt-2003-vr /lm harness, 2026-09-10.
# Launch the game, click through the ANSI launcher dialog, capture frames.
# Capture is BitBlt via CopyFromScreen -- never PrintWindow (stale DWM frames).
param(
  [Parameter(Mandatory=$true)][string]$Action,
  [string]$Out = "",
  [int]$Seconds = 10
)

$ErrorActionPreference = "Stop"
$GameDir = "D:\Program Files (x86)\Steam\steamapps\common\Manhunt"

if (-not ("W32" -as [type])) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class W32 {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  // ANSI on purpose: this game's launcher dialog is ANSI, and the W variants
  // return only the first character ("P" for Play), which reads exactly like
  // "no Play button found".
  [DllImport("user32.dll", CharSet=CharSet.Ansi)] public static extern int GetWindowTextA(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Ansi)] public static extern int GetClassNameA(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
}
"@
}

function Get-GameWindows {
  $p = Get-Process manhunt -ErrorAction SilentlyContinue
  if (-not $p) { return @() }
  $pids = @($p | ForEach-Object { $_.Id })
  $found = New-Object System.Collections.ArrayList
  $cb = [W32+EnumProc]{
    param($h,$l)
    $wpid = 0
    [void][W32]::GetWindowThreadProcessId($h, [ref]$wpid)
    if ($pids -contains [int]$wpid) {
      $sb = New-Object System.Text.StringBuilder 512
      [void][W32]::GetWindowTextA($h, $sb, 512)
      $cn = New-Object System.Text.StringBuilder 256
      [void][W32]::GetClassNameA($h, $cn, 256)
      $r = New-Object W32+RECT
      [void][W32]::GetWindowRect($h, [ref]$r)
      [void]$found.Add([pscustomobject]@{
        H = $h; Title = $sb.ToString(); Class = $cn.ToString()
        Vis = [W32]::IsWindowVisible($h)
        X = $r.L; Y = $r.T; W = ($r.R - $r.L); Ht = ($r.B - $r.T)
      })
    }
    return $true
  }
  [void][W32]::EnumWindows($cb, [IntPtr]::Zero)
  return $found
}

function Save-Shot([string]$path) {
  $w = Get-GameWindows | Where-Object { $_.Vis -and $_.W -gt 100 -and $_.Ht -gt 100 } |
       Sort-Object { $_.W * $_.Ht } -Descending | Select-Object -First 1
  if (-not $w) { Write-Output "SHOT: no visible game window"; return $false }
  [void][W32]::SetForegroundWindow($w.H)
  Start-Sleep -Milliseconds 400
  Add-Type -AssemblyName System.Drawing
  $bmp = New-Object System.Drawing.Bitmap $w.W, $w.Ht
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($w.X, $w.Y, 0, 0, (New-Object System.Drawing.Size $w.W, $w.Ht))
  $g.Dispose()
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  Write-Output ("SHOT: {0}  ({1}x{2} at {3},{4}) title='{5}'" -f $path, $w.W, $w.Ht, $w.X, $w.Y, $w.Title)
  return $true
}

switch ($Action) {

  "launch" {
    if (Get-Process manhunt -ErrorAction SilentlyContinue) { Write-Output "ALREADY RUNNING"; break }
    $log = Join-Path $GameDir "manhunt_vr_proxy_log.txt"
    if (Test-Path $log) {
      $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
      Move-Item $log (Join-Path $GameDir "manhunt_vr_proxy_log.prev-$stamp.txt")
      Write-Output "rotated old proxy log"
    }
    Start-Process "steam://rungameid/12130"
    Write-Output "LAUNCHED via steam://rungameid/12130"
  }

  "windows" {
    Get-GameWindows | Format-Table -AutoSize | Out-String -Width 200
  }

  "play" {
    # Find the launcher dialog's Play button and BM_CLICK it.
    $top = Get-GameWindows | Where-Object { $_.Vis }
    $clicked = $false
    foreach ($t in $top) {
      $kids = New-Object System.Collections.ArrayList
      $cb = [W32+EnumProc]{
        param($h,$l)
        $sb = New-Object System.Text.StringBuilder 256
        [void][W32]::GetWindowTextA($h, $sb, 256)
        $cn = New-Object System.Text.StringBuilder 256
        [void][W32]::GetClassNameA($h, $cn, 256)
        [void]$kids.Add([pscustomobject]@{ H=$h; Text=$sb.ToString(); Class=$cn.ToString() })
        return $true
      }
      [void][W32]::EnumChildWindows($t.H, $cb, [IntPtr]::Zero)
      foreach ($k in $kids) {
        Write-Output ("  child of '{0}': class='{1}' text='{2}'" -f $t.Title, $k.Class, $k.Text)
        if ($k.Text -match '^\s*Play' -and $k.Class -match 'Button') {
          [void][W32]::SetForegroundWindow($t.H)
          Start-Sleep -Milliseconds 200
          [void][W32]::SendMessage($k.H, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero)  # BM_CLICK
          Write-Output "CLICKED Play"
          $clicked = $true
        }
      }
    }
    if (-not $clicked) { Write-Output "NO PLAY BUTTON FOUND" }
  }

  "shot" {
    if (-not $Out) { $Out = Join-Path $env:TEMP "manhunt-shot.png" }
    [void](Save-Shot $Out)
  }

  "close" {
    $w = Get-GameWindows | Where-Object { $_.Vis -and $_.W -gt 100 } |
         Sort-Object { $_.W * $_.Ht } -Descending | Select-Object -First 1
    if ($w) {
      [void][W32]::PostMessage($w.H, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)  # WM_CLOSE
      Write-Output "SENT WM_CLOSE"
      for ($i=0; $i -lt $Seconds; $i++) {
        Start-Sleep -Seconds 1
        if (-not (Get-Process manhunt -ErrorAction SilentlyContinue)) { Write-Output "EXITED after $i s"; break }
      }
    } else { Write-Output "no window to close" }
    if (Get-Process manhunt -ErrorAction SilentlyContinue) { Write-Output "STILL RUNNING - not killed" }
  }

  "state" {
    $p = Get-Process manhunt -ErrorAction SilentlyContinue
    if ($p) {
      Write-Output ("RUNNING pid={0} responding={1} cpu={2:N1}s" -f $p.Id, $p.Responding, $p.CPU)
    } else { Write-Output "NOT RUNNING" }
  }
}
