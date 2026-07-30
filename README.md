# 🦫 Conversor Capivara

Aplicação web full-stack para conversão de moedas em tempo real, com uma pegada divertida e um visual moderno inspirado na identidade da capivara. O projeto combina um **frontend em React (Vite)** com um **backend em Python (Flask)** que consome a API pública da [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas).

---

## ✨ Funcionalidades

- 💱 **Conversão em tempo real** entre várias moedas (BRL, USD, EUR, GBP, ARS, CAD, BTC, JPY, CNY).
- 🔄 **Botão inverter** para trocar rapidamente a moeda de origem e destino.
- 🏳️ **Seleção de moedas** com bandeiras e nomes por extenso.
- 📊 **Cotação atual** exibida logo abaixo do formulário.
- 💰 **Resultado destacado** em card com gradiente verde.
- 🦫 **Mascote capivara** como identidade visual.
- 🎨 **Layout split (pêssego + amarelo)** seguindo identidade da marca.
- 🔌 **CORS habilitado** no backend para integração com o React.
- ⚠️ **Tratamento de erros** robusto (timeout, moeda inválida, valor inválido, falha de API).

---

## 🧰 Tecnologias utilizadas

### Frontend (`Projeto/conversor-capivara/`)

| Tecnologia               | Versão  | Uso                                   |
| ------------------------ | ------- | ------------------------------------- |
| **React**                | ^19.2.7 | Biblioteca de UI                      |
| **React DOM**            | ^19.2.7 | Renderização no navegador             |
| **Vite**                 | ^8.1.1  | Build tool e dev server               |
| **@vitejs/plugin-react** | ^6.0.3  | Plugin oficial do React para Vite     |
| **Oxlint**               | ^1.71.0 | Linter rápido                         |
| **Google Fonts**         | —       | Inter (UI) + Medula One (título/logo) |

### Backend (`Projeto/index.py`)

| Tecnologia     | Uso                             |
| -------------- | ------------------------------- |
| **Python 3.x** | Linguagem principal             |
| **Flask**      | Microframework web              |
| **Flask-CORS** | Liberação de CORS para o React  |
| **Requests**   | Consumo da AwesomeAPI           |
| **AwesomeAPI** | Cotação de moedas em tempo real |

---

## 📂 Estrutura do projeto

```
Python/
├── Inicio/                       # Exercícios introdutórios de Python
│   ├── atividade_2.py
│   ├── atividade_3.py
│   ├── atividade_4.py
│   ├── atividade_5.py
│   ├── atividade_6.py
│   ├── atividade_7.py
│   ├── atividade_8.py
│   └── primeira.py
│
└── Projeto/                      # Projeto principal
    ├── index.py                  # 🐍 Backend Flask
    └── conversor-capivara/       # ⚛️ Frontend React (Vite)
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── public/
        └── src/
            ├── main.jsx
            ├── App.jsx           # Componente principal
            ├── App.css           # Estilos do app
            ├── index.css         # Reset global
            ├── img/              # Imagens (capivara)
            └── assets/           # Outros assets
```

---

## 🚀 Como rodar o projeto

### 1️⃣ Pré-requisitos

- **Node.js** 18+ e **npm**
- **Python** 3.10+
- **pip**

### 2️⃣ Backend (Flask)

Abra um terminal e execute:

```bash
# Navegar até a pasta do projeto
cd Projeto

# Instalar dependências
pip install flask flask-cors requests

# Rodar o servidor
python index.py
```

O backend ficará disponível em: **http://localhost:5000**

### 3️⃣ Frontend (React + Vite)

Abra **outro terminal** e execute:

```bash
# Navegar até a pasta do frontend
cd Projeto/conversor-capivara

# Instalar dependências
npm install

# Rodar o servidor de desenvolvimento
npm run dev
```

O frontend ficará disponível em: **http://localhost:5173** (porta padrão do Vite)

---

## 🛰️ API do backend

### `POST /converter`

**Request body (JSON):**

```json
{
  "de": "BRL",
  "para": "USD",
  "valor": 100.0
}
```

**Resposta de sucesso (200):**

```json
{
  "cotacao": 0.1987,
  "resultado": 19.87,
  "mensagem": "💰 100.00 BRL = 19.87 USD"
}
```

**Resposta de erro (400):**

```json
{
  "erro": "Digite um número válido para o valor!"
}
```

---

## 🎨 Identidade visual

- **Paleta principal:**
  - 🟠 Laranja pêssego (`#ffc074` / `#ff8c42` / `#ff7a26`)
  - 🟡 Amarelo (`#fad02c`)
  - 🟢 Verde sucesso (`#2ecc71` / `#27ae60`)
  - ⚫ Preto suave (`#1a1a1a`)
- **Fontes:**
  - **Medula One** — títulos e logo
  - **Inter** — labels, inputs e textos auxiliares

---

## 🦫 Sobre o nome

O **Conversor Capivara** nasceu como um projeto de estudos em Python + React, com uma identidade visual baseada na capivara — um animal tranquilo, simpático e "de boa", que representa bem o espírito de um conversor simples e direto, sem complicação. 🌿

---

## 📜 Licença

Projeto de estudo, sem fins lucrativos. Sinta-se à vontade para usar como base para os seus próprios experimentos.
