#!/usr/bin/env python3
import os
import argparse
from pathlib import Path
from PIL import Image

def parse_size(size_str):
    """Phân tích chuỗi kích thước (VD: '128' -> (128, 128) hoặc '128x64' -> (128, 64))"""
    if not size_str:
        return None
    try:
        if 'x' in size_str.lower():
            w, h = map(int, size_str.lower().split('x'))
            return (w, h)
        else:
            s = int(size_str)
            return (s, s)
    except ValueError:
        raise argparse.ArgumentTypeError("Kích thước không hợp lệ! Hãy nhập dạng '128' hoặc '128x128'.")

def parse_color(hex_str):
    """Chuyển mã màu HEX sang tuple RGB"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) != 6:
        raise ValueError("Mã HEX phải có 6 ký tự (VD: #FF00FF)")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def remove_bg_pixel_art(img, tolerance=10, custom_bg_color=None, mode='flood'):
    """
    Tách nền chuyên dụng cho Pixel Art:
    - mode='flood': Loang từ các cạnh ngoài vào (tránh xóa nhầm chi tiết cùng màu bên trong nhân vật).
    - mode='global': Xóa toàn bộ pixel trùng màu nền trên khắp bức ảnh (dùng khi có khoảng trống giữa tay/chân).
    """
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # Tự động lấy màu ở góc trên cùng bên trái nếu người dùng không chỉ định màu
    if custom_bg_color is not None:
        bg_color = custom_bg_color
    else:
        bg_color = pixels[0, 0][:3]

    # Nếu góc ảnh vốn đã trong suốt hoàn toàn và không chỉ định màu, bỏ qua bước tách
    if custom_bg_color is None and pixels[0, 0][3] == 0:
        return img

    def is_match(p):
        if p[3] == 0:
            return True
        return (abs(p[0] - bg_color[0]) <= tolerance and
                abs(p[1] - bg_color[1]) <= tolerance and
                abs(p[2] - bg_color[2]) <= tolerance)

    if mode == 'global':
        for y in range(height):
            for x in range(width):
                if is_match(pixels[x, y]):
                    pixels[x, y] = (0, 0, 0, 0)
    else:
        # Thuật toán BFS Flood-fill từ toàn bộ viền ngoài của ảnh
        visited = set()
        queue = []

        for x in range(width):
            queue.append((x, 0))
            queue.append((x, height - 1))
        for y in range(height):
            queue.append((0, y))
            queue.append((width - 1, y))

        while queue:
            x, y = queue.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))

            if is_match(pixels[x, y]):
                pixels[x, y] = (0, 0, 0, 0)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                        queue.append((nx, ny))

    return img

def resize_pixel_art(img, target_size):
    """Resize ảnh bằng thuật toán Nearest Neighbor để giữ nguyên độ sắc nét của hạt pixel"""
    if not target_size:
        return img
    return img.resize(target_size, resample=Image.Resampling.NEAREST)

def save_compressed_png(img, output_path, quantize_colors=True):
    """
    Nén ảnh PNG giữ nguyên chất lượng:
    - Chuyển từ 32-bit RGBA sang 8-bit Indexed PNG (giảm 60-80% dung lượng mà không mất màu pixel art).
    - Nén Zlib ở mức tối đa (compress_level=9).
    """
    if quantize_colors:
        # FastOctree (method=2) hỗ trợ lượng tử hóa ảnh có kênh Alpha (trong suốt)
        img = img.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    
    img.save(output_path, format="PNG", optimize=True, compress_level=9)

def process_batch(input_dir, output_dir, size, tolerance, bg_color, mode, no_quantize):
    in_path = Path(input_dir)
    out_path = Path(output_dir)

    if not in_path.exists():
        print(f"[!] Lỗi: Thư mục đầu vào '{in_path}' không tồn tại.")
        return

    out_path.mkdir(parents=True, exist_ok=True)
    valid_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif'}
    files = [f for f in in_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]

    if not files:
        print(f"[!] Không tìm thấy file ảnh nào trong '{in_path}'.")
        return

    print(f"[*] Tìm thấy {len(files)} ảnh. Bắt đầu xử lý...")
    print("-" * 50)

    total_saved_kb = 0
    success_count = 0

    for file_path in files:
        try:
            with Image.open(file_path) as img:
                # 1. Tách nền
                if mode != 'none':
                    img = remove_bg_pixel_art(img, tolerance=tolerance, custom_bg_color=bg_color, mode=mode)
                
                # 2. Resize (nếu có)
                if size:
                    img = resize_pixel_art(img, size)

                # 3. Xuất file PNG (giữ nguyên tên gốc) và nén
                out_file = out_path / f"{file_path.stem}.png"
                save_compressed_png(img, out_file, quantize_colors=not no_quantize)

                # Thống kê dung lượng
                orig_kb = file_path.stat().st_size / 1024
                new_kb = out_file.stat().st_size / 1024
                total_saved_kb += (orig_kb - new_kb)
                success_count += 1

                print(f"[OK] {file_path.name} -> {out_file.name} | {img.size[0]}x{img.size[1]}px | {orig_kb:.1f}KB -> {new_kb:.1f}KB")

        except Exception as e:
            print(f"[LỖI] Không thể xử lý {file_path.name}: {e}")

    print("-" * 50)
    print(f"[*] Hoàn tất! Đã xử lý {success_count}/{len(files)} ảnh vào thư mục '{out_path}'.")
    if total_saved_kb > 0:
        print(f"[*] Tổng dung lượng tiết kiệm được: {total_saved_kb:.1f} KB")

def main():
    parser = argparse.ArgumentParser(
        description="CLI Tool: Tách nền, Resize và Nén ảnh Pixel Art hàng loạt."
    )
    parser.add_argument("-i", "--input", default="input", help="Thư mục ảnh đầu vào (mặc định: input)")
    parser.add_argument("-o", "--output", default="output", help="Thư mục ảnh đầu ra (mặc định: output)")
    parser.add_argument("-s", "--size", type=parse_size, default=None, help="Kích thước resize, VD: '128' hoặc '128x128'")
    parser.add_argument("-t", "--tolerance", type=int, default=15, help="Độ sai số màu nền từ 0-255 (mặc định: 15, hữu ích khi nền bị nhiễu nhẹ)")
    parser.add_argument("-c", "--color", type=parse_color, default=None, help="Chỉ định mã màu nền HEX cần xóa (VD: '#FFFFFF'). Mặc định tự lấy màu ở góc ảnh.")
    parser.add_argument("-m", "--mode", choices=['flood', 'global', 'none'], default='flood', 
                        help="Chế độ tách nền: 'flood' (loang từ viền, an toàn cho chi tiết bên trong), 'global' (xóa mọi pixel trùng màu nền), 'none' (không tách nền)")
    parser.add_argument("--no-quantize", action="store_true", help="Tắt chế độ nén 8-bit (giữ nguyên 32-bit RGBA nếu ảnh có quá nhiều hiệu ứng chuyển màu phức tạp)")

    args = parser.parse_args()
    process_batch(args.input, args.output, args.size, args.tolerance, args.color, args.mode, args.no_quantize)

if __name__ == "__main__":
    main()
