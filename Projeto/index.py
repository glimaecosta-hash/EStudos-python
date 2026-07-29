import requests

def buscar_cotacao(moeda):
    """Busca a cotação em tempo real da moeda escolhida."""
    url = f"https://economia.awesomeapi.com.br/json/last/{moeda}-BRL"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        chave = f"{moeda}BRL"
        return float(dados[chave]["bid"])
    except Exception:
        print("\n❌ Erro ao se conectar com a API. Verifique sua conexão com a internet.")
        return None

# Loop principal do programa
while True:
    print("\n" + "=" * 40)
    print("      CONVERSOR DE MOEDAS EM TEMPO REAL      ")
    print("=" * 40)

    # 1. Entrada de valor com validação
    entrada = input("\nDigite o valor em Reais (R$) ou 'S' para sair: ").strip()
    
    if entrada.lower() == 's':
        print("\nEncerrando o programa... Até logo! 👋")
        break

    # Substitui vírgula por ponto para aceitar formatos como 50,50
    entrada = entrada.replace(",", ".")

    try:
        valor_reais = float(entrada)
        if valor_reais <= 0:
            print("⚠️ Por favor, digite um valor maior que zero.")
            continue
    except ValueError:
        print("❌ Entrada inválida! Por favor, digite apenas números.")
        continue

    # 2. Menu de opções
    print("\nEscolha a moeda para conversão:")
    print("1 - Dólar (USD)")
    print("2 - Euro (EUR)")
    print("3 - Bitcoin (BTC)")
    print("4 - Sair")

    opcao = input("Digite a opção (1-4): ").strip()

    if opcao == "1":
        moeda = "USD"
    elif opcao == "2":
        moeda = "EUR"
    elif opcao == "3":
        moeda = "BTC"
    elif opcao == "4":
        print("\nEncerrando o programa... Até logo! 👋")
        break
    else:
        print("❌ Opção de moeda inválida!")
        continue

    # 3. Buscar Cotação e Calcular
    cotacao = buscar_cotacao(moeda)

    if cotacao:
        valor_convertido = valor_reais / cotacao
        
        print("\n" + "-" * 40)
        print(f"📌 Cotação atual do {moeda}: R$ {cotacao:.2f}")
        
        # Formatação especial caso a moeda seja Bitcoin (para mostrar mais casas decimais)
        if moeda == "BTC":
            print(f"💰 R$ {valor_reais:.2f} equivalem a: {valor_convertido:.6f} {moeda}")
        else:
            print(f"💰 R$ {valor_reais:.2f} equivalem a: {valor_convertido:.2f} {moeda}")
            
        print("-" * 40)