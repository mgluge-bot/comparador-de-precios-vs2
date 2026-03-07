import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

productos = [
    {
        "nombre": "Nivea Sun Tono Medio",
        "farmacity": "https://www.farmacity.com/protector-solar-nivea-sun-tono-medio-fps-50-x-40-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/protector-solar-facial-nivea-sun-ultra-light-daily-fluid-tono-medio-fps-50--para-todo-tipo-de-piel-x-40-ml/p"
    },
    {
        "nombre": "Vichy Capital Soleil",
        "farmacity": "https://www.farmacity.com/aceite-solar-invisible-vichy-capital-soleil-cell-protect-spf-50-x-200-ml/p",
        "farmaplus": "https://www.farmaplus.com.ar/vichy-capital-soleil-oil-invisible-cell-protect-spf50-200ml/p"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0"
}
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 15)

def precio_farmacity(url):
    try:
        driver.get(url)

        precio = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".vtex-product-price-1-x-sellingPriceValue")
            )
        )

        return precio.text, "NA"

    except:
        return "NA", "NA"

def precio_farmaplus(url):
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        texto = soup.get_text()

        precios = re.findall(r"\$\s?[\d\.]+", texto)

        precio = precios[0] if len(precios) > 0 else "NA"
        lista = precios[1] if len(precios) > 1 else "NA"

        return precio, lista
    except:
        return "NA", "NA"


data = []

for p in productos:

    pf, lf = precio_farmacity(p["farmacity"])
    pp, lp = precio_farmaplus(p["farmaplus"])

    data.append({
        "fecha": datetime.date.today(),
        "producto": p["nombre"],
        "precio_farmacity": pf,
        "lista_farmacity": lf,
        "precio_farmaplus": pp,
        "lista_farmaplus": lp
    })

driver.quit()

df = pd.DataFrame(data)

df.to_csv("precios.csv", mode="a", index=False, header=not pd.io.common.file_exists("precios.csv"))
