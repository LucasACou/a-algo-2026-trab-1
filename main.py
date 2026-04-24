import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options

from urllib.parse import urlparse
from lxml import etree

import re
import logging
import time
import os
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

# testes
# url =  "https://www.uol.com.br/"
# xpath = "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

# url =  "https://b3.com.br/"
# xpath = '//*[@id="quotes-container"]/div/span'

# url = https://br.investing.com/currencies/usd-brl
# xpath = //div[@data-test='instrument-price-last']

"""
Sistema de monitoramento de valores em páginas web utilizando Selenium e interface gráfica.

Este módulo implementa:

- Validação de entrada do usuário (nome, URL e XPath)
- Monitoramento contínuo de elementos em páginas web
- Detecção de mudanças em valores (ex: cotação)
- Registro de logs em arquivo e interface gráfica
- Interface gráfica baseada em Tkinter
- Execução paralela utilizando threads

Componentes principais:

- Funções utilitárias de validação e automação
- Sistema de logging integrado
- Classe InterfaceMonitoramento (GUI)
- Execução de monitoramento em background

Dependências principais:

- Selenium (automação web)
- Tkinter (interface gráfica)
- threading (execução concorrente)
"""

logging.basicConfig(
    filename='log_usuario.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Usuário: %(user)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

usuario_sessao = "Desconhecido"

log_queue = queue.Queue()
monitoramento_ativo = False
inicio_monitoramento = None

def registrar_log(mensagem, nivel="info"):
    """
    Registra mensagens no log do sistema.

    :param mensagem: Texto da mensagem a ser registrada
    :type mensagem: str
    :param nivel: Nível do log (info, warning ou error)
    :type nivel: str
    :return: None
    """
    extra_data = {'user': usuario_sessao}
    print(mensagem)

    enviar_log_interface(mensagem)

    if nivel == "info":
        logging.info(mensagem, extra=extra_data)
    elif nivel == "error":
        logging.error(mensagem, extra=extra_data)
    elif nivel == "warning":
        logging.warning(mensagem, extra=extra_data)


def url_valida(url):
    """
    Verifica se uma URL é válida.

    :param url: URL a ser validada
    :type url: str
    :return: True se válida, False caso contrário
    :rtype: bool
    """
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except Exception:
        return False


def pedir_url():
    """
    Solicita ao usuário uma URL válida.

    :return: URL válida fornecida pelo usuário
    :rtype: str
    """
    while True:
        url = input("Digite o URL: ").strip()
        registrar_log(f"Usuário digitou a URL: {url}")

        if url_valida(url):
            return url
        else:
            registrar_log(f"URL inválida tentada: {url}", "warning")
            print("URL inválida! Tente novamente.\n")


def xpath_valido(xpath):
    """
    Verifica se um XPath é válido.

    :param xpath: Expressão XPath
    :type xpath: str
    :return: True se válido, False caso contrário
    :rtype: bool
    """
    if not xpath or not xpath.startswith("//"):
        return False
    try:
        etree.XPath(xpath)
        return True
    except Exception:
        return False


def pedir_xpath():
    """
    Solicita ao usuário um XPath válido.

    :return: XPath válido
    :rtype: str
    """
    while True:
        xpath = input("Digite o XPath: ").strip()
        registrar_log(f"Usuário digitou o XPath: {xpath}")

        if xpath_valido(xpath):
            return xpath
        else:
            registrar_log(f"XPath inválido tentado: {xpath}", "warning")
            print("XPath inválido! Tente novamente.\n")


def encontrar_elemento(driver, xpath):
    """
    Busca um elemento na página utilizando XPath.

    Tenta encontrar diretamente e, caso não encontre,
    procura dentro de iframes.

    :param driver: Instância do WebDriver
    :type driver: selenium.webdriver
    :param xpath: XPath do elemento
    :type xpath: str
    :return: Elemento encontrado ou None
    """
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception:
        pass

    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for iframe in iframes:
        driver.switch_to.frame(iframe)
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception:
            driver.switch_to.default_content()

    return None


def salvar_elementos(mensagem):
    """
    Preenche e envia um formulário com uma mensagem.

    :param mensagem: Texto a ser enviado
    :type mensagem: str
    :return: None
    """
    input_escrever = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//textarea[@name="my-textarea"]'))
    )
    input_escrever.send_keys(mensagem)

    time.sleep(5)

    botao_salvar = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    botao_salvar.click()


def validar_e_pedir_nome():
    """
    Solicita e valida o nome do usuário via terminal.

    O nome deve conter apenas letras (incluindo acentos)
    e ter no mínimo 3 caracteres.

    :return: Nome válido do usuário
    :rtype: str
    """
    global usuario_sessao
    while True:
        nome = input("\nPor favor, insira seu nome de usuário: ").strip()

        if len(nome) >= 3 and re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome):
            usuario_sessao = nome
            registrar_log(f"LOGIN: Usuário '{nome}' acessou o sistema.")
            return nome
        else:
            print("Erro: O nome deve conter apenas letras e ter no mínimo 3 caracteres.")
            logging.warning(f"Tentativa de login inválida com o input: '{nome}'", extra={'user': 'Sistema'})


def validar_nome_interface(nome):
    """
    Valida o nome do usuário vindo da interface gráfica.

    A validação exige:
    - Mínimo de 3 caracteres
    - Apenas letras (incluindo acentos) e espaços

    :param nome: Nome digitado pelo usuário
    :type nome: str
    :return: True se válido, False caso contrário
    :rtype: bool
    """
    return len(nome.strip()) >= 3 and re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome.strip())


def enviar_log_interface(mensagem):
    """
    Envia uma mensagem para a fila de logs da interface gráfica.

    A mensagem é formatada com horário e usuário antes de ser exibida.

    :param mensagem: Texto do log
    :type mensagem: str
    :return: None
    """
    horario = time.strftime("%H:%M:%S")
    log_queue.put(f"[{horario}] [Usuário: {usuario_sessao}] {mensagem}")


def executar_monitoramento_interface(nome, url, xpath):
    """
    Executa o processo de monitoramento em uma thread separada.

    Responsável por:
    - Inicializar o WebDriver
    - Acessar a URL informada
    - Monitorar o elemento via XPath
    - Detectar mudanças no valor
    - Registrar logs durante todo o processo
    - Encerrar automaticamente após tempo limite ou erro

    O monitoramento pode ser interrompido manualmente
    através da variável global `monitoramento_ativo`.

    :param nome: Nome do usuário
    :type nome: str
    :param url: URL a ser monitorada
    :type url: str
    :param xpath: XPath do elemento monitorado
    :type xpath: str
    :return: None
    """
    global usuario_sessao, driver, monitoramento_ativo, inicio_monitoramento

    usuario_sessao = nome
    monitoramento_ativo = True

    try:
        registrar_log(f"LOGIN: Usuário '{nome}' acessou o sistema.")
        registrar_log("Iniciando script de monitoramento.")

        registrar_log(f"Usuário digitou a URL: {url}")
        registrar_log(f"URL válida: {url}")

        registrar_log(f"Usuário digitou o XPath: {xpath}")
        registrar_log(f"XPath válido: {xpath}")

        # CONFIGURAÇÂO DO DRIVER DE NAVEGAÇÂO ==============================================
        # options
        options = Options()
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--log-level=3')
        # services
        # driver
        driver = webdriver.Edge(options=options)
        
        # MINERAÇÂO / LOOP PRINCIPAL =======================================================

        driver.get(url)
        original_tab = driver.current_window_handle

        elemento = encontrar_elemento(driver, xpath)
        if elemento is None or not elemento.text or not elemento.text.strip():
            registrar_log("Elemento não encontrado ou sem texto!", "error")
            driver.quit()
            return

        valor_antigo = elemento.text
        registrar_log(f"Cotação capturada: {valor_antigo}")

        mudou = False
        tempo_max = 600  # 10 minutos executando
        inicio = time.time()
        inicio_monitoramento = inicio

        while True:

            if not monitoramento_ativo:
                registrar_log("Monitoramento interrompido pelo usuário.", "warning")
                break

            if time.time() - inicio > tempo_max:
                registrar_log("Monitoramento encerrado por segurança.", "warning")
                break

            elemento = encontrar_elemento(driver, xpath)

            if elemento is None:
                registrar_log("Elemento não encontrado durante execução!", "error")
                break

            valor_novo = elemento.text

            if not valor_novo:
                registrar_log("Elemento sem texto!", "warning")
                break

            if valor_novo != valor_antigo:
                registrar_log(f"A cotação mudou para: {valor_novo}")
                mudou = True
                break

            registrar_log("O valor ainda é o mesmo. Aguardando...")
            time.sleep(10)

        # SALVAR VALORES ===================================================================
        if mudou:
            salvar_mensagem = f"""O valor antigo era: {valor_antigo}
O novo valor é: {valor_novo}
"""

            driver.switch_to.new_window('tab')
            driver.get("https://www.selenium.dev/selenium/web/web-form.html")
            salvar_elementos(salvar_mensagem)
        else:
            registrar_log("Nenhuma mudança detectada. Nada foi salvo.")

        time.sleep(10)
        driver.quit()

    except Exception as erro:
        registrar_log(f"Erro inesperado: {erro}", "error")

    finally:
        monitoramento_ativo = False
        inicio_monitoramento = None
        try:
            if driver is not None:
                driver.quit()
        except Exception:
            pass


# ===================== INTERFACE TKINTER =====================

class InterfaceMonitoramento:
    """
    Interface gráfica do sistema de monitoramento.

    Implementa a GUI utilizando Tkinter, permitindo:

    - Entrada de dados do usuário (nome, URL, XPath)
    - Controle de execução (iniciar/parar monitoramento)
    - Exibição de logs em tempo real
    - Exibição do tempo de execução
    - Feedback visual do estado do sistema

    A interface utiliza:
    - Threads para execução do monitoramento sem travar a UI
    - Queue para comunicação entre thread e interface
    """
    def __init__(self, janela):
        """
        Inicializa a interface gráfica.

        :param janela: Instância principal do Tkinter (Tk)
        :type janela: tkinter.Tk
        """
        self.janela = janela
        self.janela.title("Monitor de Preço com Selenium")
        self.janela.geometry("920x680")
        self.janela.minsize(860, 620)
        self.janela.configure(bg="#0f172a")

        self.thread_monitoramento = None
        self.imagem_tk = None

        self.configurar_estilo()
        self.criar_layout()
        self.carregar_imagem_fixa()
        self.atualizar_logs()
        self.atualizar_tempo()

    def configurar_estilo(self):
        """
        Configura o estilo visual da interface gráfica.

        Define cores, fontes e estilos dos componentes Tkinter,
        incluindo botões, labels, frames e campos de entrada.

        Utiliza o tema 'clam' como base.

        :return: None
        """
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure("Fundo.TFrame", background="#0f172a")
        estilo.configure("Card.TFrame", background="#1e293b")
        estilo.configure("Card.TLabelframe", background="#1e293b", foreground="#e2e8f0", bordercolor="#334155")
        estilo.configure("Card.TLabelframe.Label", background="#1e293b", foreground="#38bdf8", font=("Arial", 10, "bold"))
        estilo.configure("Titulo.TLabel", background="#0f172a", foreground="#f8fafc", font=("Arial", 22, "bold"))
        estilo.configure("Subtitulo.TLabel", background="#0f172a", foreground="#94a3b8", font=("Arial", 10))
        estilo.configure("Texto.TLabel", background="#1e293b", foreground="#e2e8f0", font=("Arial", 10))
        estilo.configure("Status.TLabel", background="#1e293b", foreground="#f8fafc", font=("Arial", 10, "bold"))
        estilo.configure("TEntry", fieldbackground="#f8fafc", foreground="#0f172a")
        estilo.configure("Iniciar.TButton", background="#22c55e", foreground="#052e16", font=("Arial", 10, "bold"), padding=8)
        estilo.map("Iniciar.TButton", background=[("active", "#16a34a"), ("disabled", "#64748b")])
        estilo.configure("Parar.TButton", background="#ef4444", foreground="#450a0a", font=("Arial", 10, "bold"), padding=8)
        estilo.map("Parar.TButton", background=[("active", "#dc2626"), ("disabled", "#64748b")])

    def criar_layout(self):
        """
        Cria e organiza todos os componentes da interface gráfica.

        Estrutura da interface:

        - Título e subtítulo
        - Formulário de entrada (nome, URL, XPath)
        - Área de imagem decorativa
        - Status do sistema (usuário e tempo)
        - Botões de controle (iniciar/parar)
        - Área de logs com rolagem

        Utiliza o gerenciador de layout 'pack' e 'grid'.

        :return: None
        """
        frame_principal = ttk.Frame(self.janela, padding=18, style="Fundo.TFrame")
        frame_principal.pack(fill="both", expand=True)

        titulo = ttk.Label(
            frame_principal,
            text="Monitor de Cotação",
            style="Titulo.TLabel"
        )
        titulo.pack(anchor="w")

        subtitulo = ttk.Label(
            frame_principal,
            text="Interface Trabalho Analise de Algoritmo",
            style="Subtitulo.TLabel"
        )
        subtitulo.pack(anchor="w", pady=(0, 14))

        frame_topo = ttk.Frame(frame_principal, style="Fundo.TFrame")
        frame_topo.pack(fill="x", pady=(0, 12))

        frame_campos = ttk.LabelFrame(frame_topo, text="Dados do monitoramento", padding=14, style="Card.TLabelframe")
        frame_campos.pack(side="left", fill="both", expand=True, padx=(0, 12))

        ttk.Label(frame_campos, text="Nome do usuário:", style="Texto.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_usuario = ttk.Entry(frame_campos)
        self.entry_usuario.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frame_campos, text="URL:", style="Texto.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_url = ttk.Entry(frame_campos)
        self.entry_url.grid(row=1, column=1, sticky="ew", pady=6)

        ttk.Label(frame_campos, text="XPath:", style="Texto.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_xpath = ttk.Entry(frame_campos)
        self.entry_xpath.grid(row=2, column=1, sticky="ew", pady=6)

        aviso_tempo = ttk.Label(
            frame_campos,
            text="Tempo máximo de monitoramento: 600s",
            style="Texto.TLabel"
        )
        aviso_tempo.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

        frame_campos.columnconfigure(1, weight=1)

        frame_imagem = ttk.LabelFrame(frame_topo, text="Imagem decorativa", padding=12, style="Card.TLabelframe")
        frame_imagem.pack(side="right", fill="both")

        self.label_imagem = tk.Label(
            frame_imagem,
            text="pablo_lancha.png",
            bg="#1e293b",
            fg="#94a3b8",
            width=200,
            height=15,
            anchor="center"
        )
        self.label_imagem.pack(fill="both", expand=True)

        frame_status = ttk.LabelFrame(frame_principal, text="Status", padding=12, style="Card.TLabelframe")
        frame_status.pack(fill="x", pady=(0, 12))

        self.label_usuario_logado = ttk.Label(frame_status, text="Usuário logado: Desconhecido", style="Status.TLabel")
        self.label_usuario_logado.pack(side="left", padx=(0, 35))

        self.label_tempo = ttk.Label(frame_status, text="Tempo buscando valor: 00:00:00", style="Status.TLabel")
        self.label_tempo.pack(side="left")

        frame_botoes = ttk.Frame(frame_principal, style="Fundo.TFrame")
        frame_botoes.pack(fill="x", pady=(0, 12))

        self.botao_iniciar = ttk.Button(
            frame_botoes,
            text="Iniciar monitoramento",
            command=self.iniciar_monitoramento,
            style="Iniciar.TButton"
        )
        self.botao_iniciar.pack(side="left", padx=(0, 8))

        self.botao_parar = ttk.Button(
            frame_botoes,
            text="Parar monitoramento",
            command=self.parar_monitoramento,
            state="disabled",
            style="Parar.TButton"
        )
        self.botao_parar.pack(side="left")

        frame_logs = ttk.LabelFrame(frame_principal, text="Logs do sistema", padding=12, style="Card.TLabelframe")
        frame_logs.pack(fill="both", expand=True)

        self.text_logs = tk.Text(
            frame_logs,
            height=15,
            wrap="word",
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#f8fafc",
            relief="flat",
            font=("Consolas", 10)
        )
        self.text_logs.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_logs, orient="vertical", command=self.text_logs.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_logs.configure(yscrollcommand=scrollbar.set)

    def carregar_imagem_fixa(self):
        """
        Carrega e exibe uma imagem decorativa na interface.

        Redimensiona automaticamente para caber no layout.

        :return: None
        """
        caminho = os.path.join(os.getcwd(), "pablo_lancha.png")

        try:
            imagem = tk.PhotoImage(file=caminho)

            largura_max = 220
            altura_max = 180
            largura = imagem.width()
            altura = imagem.height()
            fator = max(1, int(max(largura / largura_max, altura / altura_max)))

            if fator > 1:
                imagem = imagem.subsample(fator, fator)

            self.imagem_tk = imagem
            self.label_imagem.configure(image=self.imagem_tk, text="")
        except Exception:
            self.label_imagem.configure(
                text="Imagem não encontrada"
            )

    def iniciar_monitoramento(self):
        """
        Inicia o monitoramento em uma nova thread.

        Realiza:
        - Validação dos dados de entrada
        - Atualização do estado da interface
        - Criação e execução da thread de monitoramento

        :return: None
        """
        global monitoramento_ativo

        nome = self.entry_usuario.get().strip()
        url = self.entry_url.get().strip()
        xpath = self.entry_xpath.get().strip()

        if not validar_nome_interface(nome):
            messagebox.showerror("Erro", "O nome deve conter apenas letras e ter no mínimo 3 caracteres.")
            return

        if not url_valida(url):
            messagebox.showerror("Erro", "URL inválida! Tente novamente.")
            registrar_log(f"URL inválida tentada: {url}", "warning")
            return

        if not xpath_valido(xpath):
            messagebox.showerror("Erro", "XPath inválido! Tente novamente.")
            registrar_log(f"XPath inválido tentado: {xpath}", "warning")
            return

        self.label_usuario_logado.configure(text=f"Usuário logado: {nome}")
        monitoramento_ativo = True

        self.botao_iniciar.configure(state="disabled")
        self.botao_parar.configure(state="normal")

        self.thread_monitoramento = threading.Thread(
            target=executar_monitoramento_interface,
            args=(nome, url, xpath),
            daemon=True
        )
        self.thread_monitoramento.start()

    def parar_monitoramento(self):
        """
        Interrompe o monitoramento em execução.

        Atualiza o estado global e registra log da ação.

        :return: None
        """
        global monitoramento_ativo
        monitoramento_ativo = False
        registrar_log("Parada manual solicitada pelo usuário.", "warning")
        driver.quit()
        exit()
        self.botao_parar.configure(state="disabled")

    def atualizar_logs(self):
        """
        Atualiza continuamente a área de logs da interface.

        Consome mensagens da fila de logs e exibe na tela.

        :return: None
        """
        while not log_queue.empty():
            mensagem = log_queue.get()
            self.text_logs.insert("end", mensagem + "\n")
            self.text_logs.see("end")

        if not monitoramento_ativo:
            self.botao_iniciar.configure(state="normal")
            self.botao_parar.configure(state="disabled")

        self.janela.after(500, self.atualizar_logs)

    def atualizar_tempo(self):
        """
        Atualiza o tempo de execução do monitoramento na interface.

        Exibe o tempo no formato HH:MM:SS.

        :return: None
        """
        if monitoramento_ativo and inicio_monitoramento is not None:
            segundos_total = int(time.time() - inicio_monitoramento)
            horas = segundos_total // 3600
            minutos = (segundos_total % 3600) // 60
            segundos = segundos_total % 60
            self.label_tempo.configure(
                text=f"Tempo buscando valor: {horas:02d}:{minutos:02d}:{segundos:02d}"
            )
        else:
            self.label_tempo.configure(text="Tempo buscando valor: 00:00:00")

        self.janela.after(1000, self.atualizar_tempo)


# ===================== EXECUÇÃO =====================

if __name__ == "__main__":
    janela = tk.Tk()
    app = InterfaceMonitoramento(janela)
    janela.mainloop()
