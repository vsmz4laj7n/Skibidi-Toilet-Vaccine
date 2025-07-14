#!/usr/bin/python3.12
import subprocess
import psutil
from colorama import Fore, Style

# Global variable to track scrcpy process
scrcpy_process = None

def run_scrcpy(device_serial):
    """Run scrcpy for the specified device serial."""
    global scrcpy_process
    if scrcpy_process and scrcpy_process.is_running():
        return "", f"{Fore.YELLOW}scrcpy đã đang chạy cho thiết bị {device_serial}{Style.RESET_ALL}"
    
    try:
        # Check if scrcpy is installed
        check_cmd = "scrcpy --version"
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return "", f"{Fore.RED}Lỗi: scrcpy không được cài đặt hoặc không tìm thấy. Vui lòng cài đặt scrcpy trước.{Style.RESET_ALL}"
        
        # Run scrcpy with the specified device serial
        cmd = f"scrcpy -s {device_serial} --no-audio"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        scrcpy_process = psutil.Process(process.pid)
        
        # Wait briefly to capture initial output or errors
        try:
            stdout, stderr = process.communicate(timeout=5)
            if process.returncode != 0:
                scrcpy_process = None
                return "", f"{Fore.RED}Lỗi khi chạy scrcpy: {stderr.strip()}{Style.RESET_ALL}"
            return f"{Fore.GREEN}Đã khởi chạy scrcpy cho thiết bị {device_serial}{Style.RESET_ALL}", ""
        except subprocess.TimeoutExpired:
            # If timeout expires, scrcpy is likely running successfully in a new window
            return f"{Fore.GREEN}Đã khởi chạy scrcpy cho thiết bị {device_serial}{Style.RESET_ALL}", ""
    except subprocess.CalledProcessError as e:
        scrcpy_process = None
        return "", f"{Fore.RED}Lỗi: {e}{Style.RESET_ALL}"
    except psutil.NoSuchProcess:
        scrcpy_process = None
        return "", f"{Fore.RED}Lỗi: Không thể theo dõi quá trình scrcpy.{Style.RESET_ALL}"

def stop_scrcpy():
    """Stop the running scrcpy process."""
    global scrcpy_process
    if scrcpy_process and scrcpy_process.is_running():
        try:
            scrcpy_process.terminate()
            scrcpy_process.wait(timeout=5)
            scrcpy_process = None
            return f"{Fore.YELLOW}Đã dừng scrcpy.{Style.RESET_ALL}", ""
        except psutil.TimeoutExpired:
            scrcpy_process.kill()
            scrcpy_process = None
            return f"{Fore.YELLOW}Đã buộc dừng scrcpy sau khi hết thời gian chờ.{Style.RESET_ALL}", ""
        except psutil.NoSuchProcess:
            scrcpy_process = None
            return "", f"{Fore.RED}Lỗi: Không tìm thấy quá trình scrcpy.{Style.RESET_ALL}"
    return "", f"{Fore.RED}Không có scrcpy đang chạy.{Style.RESET_ALL}"

def is_scrcpy_running():
    """Check if scrcpy is currently running."""
    global scrcpy_process
    return scrcpy_process is not None and scrcpy_process.is_running()
