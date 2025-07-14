#!/usr/bin/python3.12
import sys
import time
import re
import signal
from colorama import init, Fore, Style
from questionary import select, Style as QuestionaryStyle, text
from device_manager import get_connected_devices, select_device, list_installed_apps
from command_executor import execute_command, start_youtube_loop, stop_youtube_loop, get_loop_status_message, start_app_loop, stop_app_loop
from scrcpy_manager import run_scrcpy, stop_scrcpy, is_scrcpy_running

# Initialize colorama for colored output
init()

# Global flag to control main loop
return_to_device_selection = False

# Global flag to control command output display (omit by default)
show_command_output = False

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully shut down the script."""
    print(f"\n{Fore.YELLOW}Đã nhận Ctrl+C, đang dừng các vòng lặp và scrcpy...{Style.RESET_ALL}")
    stop_youtube_loop()
    stop_app_loop()
    stop_scrcpy()
    print(f"{Fore.GREEN}Đã thoát chương trình.{Style.RESET_ALL}")
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Embedded commands (previously in commands.json)
COMMANDS = [
    {
        "name": "Tắt YouTube",
        "command": "adb -s {device_serial} shell am force-stop com.google.android.youtube"
    },
    {
        "name": "Vô hiệu hóa YouTube",
        "command": "adb -s {device_serial} shell pm disable-user --user 0 com.google.android.youtube"
    },
    {
        "name": "Kích hoạt YouTube",
        "command": "adb -s {device_serial} shell pm enable com.google.android.youtube"
    },
    {
        "name": "Vòng lặp Thoát YouTube",
        "action": "loop_youtube"
    },
    {
        "name": "Dừng Vòng lặp YouTube",
        "action": "stop_youtube_loop"
    },
    {
        "name": "Tìm kiếm Hoạt động Ứng dụng",
        "action": "search_app_activity"
    },
    {
        "name": "Danh sách tất cả ứng dụng",
        "action": "list_all_apps"
    },
    {
        "name": "Bật scrcpy",
        "action": "run_scrcpy"
    },
    {
        "name": "Tắt scrcpy",
        "action": "stop_scrcpy"
    },
    {
        "name": "Lấy Ứng dụng Đang Chạy",
        "action": "get_current_app"
    },
    {
        "name": "Buộc Dừng Ứng dụng theo Tên Gói",
        "action": "force_stop_by_package"
    },
    {
        "name": "Buộc Dừng Ứng dụng Đang Chạy",
        "action": "force_stop_current_app"
    },
    {
        "name": "Vòng lặp Buộc Dừng theo Tên Gói",
        "action": "loop_force_stop_by_package"
    },
    {
        "name": "Dừng Vòng lặp Ứng dụng",
        "action": "stop_app_loop"
    },
    {
        "name": "Bật/Tắt Hiển thị Đầu ra Lệnh",
        "action": "toggle_command_output"
    },
    {
        "name": "Quay lại chọn thiết bị",
        "action": "return_to_device_selection"
    }
]

def show_menu(device_serial, commands, device_name=None, display_choice="Tên thiết bị (IP)"):
    """Show interactive menu with dynamic message updates."""
    global return_to_device_selection, show_command_output
    custom_style = QuestionaryStyle([
        ('qmark', 'fg:#673ab8 bold'),
        ('question', 'fg:#ffffff bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#ff9f43 bold'),
        ('selected', 'fg:#5c35cc bold'),
    ])

    last_message = ""
    choice = None  # Initialize choice to avoid UnboundLocalError
    while True:
        # Get the latest loop status message
        message = get_loop_status_message()
        if is_scrcpy_running():
            message = f"{message} | scrcpy đang chạy" if message else "scrcpy đang chạy"
        # Add command output status to the message
        output_status = "Bật" if show_command_output else "Tắt"
        message = f"{message} | Đầu ra lệnh: {output_status}" if message else f"Đầu ra lệnh: {output_status}"

        # Device display logic
        if display_choice == "Tên thiết bị (IP)":
            device_display = f"{device_name} ({device_serial})" if device_name else device_serial
        elif display_choice == "Thiết bị IP":
            device_display = device_serial
        elif display_choice == "Chỉ tên thiết bị":
            device_display = device_name if device_name else device_serial
        else:
            device_display = device_serial

        # Get user choice
        choice = select(
            f"Thiết bị đã chọn: {device_display}\nCác lệnh có sẵn:",
            choices=[cmd["name"] for cmd in commands] + ["Thoát"],
            style=custom_style
        ).ask()

        # Clear previous output and print updated menu
        print("\033[2A\033[K")  # Move up 2 lines and clear the line
        print(f"Các lệnh có sẵn: (Sử dụng phím mũi tên)")
        for cmd in commands:
            print(f" {'»' if cmd['name'] == choice else ' '} {cmd['name']}")
        print(f"=> {message or ' '}")
        last_message = message

        if choice == "Thoát":
            if stop_youtube_loop() or stop_app_loop():
                print(f"\033[2A\033[K=> {Fore.YELLOW}Đã dừng tất cả các vòng lặp.{Style.RESET_ALL}")
            stop_scrcpy()  # Stop scrcpy when exiting
            print(f"{Fore.GREEN}Đang thoát...{Style.RESET_ALL}")
            sys.exit(0)

        for cmd in commands:
            if cmd["name"] == choice:
                if cmd.get("action") == "loop_youtube":
                    start_youtube_loop(device_serial)
                    print(f"\033[2A\033[K=> {Fore.YELLOW}Đã bắt đầu vòng lặp YouTube trong nền.{Style.RESET_ALL}")
                elif cmd.get("action") == "stop_youtube_loop":
                    if stop_youtube_loop():
                        print(f"\033[2A\033[K=> {Fore.YELLOW}Đã dừng vòng lặp YouTube.{Style.RESET_ALL}")
                    else:
                        print(f"\033[2A\033[K=> {Fore.RED}Không có vòng lặp YouTube nào đang chạy.{Style.RESET_ALL}")
                elif cmd.get("action") == "stop_app_loop":
                    if stop_app_loop():
                        print(f"\033[2A\033[K=> {Fore.YELLOW}Đã dừng vòng lặp ứng dụng.{Style.RESET_ALL}")
                    else:
                        print(f"\033[2A\033[K=> {Fore.RED}Không có vòng lặp ứng dụng nào đang chạy.{Style.RESET_ALL}")
                elif cmd.get("action") == "search_app_activity":
                    # Prompt user for search query
                    query = text(
                        "Nhập từ khóa tìm kiếm (trong tên ứng dụng hoặc gói):",
                        style=custom_style
                    ).ask()
                    if not query:
                        print(f"\033[2A\033[K=> {Fore.RED}Không nhập từ khóa, hủy tìm kiếm.{Style.RESET_ALL}")
                        continue
                    # List installed apps (excluding system) and filter by query
                    app_list = list_installed_apps(device_serial, exclude_system=True)
                    if not app_list:
                        print(f"{Fore.RED}Không tìm thấy ứng dụng người dùng hoặc xảy ra lỗi.{Style.RESET_ALL}")
                        continue
                    # Filter apps based on query
                    query = query.lower()
                    filtered_apps = [
                        app for app in app_list
                        if query in app['label'].lower() or query in app['package'].lower()
                    ]
                    if not filtered_apps:
                        print(f"{Fore.RED}Không tìm thấy ứng dụng nào khớp với từ khóa '{query}'.{Style.RESET_ALL}")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in filtered_apps] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    # Extract package name from selection
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    action = select(
                        "Chọn hành động:",
                        choices=["Buộc dừng một lần", "Vòng lặp Dừng", "Hủy"],
                        style=custom_style
                    ).ask()
                    if action == "Buộc dừng một lần":
                        print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}{Style.RESET_ALL}")
                        output, error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                        if error:
                            print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                        elif show_command_output and output:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Đã buộc dừng ứng dụng {app_package}.{Style.RESET_ALL}")
                    elif action == "Vòng lặp Dừng":
                        start_app_loop(device_serial, app_package)
                        print(f"\033[2A\033[K=> {Fore.YELLOW}Đã bắt đầu vòng lặp dừng cho {app_package} trong nền.{Style.RESET_ALL}")
                elif cmd.get("action") == "list_all_apps":
                    # List all apps (including system) and let user select
                    app_list = list_installed_apps(device_serial, exclude_system=False)
                    if not app_list:
                        print(f"{Fore.RED}Không tìm thấy ứng dụng hoặc xảy ra lỗi.{Style.RESET_ALL}")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in app_list] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    # Extract package name from selection
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    action = select(
                        "Chọn hành động:",
                        choices=["Buộc dừng một lần", "Vòng lặp Dừng", "Vô hiệu hóa", "Kích hoạt", "Hủy"],
                        style=custom_style
                    ).ask()
                    if action == "Buộc dừng một lần":
                        print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}{Style.RESET_ALL}")
                        output, error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                        if error:
                            print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                        elif show_command_output and output:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Đã buộc dừng ứng dụng {app_package}.{Style.RESET_ALL}")
                    elif action == "Vòng lặp Dừng":
                        start_app_loop(device_serial, app_package)
                        print(f"\033[2A\033[K=> {Fore.YELLOW}Đã bắt đầu vòng lặp dừng cho {app_package} trong nền.{Style.RESET_ALL}")
                    elif action == "Vô hiệu hóa":
                        print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell pm disable-user --user 0 {app_package}{Style.RESET_ALL}")
                        output, error = execute_command(f"adb -s {device_serial} shell pm disable-user --user 0 {app_package}")
                        if error:
                            print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                        elif show_command_output and output:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Đã vô hiệu hóa ứng dụng {app_package}.{Style.RESET_ALL}")
                    elif action == "Kích hoạt":
                        print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell pm enable {app_package}{Style.RESET_ALL}")
                        output, error = execute_command(f"adb -s {device_serial} shell pm enable {app_package}")
                        if error:
                            print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                        elif show_command_output and output:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.GREEN}Đã kích hoạt ứng dụng {app_package}.{Style.RESET_ALL}")
                elif cmd.get("action") == "run_scrcpy":
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang khởi chạy scrcpy cho thiết bị {device_serial}{Style.RESET_ALL}")
                    output, error = run_scrcpy(device_serial)
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    else:
                        print(f"\033[1A\033[K=> {Fore.GREEN}{'Kết quả: ' + output if show_command_output and output else 'Đã khởi chạy scrcpy.'}{Style.RESET_ALL}")
                elif cmd.get("action") == "stop_scrcpy":
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang dừng scrcpy cho thiết bị {device_serial}{Style.RESET_ALL}")
                    output, error = stop_scrcpy()
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    else:
                        print(f"\033[1A\033[K=> {Fore.GREEN}{'Kết quả: ' + output if show_command_output and output else 'Đã dừng scrcpy.'}{Style.RESET_ALL}")
                elif cmd.get("action") == "get_current_app":
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang lấy ứng dụng đang chạy...{Style.RESET_ALL}")
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    elif output:
                        # Extract package name from output like "mCurrentFocus=Window{d1bd98d u0 com.mojang.minecraftpe/com.mojang.minecraftpe.MainActivity}"
                        # or "mFocusedApp=ActivityRecord{e6f7bff u0 com.mojang.minecraftpe/.MainActivity} t347}"
                        match = re.search(r'(\w+\.)+\w+(?=/|\./)', output)
                        if match:
                            package_name = match.group(0)
                            print(f"\033[1A\033[K=> {Fore.GREEN}App Package: {package_name}{Style.RESET_ALL}")
                            if show_command_output:
                                print(f"=> {Fore.GREEN}Đầu ra gốc: {output}{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.RED}Không thể xác định tên gói ứng dụng từ đầu ra: {output}{Style.RESET_ALL}")
                elif cmd.get("action") == "force_stop_current_app":
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang lấy ứng dụng đang chạy...{Style.RESET_ALL}")
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    elif output:
                        # Extract package name from output
                        match = re.search(r'(\w+\.)+\w+(?=/|\./)', output)
                        if match:
                            package_name = match.group(0)
                            print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell am force-stop {package_name}{Style.RESET_ALL}")
                            output, error = execute_command(f"adb -s {device_serial} shell am force-stop {package_name}")
                            if error:
                                print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                            elif show_command_output and output:
                                print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                            else:
                                print(f"\033[1A\033[K=> {Fore.GREEN}Đã buộc dừng ứng dụng {package_name}.{Style.RESET_ALL}")
                        else:
                            print(f"\033[1A\033[K=> {Fore.RED}Không thể xác định tên gói ứng dụng từ đầu ra: {output}{Style.RESET_ALL}")
                elif cmd.get("action") == "force_stop_by_package":
                    # Prompt user for package name
                    package_name = text(
                        "Nhập tên gói ứng dụng (package name):",
                        style=custom_style
                    ).ask()
                    if not package_name:
                        print(f"\033[2A\033[K=> {Fore.RED}Không nhập tên gói, hủy thao tác.{Style.RESET_ALL}")
                        continue
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: adb -s {device_serial} shell am force-stop {package_name}{Style.RESET_ALL}")
                    output, error = execute_command(f"adb -s {device_serial} shell am force-stop {package_name}")
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    elif show_command_output and output:
                        print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                    else:
                        print(f"\033[1A\033[K=> {Fore.GREEN}Đã buộc dừng ứng dụng {package_name}.{Style.RESET_ALL}")
                elif cmd.get("action") == "loop_force_stop_by_package":
                    # Prompt user for package name
                    package_name = text(
                        "Nhập tên gói ứng dụng (package name):",
                        style=custom_style
                    ).ask()
                    if not package_name:
                        print(f"\033[2A\033[K=> {Fore.RED}Không nhập tên gói, hủy thao tác.{Style.RESET_ALL}")
                        continue
                    start_app_loop(device_serial, package_name)
                    print(f"\033[2A\033[K=> {Fore.YELLOW}Đã bắt đầu vòng lặp dừng cho {package_name} trong nền.{Style.RESET_ALL}")
                elif cmd.get("action") == "toggle_command_output":
                    show_command_output = not show_command_output
                    status = "Bật" if show_command_output else "Tắt"
                    print(f"\033[2A\033[K=> {Fore.YELLOW}Hiển thị đầu ra lệnh: {status}{Style.RESET_ALL}")
                elif cmd.get("action") == "return_to_device_selection":
                    print(f"\033[2A\033[K=> {Fore.YELLOW}Đang quay lại menu chọn thiết bị...{Style.RESET_ALL}")
                    if stop_youtube_loop() or stop_app_loop():
                        print(f"\033[2A\033[K=> {Fore.YELLOW}Đã dừng tất cả các vòng lặp.{Style.RESET_ALL}")
                    stop_scrcpy()  # Stop scrcpy before returning to device selection
                    return_to_device_selection = True
                    return
                else:
                    print(f"\033[2A\033[K=> {Fore.CYAN}Đang thực thi: {cmd['command'].format(device_serial=device_serial)}{Style.RESET_ALL}")
                    output, error = execute_command(cmd["command"].format(device_serial=device_serial))
                    if error:
                        print(f"\033[1A\033[K=> {Fore.RED}Lỗi: {error}{Style.RESET_ALL}")
                    elif show_command_output and output:
                        print(f"\033[1A\033[K=> {Fore.GREEN}Kết quả: {output}{Style.RESET_ALL}")
                    else:
                        print(f"\033[1A\033[K=> {Fore.GREEN}Lệnh thực thi thành công.{Style.RESET_ALL}")
                break
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

def main():
    print(f"{Fore.CYAN}Bộ chọn Lệnh Thiết bị ADB{Style.RESET_ALL}")

    while True:
        devices = get_connected_devices()
        if not devices:
            print(f"{Fore.RED}Không tìm thấy thiết bị. Vui lòng kết nối thiết bị và đảm bảo ADB được thiết lập chính xác.{Style.RESET_ALL}")
            sys.exit(1)

        # Ask user how to display device info
        display_choice = select(
            "Bạn muốn hiển thị thông tin thiết bị như thế nào?",
            choices=[
                "Tên thiết bị (IP)",
                "Thiết bị IP",
                "Chỉ tên thiết bị"
            ]
        ).ask()

        device_serial, device_name = select_device(devices, display_choice)

        global return_to_device_selection
        return_to_device_selection = False
        show_menu(device_serial, COMMANDS, device_name, display_choice)

        if not return_to_device_selection:
            break

if __name__ == "__main__":
    main()
