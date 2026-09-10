# SendInput with SCANCODES into the focused Manhunt window.
#
# Scancodes, not virtual keys: DirectInput-era games read scancodes, and a VK
# that maps differently on another layout silently does nothing.
#
# ⚠️ 2026-09-10 -- THE STRUCT SIZE IS THE WHOLE STORY.
# INPUT is 28 bytes in a 32-bit process and 40 in a 64-bit one (DWORD type,
# 4 bytes of padding, then a 32-byte union). PowerShell here is 64-bit. A
# harness declaring Size=28 gets ERROR_INVALID_PARAMETER (87) from SendInput,
# which returns 0 and injects NOTHING -- and a caller that does not check the
# return value reads that as "this game ignores synthetic input". Every
# SendInput result recorded against this game before today must be re-checked
# against this. Always assert the return value equals the number of events.
$ErrorActionPreference = "Stop"

if (-not ("SI2" -as [type])) {
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class SI2 {
  [StructLayout(LayoutKind.Sequential)] public struct KEYBDINPUT {
    public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  // Explicit layout sized for the CURRENT bitness: 40 on x64, 28 on x86.
  // The union sits after the DWORD type plus its alignment padding.
  [StructLayout(LayoutKind.Explicit)] public struct INPUT {
    [FieldOffset(0)] public uint type;
    [FieldOffset(8)] public KEYBDINPUT ki;
    [FieldOffset(8)] public MOUSEINPUT mi;
  }
  [DllImport("user32.dll", SetLastError=true)] public static extern uint SendInput(uint n, INPUT[] p, int cb);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  public const uint KEYEVENTF_SCANCODE = 0x0008;
  public const uint KEYEVENTF_KEYUP    = 0x0002;
  public const uint KEYEVENTF_EXTENDED = 0x0001;
}
"@
}

function Focus-Game {
  $p = Get-Process manhunt -ErrorAction SilentlyContinue
  if (-not $p) { throw "manhunt is not running" }
  $h = ($p | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1).MainWindowHandle
  if ($h) { [void][SI2]::SetForegroundWindow($h) }
  Start-Sleep -Milliseconds 300
}

function Send-Scan([int]$scan, [int]$holdMs, [bool]$ext) {
  $flags = [SI2]::KEYEVENTF_SCANCODE
  if ($ext) { $flags = $flags -bor [SI2]::KEYEVENTF_EXTENDED }
  $sz = [Runtime.InteropServices.Marshal]::SizeOf([type]"SI2+INPUT")

  $d = New-Object SI2+INPUT; $d.type = 1; $d.ki.wScan = [uint16]$scan; $d.ki.dwFlags = $flags
  $u = New-Object SI2+INPUT; $u.type = 1; $u.ki.wScan = [uint16]$scan; $u.ki.dwFlags = ($flags -bor [SI2]::KEYEVENTF_KEYUP)

  $n1 = [SI2]::SendInput(1, @($d), $sz)
  $e1 = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
  Start-Sleep -Milliseconds $holdMs
  $n2 = [SI2]::SendInput(1, @($u), $sz)
  $ok = ($n1 -eq 1 -and $n2 -eq 1)
  Write-Output ("scan 0x{0:X2} ext={1} hold={2}ms -> down={3} up={4} cb={5} {6}" -f `
    $scan, $ext, $holdMs, $n1, $n2, $sz, $(if ($ok) { "OK" } else { "FAILED err=$e1" }))
  return $ok
}

# Called as: keys.ps1 <scan> [holdMs] [ext]
$scan   = if ($args.Count -ge 1) { [int]$args[0] } else { 0x11 }
$holdMs = if ($args.Count -ge 2) { [int]$args[1] } else { 400 }
$ext    = if ($args.Count -ge 3) { [bool]::Parse($args[2]) } else { $false }

Focus-Game
Send-Scan $scan $holdMs $ext | Where-Object { $_ -is [string] }
