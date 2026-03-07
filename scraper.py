import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrapear_producto(url):
    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        precio_actual = None
        precio_lista = None
        promo = None

        # precio actual
        precio = soup.select_one('[class*="price"]')
        if precio:
            precio_actual = precio.text.strip()

        # precio anterior
        precio_old = soup.select_one('[class*="list"]')
        if precio_old:
            precio_lista = precio_old.text.strip()

        # promo texto
        promo_tag = soup.find(string=lambda t: "2x1" in t or "2X1" in t if t else False)
        if promo_tag:
            promo = promo_tag.strip()

        return precio_actual, precio_lista, promo

    except:
        return None, None, None


df = pd.read_excel("productos.xlsx")

resultados = []

for _, row in df.iterrows():

    producto = row["producto"]

    precio_fc, lista_fc, promo_fc = scrapear_producto(row["farmacity_url"])
    precio_fp, lista_fp, promo_fp = scrapear_producto(row["farmaplus_url"])

    resultados.append({
        "fecha": datetime.today().date(),
        "producto": producto,
        "precio_farmacity": precio_fc,
        "precio_lista_farmacity": lista_fc,
        "promo_farmacity": promo_fc,
        "precio_farmaplus": precio_fp,
        "precio_lista_farmaplus": lista_fp,
        "promo_farmaplus": promo_fp
    })


df_final = pd.DataFrame(resultados)

archivo = "comparador_precios.xlsx"

try:
    historial = pd.read_excel(archivo)
    df_final = pd.concat([historial, df_final])
except:
    pass

df_final.to_excel(archivo, index=False)

print("scraping terminado")
