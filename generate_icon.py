import os
from PIL import Image, ImageDraw

def draw_vector_mic_icon(size: int = 64) -> Image.Image:
    # High-resolution image with antialiased supersampling (draw at 4x then downscale)
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Circular Badge: Modern Gradient-like Crimson/Coral
    # Rounded badge padding
    pad = int(s * 0.05)
    badge_rect = [pad, pad, s - pad, s - pad]
    # Primary red fill
    draw.ellipse(badge_rect, fill=(225, 29, 72, 255)) # Vibrant Rose/Crimson
    
    # Subtle inner border/ring
    ring_pad = pad + int(s * 0.02)
    draw.ellipse([ring_pad, ring_pad, s - ring_pad, s - ring_pad], outline=(255, 255, 255, 80), width=max(1, int(s * 0.02)))

    # 2. Microphone Geometry in Pure White
    # Center coordinates
    cx = s // 2
    cy = int(s * 0.45)
    
    # Capsule (Microphone Body)
    capsule_w = int(s * 0.22)
    capsule_h = int(s * 0.38)
    capsule_x0 = cx - capsule_w // 2
    capsule_y0 = cy - capsule_h // 2
    capsule_x1 = cx + capsule_w // 2
    capsule_y1 = cy + capsule_h // 2
    radius = capsule_w // 2

    # Draw rounded capsule
    draw.rounded_rectangle(
        [capsule_x0, capsule_y0, capsule_x1, capsule_y1],
        radius=radius,
        fill=(255, 255, 255, 255)
    )

    # 3. U-shaped Cradle (Arc) around capsule
    arc_w = int(s * 0.38)
    arc_h = int(s * 0.40)
    arc_x0 = cx - arc_w // 2
    arc_y0 = cy - int(capsule_h * 0.15)
    arc_x1 = cx + arc_w // 2
    arc_y1 = arc_y0 + arc_h
    line_w = max(2, int(s * 0.055))

    draw.arc(
        [arc_x0, arc_y0, arc_x1, arc_y1],
        start=0,
        end=180,
        fill=(255, 255, 255, 255),
        width=line_w
    )

    # 4. Vertical Stand Stem
    stem_top = arc_y1
    stem_h = int(s * 0.14)
    stem_bottom = stem_top + stem_h
    draw.line(
        [(cx, stem_top), (cx, stem_bottom)],
        fill=(255, 255, 255, 255),
        width=line_w
    )

    # 5. Base Plate
    base_w = int(s * 0.32)
    draw.line(
        [(cx - base_w // 2, stem_bottom), (cx + base_w // 2, stem_bottom)],
        fill=(255, 255, 255, 255),
        width=line_w
    )

    # Downscale with high quality Lanczos filter for razor-sharp antialiasing
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

assets_dir = r"C:\Users\eGe\Vault\300-PR~1\ANTIGR~1\assets"
os.makedirs(assets_dir, exist_ok=True)

# Generate multi-resolution images
sizes = [16, 24, 32, 48, 64, 128]
images = [draw_vector_mic_icon(sz) for sz in sizes]

# Save PNGs and multi-res ICO
png_path = os.path.join(assets_dir, "app_icon.png")
ico_path = os.path.join(assets_dir, "app_icon.ico")

images[-2].save(png_path) # 64x64 PNG
images[0].save(
    ico_path,
    format="ICO",
    sizes=[(sz, sz) for sz in sizes],
    append_images=images[1:]
)

print(f"Generated {ico_path} ({os.path.getsize(ico_path)} bytes)")
print(f"Generated {png_path} ({os.path.getsize(png_path)} bytes)")
