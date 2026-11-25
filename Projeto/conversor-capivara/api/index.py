import math
import time
import traceback

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Recusa corpos de requisição maiores que 1 KB (o JSON esperado tem ~50 bytes)
app.config["MAX_CONTENT_LENGTH"] = 1024

# O site e a API ficam no mesmo domínio (Vercel), então não há CORS:
# o navegador bloqueia outros sites de chamarem esta API.

MOEDAS_VALIDAS = {"BRL", "USD", "EUR", "GBP", "ARS", "CAD", "BTC", "JPY", "CNY"}
VALOR_MAXIMO = 1_000_000_000_000  # 1 trilhão
CACHE_SEGUNDOS = 60

HEADERS = {"User-Agent": "Mozilla/5.0 (conversor-capivara)"}

# Cache em memória: {(de, para): (momento, cotacao)}
_cache = {}


@app.after_request
def headers_de_seguranca(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    return response


# Respostas de erro sempre em JSON e sem detalhes internos
@app.errorhandler(404)
def nao_encontrado(_):
    return jsonify({"erro": "Rota não encontrada."}), 404


@app.errorhandler(405)
def metodo_nao_permitido(_):
    return jsonify({"erro": "Método não permitido."}), 405


@app.errorhandler(413)
def corpo_grande(_):
    return jsonify({"erro": "Requisição muito grande."}), 413


@app.errorhandler(500)
def erro_interno(_):
    return jsonify({"erro": "Erro interno. Tente novamente mais tarde."}), 500


# ---------------------------------------------------------------- cotações

def _awesome_bid(de, para):
    """Busca a cotação de/para na AwesomeAPI. Retorna float ou None."""
    url = f"https://economia.awesomeapi.com.br/json/last/{de}-{para}"
    res = requests.get(url, headers=HEADERS, timeout=10)
    try:
        dados = res.json()
    except ValueError:
        dados = {}
    chave = f"{de}{para}"
    if res.status_code == 200 and isinstance(dados, dict) and chave in dados:
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
        return float(res.json()["data"]["rates"][para])
    except (ValueError, KeyError, TypeError):
        print(f"[Coinbase] {de}-{para} falhou: HTTP {res.status_code} - {res.text[:200]}")
        return None


def cotacao_er_api(de, para):
    """Reserva: open.er-api.com (sem chave; não tem BTC)."""
    res = requests.get(f"https://open.er-api.com/v6/latest/{de}", headers=HEADERS, timeout=10)
    try:
        return float(res.json()["rates"][para])
    except (ValueError, KeyError, TypeError):
        print(f"[ER-API] {de}-{para} falhou: HTTP {res.status_code} - {res.text[:200]}")
        return None


def obter_cotacao(de, para):
    """Usa o cache se a cotação for recente; senão tenta cada fonte em ordem."""
    agora = time.time()
    em_cache = _cache.get((de, para))
    if em_cache and agora - em_cache[0] < CACHE_SEGUNDOS:
        return em_cache[1]

    for fonte in (cotacao_awesome, cotacao_coinbase, cotacao_er_api):
        try:
            cotacao = fonte(de, para)
        except requests.exceptions.RequestException as e:
            print(f"[{fonte.__name__}] erro de rede: {e}")
            continue
        if cotacao is not None and math.isfinite(cotacao) and cotacao > 0:
            _cache[(de, para)] = (agora, cotacao)
            return cotacao
    return None


# ------------------------------------------------------------------- rota

@app.route("/api/converter", methods=["POST"])
@app.route("/converter", methods=["POST"])
def converter():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie um JSON com 'de', 'para' e 'valor'."}), 400

    de = dados.get("de")
    para = dados.get("para")
    valor_raw = dados.get("valor")

    if not isinstance(de, str) or not isinstance(para, str) \
            or de not in MOEDAS_VALIDAS or para not in MOEDAS_VALIDAS:
        return jsonify({"erro": f"Moeda inválida. Use apenas: {', '.join(sorted(MOEDAS_VALIDAS))}"}), 400

    if not isinstance(valor_raw, (str, int, float)) or isinstance(valor_raw, bool) \
            or str(valor_raw).strip() == "":
        return jsonify({"erro": "Por favor, digite um valor!"}), 400

    texto_valor = str(valor_raw).strip().replace(",", ".")
    if len(texto_valor) > 20:
        return jsonify({"erro": "Valor muito longo."}), 400
    try:
        valor = float(texto_valor)
    except ValueError:
        return jsonify({"erro": "Digite um número válido para o valor!"}), 400

    # Bloqueia "nan", "inf", "1e400" etc.
    if not math.isfinite(valor):
        return jsonify({"erro": "Digite um número válido para o valor!"}), 400
    if valor < 0:
        return jsonify({"erro": "Digite um valor maior ou igual a zero!"}), 400
    if valor > VALOR_MAXIMO:
        return jsonify({"erro": "Valor muito alto. O máximo é 1 trilhão."}), 400

    if de == para:
        return jsonify({
            "cotacao": 1.0,
            "resultado": valor,
            "mensagem": f"Mesma moeda selecionada!\n\n💰 {valor:.2f} {de} = {valor:.2f} {para}",
        })

    try:
        cotacao = obter_cotacao(de, para)
    except Exception:
        traceback.print_exc()  # detalhe só no log da Vercel
        return jsonify({"erro": "Erro interno. Tente novamente mais tarde."}), 500

    if cotacao is None:
        return jsonify({"erro": f"Não foi possível obter cotação de {de} para {para}."}), 502

    return jsonify({
        "de": de,
        "para": para,
        "valor": valor,
        "cotacao": cotacao,
        "resultado": valor * cotacao,
    }), 200


if __name__ == "__main__":
    # Apenas para rodar no computador; na Vercel este bloco não é usado
    app.run(host="127.0.0.1", port=5000, debug=True)
