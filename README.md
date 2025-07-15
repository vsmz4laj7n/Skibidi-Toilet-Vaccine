# Skibidi-Toilet-Vaccine – Phiên bản “Phụ huynh siêu cấp”

> *Vâng, bạn không nhìn nhầm đâu.* Đây là **remote kiểm soát con trẻ** giả danh công cụ ADB. Nó không yêu cầu root (vì chúng ta là những phụ huynh văn minh, không muốn "đục khoét" ROM), nhưng đủ quyền lực để đóng sập YouTube ngay khi tiếng nhạc "Skibidi" vừa vang lên.
> **Tuyên bố chịu trách nhiệm**: Trẻ em 0–99 tuổi có thể sẽ khóc. Bạn đã được cảnh báo!

---

## Tóm tắt chức năng

| Tính năng                        | Công dụng (cực kỳ “phụ huynh”)                                         |
| -------------------------------- | ---------------------------------------------------------------------- |
| **Buộc dừng ứng dụng**           | Tắt YouTube, CH Play hoặc *bất kỳ* app nào khiến bạn đau đầu.          |
| **Vòng lặp giám sát**            | App vừa mở? 5 giây sau đã bị kết liễu. Trẻ chưa kịp bấm video thứ hai. |
| **Quản lý âm lượng & phím cứng** | Giảm âm lượng xuống 0 cho đến khi bài tập về nhà xong.                 |
| **scrcpy một chạm**              | Chiếu màn hình thiết bị lên PC để đảm bảo không có "nội dung lạ".      |

---

## Giới hạn (Đọc kỹ kẻo than!)

1. **Không root, không khóc!**
   Công cụ *không* can thiệp sâu vào hệ thống. Nếu ROM của bé yêu chặn lệnh ADB nào đó, bạn đành chịu.
2. **Quyền hạn tùy ROM**
   Mỗi hãng Android thích tự chế permission. Lỗi `SecurityException`? – Không phải lỗi của tool, mà là của *vũ trụ*.🥲
3. **Bắt buộc bật Developer Options**

   * *USB debugging* **và** *USB debugging (Security settings)*
   * Hoặc *Wireless debugging* (nếu bạn ghét dây).
     Không bật = tool bất lực.
4. **Giả lập keyevent**
   Một số máy (đặc biệt Xiaomi, Oppo đời mới) chặn `input keyevent`. Nếu lệnh "nhấn Home" không phản hồi – xin chia buồn.

---

## Yêu cầu hệ thống

* **OS**: Windows / macOS / Linux (hơi ít thôi, chứ đủ dùng).
* **Python ≥ 3.12** – vì code author thích những thứ mới mẻ.
* **ADB** (Android Platform‑Tools).
* **scrcpy** ≥ 2.4 (không có cũng được, nhưng mất fun).
* **Thư viện Python**: `questionary`, `rich`, `psutil`, `colorama`.
* **Thiết bị Android** đã **mở khóa OEM** *\[đùa chút]* – chỉ cần Developer Options & Debugging.

---

## Cài đặt (từng bước không khóc)

> Ví dụ bên dưới dùng dấu **\$** cho bash, **PS>** cho PowerShell.

### 1 – Cài Python 3.12

* **Windows**: Tải installer từ python.org & tick *Add to PATH*.
* **macOS**: `brew install python@3.12`.
* **Ubuntu/Debian**:  `$ sudo apt install python3.12 python3-pip`.

### 2 – Cài ADB & scrcpy

* **Windows**: Giải nén *platform‑tools* và *scrcpy* vào `C:\tools`, thêm vào PATH.
* **macOS**: `brew install android-platform-tools scrcpy`.
* **Linux**: `$ sudo apt install android-tools-adb scrcpy` (hoặc tương đương).

### 3 – Clone dự án

```bash
$ git clone https://github.com/vsmz4laj7n/Skibidi-Toilet-Vaccine.git
$ cd Skibidi-Toilet-Vaccine
```

### 4 – Cài thư viện Python

```bash
$ pip install -r requirements.txt  # hoặc
$ pip install questionary rich psutil colorama
```

### 5 – Chuẩn bị điện thoại

1. Mở **Cài đặt → Giới thiệu → Số hiệu bản dựng** (gõ 7 lần).
2. Vào **Tùy chọn nhà phát triển**: bật **Gỡ lỗi USB** *và* **USB debugging (Security settings)**.
3. (Tuỳ chọn) Bật **Gỡ lỗi không dây** → Ghép cặp qua mã PIN → Lấy IP.

### 6 – Kết nối ADB

* **USB**:

  ```bash
  $ adb devices  # Đồng ý "Allow USB debugging" trên điện thoại
  ```
* **Wi‑Fi** (sau khi đã kết nối USB một lần):

  ```bash
  $ adb tcpip 5555
  $ adb connect <IP-thiết-bị>:5555
  ```

> Thấy trạng thái `device`? Xin chúc mừng, bạn đã sẵn sàng "đàn áp" YouTube.

---

## Cách sử dụng (phiên bản rút gọn)

```bash
$ python main.py
```

1. Chọn cách hiển thị thiết bị (tên, IP…).
2. Chọn thiết bị.
3. Menu hiện ra – bạn tha hồ:

   * **Tắt/khóa YouTube** tức thì hoặc theo *vòng lặp mãi mãi*.
   * **Khoá CH Play** để bé khỏi cài game mới.
   * **Force‑stop** bất kỳ app nào (TikTok? Bye!).
   * **Mở scrcpy** để soi màn hình từ xa.
   * **Giảm âm lượng** hay giả lập *Home/Back* không cần chạm thiết bị.

> **Mẹo**: Bật tuỳ chọn “Hiển thị đầu ra lệnh” nếu bạn muốn thấy chi tiết – và biết chắc lệnh đã trúng đích.

---

## Khắc phục sự cố nhanh

| Vấn đề              | Khả năng & Giải pháp                                               |
| ------------------- | ------------------------------------------------------------------ |
| `unauthorized`      | Mở điện thoại, nhấn **Allow USB debugging**.                       |
| `offline`           | `adb disconnect && adb devices` rồi thử lại.                       |
| `device not found`  | Kiểm tra cáp, driver, hoặc Wi‑Fi cùng mạng.                        |
| `SecurityException` | ROM chặn lệnh – thử OEM khác hoặc khóc nhẹ.                        |
| scrcpy không mở     | Kiểm tra `scrcpy --version`, đảm bảo device ở trạng thái `device`. |

---

## Cấu trúc thư mục

```
├── main.py               # Menu tương tác chính
├── device_manager.py     # Phát hiện & chọn thiết bị
├── command_executor.py   # Thực thi ADB & quản lý vòng lặp
├── scrcpy_manager.py     # Bật/tắt scrcpy
├── Packages_ADB.txt      # (tuỳ chọn) Danh sách gói hệ thống để lọc
└── README.md             # Chính là file bạn đang đọc
```

---

## Giấy phép

MIT – Bởi vì ngay cả phụ huynh cũng yêu tự do phần mềm.

---

*Happy parenting & coding!* 🎉
