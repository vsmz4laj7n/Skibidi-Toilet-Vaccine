#!/usr/bin/python3.12
import sys
import time
import re
import signal
from questionary import select, Style as QuestionaryStyle, text
from device_manager import get_connected_devices, select_device, list_installed_apps
from command_executor import execute_command, start_youtube_loop, stop_youtube_loop, get_loop_status_message, start_app_loop, stop_app_loop, start_chplay_loop, stop_chplay_loop
from scrcpy_manager import run_scrcpy, stop_scrcpy, is_scrcpy_running
from rich.console import Console
from rich.table import Table

# Initialize Console with markup enabled and truecolor support
console = Console(markup=True, color_system="truecolor", force_terminal=True)

# Global flag to control main loop
return_to_device_selection = False

# Global flag to control command output display (omit by default)
show_command_output = False

# Signal handler for Ctrl+C
def signal_handler(sig, frame):
    """Xử lý Ctrl+C để thoát chương trình một cách an toàn."""
    console.print("[yellow]Đã nhận Ctrl+C, đang dừng các vòng lặp và scrcpy...[/yellow]")
    stop_youtube_loop()
    stop_app_loop()
    stop_chplay_loop()
    stop_scrcpy()
    console.print("[bold green]Đã thoát chương trình.[/bold green]")
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Nested commands structure with main options and sub-options (all in Vietnamese)
COMMANDS = [
    {
        "name": "Quản lý Ứng dụng",
        "sub_commands": [
            {
                "name": "YouTube",
                "sub_commands": [
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
                        "name": "Vòng lặp Tắt YouTube",
                        "action": "loop_youtube"
                    },
                    {
                        "name": "Dừng Vòng lặp YouTube",
                        "action": "stop_youtube_loop"
                    }
                ]
            },
            {
                "name": "CH Play",
                "sub_commands": [
                    {
                        "name": "Vô hiệu hóa CH Play",
                        "command": "adb -s {device_serial} shell pm disable-user --user 0 com.android.vending"
                    },
                    {
                        "name": "Kích hoạt CH Play",
                        "command": "adb -s {device_serial} shell pm enable com.android.vending"
                    },
                    {
                        "name": "Vòng lặp Tắt CH Play",
                        "action": "loop_chplay"
                    },
                    {
                        "name": "Dừng Vòng lặp CH Play",
                        "action": "stop_chplay_loop"
                    }
                ]
            }
        ]
    },
    {
        "name": "Quản lý Thiết bị",
        "sub_commands": [
            {
                "name": "Tìm kiếm Hoạt động Ứng dụng",
                "action": "search_app_activity"
            },
            {
                "name": "Danh sách Tất cả Ứng dụng",
                "action": "list_all_apps"
            },
            {
                "name": "Lấy Ứng dụng Đang Chạy",
                "action": "get_current_app"
            },
            {
                "name": "Buộc Dừng Ứng dụng Đang Chạy",
                "action": "force_stop_current_app"
            },
            {
                "name": "Buộc Dừng Ứng dụng theo Tên Gói",
                "action": "force_stop_by_package"
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
                "name": "Bật scrcpy",
                "action": "run_scrcpy"
            },
            {
                "name": "Tắt scrcpy",
                "action": "stop_scrcpy"
            }
        ]
    },
    {
        "name": "Kiểm soát Âm lượng",
        "sub_commands": [
            {
                "name": "Kiểm tra Âm lượng Hiện tại",
                "action": "check_volume"
            },
            {
                "name": "Tăng Âm lượng",
                "command": "adb -s {device_serial} shell input keyevent 24"
            },
            {
                "name": "Giảm Âm lượng",
                "command": "adb -s {device_serial} shell input keyevent 25"
            },
            {
                "name": "Đặt Âm lượng",
                "action": "set_volume"
            },
            {
                "name": "Tắt Âm",
                "command": "adb -s {device_serial} shell input keyevent 164"
            },
            {
                "name": "Bật Âm",
                "command": "adb -s {device_serial} shell input keyevent 164"
            }
        ]
    },
    {
        "name": "Cài đặt",
        "sub_commands": [
            {
                "name": "Bật/Tắt Hiển thị Đầu ra Lệnh",
                "action": "toggle_command_output"
            },
            {
                "name": "Quay lại Chọn Thiết bị",
                "action": "return_to_device_selection"
            }
        ]
    },
    {
        "name": "Mô phỏng Phím Cứng",
        "sub_commands": [
            {
                "name": "Mở khóa màn hình",
                "action": "unlock_screen"
            },
            {
                "name": "Nhấn nút Home",
                "action": "press_home"
            },
            {
                "name": "Nhấn nút Back",
                "action": "press_back"
            },
            {
                "name": "Khóa màn hình",
                "action": "lock_screen"
            }
        ]
    }
]

def parse_volume_output(output):
    """Parse the output of the volume command into a structured format."""
    volume_info = {
        "Muted": "N/A",
        "Muted Internally": "N/A",
        "Min": "N/A",
        "Max": "N/A",
        "streamVolume": "N/A",
        "Current": [],
        "Devices": "N/A"
    }
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("Muted:"):
            volume_info["Muted"] = line.split(":")[1].strip()
        elif line.startswith("Muted Internally:"):
            volume_info["Muted Internally"] = line.split(":")[1].strip()
        elif line.startswith("Min:"):
            volume_info["Min"] = line.split(":")[1].strip()
        elif line.startswith("Max:"):
            volume_info["Max"] = line.split(":")[1].strip()
        elif line.startswith("streamVolume:"):
            volume_info["streamVolume"] = line.split(":")[1].strip()
        elif line.startswith("Current:"):
            current_str = line.split(":", 1)[1].strip()
            devices = [d.strip() for d in current_str.split(",")]
            volume_info["Current"] = devices
        elif line.startswith("Devices:"):
            volume_info["Devices"] = line.split(":")[1].strip()
    return volume_info

def display_volume_info(volume_info):
    """Display volume information in a formatted table using rich."""
    table = Table(title="Thông tin Âm lượng (STREAM_MUSIC)", style="bold #673ab8")
    table.add_column("Trường", style="bold #ffffff")
    table.add_column("Giá trị", style="bold #ff9f43")
    table.add_column("Mô tả", style="bold #f44336")

    table.add_row(
        "Muted",
        volume_info["Muted"],
        "Âm thanh có bị tắt thủ công (qua nút âm lượng) hay không."
    )
    table.add_row(
        "Muted Internally",
        volume_info["Muted Internally"],
        "Android có tắt âm thanh này bằng lập trình hay không."
    )
    table.add_row(
        "Min, Max",
        f"{volume_info['Min']}, {volume_info['Max']}",
        "Phạm vi âm lượng của luồng này."
    )
    table.add_row(
        "streamVolume",
        volume_info["streamVolume"],
        "Giá trị toàn cục hiện tại điều khiển âm lượng phát lại."
    )
    table.add_row(
        "Current",
        "\n".join(volume_info["Current"]),
        "Ánh xạ âm lượng cho mỗi thiết bị."
    )
    table.add_row(
        "Devices",
        volume_info["Devices"],
        "Thiết bị âm thanh hiện đang được sử dụng."
    )

    console.print(table)

def show_sub_menu(device_serial, sub_commands, device_name, display_choice, parent_menu_name):
    """Hiển thị menu con với các tùy chọn cho một tùy chọn chính."""
    global return_to_device_selection, show_command_output
    custom_style = QuestionaryStyle([
        ('qmark', 'fg:#673ab8 bold'),
        ('question', 'fg:#ffffff bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#ff9f43 bold'),
        ('selected', 'fg:#5c35cc bold'),
    ])

    last_message = ""
    while True:
        # Get the latest loop status message
        message = get_loop_status_message()
        if is_scrcpy_running():
            message = f"{message} | [bold #5c35cc]scrcpy đang chạy[/bold #5c35cc]" if message else "[bold #5c35cc]scrcpy đang chạy[/bold #5c35cc]"
        # Add command output status to the message
        output_status = "Bật" if show_command_output else "Tắt"
        message = f"{message} | [bold #ffffff]Đầu ra lệnh: {output_status}[/bold #ffffff]" if message else f"[bold #ffffff]Đầu ra lệnh: {output_status}[/bold #ffffff]"

        # Device display logic
        if display_choice == "Tên thiết bị (IP)":
            device_display = f"{device_name} ({device_serial})" if device_name else device_serial
        elif display_choice == "Thiết bị IP":
            device_display = device_serial
        elif display_choice == "Chỉ tên thiết bị":
            device_display = device_name if device_name else device_serial
        else:
            device_display = device_serial

        # Get user choice from sub-menu
        choice = select(
            f"Thiết bị đã chọn: {device_display}\nMenu: {parent_menu_name}",
            choices=[cmd["name"] for cmd in sub_commands] + ["Quay lại", "Thoát"],
            style=custom_style
        ).ask()

        # Clear previous output (2 lines up) and print updated menu
        console.print("\033[2A\033[K")  # Move up 2 lines and clear
        console.print(f"Menu: [bold #673ab8]{parent_menu_name}[/bold #673ab8] (Sử dụng phím mũi tên)")
        for cmd in sub_commands:
            console.print(f" {'[bold #ff9f43]»[/bold #ff9f43]' if cmd['name'] == choice else '  '} [bold #f44336]{cmd['name']}[/bold #f44336]")
        console.print(f" {'[bold #ff9f43]»[/bold #ff9f43]' if choice == 'Quay lại' else '  '} [bold #ffffff]Quay lại[/bold #ffffff]")
        console.print(f" {'[bold #ff9f43]»[/bold #ff9f43]' if choice == 'Thoát' else '  '} [bold #ffffff]Thoát[/bold #ffffff]")
        console.print(f"=> [bold #ffffff]{message}[/bold #ffffff]")
        last_message = message

        if choice == "Thoát":
            if stop_youtube_loop() or stop_app_loop() or stop_chplay_loop():
                console.print(f"\033[2A\033[K=> [bold yellow]Đã dừng tất cả các vòng lặp.[/bold yellow]")
            stop_scrcpy()
            console.print("[bold green]Đang thoát...[/bold green]")
            sys.exit(0)

        if choice == "Quay lại":
            return

        for cmd in sub_commands:
            if cmd["name"] == choice:
                # Handle nested sub-commands (e.g., YouTube, CH Play)
                if "sub_commands" in cmd:
                    show_sub_menu(device_serial, cmd["sub_commands"], device_name, display_choice, cmd["name"])
                    break
                # Handle actions
                if cmd.get("action") == "loop_youtube":
                    start_youtube_loop(device_serial)
                    console.print(f"\033[2A\033[K=> [bold yellow]Đã bắt đầu vòng lặp YouTube trong nền.[/bold yellow]")
                elif cmd.get("action") == "stop_youtube_loop":
                    if stop_youtube_loop():
                        console.print(f"\033[2A\033[K=> [bold yellow]Đã dừng vòng lặp YouTube.[/bold yellow]")
                    else:
                        console.print(f"\033[2A\033[K=> [bold red]Không có vòng lặp YouTube nào đang chạy.[/bold red]")
                elif cmd.get("action") == "loop_chplay":
                    start_chplay_loop(device_serial)
                    console.print(f"\033[2A\033[K=> [bold yellow]Đã bắt đầu vòng lặp CH Play trong nền.[/bold yellow]")
                elif cmd.get("action") == "stop_chplay_loop":
                    if stop_chplay_loop():
                        console.print(f"\033[2A\033[K=> [bold yellow]Đã dừng vòng lặp CH Play.[/bold yellow]")
                    else:
                        console.print(f"\033[2A\033[K=> [bold red]Không có vòng lặp CH Play nào đang chạy.[/bold red]")
                elif cmd.get("action") == "stop_app_loop":
                    if stop_app_loop():
                        console.print(f"\033[2A\033[K=> [bold yellow]Đã dừng vòng lặp ứng dụng.[/bold yellow]")
                    else:
                        console.print(f"\033[2A\033[K=> [bold red]Không có vòng lặp ứng dụng nào đang chạy.[/bold red]")
                elif cmd.get("action") == "check_volume":
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang kiểm tra âm lượng cho thiết bị {device_serial}[/bold #5c35cc]")
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys audio | grep -A 10 STREAM_MUSIC")
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    else:
                        volume_info = parse_volume_output(output)
                        display_volume_info(volume_info)
                        if show_command_output and output:
                            console.print(f"[bold green]Đầu ra lệnh: {output}[/bold green]")
                elif cmd.get("action") == "set_volume":
                    max_volume_cmd = f"adb -s {device_serial} shell dumpsys audio | grep -A 10 STREAM_MUSIC | grep Max:"
                    max_out, max_err = execute_command(max_volume_cmd)
                    max_volume = 15  # Default
                    if max_out and not max_err:
                        try:
                            max_volume = int(max_out.split(":")[1].strip())
                        except (IndexError, ValueError):
                            pass
                    volume_input = text(
                        f"Nhập mức âm lượng (0-{max_volume}):",
                        style=custom_style,
                        validate=lambda x: x.isdigit() and 0 <= int(x) <= max_volume
                    ).ask()
                    if volume_input:
                        target_volume = int(volume_input)
                        # Get current volume
                        get_vol_cmd = f"adb -s {device_serial} shell dumpsys audio | grep -A 10 STREAM_MUSIC | grep 'streamVolume:'"
                        out, err = execute_command(get_vol_cmd)
                        if out and not err:
                            try:
                                current_volume = int(out.split(":")[1].strip())
                            except (IndexError, ValueError):
                                current_volume = None
                        else:
                            current_volume = None
                        if current_volume is None:
                            console.print(f"\033[1A\033[K=> [bold red]Không thể lấy âm lượng hiện tại.[/bold red]")
                        else:
                            console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang đặt âm lượng STREAM_MUSIC thành {target_volume} (hiện tại: {current_volume})[/bold #5c35cc]")
                            keyevent = None
                            if current_volume < target_volume:
                                keyevent = 24  # Volume up
                            elif current_volume > target_volume:
                                keyevent = 25  # Volume down
                            attempts = 0
                            max_attempts = abs(target_volume - current_volume) + 5
                            while current_volume != target_volume and attempts < max_attempts:
                                if keyevent is None:
                                    break
                                execute_command(f"adb -s {device_serial} shell input keyevent {keyevent}")
                                time.sleep(0.3)
                                out, err = execute_command(get_vol_cmd)
                                if out and not err:
                                    try:
                                        current_volume = int(out.split(":")[1].strip())
                                    except (IndexError, ValueError):
                                        break
                                else:
                                    break
                                attempts += 1
                            if current_volume == target_volume:
                                console.print(f"\033[1A\033[K=> [bold green]Đã đặt âm lượng thành {target_volume}.[/bold green]")
                            else:
                                console.print(f"\033[1A\033[K=> [bold yellow]Đã thử điều chỉnh âm lượng, nhưng không khớp chính xác (hiện tại: {current_volume}).[/bold yellow]")
                elif cmd.get("action") == "search_app_activity":
                    query = text(
                        "Nhập từ khóa tìm kiếm (trong tên ứng dụng hoặc gói):",
                        style=custom_style
                    ).ask()
                    if not query:
                        console.print(f"\033[2A\033[K=> [bold red]Không nhập từ khóa, hủy tìm kiếm.[/bold red]")
                        continue
                    app_list = list_installed_apps(device_serial, exclude_system=True)
                    if not app_list:
                        console.print("[bold red]Không tìm thấy ứng dụng người dùng hoặc xảy ra lỗi.[/bold red]")
                        continue
                    query = query.lower()
                    filtered_apps = [
                        app for app in app_list
                        if query in app['label'].lower() or query in app['package'].lower()
                    ]
                    if not filtered_apps:
                        console.print(f"[bold red]Không tìm thấy ứng dụng nào khớp với từ khóa '{query}'.[/bold red]")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in filtered_apps] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    action = select(
                        "Chọn hành động:",
                        choices=["Buộc dừng một lần", "Vòng lặp Dừng", "Hủy"],
                        style=custom_style
                    ).ask()
                    if action == "Buộc dừng một lần":
                        console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}[/bold #5c35cc]")
                        output, error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                        if error:
                            console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                        elif show_command_output and output:
                            console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                        else:
                            console.print(f"\033[1A\033[K=> [bold green]Đã buộc dừng ứng dụng {app_package}.[/bold green]")
                    elif action == "Vòng lặp Dừng":
                        start_app_loop(device_serial, app_package)
                        console.print(f"\033[2A\033[K=> [bold yellow]Đã bắt đầu vòng lặp dừng cho {app_package} trong nền.[/bold yellow]")
                elif cmd.get("action") == "list_all_apps":
                    app_list = list_installed_apps(device_serial, exclude_system=True)
                    if not app_list:
                        console.print("[bold red]Không tìm thấy ứng dụng hoặc xảy ra lỗi.[/bold red]")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in app_list] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    action = select(
                        "Chọn hành động:",
                        choices=["Buộc dừng một lần", "Vòng lặp Dừng", "Vô hiệu hóa", "Kích hoạt", "Hủy"],
                        style=custom_style
                    ).ask()
                    if action == "Buộc dừng một lần":
                        console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}[/bold #5c35cc]")
                        output, error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                        if error:
                            console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                        elif show_command_output and output:
                            console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                        else:
                            console.print(f"\033[1A\033[K=> [bold green]Đã buộc dừng ứng dụng {app_package}.[/bold green]")
                    elif action == "Vòng lặp Dừng":
                        start_app_loop(device_serial, app_package)
                        console.print(f"\033[2A\033[K=> [bold yellow]Đã bắt đầu vòng lặp dừng cho {app_package} trong nền.[/bold yellow]")
                    elif action == "Vô hiệu hóa":
                        console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell pm disable-user --user 0 {app_package}[/bold #5c35cc]")
                        output, error = execute_command(f"adb -s {device_serial} shell pm disable-user --user 0 {app_package}")
                        if error:
                            console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                        elif show_command_output and output:
                            console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                        else:
                            console.print(f"\033[1A\033[K=> [bold green]Đã vô hiệu hóa ứng dụng {app_package}.[/bold green]")
                    elif action == "Kích hoạt":
                        console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell pm enable {app_package}[/bold #5c35cc]")
                        output, error = execute_command(f"adb -s {device_serial} shell pm enable {app_package}")
                        if error:
                            console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                        elif show_command_output and output:
                            console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                        else:
                            console.print(f"\033[1A\033[K=> [bold green]Đã kích hoạt ứng dụng {app_package}.[/bold green]")
                elif cmd.get("action") == "run_scrcpy":
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang khởi chạy scrcpy cho thiết bị {device_serial}[/bold #5c35cc]")
                    output, error = run_scrcpy(device_serial)
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    else:
                        console.print(f"\033[1A\033[K=> [bold green]{'Kết quả: ' + output if show_command_output and output else 'Đã khởi chạy scrcpy.'}[/bold green]")
                elif cmd.get("action") == "stop_scrcpy":
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang dừng scrcpy cho thiết bị {device_serial}[/bold #5c35cc]")
                    output, error = stop_scrcpy()
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    else:
                        console.print(f"\033[1A\033[K=> [bold green]{'Kết quả: ' + output if show_command_output and output else 'Đã dừng scrcpy.'}[/bold green]")
                elif cmd.get("action") == "get_current_app":
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang lấy ứng dụng hiện tại trên thiết bị {device_serial}[/bold #5c35cc]")
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys activity activities | grep mResumedActivity")
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    elif not output:
                        console.print(f"\033[1A\033[K=> [bold red]Không tìm thấy ứng dụng đang chạy.[/bold red]")
                    else:
                        app_package = output.split()[3].split('/')[0]
                        console.print(f"\033[1A\033[K=> [bold green]Ứng dụng hiện tại: {app_package}[/bold green]")
                        if show_command_output:
                            console.print(f"[bold green]Đầu ra lệnh: {output}[/bold green]")
                elif cmd.get("action") == "force_stop_current_app":
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang lấy và buộc dừng ứng dụng hiện tại trên thiết bị {device_serial}[/bold #5c35cc]")
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys activity activities | grep mResumedActivity")
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    elif not output:
                        console.print(f"\033[1A\033[K=> [bold red]Không tìm thấy ứng dụng đang chạy.[/bold red]")
                    else:
                        app_package = output.split()[3].split('/')[0]
                        console.print(f"\033[1A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}[/bold #5c35cc]")
                        stop_output, stop_error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                        if stop_error:
                            console.print(f"\033[1A\033[K=> [bold red]Lỗi: {stop_error}[/bold red]")
                        elif show_command_output and stop_output:
                            console.print(f"\033[1A\033[K=> [bold green]Kết quả: {stop_output}[/bold green]")
                        else:
                            console.print(f"\033[1A\033[K=> [bold green]Đã buộc dừng ứng dụng {app_package}.[/bold green]")
                elif cmd.get("action") == "force_stop_by_package":
                    app_list = list_installed_apps(device_serial, exclude_system=True)
                    if not app_list:
                        console.print("[bold red]Không tìm thấy ứng dụng hoặc xảy ra lỗi.[/bold red]")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in app_list] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: adb -s {device_serial} shell am force-stop {app_package}[/bold #5c35cc]")
                    output, error = execute_command(f"adb -s {device_serial} shell am force-stop {app_package}")
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    elif show_command_output and output:
                        console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                    else:
                        console.print(f"\033[1A\033[K=> [bold green]Đã buộc dừng ứng dụng {app_package}.[/bold green]")
                elif cmd.get("action") == "loop_force_stop_by_package":
                    app_list = list_installed_apps(device_serial, exclude_system=True)
                    if not app_list:
                        console.print("[bold red]Không tìm thấy ứng dụng hoặc xảy ra lỗi.[/bold red]")
                        continue
                    app_choice = select(
                        "Chọn một ứng dụng: (Sử dụng phím mũi tên để cuộn)",
                        choices=[f"{app['label']} ({app['package']})" for app in app_list] + ["Hủy"],
                        style=custom_style
                    ).ask()
                    if app_choice == "Hủy":
                        continue
                    app_package = app_choice.split('(')[-1].rstrip(')')
                    start_app_loop(device_serial, app_package)
                    console.print(f"\033[2A\033[K=> [bold yellow]Đã bắt đầu vòng lặp dừng cho {app_package} trong nền.[/bold yellow]")
                elif cmd.get("action") == "toggle_command_output":
                    show_command_output = not show_command_output
                    status = "Bật" if show_command_output else "Tắt"
                    console.print(f"\033[2A\033[K=> [bold yellow]Hiển thị đầu ra lệnh đã được {status}.[/bold yellow]")
                elif cmd.get("action") == "return_to_device_selection":
                    return_to_device_selection = True
                    return
                # Handle direct commands
                elif "command" in cmd:
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang thực thi: {cmd['command'].format(device_serial=device_serial)}[/bold #5c35cc]")
                    output, error = execute_command(cmd["command"].format(device_serial=device_serial))
                    if error:
                        console.print(f"\033[1A\033[K=> [bold red]Lỗi: {error}[/bold red]")
                    elif show_command_output and output:
                        console.print(f"\033[1A\033[K=> [bold green]Kết quả: {output}[/bold green]")
                    else:
                        console.print(f"\033[1A\033[K=> [bold green]Lệnh đã được thực thi thành công.[/bold green]")
                elif cmd.get("action") == "unlock_screen":
                    # Wake up device
                    console.print(f"\033[2A\033[K=> [bold #5c35cc]Đang đánh thức thiết bị...[/bold #5c35cc]")
                    execute_command(f"adb -s {device_serial} shell input keyevent 224")  # WAKEUP
                    time.sleep(0.5)
                    # Try to dismiss keyguard
                    execute_command(f"adb -s {device_serial} shell input keyevent 82")  # MENU
                    time.sleep(0.5)
                    # Check if still locked
                    output, error = execute_command(f"adb -s {device_serial} shell dumpsys window | grep mDreamingLockscreen")
                    if output and "mDreamingLockscreen=true" in output:
                        has_password = select(
                            "Màn hình khóa có mật khẩu không?",
                            choices=["Có", "Không"]
                        ).ask()
                        if has_password == "Không":
                            # Perform swipe up to unlock (coordinates may need adjustment per device)
                            execute_command(f"adb -s {device_serial} shell input swipe 300 1000 300 300 300")
                            console.print(f"\033[1A\033[K=> [bold green]Đã thực hiện vuốt để mở khóa.[/bold green]")
                        else:
                            passcode = text("Nhập mã PIN/mật khẩu mở khóa màn hình:").ask()
                            if passcode:
                                for digit in passcode:
                                    if digit.isdigit():
                                        keycode = 7 + int(digit)
                                        execute_command(f"adb -s {device_serial} shell input keyevent {keycode}")
                                        time.sleep(0.2)
                                    else:
                                        execute_command(f"adb -s {device_serial} shell input text '{digit}'")
                                        time.sleep(0.2)
                                execute_command(f"adb -s {device_serial} shell input keyevent 66")  # ENTER
                                # Swipe up after entering password
                                execute_command(f"adb -s {device_serial} shell input swipe 300 1000 300 300 300")
                                console.print(f"\033[1A\033[K=> [bold green]Đã nhập mật khẩu và vuốt để mở khóa.[/bold green]")
                            else:
                                console.print(f"\033[1A\033[K=> [bold yellow]Không nhập mật khẩu, thiết bị có thể vẫn bị khóa.[/bold yellow]")
                    else:
                        console.print(f"\033[1A\033[K=> [bold green]Thiết bị đã được đánh thức và mở khóa (nếu không có mã bảo vệ).[/bold green]")
                elif cmd.get("action") == "press_home":
                    execute_command(f"adb -s {device_serial} shell input keyevent 3")
                    console.print(f"\033[1A\033[K=> [bold green]Đã nhấn nút Home.[/bold green]")
                elif cmd.get("action") == "press_back":
                    execute_command(f"adb -s {device_serial} shell input keyevent 4")
                    console.print(f"\033[1A\033[K=> [bold green]Đã nhấn nút Back.[/bold green]")
                elif cmd.get("action") == "lock_screen":
                    execute_command(f"adb -s {device_serial} shell input keyevent 26")
                    console.print(f"\033[1A\033[K=> [bold green]Đã khóa màn hình thiết bị.[/bold green]")

def show_menu(device_serial, commands, device_name=None, display_choice="Tên thiết bị (IP)"):
    """Hiển thị menu chính với các tùy chọn màu sắc cho tùy chọn chính và thông tin trạng thái."""
    global return_to_device_selection, show_command_output
    custom_style = QuestionaryStyle([
        ('qmark', 'fg:#673ab8 bold'),
        ('question', 'fg:#ffffff bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#ff9f43 bold'),
        ('selected', 'fg:#5c35cc bold'),
    ])

    last_message = ""
    while True:
        # Get the latest loop status message
        message = get_loop_status_message()
        if is_scrcpy_running():
            message = f"{message} | [bold #5c35cc]scrcpy đang chạy[/bold #5c35cc]" if message else "[bold #5c35cc]scrcpy đang chạy[/bold #5c35cc]"
        # Add command output status to the message
        output_status = "Bật" if show_command_output else "Tắt"
        message = f"{message} | [bold #ffffff]Đầu ra lệnh: {output_status}[/bold #ffffff]" if message else f"[bold #ffffff]Đầu ra lệnh: {output_status}[/bold #ffffff]"

        # Device display logic
        if display_choice == "Tên thiết bị (IP)":
            device_display = f"{device_name} ({device_serial})" if device_name else device_serial
        elif display_choice == "Thiết bị IP":
            device_display = device_serial
        elif display_choice == "Chỉ tên thiết bị":
            device_display = device_name if device_name else device_serial
        else:
            device_display = device_serial

        # Get user choice from main menu
        choice = select(
            f"Thiết bị đã chọn: {device_display}\nCác lệnh chính:",
            choices=[cmd["name"] for cmd in commands] + ["Thoát"],
            style=custom_style
        ).ask()

        # Clear previous output (2 lines up) and print updated menu
        console.print("\033[2A\033[K")  # Move up 2 lines and clear
        console.print(f"Các lệnh chính: (Sử dụng phím mũi tên)")
        for cmd in commands:
            console.print(f" {'[bold #ff9f43]»[/bold #ff9f43]' if cmd['name'] == choice else '  '} [bold #673ab8]{cmd['name']}[/bold #673ab8]")
        console.print(f" {'[bold #ff9f43]»[/bold #ff9f43]' if choice == 'Thoát' else '  '} [bold #ffffff]Thoát[/bold #ffffff]")
        console.print(f"=> [bold #ffffff]{message}[/bold #ffffff]")
        last_message = message

        if choice == "Thoát":
            if stop_youtube_loop() or stop_app_loop() or stop_chplay_loop():
                console.print(f"\033[2A\033[K=> [bold yellow]Đã dừng tất cả các vòng lặp.[/bold yellow]")
            stop_scrcpy()
            console.print("[bold green]Đang thoát...[/bold green]")
            sys.exit(0)

        for cmd in commands:
            if cmd["name"] == choice:
                show_sub_menu(device_serial, cmd["sub_commands"], device_name, display_choice, cmd["name"])
                break
        if return_to_device_selection:
            break
        time.sleep(0.1)

def check_active_devices(devices):
    """Kiểm tra thiết bị nào đang hoạt động (không ở trạng thái khóa màn hình)."""
    active_devices = []
    inactive_devices = []
    for device in devices:
        serial = device['serial']
        name = device['name']
        output, error = execute_command(f"adb -s {serial} shell dumpsys window | grep mDreamingLockscreen")
        if error:
            inactive_devices.append(f"{name} ({serial}): Lỗi - {error}")
        elif "mDreamingLockscreen=false" in output:
            active_devices.append(f"{name} ({serial}): Đang hoạt động (mở khóa)")
        else:
            inactive_devices.append(f"{name} ({serial}): Không hoạt động (khóa hoặc không xác định)")

    console.print("[bold #673ab8]Kết quả kiểm tra trạng thái thiết bị:[/bold #673ab8]")
    if active_devices:
        console.print("[bold green]Thiết bị đang hoạt động:[/bold green]")
        for device in active_devices:
            console.print(f"  - {device}")
    else:
        console.print("[bold yellow]Không có thiết bị nào đang hoạt động.[/bold yellow]")

    if inactive_devices:
        console.print("[bold red]Thiết bị không hoạt động:[/bold red]")
        for device in inactive_devices:
            console.print(f"  - {device}")

    console.input("[bold #673ab8]Nhấn Enter để quay lại menu chọn thiết bị...[/bold #673ab8]")

def main():
    console.print("[bold #673ab8]Bộ chọn Lệnh Thiết bị ADB[/bold #673ab8]")

    while True:
        devices = get_connected_devices()
        if not devices:
            console.print("[bold red]Không tìm thấy thiết bị. Vui lòng kết nối thiết bị và đảm bảo ADB được thiết lập chính xác.[/bold red]")
            sys.exit(1)

        display_choice = select(
            "Bạn muốn hiển thị thông tin thiết bị như thế nào?",
            choices=[
                "Tên thiết bị (IP)",
                "Thiết bị IP",
                "Chỉ tên thiết bị",
                "Kiểm tra thiết bị đang hoạt động",
                "Thoát"
            ]
        ).ask()

        if display_choice == "Kiểm tra thiết bị đang hoạt động":
            check_active_devices(devices)
            continue
        elif display_choice == "Thoát":
            console.print("[bold green]Đang thoát...[/bold green]")
            sys.exit(0)

        device_serial, device_name = select_device(devices, display_choice)

        global return_to_device_selection
        return_to_device_selection = False
        show_menu(device_serial, COMMANDS, device_name, display_choice)

        if not return_to_device_selection:
            break

if __name__ == "__main__":
    main()
