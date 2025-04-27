from flask import Flask, request, jsonify
from joblib import load
import numpy as np
import pandas as pd

app = Flask(__name__)
modelo = load("meu_modelo_treinado.joblib")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
