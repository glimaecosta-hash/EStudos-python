from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)

# ✅ CORS configurado explicitamente para liberar o front no Vercel e qualquer origem
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=False,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)


@app.after_request
def add_cors_headers(response):
    """Garante que os headers de CORS sejam enviados em TODAS as respostas,
    inclusive nas respostas automáticas de preflight (OPTIONS)."""
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response


MOEDAS_VALIDAS = {"BRL", "USD", "EUR", "GBP", "ARS", "CAD", "BTC", "JPY", "CNY"}

HEADERS = {"User-Agent": "Mozilla/5.0 (conversor-capivara)"}


def _awesome_bid(de, para):
    """Busca a cotação de/para na AwesomeAPI. Retorna float ou None."""
    url = f"https://economia.awesomeapi.com.br/json/last/{de}-{para}"
    res = requests.get(url, headers=HEADERS, timeout=10)
    try:
        dados = res.json()
    except ValueError:
        dados = {}
    chave = f"{de}{para}"
    if res.status_code == 200 and chave in dados:
        return float(dados[chave]["bid"])
    print(f"[AwesomeAPI] {de}-{para} falhou: HTTP {res.status_code} - {res.text[:200]}")
    return None


def cotacao_awesome(de, para):
    """Tenta o par direto e, se não existir, calcula passando pelo BRL."""
    direto = _awesome_bid(de, para)
    if direto is not None:
        return direto
    cot_de = 1.0 if de == "BRL" else _awesome_bid(de, "BRL")
    cot_para = 1.0 if para == "BRL" else _awesome_bid(para, "BRL")
    if cot_de is None or cot_para is None:
        return None
    return cot_de / cot_para


def cotacao_coinbase(de, para):
    """Reserva com Bitcoin: Coinbase (sem chave; moedas comuns e BTC)."""
    res = requests.get(
        "https://api.coinbase.com/v2/exchange-rates",
        params={"currency": de}, headers=HEADERS, timeout=10,
    )
    try:
        rates = res.json()["data"]["rates"]
        return float(rates[para])
    except (ValueError, KeyError, TypeError):
        print(f"[Coinbase] {de}-{para} falhou: HTTP {res.status_code} - {res.text[:200]}")
        return None


def cotacao_er_api(de, para):
    """Reserva: open.er-api.com (sem chave; não tem BTC)."""
    res = requests.get(f"https://open.er-api.com/v6/latest/{de}", headers=HEADERS, timeout=10)
    dados = res.json()
    if dados.get("result") == "success" and para in dados.get("rates", {}):
        return float(dados["rates"][para])
    print(f"[ER-API] {de}-{para} falhou: HTTP {res.status_code} - {res.text[:200]}")
    return None

# ✅ Adicionada a rota /api/converter
@app.route('/api/converter', methods=['POST'])
@app.route('/converter', methods=['POST'])
def converter():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Nenhum dado enviado."}), 400

    de = dados.get('de')
    para = dados.get('para')
    valor_raw = dados.get('valor')

    if valor_raw is None or str(valor_raw).strip() == "":
        return jsonify({"erro": "Por favor, digite um valor!"}), 400

    try:
        valor = float(str(valor_raw).replace(",", "."))
        if valor < 0:
            return jsonify({"erro": "Digite um valor maior ou igual a zero!"}), 400
    except ValueError:
        return jsonify({"erro": "Digite um número válido para o valor!"}), 400

    if de not in MOEDAS_VALIDAS or para not in MOEDAS_VALIDAS:
        return jsonify({"erro": f"Moeda inválida. Use apenas: {', '.join(sorted(MOEDAS_VALIDAS))}"}), 400

    if de == para:
        return jsonify({
            "cotacao": 1.0,
            "resultado": valor,
            "mensagem": f"Mesma moeda selecionada!\n\n💰 {valor:.2f} {de} = {valor:.2f} {para}"
        })

    try:
        # Tenta cada fonte em ordem até uma responder
        cotacao = None
        for fonte in (cotacao_awesome, cotacao_coinbase, cotacao_er_api):
            try:
                cotacao = fonte(de, para)
            except requests.exceptions.RequestException as e:
                print(f"[{fonte.__name__}] erro de rede: {e}")
            if cotacao is not None:
                break
        if cotacao is None:
            return jsonify({"erro": f"Não foi possível obter cotação de {de} para {para}."}), 502

        resultado = valor * cotacao

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
        print("\n[ERRO INESPERADO] -------------------------")
        traceback.print_exc()
        print("---------------------------------------------\n")
        return jsonify({
            "erro": f"Erro interno: {type(e).__name__} - {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)