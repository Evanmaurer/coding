import pandas as pd
from bs4 import BeautifulSoup
import requests
#no full products page so my diffrent varble for every link 
main_url = "https://www.mysimplynatural.com/product-category/"
cbd_url = main_url + "hemp-cbd/"
crystal_url = main_url + "crystals/"
oils_url = main_url + "essential-oils"
body_url = main_url + "body-products/"
foods_url = main_url + "food-drink/"
wellness_url = main_url + "health/"
pets_url = main_url + "pet-products/"

#setting DataFrame to export to exile file  
file_name = "Items_price.csv"

headers = {
    'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 8.12; MSIEMobile6.0)"
}
df = pd.DataFrame()
def collect_data(url):
    r = requests.get(url, headers= headers)
    soup = BeautifulSoup(r.content, "html.parser")
    products = soup.find_all("li", class_="product")
    data =[]
    for product in products:
            name = product.find("h2", class_="woocommerce-loop-product__title").text.strip()
            price = product.find("span", class_="woocommerce-Price-amount").text.strip()
            data.append([name, price])
            df = pd.DataFrame(data, columns=["Product Name", "Price"])
            df.to_csv("Items_price.csv", mode='a', index=False, header=False)
    
collect_data(cbd_url)
collect_data(crystal_url)
collect_data(oils_url)
collect_data(body_url)
collect_data(foods_url)
collect_data(wellness_url)
collect_data(pets_url)