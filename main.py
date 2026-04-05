import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time 

url = "https://www.uol.com.br/"
x_path = "//a[@title='Dólar']//span[contains(@class,'exchangeBarHeader__item__value')]"

service = Service(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service)

driver.get(url)

element = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(
        (By.XPATH, x_path)
    )
)

# depois de visível, pega o texto
valor = element.text
print("Cotação capturada:", valor)


time.sleep(10)

driver.quit()