import React, { useState } from "react";
import "./App.css";
import imgCapivara from "./img/img-removebg-preview.png";


const MOEDAS = [
  { codigo: "BRL", bandeira: "🇧🇷", nome: "Real Brasileiro" },
  { codigo: "USD", bandeira: "🇺🇸", nome: "Dólar Americano" },
  { codigo: "EUR", bandeira: "🇪🇺", nome: "Euro" },
  { codigo: "BTC", bandeira: "₿", nome: "Bitcoin" },
];


function CurrencySelect({ value, onChange, label, id }) {
  return (
    <div className="currency-select-wrapper">
      <label htmlFor={id}>{label}</label>
      <div className="currency-select-box">
        <select
          id={id}
          className="currency-select"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          {MOEDAS.map((m) => (
            <option key={m.codigo} value={m.codigo}>
              {m.bandeira} {m.codigo} — {m.nome}
            </option>
          ))}
        </select>
        <span className="currency-select-arrow">▾</span>
      </div>
    </div>
  );
}


function RateCard({ cotacao, moedaDe, moedaPara, loading, error }) {
  if (loading) {
    return (
      <div className="rate-card rate-card-loading">
        <div className="spinner" />
        <span>Buscando cotação...</span>
      </div>
    );
  }
  if (error) {
    return <div className="rate-card rate-card-error">⚠️ {error}</div>;
  }
  if (!cotacao) {
    return (
      <div className="rate-card rate-card-empty">
        Insira um valor e clique em <strong>Converter</strong>
      </div>
    );
  }
  return (
    <div className="rate-card">
      <div className="rate-card-line">
        <span className="rate-label">Cotação:</span>
        <span className="rate-value">
          1 {moedaDe} = <strong>{cotacao}</strong> {moedaPara}
        </span>
      </div>
      <div className="rate-card-trend">
        <span className="trend-up">▲ 0,42%</span>
        <span className="trend-period">nas últimas 24h</span>
      </div>
    </div>
  );
}

function App() {
  const [moedaDe, setMoedaDe] = useState("BRL");
  const [moedaPara, setMoedaPara] = useState("USD");
  const [valor, setValor] = useState("");
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  
  const handleValorChange = (e) => {
    const raw = e.target.value.replace(/[^0-9.,]/g, "").replace(",", ".");
    setValor(raw);
  };

  const handleInverter = () => {
    setMoedaDe(moedaPara);
    setMoedaPara(moedaDe);
    setResultado(null);
    setError("");
  };

  const formatarNumero = (n, casas = 2) =>
    Number(n).toLocaleString("pt-BR", {
      minimumFractionDigits: casas,
      maximumFractionDigits: casas,
    });

  const handleConverter = async (e) => {
    e.preventDefault();
    setError("");

    if (!valor || Number(valor) <= 0) {
      setError("Digite um valor válido maior que zero.");
      return;
    }

    setLoading(true);
    setResultado(null);

    try {
      const response = await fetch("http://localhost:5000/converter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ de: moedaDe, para: moedaPara, valor }),
      });

      const data = await response.json();

      if (response.ok) {
        setResultado({
          valor: data.valor,
          resultado: data.resultado,
          cotacao: data.cotacao,
          mensagem: data.mensagem || null,
        });
      } else {
        setError(data.erro || "Erro ao realizar a conversão.");
      }
    } catch {
      setError(
        "Não foi possível conectar à API. Verifique se ela está rodando.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="card-wrapper">
        
        <div className="left-panel">
          <div className="form-card">
            <h2 className="panel-title">Digite o Valor</h2>
            <p className="panel-subtitle">
              Converta entre moedas em tempo real
            </p>

            <form onSubmit={handleConverter} className="form">
              
              <div className="form-row">
                <CurrencySelect
                  id="moeda-de"
                  label="De"
                  value={moedaDe}
                  onChange={setMoedaDe}
                />
                <button
                  type="button"
                  className="btn-inverter"
                  onClick={handleInverter}
                  title="Inverter moedas"
                  aria-label="Inverter moedas"
                >
                  ⇅
                </button>
              </div>

              <div className="amount-wrapper">
                <label htmlFor="valor">Valor</label>
                <input
                  id="valor"
                  type="text"
                  inputMode="decimal"
                  className="amount-input"
                  placeholder="0,00"
                  value={valor}
                  onChange={handleValorChange}
                />
              </div>

              <CurrencySelect
                id="moeda-para"
                label="Para"
                value={moedaPara}
                onChange={setMoedaPara}
              />

              <button
                type="submit"
                className="btn-converter"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="btn-spinner" /> Convertendo...
                  </>
                ) : (
                  <>⚡ Converter agora</>
                )}
              </button>

              {error && <div className="form-error">⚠️ {error}</div>}
            </form>

            <div className="cotacao-section">
              <span className="cotacao-label">Cotação atual</span>
              <RateCard
                cotacao={
                  resultado
                    ? `${formatarNumero(resultado.cotacao, moedaPara === "BTC" ? 6 : 4)}`
                    : null
                }
                moedaDe={moedaDe}
                moedaPara={moedaPara}
                loading={loading}
                error={!loading && error}
              />
              {resultado && !resultado.mensagem && (
                <div className="resultado-final">
                  <span className="resultado-final-label">Você recebe:</span>
                  <span className="resultado-final-valor">
                    {moedaPara === "BTC"
                      ? `${formatarNumero(resultado.resultado, 6)} ${moedaPara}`
                      : `${formatarNumero(resultado.resultado)} ${moedaPara}`}
                  </span>
                </div>
              )}
              {resultado?.mensagem && (
                <div className="resultado-mensagem">{resultado.mensagem}</div>
              )}
            </div>
          </div>

          <button className="btn-sair" onClick={() => window.close()}>
            Sair
          </button>
        </div>

        {/* PAINEL DIREITO: Capivara */}
        <div className="right-panel">
          <h1 className="main-title">
            CONVERSOR
            <br />
            DE
            <br />
            MOEDAS
          </h1>
          <div className="capivara-container">
            <img
              src={imgCapivara}
              alt="Capivara com dinheiro"
              className="capivara-img"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
