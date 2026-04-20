import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from dotenv import load_dotenv

import time
import os

# testes
# url =  "https://www.uol.com.br/"
# xpath = "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

url =  "https://b3.com.br/"
xpath = '//*[@id="quotes-container"]/div/span'

# ======= FUNCTION =======
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

def enviar_email(mensagem):

    # clica no botão de escrever
    botao_escrever = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and text()="Escrever"]'))
    )
    botao_escrever.click()

    # campo do destinatario
    campo_para = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@role="combobox" and @aria-label="Destinatários"]'))
    )

    time.sleep(1)

    campo_para.send_keys('lucas.coutinho@iesb.edu.br')
    campo_para.send_keys(Keys.ENTER)

    # campo assunto
    campo_assunto = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@name="subjectbox" and @aria-label="Assunto"]'))
    )
    campo_assunto.send_keys("Alteração de preço")

    # campo corpo
    corpo = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="Corpo da mensagem"]'))
    )
    corpo.send_keys(mensagem)

# ======= MAIN ===========
# load_dotenv()
# gmail = os.getenv("GMAIL")
# senha = os.getenv("SENHA")

#url = input("Digite o URL: ")
#xpath = input("Digite o Xpath: ")

# CONFIGURAÇÂO DO DRIVER DE NAVEGAÇÂO

# options
options = Options()
profile_path = os.path.abspath("edge_selenium_profile")
options.add_argument(f"user-data-dir={profile_path}")
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
# services
service = Service(executable_path="msedgedriver.exe")
# driver
driver = webdriver.Edge(service=service, options=options)



# MINERAÇÂO / LOOP PRINCIPAL

driver.get(url)
original_tab = driver.current_window_handle

valor_antigo = encontrar_elemento(driver, xpath).text
print(f"Cotação capturada: {valor_antigo}")

while True:
    valor_novo = encontrar_elemento(driver, xpath).text
    
    if valor_novo != valor_antigo:
        print(f"O cotação mudou para: {valor_novo}")
        break
    
    print("O valor ainda é o mesmo. Aguardando...")
    time.sleep(10)



# driver.switch_to.window(original_tab) 
# time.sleep(3) 
# driver.switch_to.window(driver.window_handles[1])


# EMAIL

mensagem = f"""O valor antigo era: {valor_antigo}

O novo valor é: {valor_novo}

--
A disposição,

Agente Autônomo
"""

driver.switch_to.new_window('tab')
driver.get("https://gmail.com")

enviar_email(mensagem)

time.sleep(100)

driver.quit()