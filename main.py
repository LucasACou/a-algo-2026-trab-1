import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from dotenv import load_dotenv

from urllib.parse import urlparse
from lxml import etree

import time
import os

# testes
# url =  "https://www.uol.com.br/"
# xpath = "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

# url =  "https://b3.com.br/"
# xpath = '//*[@id="quotes-container"]/div/span'

# url = https://br.investing.com/currencies/usd-brl
# xpath = //div[@data-test='instrument-price-last']

# ======= FUNCTION =======

def url_valida(url):
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except:
        return False
    
def pedir_url():
    while True:
        url = input("Digite o URL: ").strip()
        
        if url_valida(url):
            return url
        else:
            print("URL inválida! Tente novamente.\n")

def xpath_valido(xpath):
    if not xpath or not xpath.startswith("//"):
        return False
    try:
        etree.XPath(xpath)
        return True
    except:
        return False

def pedir_xpath():
    while True:
        xpath = input("Digite o XPath: ").strip()

        if xpath_valido(xpath):
            return xpath
        else:
            print("XPath inválido! Tente novamente.\n")

def encontrar_elemento(driver, xpath):
    # 1. tenta direto
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except:
        pass

    # 2. tenta em iframes
    iframes = driver.find_elements(By.TAG_NAME, "iframe")

    for iframe in iframes:
        driver.switch_to.frame(iframe)
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except:
            driver.switch_to.default_content()

    return None

def salvar_elementos(mensagem):

    # seleciona o input de escrever
    input_escrever = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//textarea[@name="my-textarea"]'))
    )
    input_escrever.send_keys(mensagem)

    time.sleep(5)

    # clica no botao de salvar
    botao_salvar = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    botao_salvar.click()


# ======= MAIN ===========
url = pedir_url()
print("URL válida:", url)

xpath = pedir_xpath()
print("XPath válido:", xpath)

# CONFIGURAÇÂO DO DRIVER DE NAVEGAÇÂO ==============================================
# options
options = Options()
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
# services
service = Service(executable_path="msedgedriver.exe")
# driver
driver = webdriver.Edge(service=service, options=options)

# MINERAÇÂO / LOOP PRINCIPAL =======================================================

driver.get(url)
original_tab = driver.current_window_handle

elemento = encontrar_elemento(driver, xpath)
if not elemento.text or not elemento.text.strip():
    print("Elemento não encontrado ou sem texto!")
    driver.quit()
    exit()

valor_antigo = elemento.text
print(f"Cotação capturada: {valor_antigo}")

mudou = False
tempo_max = 600 # 10 minutos executando
inicio = time.time()

while True:

    if time.time() - inicio > tempo_max:
        print("Monitoramento encerrado por segurança.")
        break

    elemento = encontrar_elemento(driver, xpath)

    if elemento is None:
        print("Elemento não encontrado durante execução!")
        break

    valor_novo = elemento.text

    if not valor_novo:
        print("Elemento sem texto!")
        break

    if valor_novo != valor_antigo:
        print(f"A cotação mudou para: {valor_novo}")
        mudou = True
        break
    
    print("O valor ainda é o mesmo. Aguardando...")
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
    print("Nenhuma mudança detectada. Nada foi salvo.")

time.sleep(10)

driver.quit()