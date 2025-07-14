# Skibidi-Toilet-Vaccine

`Skibidi-Toilet-Vaccine` là một công cụ quản lý thiết bị Android thông qua ADB (Android Debug Bridge) và tích hợp với `scrcpy` để điều khiển thiết bị từ máy tính. Công cụ này cung cấp giao diện dòng lệnh tương tác để thực hiện các tác vụ như buộc dừng ứng dụng, vô hiệu hóa/kích hoạt ứng dụng, chạy vòng lặp giám sát ứng dụng (ví dụ: YouTube), và sử dụng `scrcpy` để chiếu màn hình thiết bị Android. Hỗ trợ đa nền tảng (Linux, macOS, Windows).

Công cụ này hữu ích cho:
- Buộc dừng hoặc quản lý các ứng dụng cụ thể (bao gồm ứng dụng hệ thống và người dùng).
- Giám sát và tự động dừng các ứng dụng như YouTube.
- Chiếu và điều khiển màn hình thiết bị Android qua `scrcpy`.
- Tùy chỉnh hiển thị thông tin thiết bị (tên thiết bị, IP, hoặc cả hai).

---

## Yêu cầu hệ thống

- **Hệ điều hành**: Linux, macOS, hoặc Windows.
- **Python**: Phiên bản 3.12 hoặc mới hơn.
- **ADB (Android Debug Bridge)**: Công cụ giao tiếp với thiết bị Android.
- **scrcpy**: Công cụ để chiếu và điều khiển màn hình thiết bị Android.
- **Thiết bị Android**: Kích hoạt chế độ nhà phát triển và bật Gỡ lỗi USB (hoặc kết nối Wi-Fi cho ADB không dây).

---

## Cài đặt

Dưới đây là hướng dẫn chi tiết để cài đặt các thành phần cần thiết trên Linux, macOS và Windows.

### 1. Cài đặt Python

#### Linux
Hầu hết các bản phân phối Linux đã cài sẵn Python. Để kiểm tra hoặc cài đặt Python 3.12:
```bash
python3 --version
```
Nếu cần cài đặt:
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install python3.12 python3-pip
  ```
- **Fedora**:
  ```bash
  sudo dnf install python3.12 python3-pip
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S python python-pip
  ```

#### macOS
Sử dụng Homebrew để cài đặt Python 3.12:
```bash
brew install python@3.12
```
Xác minh:
```bash
python3.12 --version
pip3.12 --version
```

#### Windows
1. Tải Python 3.12 từ [trang chính thức](https://www.python.org/downloads/).
2. Chạy trình cài đặt, đảm bảo chọn **Add Python to PATH**.
3. Xác minh:
   ```cmd
   python --version
   pip --version
   ```

### 2. Cài đặt ADB

#### Linux
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install android-tools-adb
  ```
- **Fedora**:
  ```bash
  sudo dnf install android-tools
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S android-tools
  ```
- Xác minh:
  ```bash
  adb --version
  ```

#### macOS
Sử dụng Homebrew:
```bash
brew install android-platform-tools
```
Xác minh:
```bash
adb --version
```

#### Windows
1. Tải Android SDK Platform Tools từ [trang chính thức](https://developer.android.com/studio/releases/platform-tools).
2. Giải nén vào thư mục (ví dụ: `C:\platform-tools`).
3. Thêm thư mục `platform-tools` vào biến môi trường PATH:
   - Nhấn **Win + R**, gõ `sysdm.cpl`, nhấn Enter.
   - Vào tab **Advanced** > **Environment Variables**.
   - Trong **System Variables**, chỉnh sửa **Path**, thêm đường dẫn đến `platform-tools`.
4. Xác minh:
   ```cmd
   adb --version
   ```

### 3. Cài đặt scrcpy

#### Linux
- **Ubuntu/Debian**:
  ```bash
  sudo apt update
  sudo apt install scrcpy
  ```
- **Fedora**:
  ```bash
  sudo dnf install scrcpy
  ```
- **Arch Linux**:
  ```bash
  sudo pacman -S scrcpy
  ```
- Xác minh:
  ```bash
  scrcpy --version
  ```

#### macOS
Sử dụng Homebrew:
```bash
brew install scrcpy
```
Xác minh:
```bash
scrcpy --version
```

#### Windows
1. Tải `scrcpy` từ [GitHub chính thức](https://github.com/Genymobile/scrcpy/releases).
2. Giải nén vào thư mục (ví dụ: `C:\scrcpy`).
3. Thêm thư mục `scrcpy` vào biến môi trường PATH (tương tự cách thêm `platform-tools`).
4. Xác minh:
   ```cmd
   scrcpy --version
   ```

### 4. Cài đặt thư viện Python

Công cụ yêu cầu các thư viện `colorama`, `psutil`, và `questionary`. Cài đặt bằng pip:
```bash
pip3 install colorama psutil questionary
```

### 5. Thiết lập kết nối với thiết bị Android

Để sử dụng công cụ, bạn cần kết nối thiết bị Android với máy tính qua USB hoặc Wi-Fi. Dưới đây là hướng dẫn chi tiết.

#### Kích hoạt chế độ nhà phát triển
1. Trên thiết bị Android:
   - Vào **Cài đặt** > **Giới thiệu về điện thoại**.
   - Nhấn 7 lần vào **Số hiệu bản dựng** để bật chế độ nhà phát triển.
   - Vào **Cài đặt** > **Hệ thống** > **Tùy chọn nhà phát triển**.
   - Bật **Gỡ lỗi USB** (cho kết nối USB) hoặc **Gỡ lỗi USB qua Wi-Fi** (cho kết nối không dây).

#### Kết nối qua USB
1. Kết nối thiết bị Android với máy tính bằng cáp USB.
2. Trên thiết bị, cho phép gỡ lỗi USB khi được yêu cầu.
3. Xác minh kết nối:
   ```bash
   adb devices
   ```
   Nếu thấy thiết bị với trạng thái `device` (ví dụ: `1234567890abcdef device`), kết nối đã thành công.

#### Kết nối qua Wi-Fi
1. Đảm bảo thiết bị Android và máy tính ở cùng mạng Wi-Fi.
2. Kết nối thiết bị qua USB và chạy:
   ```bash
   adb tcpip 5555
   ```
3. Tìm địa chỉ IP của thiết bị:
   - Vào **Cài đặt** > **Wi-Fi**, nhấn vào mạng đang kết nối để xem IP (thường dạng `192.168.x.x`).
   - Hoặc chạy:
     ```bash
     adb shell ip addr show wlan0 | grep inet
     ```
4. Ngắt cáp USB và kết nối qua Wi-Fi:
   ```bash
   adb connect <device-ip>:5555
   ```
   Thay `<device-ip>` bằng địa chỉ IP của thiết bị.
5. Xác minh:
   ```bash
   adb devices
   ```
   Thiết bị sẽ xuất hiện với trạng thái `device` (ví dụ: `192.168.1.100:5555 device`).
6. Để sử dụng `scrcpy` qua Wi-Fi, chạy:
   ```bash
   scrcpy -s <device-ip>:5555
   ```

#### Lưu ý khi kết nối
- Nếu thiết bị hiển thị trạng thái `unauthorized`, kiểm tra và cấp quyền trên thiết bị.
- Nếu thiết bị hiển thị trạng thái `offline`, khởi động lại kết nối bằng `adb disconnect` rồi thử lại.
- Đảm bảo không có tường lửa chặn cổng 5555 trên máy tính hoặc thiết bị.

### 6. Cài đặt Skibidi-Toilet-Vaccine

- Tải mã nguồn từ kho lưu trữ:
   ```bash
   git clone https://github.com/vsmz4laj7n/Skibidi-Toilet-Vaccine.git
   cd Skibidi-Toilet-Vaccine
   ```

---

## Sử dụng công cụ

1. Chạy chương trình:
   ```bash
   python3 main.py
   ```
2. Chọn cách hiển thị thông tin thiết bị (Tên thiết bị + IP, chỉ IP, hoặc chỉ tên).
3. Chọn thiết bị từ danh sách thiết bị Android được kết nối.
4. Sử dụng menu tương tác để thực hiện các lệnh:
   - **Tắt YouTube**: Buộc dừng ứng dụng YouTube.
   - **Vô hiệu hóa/Kích hoạt YouTube**: Vô hiệu hóa hoặc kích hoạt YouTube.
   - **Vòng lặp Thoát YouTube**: Tự động dừng YouTube khi phát hiện hoạt động.
   - **Tìm kiếm Hoạt động Ứng dụng**: Tìm và thao tác với ứng dụng dựa trên từ khóa.
   - **Danh sách tất cả ứng dụng**: Liệt kê và thao tác với tất cả ứng dụng.
   - **Bật/Tắt scrcpy**: Chiếu và điều khiển màn hình thiết bị.
   - **Lấy Ứng dụng Đang Chạy**: Xem ứng dụng hiện tại.
   - **Buộc Dừng Ứng dụng**: Dừng ứng dụng cụ thể hoặc ứng dụng đang chạy.
   - **Vòng lặp Buộc Dừng**: Tự động dừng ứng dụng cụ thể khi phát hiện hoạt động.
   - **Bật/Tắt Hiển thị Đầu ra Lệnh**: Hiển thị/ẩn đầu ra chi tiết của lệnh.
   - **Quay lại chọn thiết bị**: Chuyển về menu chọn thiết bị.
   - **Thoát**: Thoát chương trình, dừng các vòng lặp và `scrcpy`.

---

## Cấu trúc mã nguồn

- `main.py`: Xử lý giao diện menu và điều phối lệnh.
- `device_manager.py`: Quản lý thiết bị và thông tin ứng dụng.
- `command_executor.py`: Thực thi lệnh ADB và quản lý vòng lặp giám sát.
- `scrcpy_manager.py`: Quản lý `scrcpy` để chiếu và điều khiển màn hình.

---

## Giải quyết sự cố

- **Không tìm thấy thiết bị**:
  - Kiểm tra **Gỡ lỗi USB** hoặc **Gỡ lỗi USB qua Wi-Fi** đã bật.
  - Chạy `adb devices` để xác minh kết nối.
  - Cài đặt lại ADB nếu cần.
- **scrcpy không chạy**:
  - Xác minh cài đặt bằng `scrcpy --version`.
  - Đảm bảo thiết bị ở trạng thái `device`.
- **Lỗi Python module**:
  - Cài đặt thư viện bằng `pip3 install colorama psutil questionary`.
- **Kết nối Wi-Fi thất bại**:
  - Kiểm tra thiết bị và máy tính trên cùng mạng Wi-Fi.
  - Đảm bảo cổng `<Port>` không bị chặn bởi tường lửa.

---

## Đóng góp

- Fork kho lưu trữ và gửi pull request với cải tiến.
- Báo cáo lỗi hoặc đề xuất tính năng qua Issues trên GitHub.

---
