# Draws apple-touch-icon.png (180x180) and og-image.png (1200x630) for the website, from the app icon's shapes
# and the Today screenshot. Run from anywhere: powershell -ExecutionPolicy Bypass -File website/scripts/build-images.ps1
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent

function Heart([System.Drawing.Graphics]$g, [float]$x, [float]$y, [float]$s) {
    # The app icon's heart (108-unit grid), drawn at ($x, $y) and scale $s.
    $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    function P([float]$a, [float]$b) { New-Object System.Drawing.PointF(($x + $a * $s), ($y + $b * $s)) }
    $p.AddBezier((P 54 77), (P 33 62), (P 28 51), (P 28 43))
    $p.AddBezier((P 28 43), (P 28 35.5), (P 34 30), (P 41 30))
    $p.AddBezier((P 41 30), (P 46.5 30), (P 51 33), (P 54 38))
    $p.AddBezier((P 54 38), (P 57 33), (P 61.5 30), (P 67 30))
    $p.AddBezier((P 67 30), (P 74 30), (P 80 35.5), (P 80 43))
    $p.AddBezier((P 80 43), (P 80 51), (P 75 62), (P 54 77))
    $p.CloseFigure()
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush((P 40 30), (P 66 77), [System.Drawing.Color]::FromArgb(255, 255, 138, 203), [System.Drawing.Color]::FromArgb(255, 194, 0, 107))
    $blend = New-Object System.Drawing.Drawing2D.ColorBlend(3)
    $blend.Colors = @([System.Drawing.Color]::FromArgb(255, 255, 138, 203), [System.Drawing.Color]::FromArgb(255, 255, 46, 147), [System.Drawing.Color]::FromArgb(255, 194, 0, 107))
    $blend.Positions = @(0.0, 0.45, 1.0)
    $brush.InterpolationColors = $blend
    $g.FillPath($brush, $p)
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(204, 255, 255, 255), [float](1.6 * $s))
    $g.DrawPath($pen, $p)
    $shine = New-Object System.Drawing.Drawing2D.GraphicsPath
    $shine.AddBezier((P 35 41), (P 35 36), (P 39 33.5), (P 43 33.5))
    $shine.AddBezier((P 43 33.5), (P 46.5 33.5), (P 49 35.5), (P 50.5 38.5))
    $shine.AddBezier((P 50.5 38.5), (P 46 38), (P 40 40), (P 37 45))
    $shine.AddBezier((P 37 45), (P 35.8 44.2), (P 35 42.8), (P 35 41))
    $g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(215, 255, 255, 255))), $shine)
}

function Sparkle([System.Drawing.Graphics]$g, [float]$cx, [float]$cy, [float]$r, [System.Drawing.Color]$c) {
    $pts = @(
        (New-Object System.Drawing.PointF($cx, ($cy - $r))), (New-Object System.Drawing.PointF(($cx + $r * 0.3), ($cy - $r * 0.3))),
        (New-Object System.Drawing.PointF(($cx + $r), $cy)), (New-Object System.Drawing.PointF(($cx + $r * 0.3), ($cy + $r * 0.3))),
        (New-Object System.Drawing.PointF($cx, ($cy + $r))), (New-Object System.Drawing.PointF(($cx - $r * 0.3), ($cy + $r * 0.3))),
        (New-Object System.Drawing.PointF(($cx - $r), $cy)), (New-Object System.Drawing.PointF(($cx - $r * 0.3), ($cy - $r * 0.3)))
    )
    $g.FillPolygon((New-Object System.Drawing.SolidBrush($c)), $pts)
}

function Background([System.Drawing.Graphics]$g, [int]$w, [int]$h) {
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush((New-Object System.Drawing.Point(0, 0)), (New-Object System.Drawing.Point($w, $h)), [System.Drawing.Color]::FromArgb(255, 255, 214, 236), [System.Drawing.Color]::FromArgb(255, 217, 166, 255))
    $blend = New-Object System.Drawing.Drawing2D.ColorBlend(3)
    $blend.Colors = @([System.Drawing.Color]::FromArgb(255, 255, 214, 236), [System.Drawing.Color]::FromArgb(255, 255, 166, 213), [System.Drawing.Color]::FromArgb(255, 217, 166, 255))
    $blend.Positions = @(0.0, 0.55, 1.0)
    $brush.InterpolationColors = $blend
    $g.FillRectangle($brush, 0, 0, $w, $h)
}

function NewCanvas([int]$w, [int]$h) {
    $bmp = New-Object System.Drawing.Bitmap($w, $h)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    return @($bmp, $g)
}

# Home-screen icon: square and opaque, as iOS rounds its own corners.
$c = NewCanvas 180 180; $bmp = $c[0]; $g = $c[1]
Background $g 180 180
Heart $g -6 -4 1.78
Sparkle $g 146 38 10 ([System.Drawing.Color]::White)
Sparkle $g 34 132 7 ([System.Drawing.Color]::FromArgb(255, 255, 228, 138))
$bmp.Save((Join-Path $root 'apple-touch-icon.png'), [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()

# Sharing image: the icon, the name and promise on the left, the Today screen on the right.
$c = NewCanvas 1200 630; $bmp = $c[0]; $g = $c[1]
Background $g 1200 630
Heart $g 40 30 2.0
Sparkle $g 1130 60 16 ([System.Drawing.Color]::White)
Sparkle $g 640 560 11 ([System.Drawing.Color]::FromArgb(255, 255, 228, 138))
Sparkle $g 90 560 9 ([System.Drawing.Color]::White)
$ink = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 74, 13, 51))
$soft = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 122, 58, 96))
$g.DrawString('Gentle', (New-Object System.Drawing.Font('Segoe UI', 64, [System.Drawing.FontStyle]::Bold)), $ink, 222, 92)
$g.DrawString("A free pacing app for chronic illness", (New-Object System.Drawing.Font('Segoe UI', 28, [System.Drawing.FontStyle]::Bold)), $ink, (New-Object System.Drawing.RectangleF(70, 262, 720, 60)))
$g.DrawString("Daily energy points from your watch. No subscriptions, ever. Your data stays on your phone.", (New-Object System.Drawing.Font('Segoe UI', 22)), $soft, (New-Object System.Drawing.RectangleF(70, 340, 640, 140)))
# The phone, with a rounded screen
$shot = [System.Drawing.Image]::FromFile((Join-Path $root 'img\app\today-pink.jpg'))
$pw = 270; $ph = [int]($pw * $shot.Height / $shot.Width)
$px = 820; $py = 60
$frame = New-Object System.Drawing.Drawing2D.GraphicsPath
$r = 34; $fx = $px - 10; $fy = $py - 10; $fw = $pw + 20; $fh = 600
$frame.AddArc($fx, $fy, $r * 2, $r * 2, 180, 90); $frame.AddArc($fx + $fw - $r * 2, $fy, $r * 2, $r * 2, 270, 90)
$frame.AddLine(($fx + $fw), ($fy + $r), ($fx + $fw), ($fy + $fh)); $frame.AddLine(($fx + $fw), ($fy + $fh), $fx, ($fy + $fh)); $frame.CloseFigure()
$g.FillPath((New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 74, 13, 51))), $frame)
$clip = New-Object System.Drawing.Drawing2D.GraphicsPath
$r2 = 26
$clip.AddArc($px, $py, $r2 * 2, $r2 * 2, 180, 90); $clip.AddArc($px + $pw - $r2 * 2, $py, $r2 * 2, $r2 * 2, 270, 90)
$clip.AddLine(($px + $pw), ($py + $r2), ($px + $pw), 640); $clip.AddLine(($px + $pw), 640, $px, 640); $clip.CloseFigure()
$g.SetClip($clip)
$g.DrawImage($shot, $px, $py, $pw, $ph)
$g.ResetClip()
$shot.Dispose()
$bmp.Save((Join-Path $root 'og-image.png'), [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
"apple-touch-icon.png and og-image.png written"
