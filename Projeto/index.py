from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
# Habilita CORS para aceitar requisições vindo da sua aplicação React
CORS(app)

# Moedas suportadas pela AwesomeAPI (paridade com BRL)
MOEDAS_VALIDAS = {"BRL", "USD", "EUR", "GBP", "ARS", "CAD", "BTC", "JPY", "CNY"}


@app.route('/converter', methods=['POST'])
def converter():
    dados = request.get_json()

    # Validação do corpo da requisição enviado pelo React
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado."}), 400

    de = dados.get('de')
    para = dados.get('para')
    valor_raw = dados.get('valor')

    # 1. Validação de presença do valor
    if valor_raw is None or str(valor_raw).strip() == "":
        return jsonify({"erro": "Por favor, digite um valor!"}), 400

    # 2. Conversão e Validação Numérica
    try:
        valor = float(str(valor_raw).replace(",", "."))
        if valor < 0:
            return jsonify({"erro": "Digite um valor maior ou igual a zero!"}), 400
    except ValueError:
        return jsonify({"erro": "Digite um número válido para o valor!"}), 400

    # Validação das moedas informadas
    if de not in MOEDAS_VALIDAS or para not in MOEDAS_VALIDAS:
        return jsonify({"erro": f"Moeda inválida. Use apenas: {', '.join(sorted(MOEDAS_VALIDAS))}"}), 400

    # 3. Mesma Moeda
    if de == para:
        return jsonify({
            "cotacao": 1.0,
            "resultado": valor,
            "mensagem": f"Mesma moeda selecionada!\n\n💰 {valor:.2f} {de} = {valor:.2f} {para}"
        })

    # 4. Requisição de Cotações para a AwesomeAPI
    try:
        # Tenta paridade direta primeiro
        url = f"https://economia.awesomeapi.com.br/json/last/{de}-{para}"
        res = requests.get(url, timeout=10)
        dados_api = res.json()
        chave = f"{de}{para}"

        if chave in dados_api:
            cotacao = float(dados_api[chave]["bid"])
            resultado = valor * cotacao
        else:
            # Caso a paridade direta não exista (ex: EUR para BTC), calcula via BRL
            cotacao_de, cotacao_para = 1.0, 1.0

            # Se 'de' não é BRL, busca cotação de 'de' para BRL
            if de != "BRL":
                url_de = f"https://economia.awesomeapi.com.br/json/last/{de}-BRL"
                r_de = requests.get(url_de, timeout=10).json()
                chave_de = f"{de}BRL"
                if chave_de not in r_de:
                    return jsonify({"erro": f"Não foi possível obter cotação de {de}."}), 400
                cotacao_de = float(r_de[chave_de]["bid"])

            # Se 'para' não é BRL, busca cotação de 'para' para BRL
            if para != "BRL":
                url_para = f"https://economia.awesomeapi.com.br/json/last/{para}-BRL"
                r_para = requests.get(url_para, timeout=10).json()
                chave_para = f"{para}BRL"
                if chave_para not in r_para:
                    return jsonify({"erro": f"Não foi possível obter cotação de {para}."}), 400
                cotacao_para = float(r_para[chave_para]["bid"])

            # valor em BRL = valor * cotacao_de (se de != BRL, senão 1)
            # resultado = valor_em_brl / cotacao_para
            cotacao = cotacao_de / cotacao_para
            resultado = (valor * cotacao_de) / cotacao_para

        # Retorna os dados calculados para o React
        return jsonify({
            "de": de,
            "para": para,
            "valor": valor,
            "cotacao": cotacao,
            "resultado": resultado
        }), 200

    except requests.exceptions.Timeout:
        print("[ERRO] Timeout ao consultar a AwesomeAPI")
        return jsonify({"erro": "A API de cotação demorou demais para responder."}), 504
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha de rede: {e}")
        return jsonify({"erro": "Falha de rede ao buscar cotação."}), 502
    except Exception as e:
        # Imprime o stack trace completo no terminal para facilitar diagnóstico
        print("\n[ERRO INESPERADO] -------------------------")
        traceback.print_exc()
        print("---------------------------------------------\n")
        return jsonify({
            "erro": f"Erro interno: {type(e).__name__} - {str(e)}"
        }), 500


if __name__ == "__main__":
    # Roda a API localmente na porta 5000
    app.run(host="0.0.0.0", port=5000, debug=True)