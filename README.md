# Skibidi-Toilet-Vaccine

`Skibidi-Toilet-Vaccine` là một công cụ dòng lệnh tương tác để quản lý thiết bị Android thông qua ADB (Android Debug Bridge) và `scrcpy` để chiếu màn hình và điều khiển thiết bị. Công cụ cung cấp giao diện thân thiện với người dùng để thực hiện các tác vụ như buộc dừng ứng dụng, kích hoạt/vô hiệu hóa ứng dụng, chạy vòng lặp nền để giám sát và dừng các ứng dụng cụ thể (ví dụ: YouTube hoặc Google Play Store), và điều khiển `scrcpy` để chiếu màn hình thiết bị. Công cụ hỗ trợ đa nền tảng (Linux, macOS, Windows) và phù hợp cho cả kết nối có dây (USB) và không dây (Wi-Fi).

Công cụ này hữu ích cho:
- Buộc dừng hoặc quản lý các ứng dụng cụ thể (bao gồm ứng dụng hệ thống và người dùng).
- Tự động giám sát và dừng các ứng dụng như YouTube hoặc Google Play Store.
- Chiếu và điều khiển màn hình thiết bị Android bằng `scrcpy`.
- Tùy chỉnh hiển thị thông tin thiết bị (tên thiết bị, IP, hoặc cả hai).

---

## Yêu cầu hệ thống

- **Hệ điều hành**: Linux, macOS, hoặc Windows.
- **Python**: Phiên bản 3.12 hoặc cao hơn.
- **ADB (Android Debug Bridge)**: Cần thiết để giao tiếp với thiết bị Android.
- **scrcpy**: Cần thiết để chiếu và điều khiển màn hình thiết bị.
- **Thiết bị Android**: Bật chế độ nhà phát triển và kích hoạt Gỡ lỗi USB hoặc Gỡ lỗi Wi-Fi.

---

## Cài đặt

Dưới đây là hướng dẫn chi tiết để cài đặt các thành phần cần thiết trên Linux, macOS và Windows.

### 1. Cài đặt Python

#### Linux
Hầu hết các bản phân phối Linux đã có Python. Để kiểm tra hoặc cài đặt Python 3.12:
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
1. Tải Python 3.12 từ [trang web chính thức](https://www.python.org/downloads/).
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
1. Tải Android SDK Platform Tools từ [trang web chính thức](https://developer.android.com/studio/releases/platform-tools).
2. Giải nén vào một thư mục (ví dụ: `C:\platform-tools`).
3. Thêm thư mục `platform-tools` vào biến PATH của hệ thống:
   - Nhấn **Win + R**, gõ `sysdm.cpl`, nhấn Enter.
   - Vào tab **Nâng cao** > **Biến môi trường**.
   - Trong **Biến hệ thống**, chỉnh sửa **Path**, thêm đường dẫn đến thư mục `platform-tools`.
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
2. Giải nén vào một thư mục (ví dụ: `C:\scrcpy`).
3. Thêm thư mục `scrcpy` vào biến PATH của hệ thống (tương tự như `platform-tools`).
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

Để sử dụng công cụ, cần kết nối thiết bị Android với máy tính qua USB hoặc Wi-Fi. Dưới đây là các bước chi tiết:

#### Kích hoạt chế độ nhà phát triển
1. Trên thiết bị Android:
   - Vào **Cài đặt** > **Giới thiệu về điện thoại**.
   - Nhấn 7 lần vào **Số hiệu bản dựng** để bật chế độ nhà phát triển.
   - Vào **Cài đặt** > **Hệ thống** > **Tùy chọn nhà phát triển**.
   - Bật **Gỡ lỗi USB** (cho kết nối USB) hoặc **Gỡ lỗi không dây** (cho kết nối Wi-Fi).

#### Kết nối qua USB
1. Kết nối thiết bị Android với máy tính bằng cáp USB.
2. Cho phép gỡ lỗi USB khi được yêu cầu trên thiết bị.
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
   - Vào **Cài đặt** > **Wi-Fi**, nhấn vào mạng đang kết nối để xem IP (ví dụ: `192.168.x.x`).
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
6. Để sử dụng `scrcpy` qua Wi-Fi:
   ```bash
   scrcpy -s <device-ip>:5555
   ```

#### Lưu ý khi kết nối
- Nếu thiết bị hiển thị trạng thái `unauthorized`, kiểm tra và cấp quyền trên thiết bị.
- Nếu thiết bị hiển thị trạng thái `offline`, chạy `adb disconnect` rồi thử lại.
- Đảm bảo không có tường lửa chặn cổng 5555 trên máy tính hoặc thiết bị.

### 6. Cài đặt Skibidi-Toilet-Vaccine

Tải mã nguồn từ kho lưu trữ và di chuyển vào thư mục dự án:
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
2. Chọn cách hiển thị thông tin thiết bị (Tên thiết bị + IP, Chỉ IP, hoặc Chỉ tên thiết bị).
3. Chọn thiết bị từ danh sách các thiết bị Android được kết nối.
4. Sử dụng menu tương tác để thực hiện các lệnh:
   - **Tắt YouTube**: Buộc dừng ứng dụng YouTube.
   - **Vô hiệu hóa/Kích hoạt YouTube**: Vô hiệu hóa hoặc kích hoạt ứng dụng YouTube.
   - **Vòng lặp Thoát YouTube**: Tự động dừng YouTube khi phát hiện hoạt động.
   - **Vòng lặp Thoát CH-Play**: Tự động dừng Google Play Store khi phát hiện hoạt động.
   - **Tìm kiếm Hoạt động Ứng dụng**: Tìm kiếm ứng dụng theo từ khóa và thực hiện các hành động (buộc dừng hoặc vòng lặp dừng).
   - **Danh sách tất cả ứng dụng**: Liệt kê tất cả ứng dụng (bao gồm ứng dụng hệ thống) và thực hiện các hành động (buộc dừng, vòng lặp dừng, vô hiệu hóa, hoặc kích hoạt).
   - **Bật/Tắt scrcpy**: Bắt đầu hoặc dừng chiếu màn hình bằng `scrcpy`.
   - **Lấy Ứng dụng Đang Chạy**: Xem ứng dụng hiện đang chạy.
   - **Buộc Dừng Ứng dụng theo Tên Gói**: Buộc dừng một ứng dụng bằng cách nhập tên gói.
   - **Buộc Dừng Ứng dụng Đang Chạy**: Buộc dừng ứng dụng hiện đang chạy.
   - **Vòng lặp Buộc Dừng theo Tên Gói**: Tự động dừng một ứng dụng cụ thể khi phát hiện hoạt động.
   - **Dừng Vòng lặp Ứng dụng**: Dừng bất kỳ vòng lặp ứng dụng nào đang chạy.
   - **Bật/Tắt Hiển thị Đầu ra Lệnh**: Bật/tắt hiển thị chi tiết đầu ra của lệnh.
   - **Quay lại chọn thiết bị**: Quay lại menu chọn thiết bị.
   - **Thoát**: Thoát chương trình, dừng tất cả các vòng lặp và `scrcpy`.

---

## Cấu trúc mã nguồn

- `main.py`: Xử lý menu tương tác và điều phối thực thi lệnh.
- `device_manager.py`: Quản lý phát hiện thiết bị, lựa chọn thiết bị, và lấy thông tin ứng dụng.
- `command_executor.py`: Thực thi các lệnh ADB và quản lý các vòng lặp giám sát nền.
- `scrcpy_manager.py`: Quản lý `scrcpy` để chiếu và điều khiển màn hình.
- `Packages_ADB.txt` (tùy chọn): Liệt kê các gói hệ thống để lọc trong quá trình tìm kiếm ứng dụng (nếu có).

---

## Giải quyết sự cố

- **Không tìm thấy thiết bị**:
  - Đảm bảo **Gỡ lỗi USB** hoặc **Gỡ lỗi không dây** đã được bật.
  - Chạy `adb devices` để xác minh kết nối.
  - Cài đặt lại ADB nếu cần.
- **scrcpy không chạy**:
  - Xác minh cài đặt bằng `scrcpy --version`.
  - Đảm bảo thiết bị ở trạng thái `device`.
- **Lỗi module Python**:
  - Cài đặt các thư viện bằng `pip3 install colorama psutil questionary`.
- **Lỗi kết nối Wi-Fi**:
  - Xác minh thiết bị và máy tính ở cùng mạng Wi-Fi.
  - Đảm bảo cổng 5555 không bị chặn bởi tường lửa.
- **Không tìm thấy Packages_ADB.txt**:
  - Công cụ vẫn hoạt động nhưng không lọc ứng dụng hệ thống khi tìm kiếm.

---

## Đóng góp

- Fork kho lưu trữ và gửi pull request với các cải tiến.
- Báo cáo lỗi hoặc đề xuất tính năng qua Issues trên GitHub.

---
