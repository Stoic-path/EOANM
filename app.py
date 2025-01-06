import os #para trabajar con archivos y carpetas del sistema operativo
import re #for transformar los nombres de los productos y guardarlos sin q me mande error
from datetime import datetime #guardar fechas
import pandas as pd # for poder trabajar con excel
import requests #for hacer solicitudes a un pagina web, amazon
from bs4 import BeautifulSoup # For webscraping
import streamlit as st #Our GUI

#pip install pip install pandas requests beautifulsoup4 streamlit openpyxl lxml

def get_product_info(url):
    headers = {
        #Indica al servidor la información sobre el navegador y el ordenador que supuestamente estamos usando,xq servers validan el user
        #agent para verificar q no es un bot.
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9'
    }



    response = requests.get(url, headers=headers) #obtengo html
    soup = BeautifulSoup(response.text, 'lxml') #parseo html

    try:
        title = soup.find(id='productTitle').get_text(strip=True)
    except AttributeError:
        title = 'No title found'

    try:
        image_url = soup.find(id='landingImage')['src']
    except (AttributeError, TypeError):
        image_url = 'None'

    try:
        price = soup.find('span', {'class': 'a-price-whole'}).get_text(strip=True)


    except(AttributeError, TypeError):
        price = 'No price found'

    return title, image_url, price

def save_image(image_url, product_name):
    folder = "busquedas"
    os.makedirs(folder, exist_ok=True)

    valid_filename = re.sub(r'[<>:/\\|?*]', '', product_name)
    valid_filename = valid_filename[:10]
    filepath = os.path.join(folder, valid_filename + '.jpg')

    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1

    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filepath
    return None

def save_to_excel(data):
    df = pd.DataFrame(data)
    file_name = f"busquedas.xlsx"

    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        df = pd.concat([existing_df, df],ignore_index=True)

    df.to_excel(file_name, index=False)
    return file_name

def get_search_result(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9'
    }

    urlAmazon = f"https://www.amazon.com/s?k={query}"
    response = requests.get(urlAmazon, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml') #Convertir una cadena de texto en una estructura que un programa puede manejar

    product_links = []
    for link in soup.find_all('a', {'class': 'a-link-normal s-no-outline'}, href=True):
        product_links.append("https://www.amazon.com" + link['href'])
    return product_links




#Streamlit App
st.title("Scraper de productos de Amazon")

search_query = st.text_input("Introduce tu búsqueda en Amazon:")

if search_query:
    st.write(f"Resultados para: {search_query}")
    product_urls = get_search_result(search_query)

    if product_urls:
        all_data = []
        for url in product_urls[:10]:
            title, image_url, price = get_product_info(url)

            if title != 'No title found':
                data = {
                    'Fecha': datetime.now().strftime('%Y-%m-%d'),
                    'Titulo': title,
                    'Precio': price,
                    'URL Imagen': image_url,
                    'URL Producto': url
                }

                all_data.append(data)

                if image_url:
                    save_image(image_url, title)


        if all_data:
            df = pd.DataFrame(all_data)
            st.write("### Información de los productos:")
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
                [{'selector':'th', 'props' : [('text-align', 'left')]}]
            ))

            #Guardar los datos en Excel
            file_name = save_to_excel(all_data)
            st.success(f"### Datos guardados en: {file_name}")
        else:
            st.error("No se encontraron productos válidos.")
    else:
        st.error("No se encontrarorn resultados para tu búsqueda")






