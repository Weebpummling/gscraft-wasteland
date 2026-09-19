# One real right-click in the Minecraft test client (phase 45): focus the window, click once to grab the mouse, right-click,
# then Esc to close whatever opened. Prints one line saying what it did. Local test client only.
Add-Type -AssemblyName Microsoft.VisualBasic
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
$p = Get-Process javaw -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "Minecraft*" } | Select-Object -First 1
if (-not $p) { Write-Output "no Minecraft window"; exit 0 }
[Microsoft.VisualBasic.Interaction]::AppActivate($p.Id)
[Win]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 900
$r = New-Object Win+RECT
[Win]::GetWindowRect($p.MainWindowHandle, [ref]$r) | Out-Null
$cx = [int](($r.L + $r.R) / 2); $cy = [int](($r.T + $r.B) / 2)
[Win]::SetCursorPos($cx, $cy) | Out-Null
Start-Sleep -Milliseconds 300
# no Esc first: with no screen open it would OPEN the pause menu. A left click grabs the mouse (an ungrabbed click does nothing else)
[Win]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero); [Win]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 700
[Win]::mouse_event(0x0008, 0, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 120; [Win]::mouse_event(0x0010, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 1200
[System.Windows.Forms.SendKeys]::SendWait("{ESC}")
Write-Output "clicked at $cx,$cy in [$($p.MainWindowTitle)]"
