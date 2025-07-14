# Skibidi-Toilet-Vaccine

`Skibidi-Toilet-Vaccine` is an interactive command-line tool for managing Android devices via ADB (Android Debug Bridge) and `scrcpy` for screen mirroring and control. It provides a user-friendly interface to perform tasks such as force-stopping apps, enabling/disabling apps, running background loops to monitor and stop specific apps (e.g., YouTube or Google Play Store), and controlling `scrcpy` for device screen mirroring. The tool supports multiple platforms (Linux, macOS, Windows) and is designed for both wired (USB) and wireless (Wi-Fi) ADB connections.

This tool is useful for:
- Force-stopping or managing specific apps (including system and user apps).
- Automatically monitoring and stopping apps like YouTube or Google Play Store.
- Mirroring and controlling Android device screens using `scrcpy`.
- Customizing device information display (device name, IP, or both).

---

## System Requirements

- **Operating System**: Linux, macOS, or Windows.
- **Python**: Version 3.12 or higher.
- **ADB (Android Debug Bridge)**: Required for communication with Android devices.
- **scrcpy**: Required for screen mirroring and device control.
- **Android Device**: Developer mode enabled with USB Debugging or Wi-Fi Debugging activated.

---

## Installation

Below are detailed instructions for setting up the required components on Linux, macOS, and Windows.

### 1. Install Python

#### Linux
Most Linux distributions include Python. To check or install Python 3.12:
```bash
python3 --version
```
If needed, install:
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
Use Homebrew to install Python 3.12:
```bash
brew install python@3.12
```
Verify:
```bash
python3.12 --version
pip3.12 --version
```

#### Windows
1. Download Python 3.12 from the [official website](https://www.python.org/downloads/).
2. Run the installer, ensuring **Add Python to PATH** is selected.
3. Verify:
   ```cmd
   python --version
   pip --version
   ```

### 2. Install ADB

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
- Verify:
  ```bash
  adb --version
  ```

#### macOS
Use Homebrew:
```bash
brew install android-platform-tools
```
Verify:
```bash
adb --version
```

#### Windows
1. Download Android SDK Platform Tools from the [official website](https://developer.android.com/studio/releases/platform-tools).
2. Extract to a directory (e.g., `C:\platform-tools`).
3. Add the `platform-tools` directory to the system PATH:
   - Press **Win + R**, type `sysdm.cpl`, and press Enter.
   - Go to **Advanced** > **Environment Variables**.
   - Under **System Variables**, edit **Path** and add the `platform-tools` directory.
4. Verify:
   ```cmd
   adb --version
   ```

### 3. Install scrcpy

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
- Verify:
  ```bash
  scrcpy --version
  ```

#### macOS
Use Homebrew:
```bash
brew install scrcpy
```
Verify:
```bash
scrcpy --version
```

#### Windows
1. Download `scrcpy` from the [official GitHub releases](https://github.com/Genymobile/scrcpy/releases).
2. Extract to a directory (e.g., `C:\scrcpy`).
3. Add the `scrcpy` directory to the system PATH (similar to `platform-tools`).
4. Verify:
   ```cmd
   scrcpy --version
   ```

### 4. Install Python Dependencies

The tool requires the `colorama`, `psutil`, and `questionary` Python libraries. Install them using pip:
```bash
pip3 install colorama psutil questionary
```

### 5. Set Up Android Device Connection

To use the tool, connect your Android device to your computer via USB or Wi-Fi. Follow these steps:

#### Enable Developer Mode
1. On your Android device:
   - Go to **Settings** > **About phone**.
   - Tap **Build number** 7 times to enable Developer Mode.
   - Navigate to **Settings** > **System** > **Developer options**.
   - Enable **USB Debugging** (for USB connections) or **Wireless Debugging** (for Wi-Fi connections).

#### Connect via USB
1. Connect your Android device to your computer using a USB cable.
2. Allow USB debugging when prompted on the device.
3. Verify the connection:
   ```bash
   adb devices
   ```
   If a device appears with the status `device` (e.g., `1234567890abcdef device`), the connection is successful.

#### Connect via Wi-Fi
1. Ensure your Android device and computer are on the same Wi-Fi network.
2. Connect the device via USB and run:
   ```bash
   adb tcpip 5555
   ```
3. Find the device's IP address:
   - Go to **Settings** > **Wi-Fi**, tap the connected network to view the IP (e.g., `192.168.x.x`).
   - Or run:
     ```bash
     adb shell ip addr show wlan0 | grep inet
     ```
4. Disconnect the USB cable and connect via Wi-Fi:
   ```bash
   adb connect <device-ip>:5555
   ```
   Replace `<device-ip>` with the device's IP address.
5. Verify:
   ```bash
   adb devices
   ```
   The device should appear with the status `device` (e.g., `192.168.1.100:5555 device`).
6. To use `scrcpy` via Wi-Fi:
   ```bash
   scrcpy -s <device-ip>:5555
   ```

#### Connection Notes
- If the device shows as `unauthorized`, check the device and allow permissions.
- If the device shows as `offline`, run `adb disconnect` and reconnect.
- Ensure no firewall is blocking port 5555 on your computer or device.

### 6. Install Skibidi-Toilet-Vaccine

Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/vsmz4laj7n/Skibidi-Toilet-Vaccine.git
cd Skibidi-Toilet-Vaccine
```

---

## Usage

1. Run the program:
   ```bash
   python3 main.py
   ```
2. Select how to display device information (Device Name + IP, IP only, or Device Name only).
3. Choose a device from the list of connected Android devices.
4. Use the interactive menu to execute commands:
   - **Tắt YouTube**: Force-stop the YouTube app.
   - **Vô hiệu hóa/Kích hoạt YouTube**: Disable or enable the YouTube app.
   - **Vòng lặp Thoát YouTube**: Automatically stop YouTube when activity is detected.
   - **Vòng lặp Thoát CH-Play**: Automatically stop Google Play Store when activity is detected.
   - **Tìm kiếm Hoạt động Ứng dụng**: Search for apps by keyword and perform actions (force-stop or loop-stop).
   - **Danh sách tất cả ứng dụng**: List all apps (including system apps) and perform actions (force-stop, loop-stop, disable, or enable).
   - **Bật/Tắt scrcpy**: Start or stop screen mirroring with `scrcpy`.
   - **Lấy Ứng dụng Đang Chạy**: View the currently running app.
   - **Buộc Dừng Ứng dụng theo Tên Gói**: Force-stop an app by entering its package name.
   - **Buộc Dừng Ứng dụng Đang Chạy**: Force-stop the currently running app.
   - **Vòng lặp Buộc Dừng theo Tên Gói**: Automatically stop a specific app when activity is detected.
   - **Dừng Vòng lặp Ứng dụng**: Stop any running app loop.
   - **Bật/Tắt Hiển thị Đầu ra Lệnh**: Toggle detailed command output display.
   - **Quay lại chọn thiết bị**: Return to the device selection menu.
   - **Thoát**: Exit the program, stopping all loops and `scrcpy`.

---

## Code Structure

- `main.py`: Handles the interactive menu and orchestrates command execution.
- `device_manager.py`: Manages device detection, selection, and app information retrieval.
- `command_executor.py`: Executes ADB commands and manages background monitoring loops.
- `scrcpy_manager.py`: Manages `scrcpy` for screen mirroring and control.
- `Packages_ADB.txt` (optional): Lists system packages to filter out during app searches (if present).

---

## Troubleshooting

- **No devices found**:
  - Ensure **USB Debugging** or **Wireless Debugging** is enabled.
  - Run `adb devices` to verify the connection.
  - Reinstall ADB if necessary.
- **scrcpy fails to run**:
  - Verify installation with `scrcpy --version`.
  - Ensure the device is in `device` status.
- **Python module errors**:
  - Install dependencies with `pip3 install colorama psutil questionary`.
- **Wi-Fi connection issues**:
  - Confirm the device and computer are on the same Wi-Fi network.
  - Ensure port 5555 is not blocked by a firewall.
- **Packages_ADB.txt not found**:
  - The tool will still function but won't filter system apps during searches.

---

## Contributing

- Fork the repository and submit pull requests with improvements.
- Report bugs or suggest features via GitHub Issues.

---
