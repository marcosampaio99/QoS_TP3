import tkinter as tk
import webbrowser
from threading import Thread
import app
from waitress import serve
import os
from datetime import datetime
import pandas as pd

import socket



def run_dash_app():
    serve(app.app.server, host='127.0.0.1', port=8050)

def open_browser_and_run_dash_app(host, interval):
    app.collect_metrics(host, interval)  # Coleta métricas primeiro
    webbrowser.open('http://127.0.0.1:8050', new=1, autoraise=True)  # Abre o navegador depois
    test_label.config(text="")  # Limpa a mensagem "testando a sua ligação"
    run_dash_app()

def on_button_click():
    global host 
    host = host_entry.get()
    interval = int(interval_entry.get())
    global location 
    location = location_entry.get()
    
    root.after(100, test_label.config, {"text": "Testando a sua conexão..."}) 
    dash_thread = Thread(target=open_browser_and_run_dash_app, args=(host, interval))
    dash_thread.start()

    title.focus() #desaparece o cursor

def on_save_button_click():
    save_message = save_metrics_to_excel(location)
    save_label.config(text=save_message)

def save_metrics_to_excel(location):
    global app
    file_name = "metricas.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if app.data is not None:
        # Inserir a localidade antes dos resultados
        app.data.insert(0, 'Localidade', location)
        app.data.insert(1, 'Host', host)

        # Salvar os dados no mesmo arquivo Excel, em vez de criar um novo arquivo a cada vez
        if os.path.exists(file_path):
            existing_data = pd.read_excel(file_path, engine="openpyxl")
            app.data = pd.concat([existing_data, app.data], ignore_index=True)

        app.data.to_excel(file_path, index=False, engine="openpyxl")
        return f"Arquivo salvo com sucesso: {file_name}"
    else:
        return "Não há dados disponíveis para salvar."



root = tk.Tk()
root.title("Monitorização de Rede")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

title = tk.Label(frame, text="Universidade do Minho\nUC: Qualidade de Serviço em Redes IP\nTP3: Ferramenta para monitorização de QoS na Internet\nAno lectivo 2022/2023 — MEI / MIEI — 2o Sem", justify=tk.CENTER)
title.pack(pady=10)

image_path = "rede.png"
image = tk.PhotoImage(file=image_path)
image_label = tk.Label(frame, image=image)
image_label.pack(pady=10)

# Criar os frames para organizar os widgets
left_frame = tk.Frame(frame)
right_frame = tk.Frame(frame)

# Empacotar os frames
left_frame.pack(side=tk.LEFT, padx=(0, 10))
right_frame.pack(side=tk.RIGHT, padx=(10, 0))

host_label = tk.Label(left_frame, text="Host")
host_label.pack()
host_entry = tk.Entry(left_frame)
host_entry.pack()

interval_label = tk.Label(left_frame, text="Intervalo de tempo (segundos)")
interval_label.pack()
interval_entry = tk.Entry(left_frame)
interval_entry.pack()

location_label = tk.Label(left_frame, text="Localidade")
location_label.pack()
location_entry = tk.Entry(left_frame)
location_entry.pack()

button = tk.Button(right_frame, text="AVALIAR CONEXÃO", command=on_button_click)
button.pack(pady=10)

save_button = tk.Button(right_frame, text="SALVAR", command=on_save_button_click)
save_button.pack(pady=10)

save_label = tk.Label(right_frame, text="", justify=tk.CENTER)
save_label.pack(pady=10)

test_label = tk.Label(right_frame, text="", justify=tk.CENTER)
test_label.pack(pady=10)

root.mainloop()
