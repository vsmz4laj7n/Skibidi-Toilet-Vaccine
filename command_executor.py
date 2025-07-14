#!/usr/bin/python3.12
import subprocess
import threading
import time
from colorama import Fore, Style

# Flags and storage for loops and messages
loop_running = False
loop_thread = None
last_loop_message = ""
app_loop_running = False
app_loop_thread = None
app_last_loop_message = ""
target_app_package = ""
chplay_loop_running = False
chplay_loop_thread = None
chplay_last_loop_message = ""

def run_adb_command(command):
    """Execute an ADB command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return "", f"Lỗi: {e}"

def execute_command(command):
    """Execute a given ADB command."""
    return run_adb_command(command)

def youtube_loop(device_serial):
    """Run a loop to continuously check for YouTube activity and force-stop if detected."""
    global loop_running, last_loop_message
    while loop_running:
        output, error = run_adb_command(f"adb -s {device_serial} shell dumpsys activity activities | grep com.google.android.youtube")
        if output:
            stop_output, stop_error = run_adb_command(f"adb -s {device_serial} shell am force-stop com.google.android.youtube")
            last_loop_message = f"{Fore.YELLOW}Phát hiện hoạt động YouTube, đã buộc dừng. Kết quả: {stop_output or 'Không có'}, Lỗi: {stop_error or 'Không có'}{Style.RESET_ALL}"
        else:
            last_loop_message = ""
        time.sleep(5)

def start_youtube_loop(device_serial):
    """Start the YouTube loop in a background thread."""
    global loop_running, loop_thread
    if loop_running:
        return False
    loop_running = True
    loop_thread = threading.Thread(target=youtube_loop, args=(device_serial,), daemon=True)
    loop_thread.start()
    return True

def stop_youtube_loop():
    """Stop the YouTube loop."""
    global loop_running
    if loop_running:
        loop_running = False
        return True
    return False

def chplay_loop(device_serial):
    """Run a loop to continuously check for CH-Play activity and force-stop if detected."""
    global chplay_loop_running, chplay_last_loop_message
    while chplay_loop_running:
        output, error = run_adb_command(f"adb -s {device_serial} shell dumpsys activity activities | grep com.android.vending")
        if output:
            stop_output, stop_error = run_adb_command(f"adb -s {device_serial} shell am force-stop com.android.vending")
            chplay_last_loop_message = f"{Fore.YELLOW}Phát hiện hoạt động CH-Play, đã buộc dừng. Kết quả: {stop_output or 'Không có'}, Lỗi: {stop_error or 'Không có'}{Style.RESET_ALL}"
        else:
            chplay_last_loop_message = ""
        time.sleep(5)

def start_chplay_loop(device_serial):
    """Start the CH-Play loop in a background thread."""
    global chplay_loop_running, chplay_loop_thread
    if chplay_loop_running:
        return False
    chplay_loop_running = True
    chplay_loop_thread = threading.Thread(target=chplay_loop, args=(device_serial,), daemon=True)
    chplay_loop_thread.start()
    return True

def stop_chplay_loop():
    """Stop the CH-Play loop."""
    global chplay_loop_running
    if chplay_loop_running:
        chplay_loop_running = False
        return True
    return False

def app_loop(device_serial, app_package):
    """Run a loop to continuously check for app activity and force-stop if detected."""
    global app_loop_running, app_last_loop_message, target_app_package
    target_app_package = app_package
    while app_loop_running:
        output, error = run_adb_command(f"adb -s {device_serial} shell dumpsys activity activities | grep {app_package}")
        if output:
            stop_output, stop_error = run_adb_command(f"adb -s {device_serial} shell am force-stop {app_package}")
            app_last_loop_message = f"{Fore.YELLOW}Phát hiện hoạt động cho {app_package}, đã buộc dừng. Kết quả: {stop_output or 'Không có'}, Lỗi: {stop_error or 'Không có'}{Style.RESET_ALL}"
        else:
            app_last_loop_message = ""
        time.sleep(5)

def start_app_loop(device_serial, app_package):
    """Start the app loop in a background thread."""
    global app_loop_running, app_loop_thread
    if app_loop_running:
        return False
    app_loop_running = True
    app_loop_thread = threading.Thread(target=app_loop, args=(device_serial, app_package), daemon=True)
    app_loop_thread.start()
    return True

def stop_app_loop():
    """Stop the app loop."""
    global app_loop_running
    if app_loop_running:
        app_loop_running = False
        return True
    return False

def get_loop_status_message():
    """Return the last loop status message (prioritizing app loop, then CH-Play, then YouTube)."""
    global app_last_loop_message, chplay_last_loop_message, last_loop_message
    if app_loop_running and app_last_loop_message:
        return app_last_loop_message
    if chplay_loop_running and chplay_last_loop_message:
        return chplay_last_loop_message
    return last_loop_message
