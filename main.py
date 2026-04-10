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

#"https://www.uol.com.br/"
# "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

# testes
url =  "https://b3.com.br/"
xpath = '//*[@id="quotes-container"]/div/span/span'




# ======= functions =======
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





# ======= main =======
load_dotenv()
gmail = os.getenv("GMAIL")
senha = os.getenv("SENHA")

#url = input("Digite o URL: ")
#xpath = input("Digite o Xpath: ")

service = Service(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service)

#url de mineração
driver.get(url)
original_tab = driver.current_window_handle

#mineração dos dados
element = encontrar_elemento(driver, xpath)
valor = element.text
print("Cotação capturada:", valor)


driver.switch_to.new_window('tab')
driver.get("https://gmail.com")

input_element = driver.find_element(By.XPATH, '//*[@id="identifierId"]')
input_element.send_keys(gmail + Keys.ENTER)



time.sleep(100)

driver.quit()