from flask import Flask, request, jsonify
from joblib import load
import requests
from datetime import datetime
import numpy as np
import pandas as pd
import json
import pytz

app = Flask(__name__)
loaded = load("meu_modelo_treinado.joblib")

modelo_linear = loaded['model_linear']
modelo_rf = loaded['modelo_rf']

@app.route('/', methods=['GET'])
def hello():
    return "Hello"
    
@app.route('/prever', methods=['POST'])
def prever():
    print(f'Valor da request: {request}')
    dados = request.get_json()
    print(f'Valor de dados: {dados}')
    df = pd.DataFrame([dados['valores']])
    print(f'Valor de df: {df}')
    pred = modelo.predict(df)[0]
    
    return jsonify({'previsao': pred.tolist()})

@app.route("/calcularCorrida", methods=['GET'])
def get_precoCorrida():
    agora = datetime.now(pytz.timezone('America/Sao_Paulo'))

    # Categorias disponíveis
    listaCategorias = {
        3: {
            1: "Comfort",
            2: "UberX",
            4: "Black"
        },
        2: {
            2: "Pop"
        }
    }

    origem = request.args.get('origem')
    destino = request.args.get('destino')

    api_key = "AIzaSyD9tS2l8dl7biMckXzNjPg_sapQnxZsauM"
    rota = f"https://maps.googleapis.com/maps/api/distancematrix/json?destinations={destino}&origins={origem}&departure_time=now&key={api_key}"

    responseRota = requests.get(rota)
    jsonRota = responseRota.json()

    # Distância e duração
    distancia = jsonRota['rows'][0]['elements'][0]['distance']['value']
    duracao_segundos = jsonRota['rows'][0]['elements'][0]['duration_in_traffic']['value']

    # Data e hora
    hora_atual = agora.hour
    dia = agora.day
    mes = agora.month
    ano = agora.year
    eh_fim_de_semana = agora.weekday() in [6, 7]
    numero_dia_semana = agora.weekday()

    precos_por_categoria = {}
    if(distancia > 15000):
        model = modelo_linear
        nome_modelo = "Linear Regression"
    else:
        model = modelo_rf
        nome_modelo = "Random Forest"

    # Armazenar os preços por categoria
    precos_por_categoria = []

    print(f'--------------------{nome_modelo}----------------------------')

    # Prever categorias
    preco_pop_99 = None

    for id_empresa, categorias in listaCategorias.items():
        for id_categoria, categoria in categorias.items():
            nome_empresa = "99" if id_empresa == 2 else "Uber"

            entrada = pd.DataFrame([{
                'id_prestador': id_empresa,
                'id_categoria': id_categoria,
                'dia': dia,
                'mes': mes,
                'ano': ano,
                'eh_fim_de_semana': eh_fim_de_semana,
                'hora': hora_atual,
                'numero_dia_semana': numero_dia_semana,
                'distancia_m': distancia,
                'duracao_s': duracao_segundos,
            }])

            pred = model.predict(entrada)[0]
            preco = round(pred, 2)

            # Armazena o valor do Pop para depois usar
            if nome_empresa == "99" and categoria == "Pop":
                preco_pop_99 = preco

            if nome_empresa not in precos_por_categoria:
                precos_por_categoria[nome_empresa] = {}

            precos_por_categoria[nome_empresa][categoria] = round(pred, 2)
    
            json_precos = json.dumps(precos_por_categoria, ensure_ascii=False, indent=2)
    return json_precos


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


