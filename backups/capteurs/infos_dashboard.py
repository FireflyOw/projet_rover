import tkinter as tk, psutil, smbus2, time, adafruit_dht, board, adafruit_blinka

adress = 0x40
bus = smbus2.SMBus(1)

capt_temp = adafruit_dht.DHT22(board.D12)

def capt_air():
    try:
        bus.write_byte(adress, 0x88)
        time.sleep(0.3)
        data = bus.read_i2c_block_data(adress, 0x00, 29)

        pm1_atm = (data[10] << 8) | data[11]
        pm25_atm = (data[12] << 8) | data[13]
        pm10_atm = (data[14] << 8) | data[15]

        return {
            "pm1_atm": pm1_atm,
            "pm25_atm": pm25_atm,
            "pm10_atm": pm10_atm,
            "unite": "µg/m3",
        }
    
    except OSError:
        return {
            "pm1_atm": "Erreur!",
            "pm25_atm": "Erreur!",
            "pm10_atm": "Erreur!",
            "unite": "",
        }

def temp_hum():

    try:
        temperature = capt_temp.temperature
        humidite = capt_temp.humidity

        return {
            "temperature": temperature, 
            "humidite": humidite, 
            "unite_temp": "°C", 
            "unite_hum": "%",
        }

    except RuntimeError:
        return {
            "temperature": "Erreur!", 
            "humidite": "Erreur!", 
            "unite_temp": "", 
            "unite_hum": ""
        }

def temp_cpu():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = int(f.read()) / 1000
    return f"{temp:.1f} °C"

def fan_speed():
    try:
        with open('/sys/class/thermal/cooling_device0/cur_state', 'r') as f:
            state = int(f.read().strip())
        if state == 0:
            return "Eteint"
        else:
            return f"Allumé (niveau {state})"
    except:
        return "Non disponible"

def update():
    ram = psutil.virtual_memory()
    disque = psutil.disk_usage('/')

    label_temp_cpu.config(text=f"Température : {temp_cpu()}")
    label_cpu.config(text=f"CPU : {psutil.cpu_percent(interval=1)}%")
    label_ram.config(text=f"RAM : {ram.used // 1024 ** 2} MB / {ram.total // 1024 ** 2} MB ({ram.percent} %)")
    label_disque.config(text=f"Disque : {disque.used // 1024 ** 3} GB / {disque.total // 1024 ** 3} GB ({disque.percent} %)")
    label_fan.config(text=f"Ventilateur : {fan_speed()}")

    val_temp_hum = temp_hum()
    label_temp.config(text=f"Température : {val_temp_hum["temperature"]} {val_temp_hum["unite_temp"]}")
    label_humidite.config(text=f"Humidité : {val_temp_hum["humidite"]} {val_temp_hum["unite_hum"]}")

    valeur_air = capt_air()
    label_pm1_atm.config(text=f"PM 1 : {valeur_air['pm1_atm']} {valeur_air["unite"]}")
    label_pm25_atm.config(text=f"PM 2.5 : {valeur_air['pm25_atm']} {valeur_air["unite"]}")
    label_pm10_atm.config(text=f"PM 10 : {valeur_air['pm10_atm']} {valeur_air["unite"]}")

    root.after(1000, update)

root = tk.Tk()
root.title("Informations Raspberry Pi 5")
root.geometry("420x500")
root.configure(bg='#1a1a2e')
root.resizable(False, False)

titre = tk.Label(text="Raspberry Pi 5 Dashboard", bg="#1a1a2e", fg="#e94560", font=("Arial", 14, "bold"))
titre.pack(pady=15)

frame_style = {"bg": "#1a1a2e", "fg": "#e94560", "font": ("Arial", 11, "bold"), "padx": 10, "pady": 10}
label_style = {"bg": "#1a1a2e", "fg": "white", "font": ("Arial", 10), "anchor": "w"}

frame_systeme = tk.LabelFrame(root, text=" Performances Système ", **frame_style)
frame_systeme.pack(fill="x", padx=15, pady=10)

label_temp_cpu = tk.Label(frame_systeme, **label_style)
label_cpu = tk.Label(frame_systeme, **label_style)
label_ram = tk.Label(frame_systeme, **label_style)
label_disque = tk.Label(frame_systeme, **label_style)
label_fan = tk.Label(frame_systeme, **label_style)

for lbl in [label_temp_cpu, label_cpu, label_ram, label_disque, label_fan]:
    lbl.pack(fill="x", pady=2)

frame_meteo = tk.LabelFrame(root, text=" Environnement (AM2302) ", **frame_style)
frame_meteo.pack(fill="x", padx=15, pady=10)

label_temp = tk.Label(frame_meteo, **label_style)
label_humidite = tk.Label(frame_meteo, **label_style)

for lbl in [label_temp, label_humidite]:
    lbl.pack(fill="x", pady=2)

frame_air = tk.LabelFrame(root, text=" Qualité de l'air (HM3301) ", **frame_style)
frame_air.pack(fill="x", padx=15, pady=10)

label_pm1_atm = tk.Label(frame_air, **label_style)
label_pm25_atm = tk.Label(frame_air, **label_style)
label_pm10_atm = tk.Label(frame_air, **label_style)

for lbl in [label_pm1_atm, label_pm25_atm, label_pm10_atm]:
    lbl.pack(fill="x", pady=2)

update()
root.mainloop()