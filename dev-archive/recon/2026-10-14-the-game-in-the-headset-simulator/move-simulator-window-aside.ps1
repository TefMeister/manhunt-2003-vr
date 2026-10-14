# Waits up to 120 s for the OpenXR Simulator preview window and moves it beside the 800x600 game window,
# then gives the game the focus back, so screen capture and posted keys keep reaching the game.
Add-Type @"
using System;using System.Runtime.InteropServices;using System.Text;
public class MS{public delegate bool P(IntPtr h,IntPtr l);[DllImport("user32.dll")]static extern bool EnumWindows(P p,IntPtr l);
[DllImport("user32.dll")]static extern int GetWindowText(IntPtr h,StringBuilder s,int n);[DllImport("user32.dll")]static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")]public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int hh,bool r);[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
public static IntPtr Find(string prefix){IntPtr f=IntPtr.Zero;EnumWindows((h,l)=>{if(!IsWindowVisible(h))return true;var s=new StringBuilder(300);GetWindowText(h,s,300);if(s.ToString().StartsWith(prefix)){f=h;return false;}return true;},IntPtr.Zero);return f;}}
"@
$end = (Get-Date).AddSeconds(120)
while ((Get-Date) -lt $end) {
    $sim = [MS]::Find("OpenXR Simulator")
    if ($sim -ne [IntPtr]::Zero) {
        [MS]::MoveWindow($sim, 1300, 100, 600, 300, $true) | Out-Null
        Start-Sleep -Milliseconds 300
        $game = [MS]::Find("MANHUNT")
        if ($game -ne [IntPtr]::Zero) { [MS]::SetForegroundWindow($game) | Out-Null }
        "moved"
        exit 0
    }
    Start-Sleep -Milliseconds 200
}
"no simulator window"
