from PIL import Image, ImageDraw, ImageFilter
import math
import random

W, H = 500, 560
SCALE = 2
WS, HS = W * SCALE, H * SCALE

def ease_out_cubic(x):
    x = max(0, min(1, x))
    return 1 - (1 - x) ** 3

def ease_in_out(x):
    x = max(0, min(1, x))
    return 3 * x * x - 2 * x * x * x

def segment_progress(t, start, end):
    if t <= start:
        return 0.0
    if t >= end:
        return 1.0
    return (t - start) / (end - start)

def draw_leaf(draw, base, angle_deg, length, width, fill, outline=None):
    angle = math.radians(angle_deg)
    dx, dy = math.cos(angle), math.sin(angle)
    px, py = -dy, dx
    bx, by = base
    tip = (bx + dx * length, by + dy * length)
    m1 = (bx + dx * length * 0.35 + px * width * 0.9, by + dy * length * 0.35 + py * width * 0.9)
    m2 = (bx + dx * length * 0.78 + px * width * 0.45, by + dy * length * 0.78 + py * width * 0.45)
    m3 = (bx + dx * length * 0.78 - px * width * 0.45, by + dy * length * 0.78 - py * width * 0.45)
    m4 = (bx + dx * length * 0.35 - px * width * 0.9, by + dy * length * 0.35 - py * width * 0.9)
    draw.polygon([base, m1, m2, tip, m3, m4], fill=fill, outline=outline)

def draw_petal(draw, center, angle_deg, length, width, fill, outline=None):
    angle = math.radians(angle_deg)
    dx, dy = math.cos(angle), math.sin(angle)
    px, py = -dy, dx
    cx, cy = center
    base_r = 40 * SCALE
    bx = cx + dx * base_r
    by = cy + dy * base_r
    tx = cx + dx * (base_r + length)
    ty = cy + dy * (base_r + length)
    pts = [
        (bx - px * width * 0.35, by - py * width * 0.35),
        (bx + px * width * 0.35, by + py * width * 0.35),
        (cx + dx * (base_r + length * 0.45) + px * width, cy + dy * (base_r + length * 0.45) + py * width),
        (tx, ty),
        (cx + dx * (base_r + length * 0.45) - px * width, cy + dy * (base_r + length * 0.45) - py * width),
    ]
    draw.polygon(pts, fill=fill, outline=outline)

frames = []
n_frames = 54
cx, cy = WS // 2, int(HS * 0.38)
stem_bottom = (cx, int(HS * 0.88))
stem_top = (cx, cy + 55 * SCALE)

for i in range(n_frames):
    t = i / (n_frames - 1)
    img = Image.new("RGBA", (WS, HS), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)

    bloom_prog = ease_out_cubic(segment_progress(t, 0.24, 1.0))
    if bloom_prog > 0:
        glow = Image.new("RGBA", (WS, HS), (255, 255, 255, 0))
        gd = ImageDraw.Draw(glow)
        glow_r = int((45 + 22 * bloom_prog) * SCALE)
        gd.ellipse((cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r), fill=(255, 220, 90, int(25 + 32 * bloom_prog)))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=24 * SCALE))
        img.alpha_composite(glow)

    sp = ease_out_cubic(segment_progress(t, 0.0, 0.28))
    if sp > 0:
        stem_y = stem_bottom[1] + (stem_top[1] - stem_bottom[1]) * sp
        stem_w = int((8 + 8 * sp) * SCALE)
        d.line([stem_bottom, (cx, stem_y)], fill=(66, 150, 62, 255), width=stem_w)
        d.line([stem_bottom[0] + 3 * SCALE, stem_bottom[1], cx + 3 * SCALE, stem_y], fill=(102, 185, 96, 180), width=int(4 * SCALE))

    lp1 = ease_out_cubic(segment_progress(t, 0.18, 0.42))
    lp2 = ease_out_cubic(segment_progress(t, 0.24, 0.48))
    if lp1 > 0:
        base = (cx - 2 * SCALE, int(HS * 0.62))
        draw_leaf(d, base, 210, 110 * SCALE * lp1, 34 * SCALE * lp1, (82, 188, 76, 255), (48, 120, 45, 220))
        ang = math.radians(210)
        d.line([base, (base[0] + math.cos(ang) * 110 * SCALE * lp1, base[1] + math.sin(ang) * 110 * SCALE * lp1)], fill=(46, 120, 45, 180), width=int(3 * SCALE))
    if lp2 > 0:
        base = (cx + 2 * SCALE, int(HS * 0.68))
        draw_leaf(d, base, -30, 96 * SCALE * lp2, 30 * SCALE * lp2, (96, 198, 86, 255), (46, 120, 45, 220))
        ang = math.radians(-30)
        d.line([base, (base[0] + math.cos(ang) * 96 * SCALE * lp2, base[1] + math.sin(ang) * 96 * SCALE * lp2)], fill=(46, 120, 45, 180), width=int(3 * SCALE))

    pp = ease_out_cubic(segment_progress(t, 0.32, 0.78))
    petal_count = 22
    if pp > 0:
        for k in range(petal_count):
            ang = -90 + k * (360 / petal_count)
            wiggle = 0.85 + 0.15 * math.sin(math.radians(k * 33))
            length = 78 * SCALE * pp * wiggle
            width = 18 * SCALE * pp * (0.9 + 0.2 * math.cos(math.radians(k * 21)))
            color = (247, 198 + int(20 * math.sin(math.radians(k * 17))), 40, 255)
            outline = (220, 145, 22, 200)
            draw_petal(d, (cx, cy), ang, length, width, color, outline)

        inner_pp = ease_out_cubic(segment_progress(t, 0.4, 0.8))
        for k in range(14):
            ang = -77 + k * (360 / 14)
            length = 50 * SCALE * inner_pp * (0.92 + 0.1 * math.sin(math.radians(k * 40)))
            width = 13 * SCALE * inner_pp
            draw_petal(d, (cx, cy), ang, length, width, (255, 220, 72, 235), (226, 170, 36, 160))

    cp = ease_out_cubic(segment_progress(t, 0.58, 0.9))
    if cp > 0:
        r = int(44 * SCALE * cp)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(92, 58, 29, 255), outline=(60, 35, 18, 255), width=int(4 * SCALE))
        rnd = random.Random(123)
        dots = int(170 * cp)
        for _ in range(dots):
            a = rnd.random() * math.tau
            rr = math.sqrt(rnd.random()) * r * 0.9
            x = cx + math.cos(a) * rr
            y = cy + math.sin(a) * rr
            col = (132 + rnd.randint(-15, 20), 86 + rnd.randint(-10, 15), 34 + rnd.randint(-5, 12), 255)
            rad = max(1, int((2.8 + rnd.random() * 2.2) * SCALE * cp))
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)

    hp = ease_in_out(segment_progress(t, 0.86, 1.0))
    if hp > 0:
        sparkle = Image.new("RGBA", (WS, HS), (255, 255, 255, 0))
        sd = ImageDraw.Draw(sparkle)
        positions = [(cx - 120 * SCALE, cy - 40 * SCALE), (cx + 115 * SCALE, cy + 10 * SCALE), (cx + 20 * SCALE, cy - 130 * SCALE)]
        for sx, sy in positions:
            size = 6 * SCALE * hp
            sd.line([(sx - size, sy), (sx + size, sy)], fill=(255, 214, 73, int(120 * hp)), width=int(2 * SCALE))
            sd.line([(sx, sy - size), (sx, sy + size)], fill=(255, 214, 73, int(120 * hp)), width=int(2 * SCALE))
        sparkle = sparkle.filter(ImageFilter.GaussianBlur(radius=2 * SCALE))
        img.alpha_composite(sparkle)

    small = img.resize((W, H), Image.Resampling.LANCZOS)
    frames.append(small)

for _ in range(10):
    frames.append(frames[-1])

frames[0].save("girasol_animado.gif", save_all=True, append_images=frames[1:], duration=70, loop=0)
print("Archivo generado: girasol_animado.gif")
