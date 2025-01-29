import pandas as pd
from bs4 import BeautifulSoup
import requests

#no full products page so diffrent varble for every link 
main_url = "https://www.mysimplynatural.com/product-category/"
cbd_url = main_url + "hemp-cbd/"
crystal_url = main_url + "crystals/"
oils_url = main_url + "essential-oils"
body_url = main_url + "body-products/"
foods_url = main_url + "food-drink/"
wellness_url = main_url + "health/"
pets_url = main_url + "pet-products/"

headers = {
    'User-Agent':"Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 8.12; MSIEMobile6.0)"}

#data frame
df = pd.DataFrame()

#funtion to collect and sort all data and appened it to the csv file
def collect_data(url):
    r = requests.get(url, headers= headers)
    soup = BeautifulSoup(r.content, "html.parser")
    #getting all products to be used in for loop for price and name
    products = soup.find_all("li", class_="product")
    #couldnt find better way to add the products 
    # used this data varble to append name and price
    #then add data varble into the data frame
    data =[]
    #for loop for all products
    for product in products:
            name = product.find("h2", class_="woocommerce-loop-product__title").text.strip()
            price = product.find("span", class_="woocommerce-Price-amount").text.strip()
            data.append([name, price])
            df = pd.DataFrame(data, columns=["Product Name", "Price"])
            df.to_csv("Items_price.csv", mode='a', index=False, header=False)
    
    
#running the funtion across all urls    
collect_data(cbd_url)
collect_data(crystal_url)
collect_data(oils_url)
collect_data(body_url)
collect_data(foods_url)
collect_data(wellness_url)
collect_data(pets_url)