import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 

# "https://www.uol.com.br/"
# "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

# testes
# "https://b3.com.br/"
# "//*[@id="quotes-container"]/div/span/span"

# == functions ==
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

# == main ==
url = input("Digite o URL: ")
xpath = input("Digite o Xpath: ")

service = Service(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service)

driver.get(url)

element = encontrar_elemento(driver, xpath)

valor = element.text
print("Cotação capturada:", valor)

time.sleep(10)

driver.quit()