import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import time
from ping3 import ping
import speedtest
import webbrowser


#host = '8.8.8.8'  # Adicione esta linha para definir o host
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



def collect_latency_jitter(host, interval,count):
    latencies = []
    for _ in range(count):
        latency = ping(host, unit='ms')
        if latency is not None:
            latencies.append(latency)
        time.sleep(interval)

    jitter = [abs(latencies[i+1] - latencies[i]) for i in range(len(latencies)-1)]
    jitter.append(abs(latencies[-1] - latencies[-2]))
    return latencies, jitter


def collect_bandwidth(host, interval, count):
    download = []
    upload = []

    for _ in range(count):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_mbps = st.download() / 1e6
            upload_mbps = st.upload() / 1e6
            download.append(download_mbps)
            upload.append(upload_mbps)
        except Exception as e:
            print("Erro ao executar teste de velocidade:", e)
            download.append(None)
            upload.append(None)
        time.sleep(interval)
    return download, upload

def collect_metrics(host, interval):
    global data
    latencies, jitter = collect_latency_jitter(host, interval, count=5)
    download, upload = collect_bandwidth(host, interval, count=len(latencies))

    data = pd.DataFrame({
        'timestamp': pd.date_range(start=pd.Timestamp.now(), periods=len(latencies), freq=f'{interval}S'),
        'latency': latencies,
        'jitter': jitter,
        'download': download,
        'upload': upload,  # Adicione esta linha para incluir os dados de upload na tabela
    })

    print(data)

    update_app_layout()


   

def update_app_layout():
    app.layout = dbc.Container([
        html.H1('Monitorização de Rede', style={'text-align': 'center'}),

        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='latency-graph',
                    figure={
                        'data': [
                            go.Scatter(x=data['timestamp'], y=data['latency'], mode='lines', name='Latência')
                        ],
                        'layout': go.Layout(title='Latência Fim-a-Fim', xaxis={'title': 'Tempo(segundos)'}, yaxis={'title': 'Latência (ms)'})
                    }
                ),
            ], width=6),

            dbc.Col([
                dcc.Graph(
                    id='jitter-graph',
                    figure={
                        'data': [
                            go.Scatter(x=data['timestamp'], y=data['jitter'], mode='lines', name='Jitter')
                        ],
                        'layout': go.Layout(title='Jitter Fim-a-Fim', xaxis={'title': 'Tempo(segundos)'}, yaxis={'title': 'Jitter (ms)'})
                    }
                ),
            ], width=6),
        ]),

         dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='bandwidth-graph',
                    figure={
                        'data': [
                            go.Scatter(x=data['timestamp'], y=data['download'], mode='lines', name='Largura de Banda')
                        ],
                        'layout': go.Layout(title='Largura de Banda Disponível', xaxis={'title': 'Tempo(segundos)'}, yaxis={'title': 'Largura de Banda (Mbps)'})
                    }
                ),
            ], width=12),
        ]),


         dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='upload-graph',
                    figure={
                        'data': [
                            go.Scatter(x=data['timestamp'], y=data['upload'], mode='lines', name='Upload')
                        ],
                        'layout': go.Layout(title='Upload Disponível', xaxis={'title': 'Tempo(segundos)'}, yaxis={'title': 'Upload (Mbps)'})
                    }
                ),
            ], width=12),
        ]),

        
        dbc.Row([
            dbc.Col([
                html.H2('Tabela de Métricas', style={'text-align': 'center'}),

                dbc.Table.from_dataframe(data, striped=True, bordered=True, hover=True, responsive=True, className='table-dark')
        ], width=12),
    ]),
])



    