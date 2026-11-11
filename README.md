# 🎨 Pixel Art Batch Processor CLI

Công cụ dòng lệnh (CLI) viết bằng Python giúp **tách nền**, **thay đổi kích thước (resize)** và **nén dung lượng** hàng loạt cho ảnh Pixel Art. Chạy trực tiếp trên Terminal của cả **macOS** và **Windows** mà không làm nhòe viền (anti-aliasing) hay biến dạng hạt pixel.

## ✨ Tính năng nổi bật

* **Tách nền chuẩn Pixel Art:** Hỗ trợ 2 chế độ quét thông minh (Flood-fill từ 4 góc ảnh để bảo vệ chi tiết bên trong nhân vật, hoặc Global Color Key để xóa sạch các khe hở khép kín).
* **Giữ nguyên độ sắc nét khi Resize:** Sử dụng thuật toán nội suy `Nearest Neighbor` giúp bảo toàn 100% các cạnh sắc nét của hạt pixel, không gây mờ viền.
* **Nén ảnh tối đa (Lossless-like Compression):** Chuyển đổi từ 32-bit RGBA sang 8-bit Indexed PNG (bảng màu 256 màu kèm kênh Alpha bằng thuật toán `FASTOCTREE`) kết hợp nén Zlib mức 9. Giảm từ **60% - 80%** dung lượng file mà vẫn giữ nguyên chất lượng hiển thị.
* **Xử lý hàng loạt (Batch Processing):** Tự động đọc toàn bộ ảnh từ thư mục đầu vào, giữ nguyên tên gốc và xuất ra định dạng `.png` chuẩn xác.

---

## ⚙️ Yêu cầu hệ thống & Cài đặt

1. **Python 3.7+** đã được cài đặt trên máy.
2. Cài đặt thư viện xử lý ảnh `Pillow`:

```bash
pip install Pillow

🚀 Hướng dẫn sử dụng nhanh
Bước 1: Tạo thư mục input nằm cùng cấp với file pixel_processor.py và bỏ các ảnh cần xử lý vào đó (hỗ trợ .png, .jpg, .jpeg, .bmp, .webp, .gif).
Bước 2: Mở Terminal (macOS) hoặc Command Prompt / PowerShell (Windows) và chạy lệnh:

python pixel_processor.py

Toàn bộ ảnh sau khi tách nền và nén sẽ tự động xuất hiện trong thư mục output với định dạng .png.
🛠️ Bảng tham số dòng lệnh (CLI Options)

💡 Các ví dụ thực tế
1. Tách nền và Resize đồng loạt về 128x128px

python pixel_processor.py -s 128




