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
    print("Começou")
    dados = request.get_json()
    df = pd.DataFrame(dados["valores"])
    
    pred = modelo.predict(df)
    
    return jsonify({'previsao': pred.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
