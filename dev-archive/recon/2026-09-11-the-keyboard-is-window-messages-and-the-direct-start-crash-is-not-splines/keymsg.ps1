param(
  [Parameter(Mandatory=$true)][int]$Vk,         # virtual-key code, e.g. 0x57 = W
  [Parameter(Mandatory=$true)][int]$Scan,       # scancode, e.g. 0x11 = W
  [int]$HoldMs = 2000,
  [switch]$Extended,
  [switch]$NoRepeat,
  [switch]$WithShift,
  [switch]$WithCtrl,   # Left Ctrl = SNEAK in Manhunt (scan 0x1D, not extended)
  [ValidateSet("post","sendinput")][string]$Via = "post",
  [string]$ShotDuring = "", [string]$ShotAfter = ""
)
# Delivers ONE key press to Manhunt, either as window messages posted straight
# to its window (WM_KEYDOWN / WM_KEYUP) or through SendInput with the 64-bit
# INPUT size, asserting the return value. Keys reach this game as Windows key
# messages (the DirectInput keyboard is only used as an acquisition check).
$s = Split-Path $MyInvocation.MyCommand.Path
if (-not ("KM" -as [type])) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class KM {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll", SetLastError=true)] public static extern uint SendInput(uint n, INPUT[] a, int size);
  [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT { public ushort wVk, wScan; public uint dwFlags, time; public IntPtr dwExtraInfo; }
  [StructLayout(LayoutKind.Explicit, Size=40)] public struct INPUT { [FieldOffset(0)] public uint type; [FieldOffset(8)] public KEYBDINPUT ki; }
}
"@
}
$p = Get-Process manhunt -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { "NOT RUNNING"; return }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { "no main window"; return }
[void][KM]::SetForegroundWindow($h); Start-Sleep -Milliseconds 300
"foreground is game: $([KM]::GetForegroundWindow() -eq $h)"
$ext = if ($Extended) { 1 } else { 0 }
if ($Via -eq "post") {
  $down = 1 -bor ($Scan -shl 16) -bor ($ext -shl 24)
  $up   = $down -bor (1 -shl 30) -bor (1 -shl 31)
  if ($WithShift) { [void][KM]::PostMessage($h, 0x0100, [IntPtr]0x10, [IntPtr][int](1 -bor (0x2A -shl 16))) }
  if ($WithCtrl) { [void][KM]::PostMessage($h, 0x0100, [IntPtr]0x11, [IntPtr][int](1 -bor (0x1D -shl 16))) }
  $ok1 = [KM]::PostMessage($h, 0x0100, [IntPtr]$Vk, [IntPtr][int]$down)
  $t = Get-Date
  if ($ShotDuring) { Start-Sleep -Milliseconds ([int]($HoldMs/2)); & "$s\drive.ps1" -Action shot -Out (Join-Path $s $ShotDuring) }
  # repeat WM_KEYDOWN like a real held key (autorepeat, bit 30 set) until the hold ends
  while (((Get-Date) - $t).TotalMilliseconds -lt $HoldMs) {
    if (-not $NoRepeat) { [void][KM]::PostMessage($h, 0x0100, [IntPtr]$Vk, [IntPtr][int]($down -bor (1 -shl 30))) }
    Start-Sleep -Milliseconds 33
  }
  $ok2 = [KM]::PostMessage($h, 0x0101, [IntPtr]$Vk, [IntPtr][int]$up)
  if ($WithCtrl) { [void][KM]::PostMessage($h, 0x0101, [IntPtr]0x11, [IntPtr][int](1 -bor (0x1D -shl 16) -bor (1 -shl 30) -bor (1 -shl 31))) }
  if ($WithShift) { [void][KM]::PostMessage($h, 0x0101, [IntPtr]0x10, [IntPtr][int](1 -bor (0x2A -shl 16) -bor (1 -shl 30) -bor (1 -shl 31))) }
  "posted down=$ok1 up=$ok2 held=$HoldMs ms"
} else {
  $f = 0x0008 -bor ($(if ($Extended) { 0x0001 } else { 0 }))   # KEYEVENTF_SCANCODE (+EXTENDEDKEY)
  $a = New-Object KM+INPUT; $a.type = 1; $a.ki.wScan = [uint16]$Scan; $a.ki.dwFlags = [uint32]$f
  $r1 = [KM]::SendInput(1, @($a), 40); $e1 = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
  if ($ShotDuring) { Start-Sleep -Milliseconds ([int]($HoldMs/2)); & "$s\drive.ps1" -Action shot -Out (Join-Path $s $ShotDuring); Start-Sleep -Milliseconds ([int]($HoldMs/2)) } else { Start-Sleep -Milliseconds $HoldMs }
  $a.ki.dwFlags = [uint32]($f -bor 0x0002)   # KEYUP
  $r2 = [KM]::SendInput(1, @($a), 40); $e2 = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
  "sendinput down=$r1 (err $e1) up=$r2 (err $e2) held=$HoldMs ms"
}
if ($ShotAfter) { Start-Sleep -Milliseconds 300; & "$s\drive.ps1" -Action shot -Out (Join-Path $s $ShotAfter) }
