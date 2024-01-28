from pathlib import Path
from tkinter import *
from mttkinter import mtTkinter
import tkinter.font as tkFont
from time import strftime
import time
from socket import *
import threading
import sys

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"assets")

# NETWORK CONNECTION
PORT = 3141
HOST = "192.168.1.73"
BUFF_SIZE = 64
ADDRESS = (HOST, PORT)

# INTERFACE COLORS
dark = '#121212'
semi_dark = '#1e1e1e'
semi_semi_dark = '#2e2e2e'
purple = '#bb86fc'
light = '#bfbfbf'
semi_light = '#a8a8a8'
semi_semi_light = '#595959'
blue = '#397791'

# INTERFACE CONSTANTS
x_devices = [50, 350]
y_devices = [150, 650]
padding = 25
devices_titles = ["CLOCK", "IRRIGATION", "OUTLETS"]

# SYSTEM VARIABLES
active_devices = [0, 0, 0]
active_outlets = [0, 0, 0, 0]
water_level = 5
water_parameters = [0, 0]  # [frequency of watering, water volume]
water_frequency_titles = [['4 times a day', 0.25], ['2 times a day', 0.5], ['1 time a day', 1], ['every 2 days', 2],
                          ['every 4 days', 4], ['every week', 7], ['every 2 weeks', 14]]
water_volumes = [20, 50, 100, 150, 200, 250, 500]
parameter_change = 'x'  # string (w formacie 'x1') przechowuje zmianę wartości parametru (np. gdy włączamy gniazdko 4 to parameter_change = 's4'
initial_request = 0


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def make_gui():
    def on_closing():
        stop_event.set()
        window.destroy()
        sys.exit()

    def draw_rectangle(x1, y1, x2, y2, color, fillcolor):
        return canvas.create_rectangle(
            x1, y1,
            x2, y2,
            fill=color,
            activefill=fillcolor,
            outline=""
        )

    def draw_text(x, y, text, color, size):
        return canvas.create_text(
            x, y,
            anchor="nw",
            text=text,
            fill=color,
            font=tkFont.Font(family='Inter', size=size, weight='bold')
        )

    def draw_image_array(arr, file, x, y):
        arr.append(PhotoImage(
            file=relative_to_assets(file)))
        return canvas.create_image(
            x, y,
            image=arr[-1]
        )

    # LOGO
    def draw_logo(image):
        canvas.place(x=0, y=0)
        draw_rectangle(0, 0, 950, 80, purple, purple)
        canvas.create_image(60, 40, image=image)
        draw_text(100, 25, text="PiHoMi", color="#000000", size=30)

    # DEVICES
    def draw_devices(x_reference, y_reference, ppadding, parray_image_icon, parray_image_checkbox):
        height_device = 60
        gap_after_text = 110
        icon_image_files = ["clock-light25x25.png", "water-light30x30.png", "socket-light-light-bcg30x30.png"]
        icon_image_disabled_files = ["clock-dark25x25.png", "water-dark30x30.png", "socket-dark-light-bcg30x30.png"]

        draw_rectangle(x_reference[0], y_reference[0], x_reference[1], y_reference[1], semi_dark, semi_dark)
        draw_text(x_reference[0] + ppadding + 10, y_reference[0] + ppadding + 10, text="Devices", color=light, size=30)

        for i in range(3):
            def on_button_click(event, index=i):
                global parameter_change
                parameter_change = ''
                parameter_change = "{device}".format(device=devices_titles[index][0].lower())

            container = draw_rectangle(
                x_reference[0] + ppadding, y_reference[0] + gap_after_text + i * height_device + i * ppadding,
                x_reference[1] - ppadding, y_reference[0] + gap_after_text + (i+1) * height_device + i * ppadding,
                semi_semi_dark, dark
            )

            draw_image_array(
                parray_image_icon,
                icon_image_files[i] if active_devices[i] == 1 else icon_image_disabled_files[i],
                x_reference[0] + ppadding + 30, y_reference[0] + gap_after_text + i * height_device + i * ppadding + 30
            )
            text = draw_text(
                x_reference[0] + ppadding + 62, y_reference[0] + i * height_device + i * ppadding + gap_after_text + 23,
                text=devices_titles[i], color=semi_light if active_devices[i] == 1 else semi_semi_light, size=13
            )

            draw_image_array(
                parray_image_checkbox,
                "checkbox-yes15x15.png" if active_devices[i] == 1 else "checkbox-no15x15.png",
                x_reference[0] + ppadding + 225,
                y_reference[0] + gap_after_text + i * height_device + i * ppadding + 30
            )

            canvas.tag_bind(container, '<Button-1>', on_button_click)
            canvas.tag_bind(text, '<Button-1>', on_button_click)

    # OUTLETS
    def draw_outlets(x_reference, y_reference, ppadding, pactive_outlets, parray_image_outlet):
        outlets_height = 200
        draw_rectangle(
            x_reference[1] + 2 * ppadding, y_reference[0], window_size[0] - 2 * ppadding, y_reference[0] + outlets_height,
            semi_dark, semi_dark
        )
        draw_text(x_reference[1] + 100, y_reference[0] + ppadding, text="Outlets", color=light, size=30)

        for i in range(4):
            def on_button_click(event, index=i):
                global parameter_change
                parameter_change = ''
                parameter_change = "o{outlet_num}".format(outlet_num=index + 1)

            image = draw_image_array(
                parray_image_outlet,
                "socket-light75x75.png" if pactive_outlets[i] == 1 else "socket-dark75x75.png",
                x_reference[1] + i * (ppadding - 10) + i * 90 + 140, y_reference[0] + 4 * ppadding + 20,
            )
            text = draw_text(
                x_reference[1] + i * (ppadding-10) + i * 90 + 107, y_reference[0] + 4*ppadding + 55,
                text="{i}. enabled".format(i=i+1) if pactive_outlets[i] == 1 else "{i}. disabled".format(i=i+1),
                color=semi_light if pactive_outlets[i] == 1 else semi_semi_light,
                size=10
            )
            canvas.tag_bind(image, '<Button-1>', on_button_click)
            canvas.tag_bind(text, '<Button-1>', on_button_click)

        return outlets_height

    # IRRIGATION
    def draw_irrigation(x_reference, y_reference, ppadding, outlets_height, pwater_level=1):
        irrigation_width = 200

        bg_rectangle = draw_rectangle(
            x_reference[1] + 2 * ppadding, y_reference[0] + outlets_height + ppadding,
            x_reference[1] + 2 * ppadding + irrigation_width, y_reference[1],
            semi_dark, semi_dark
        )
        text1 = draw_text(
            x_reference[1] + 2 * ppadding + 30, y_reference[0] + outlets_height + ppadding + 20,
            text="Water level", color=semi_light, size=15
        )
        text2 = draw_text(
            x_reference[1] + 2 * ppadding + 30, y_reference[0] + outlets_height + ppadding + 40,
            text="irrigation", color=semi_semi_light, size=10
        )

        container_rectangle = draw_rectangle(
            x_reference[1] + 2 * ppadding + 75, y_reference[0] + outlets_height + ppadding + 75,
            x_reference[1] + 2 * ppadding + irrigation_width - 75, y_reference[1] - 125,
            semi_semi_dark, semi_semi_dark
        )
        water_rectangle = draw_rectangle(
            x_reference[1] + 2 * ppadding + 75, y_reference[0] + outlets_height + ppadding + 75 + (7 - pwater_level) * 10,
            x_reference[1] + 2 * ppadding + irrigation_width - 75, y_reference[1] - 125,
            blue, blue
        )

        def change_frequency(freq):
            global water_parameters, parameter_change
            water_parameters[0] = freq
            parameter_change = ''
            parameter_change = "f{frequency_value}".format(frequency_value=freq)

        def change_volume(v):
            global water_parameters, parameter_change
            water_parameters[1] = v
            parameter_change = ''
            parameter_change = "v{volume_value}".format(volume_value=v)

        def popup(e):
            menu.tk_popup(e.x_root, e.y_root)

        menu = Menu(window, tearoff=False)
        menu.add_command(label="Irrigation frequency", state="disabled", activebackground=menu.cget("background"))
        menu.add_separator()
        for frequency in water_frequency_titles:
            menu.add_command(label=str(frequency[0]), command=lambda freq=frequency[1]: change_frequency(freq))
        menu.add_separator()

        menu.add_command(label="Water volume", state="disabled", activebackground=menu.cget("background"))
        menu.add_separator()
        for volume in water_volumes:
            menu.add_command(label=str(volume)+'ml', command=lambda freq=volume: change_volume(freq))

        canvas.tag_bind(bg_rectangle, "<Button-3>", popup)
        canvas.tag_bind(text1, "<Button-3>", popup)
        canvas.tag_bind(text2, "<Button-3>", popup)
        canvas.tag_bind(container_rectangle, "<Button-3>", popup)
        canvas.tag_bind(water_rectangle, "<Button-3>", popup)

        return irrigation_width

    # CLOCK
    def draw_clock(x_reference, y_reference, ppadding, irrigation_width, outlets_height):
        draw_rectangle(
            x_reference[1] + 3 * ppadding + irrigation_width, y_reference[0] + outlets_height + ppadding,
            window_size[0] - 2 * ppadding, y_reference[1],
            semi_dark, semi_dark
        )
        draw_text(
            x_reference[1] + 3 * ppadding + irrigation_width + ppadding, y_reference[0] + outlets_height + ppadding + 20,
            text="Clock", color=light, size=30
        )

        def draw_time():
            string = strftime('%H:%M')
            lbl.config(text=string)
            lbl.after(1000, draw_time)

        lbl = Label(window, font=('calibri', 40, 'bold'),
                    background=semi_dark,
                    foreground=semi_light)

        lbl.place(x=x_reference[1] + 3 * ppadding + irrigation_width + 3 * ppadding,
                  y=y_reference[0] + outlets_height + 3 * ppadding + 20)
        draw_time()

    def draw_dashboard():
        global active_outlets, water_level, array_image_icon, array_image_checkbox, array_image_outlet

        array_image_icon = []
        array_image_checkbox = []
        array_image_outlet = []

        draw_devices(x_devices, y_devices, padding, array_image_icon, array_image_checkbox)
        outlets_height = draw_outlets(x_devices, y_devices, padding, active_outlets, array_image_outlet)
        irrigation_width = draw_irrigation(x_devices, y_devices, padding, outlets_height, water_level)
        draw_clock(x_devices, y_devices, padding, irrigation_width, outlets_height)

    def server_connection():
        global active_devices, active_outlets, water_level, water_parameters, parameter_change

        try:
            server: socket = socket(AF_INET, SOCK_STREAM)
            server.connect(ADDRESS)

        except Exception as e:
            print(f"Error: {e}")
            thread_socket.join()
            exit(1)

        while not stop_event.is_set():
            try:
                # update changes made by user to server
                if len(parameter_change) != 0:
                    data_to_send = parameter_change + '\n'
                    server.send(data_to_send.encode('utf-8'))
                    print(parameter_change)
                    parameter_change = ''

                    received_data = server.recv(BUFF_SIZE)
                    parts = received_data.decode('utf-8').split(';')
                    for i_device in range(len(active_devices)):
                        active_devices[i_device] = int(parts[i_device])
                    for i_outlet in range(len(active_devices), len(active_outlets) + len(active_devices)):
                        active_outlets[i_outlet - len(active_devices)] = int(parts[i_outlet])
                    water_level = int(parts[len(active_outlets) + len(active_devices)])
                    water_parameters[0] = float(parts[-2])
                    water_parameters[1] = int(parts[-1])

                    # print(active_devices, active_outlets, water_level, water_parameters)
                    # update_window()
                    time.sleep(1)

            except Exception as e:
                print(f"Error: {e}")
                thread_socket.join()
                exit(1)

    stop_event = threading.Event()

    thread_socket = threading.Thread(target=server_connection)
    thread_socket.start()

    window = mtTkinter.Tk()
    window.protocol("WM_DELETE_WINDOW", on_closing)  # closing the window stops a thread for GUI
    window.title('PiHoMi')
    window.geometry("950x600")
    window.resizable(False, False)
    window.configure(bg=dark)
    window_size = [950, 600]

    canvas = Canvas(
        window,
        bg=dark,
        height=550,
        width=1000,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    image_home = PhotoImage(file=relative_to_assets("home.png"))
    draw_logo(image_home)

    draw_dashboard()

    window.mainloop()


make_gui()

# thread_gui = threading.Thread(target=make_gui)
# thread_gui.start()
