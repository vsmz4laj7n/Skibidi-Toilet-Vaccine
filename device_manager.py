#!/usr/bin/python3.12
import subprocess
from questionary import select, Style as QuestionaryStyle
from rich.console import Console

console = Console()

def run_adb_command(command):
    """Execute an ADB command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return "", f"Lỗi: {e}"

def get_device_name(device_serial):
    """Get the device name/model using adb shell getprop."""
    output, error = run_adb_command(f"adb -s {device_serial} shell getprop ro.product.model")
    if error or not output:
        return device_serial
    return output.strip()

def get_connected_devices():
    """Get list of connected ADB devices with their names."""
    output, error = run_adb_command("adb devices")
    if error:
        console.print(f"[red]Lỗi khi lấy danh sách thiết bị: {error}[/red]")
        return []
    devices = []
    lines = output.splitlines()
    for line in lines[1:]:  # Skip first line ("List of devices attached")
        if line.strip():
            serial = line.split()[0]
            name = get_device_name(serial)
            devices.append({'serial': serial, 'name': name})
    return devices

def select_device(devices, display_choice="Tên thiết bị (IP)"):
    """Prompt user to select a device from connected devices, showing info as per display_choice."""
    custom_style = QuestionaryStyle([
        ('qmark', 'fg:#673ab8 bold'),
        ('question', 'fg:#ffffff bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#ff9f43 bold'),
        ('selected', 'fg:#5c35cc bold'),
    ])
    if display_choice == "Tên thiết bị (IP)":
        choices = [f"{d['name']} ({d['serial']})" for d in devices]
    elif display_choice == "Thiết bị IP":
        choices = [d['serial'] for d in devices]
    elif display_choice == "Chỉ tên thiết bị":
        choices = [d['name'] for d in devices]
    else:
        choices = [f"{d['name']} ({d['serial']})" for d in devices]
    selected = select(
        "Chọn một thiết bị:",
        choices=choices,
        style=custom_style
    ).ask()
    # Find the selected device
    for d in devices:
        if display_choice == "Tên thiết bị (IP)":
            if selected == f"{d['name']} ({d['serial']})":
                return d['serial'], d['name']
        elif display_choice == "Thiết bị IP":
            if selected == d['serial']:
                return d['serial'], d['name']
        elif display_choice == "Chỉ tên thiết bị":
            if selected == d['name']:
                return d['serial'], d['name']
    # Fallback
    return devices[0]['serial'], devices[0]['name']

def get_system_packages():
    """Return a set of system packages from Packages_ADB.txt."""
    system_packages = set()
    try:
        with open("Packages_ADB.txt", "r") as f:
            for line in f:
                if line.startswith("package:"):
                    package = line.replace("package:", "").strip()
                    system_packages.add(package)
    except FileNotFoundError:
        console.print("[red]Không tìm thấy file Packages_ADB.txt. Không thể lọc gói hệ thống.[/red]")
    return system_packages

def list_installed_apps(device_serial, exclude_system=True):
    """List installed apps, optionally excluding system packages."""
    system_packages = get_system_packages() if exclude_system else set()
    command = f"adb -s {device_serial} shell pm list packages"
    output, error = run_adb_command(command)
    if error:
        console.print(f"[red]Lỗi khi liệt kê các gói: {error}[/red]")
        return []
    packages = [line.replace('package:', '').strip() for line in output.splitlines() if line.strip()]
    # Filter out system packages if requested
    if exclude_system:
        packages = [pkg for pkg in packages if pkg not in system_packages]
    # Get app labels (names) for each package
    app_list = []
    for pkg in packages:
        label_cmd = f"adb -s {device_serial} shell dumpsys package {pkg} | grep 'application-label:'"
        label_out, _ = run_adb_command(label_cmd)
        label = label_out.replace('application-label:', '').strip() if label_out else pkg
        app_list.append({'package': pkg, 'label': label})
    return app_list
