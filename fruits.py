import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import csv

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
HEADER = {'User-Agent': USER_AGENT}
URI = "https://www.coupang.com/np/categories/194282?page="
CATEGORY = "과일"
CATEGORY_IDX = "194282"

def get_page_bs_obj(uri):
    data = requests.get(uri, headers=HEADER)
    bs_obj = BeautifulSoup(data.content, "html.parser")
    return bs_obj

def get_product_list(bs_obj):
    return bs_obj.find('ul', attrs={"class":"baby-product-list"})

def get_product_items(product_list_obj):
    return product_list_obj.find_all('li', attrs={"class": "baby-product"})

def get_item_dict_list(idx):
    page_uri = URI + str(idx)
    bs_obj = get_page_bs_obj(page_uri)
    product_list = get_product_list(bs_obj)
    product_items = get_product_items(product_list)

    num_item = len(product_items)
    result_item_list = []

    for _, item in enumerate(product_items):
        name = item.find('div', attrs={"class": "name"}).get_text().strip()
        price = item.find('strong', attrs={"class": "price-value"}).get_text().strip()
        base_price, discount_percentage = None, None

        if item.find('del', attrs={"class": "base-price"}):
            base_price = item.find('del', attrs={"class": "base-price"}).get_text().strip()
            discount_percentage = item.find('span', attrs={"class": "discount-percentage"}).get_text().strip()

        img_src = item.find('img').get("src")
        replaced_src = re.sub(r'^\/\/', '', img_src)
        
        result_item_list.append({ 
            "name": name, 
            "category": CATEGORY, 
            "price": price, 
            "base_price": base_price,
            "discount_percentage": discount_percentage,
            "img_src": replaced_src
            })

    return result_item_list


def save_item_list_dict_to_file(item_list_dict):
    df = pd.DataFrame.from_dict(item_list_dict)
    df.to_csv("fruits.csv", index=False, header=False)

def run(page_from, page_to):
    item_dict_list = []
    for idx in range(page_from, page_to):
        item_dict_list.extend(get_item_dict_list(idx))

    save_item_list_dict_to_file(item_dict_list)

run(1, 11)
