#!/usr/bin/python3.12
import subprocess
import psutil
from rich.console import Console

console = Console()

# Global variable to track scrcpy process
scrcpy_process = None

def run_scrcpy(device_serial):
    """Run scrcpy for the specified device serial."""
    global scrcpy_process
    if scrcpy_process and scrcpy_process.is_running():
        return "", "[yellow]scrcpy đã đang chạy cho thiết bị {device_serial}[/yellow]".format(device_serial=device_serial)

    try:
        # Check if scrcpy is installed
        check_cmd = "scrcpy --version"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return "", "[red]Lỗi: scrcpy không được cài đặt hoặc không tìm thấy. Vui lòng cài đặt scrcpy trước.[/red]"

        # Run scrcpy with the specified device serial
        cmd = f"scrcpy -s {device_serial} --no-audio"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        scrcpy_process = psutil.Process(process.pid)

        # Wait briefly to capture initial output or errors
        try:
            stdout, stderr = process.communicate(timeout=5)
            if process.returncode != 0:
                scrcpy_process = None
                return "", f"[red]Lỗi khi chạy scrcpy: {stderr.strip()}[/red]"
            return f"[green]Đã khởi chạy scrcpy cho thiết bị {device_serial}[/green]", ""
        except subprocess.TimeoutExpired:
            # If timeout expires, scrcpy is likely running successfully in a new window
            return f"[green]Đã khởi chạy scrcpy cho thiết bị {device_serial}[/green]", ""
    except subprocess.CalledProcessError as e:
        scrcpy_process = None
        return "", f"[red]Lỗi: {e}[/red]"
    except psutil.NoSuchProcess:
        scrcpy_process = None
        return "", "[red]Lỗi: Không thể theo dõi quá trình scrcpy.[/red]"

def stop_scrcpy():
    """Stop the running scrcpy process."""
    global scrcpy_process
    if scrcpy_process and scrcpy_process.is_running():
        try:
            scrcpy_process.terminate()
            scrcpy_process.wait(timeout=5)
            scrcpy_process = None
            return "[yellow]Đã dừng scrcpy.[/yellow]", ""
        except psutil.TimeoutExpired:
            scrcpy_process.kill()
            scrcpy_process = None
            return "[yellow]Đã buộc dừng scrcpy sau khi hết thời gian chờ.[/yellow]", ""
        except psutil.NoSuchProcess:
            scrcpy_process = None
            return "", "[red]Lỗi: Không tìm thấy quá trình scrcpy.[/red]"
    return "", "[red]Không có scrcpy đang chạy.[/red]"

def is_scrcpy_running():
    """Check if scrcpy is currently running."""
    global scrcpy_process
    return scrcpy_process is not None and scrcpy_process.is_running()
