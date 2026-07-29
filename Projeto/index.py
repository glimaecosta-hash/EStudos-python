import tkinter as tk
from tkinter import ttk, messagebox
import requests

class ConversorMoedasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Moedas da Capivara 🦫")
        self.root.geometry("760x490")
        self.root.resizable(False, False)
        self.root.configure(bg="#FAD02C")  # Amarelo vibrante de fundo

        # Estrutura em 2 Colunas (Esquerda: Formulário / Direita: Ilustração)
        self.left_frame = tk.Frame(root, bg="#FF8C42", bd=0, highlightthickness=0)
        self.left_frame.place(x=20, y=20, width=360, height=450)

        self.right_frame = tk.Frame(root, bg="#FAD02C", bd=0, highlightthickness=0)
        self.right_frame.place(x=390, y=20, width=350, height=450)

        self._montar_painel_esquerdo()
        self._montar_painel_direito()

    def _montar_painel_esquerdo(self):
        # Título da área de entrada
        lbl_titulo = tk.Label(
            self.left_frame, 
            text="PAINEL DE CONVERSÃO", 
            font=("Impact", 16), 
            bg="#FF8C42", 
            fg="#2C3E50"
        )
        lbl_titulo.pack(pady=(15, 10))

        # 1. Moeda de Origem
        lbl_de = tk.Label(
            self.left_frame, 
            text="Moeda de Origem (De):", 
            font=("Arial", 10, "bold"), 
            bg="#FF8C42", 
            fg="#2C3E50", 
            anchor="w"
        )
        lbl_de.pack(fill="x", padx=25, pady=(5, 2))

        self.combo_de = ttk.Combobox(
            self.left_frame, 
            values=["BRL (Real)", "USD (Dólar)", "EUR (Euro)", "BTC (Bitcoin)"], 
            state="readonly", 
            font=("Arial", 10)
        )
        self.combo_de.set("BRL (Real)")
        self.combo_de.pack(fill="x", padx=25, pady=(0, 8))

        # 2. Valor a Converter
        lbl_valor = tk.Label(
            self.left_frame, 
            text="Valor a converter:", 
            font=("Arial", 10, "bold"), 
            bg="#FF8C42", 
            fg="#2C3E50", 
            anchor="w"
        )
        lbl_valor.pack(fill="x", padx=25, pady=(5, 2))

        self.entry_valor = tk.Entry(
            self.left_frame, 
            font=("Arial", 11, "bold"), 
            bg="#F9F3DF", 
            bd=0, 
            justify="center"
        )
        self.entry_valor.pack(fill="x", padx=25, ipady=6, pady=(0, 8))

        # 3. Moeda de Destino
        lbl_para = tk.Label(
            self.left_frame, 
            text="Conversão desejada (Para):", 
            font=("Arial", 10, "bold"), 
            bg="#FF8C42", 
            fg="#2C3E50", 
            anchor="w"
        )
        lbl_para.pack(fill="x", padx=25, pady=(5, 2))

        self.combo_para = ttk.Combobox(
            self.left_frame, 
            values=["USD (Dólar)", "EUR (Euro)", "BRL (Real)", "BTC (Bitcoin)"], 
            state="readonly", 
            font=("Arial", 10)
        )
        self.combo_para.set("USD (Dólar)")
        self.combo_para.pack(fill="x", padx=25, pady=(0, 10))

        # Botão Converter
        btn_converter = tk.Button(
            self.left_frame, 
            text="⚡ CONVERTER AGORA", 
            font=("Arial", 10, "bold"), 
            bg="#27AE60", 
            fg="white", 
            bd=0, 
            activebackground="#219150", 
            cursor="hand2", 
            command=self.converter
        )
        btn_converter.pack(fill="x", padx=25, ipady=5, pady=(2, 10))

        # 4. Caixa de Resultado / Cotação Atual
        self.lbl_resultado = tk.Label(
            self.left_frame, 
            text="Insira um valor e clique\\nem Converter...", 
            font=("Arial", 9, "bold"), 
            bg="#F9F3DF", 
            fg="#2C3E50", 
            wraplength=280, 
            justify="center", 
            height=4
        )
        self.lbl_resultado.pack(fill="x", padx=25, pady=(5, 10))

        # Botão Sair
        btn_sair = tk.Button(
            self.left_frame, 
            text="Sair", 
            font=("Arial", 9, "bold"), 
            bg="#E74C3C", 
            fg="white", 
            bd=0, 
            cursor="hand2", 
            command=self.root.quit
        )
        btn_sair.pack(padx=25, pady=(0, 10))

    def _montar_painel_direito(self):
        # Título Estilizado
        lbl_main = tk.Label(
            self.right_frame, 
            text="CONVERSOR\nDE\nMOEDAS", 
            font=("Impact", 28), 
            bg="#FAD02C", 
            fg="#1E8449"
        )
        lbl_main.pack(pady=(20, 10))

        # Desenho da Capivara no Canvas
        canvas = tk.Canvas(self.right_frame, width=220, height=220, bg="#FAD02C", highlightthickness=0)
        canvas.pack()

        # Corpo da Capivara
        canvas.create_oval(30, 90, 180, 190, fill="#A66E38", outline="#5C3D1E", width=3)
        # Cabeça
        canvas.create_oval(110, 55, 190, 125, fill="#A66E38", outline="#5C3D1E", width=3)
        # Focinho
        canvas.create_oval(150, 80, 190, 120, fill="#8B5A2B", outline="#5C3D1E", width=2)
        # Olho
        canvas.create_oval(145, 72, 155, 82, fill="#1A1A1A")
        # Orelha
        canvas.create_oval(115, 48, 130, 70, fill="#8B5A2B", outline="#5C3D1E", width=2)
        # Notas de dinheiro na mãozinha
        canvas.create_rectangle(150, 120, 200, 148, fill="#27AE60", outline="#1E8449", width=2)
        canvas.create_text(175, 134, text="$$$", fill="white", font=("Arial", 11, "bold"))

    def converter(self):
        valor_str = self.entry_valor.get().strip().replace(",", ".")
        if not valor_str:
            messagebox.showwarning("Atenção", "Por favor, digite um valor!")
            return

        try:
            valor = float(valor_str)
            if valor < 0:
                messagebox.showwarning("Atenção", "Digite um valor maior ou igual a zero!")
                return
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido para o valor!")
            return

        de = self.combo_de.get().split()[0]
        para = self.combo_para.get().split()[0]

        if de == para:
            self.lbl_resultado.config(text=f"Mesma moeda selecionada!\n\n💰 {valor:.2f} {de} = {valor:.2f} {para}")
            return

        # Requisição para a API AwesomeAPI
        try:
            url = f"https://economia.awesomeapi.com.br/json/last/{de}-{para}"
            res = requests.get(url)
            dados = res.json()
            chave = f"{de}{para}"

            if chave in dados:
                cotacao = float(dados[chave]["bid"])
                resultado = valor * cotacao
            else:
                # Caso a paridade direta não exista (ex: EUR para BTC), calcula via BRL
                url_de = f"https://economia.awesomeapi.com.br/json/last/{de}-BRL"
                url_para = f"https://economia.awesomeapi.com.br/json/last/{para}-BRL"
                
                res_de = requests.get(url_de).json()[f"{de}BRL"]["bid"]
                res_para = requests.get(url_para).json()[f"{para}BRL"]["bid"]
                
                cotacao = float(res_de) / float(res_para)
                resultado = valor * cotacao

            # Exibe resultado formatado
            if para == "BTC":
                self.lbl_resultado.config(
                    text=f"Cotação: 1 {de} = {cotacao:.6f} {para}\n\n💰 {valor:.2f} {de} = {resultado:.6f} {para}"
                )
            else:
                self.lbl_resultado.config(
                    text=f"Cotação: 1 {de} = R$ {cotacao:.2f} {para}\n\n💰 {valor:.2f} {de} = {resultado:.2f} {para}"
                )

        except Exception as e:
            messagebox.showerror("Erro de Conexão", "Não foi possível buscar a cotação. Verifique sua conexão com a internet.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversorMoedasApp(root)
    root.mainloop()