from flask import Flask, request, jsonify
from joblib import load
import requests
from datetime import datetime
import numpy as np
import pandas as pd

app = Flask(__name__)
loaded = load("meu_modelo_treinado.joblib")
encoder = loaded['encoder']
modelo = loaded['model']

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
    agora = datetime.now()
    origem = request.args.get('origem')
    print(f'Origem: {origem}')
    destino = request.args.get('destino')
    print(f'Destio: {destino}')
    
    api_key = "AIzaSyCDmnx17lJCCO7GMJEIlqeBlRjnHxfI8b8"
    rota = f"https://maps.googleapis.com/maps/api/distancematrix/json?destinations={destino}&origins={origem}&key={api_key}"

    responseRota = requests.get(rota)
    jsonRota = responseRota.json()
    print(jsonRota)
    distancia = jsonRota['rows'][0]['elements'][0]['distance']['value']

    duracao_segundos = jsonRota['rows'][0]['elements'][0]['duration']['value']
    duracao_minutos = duracao_segundos // 60

    codigos_categorias = df['ProductID_encoded'].unique().tolist()
    precos_por_categoria = {}

    for codigo in codigos_categorias:
        entrada = pd.DataFrame([{
            'distancia_m': distancia,
            'tempo_estim_minutos': duracao_minutos,
            'ProductID_encoded': codigo,
            'dia': agora.day - 1,
            'mes': agora.month,
            'e_fim_de_semana': agora.weekday() >= 5
        }])
        pred = modelo.predict(entrada)[0]
        nome_categoria = encoder.inverse_transform([codigo])[0]
        precos_por_categoria[nome_categoria] = round(pred, 2)


    precos_ordenados = dict(sorted(precos_por_categoria.items(), key=lambda item: item[1]))
    json_precos = json.dumps(precos_ordenados, ensure_ascii=False, indent=2)
    return json_precos


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


