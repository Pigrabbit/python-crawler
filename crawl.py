import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
HEADER = {'User-Agent': USER_AGENT}
URI = "https://www.coupang.com/np/categories"

def get_page_bs_obj(uri):
    data = requests.get(uri, headers=HEADER)
    bs_obj = BeautifulSoup(data.content, "html.parser")
    return bs_obj

def get_product_list(bs_obj):
    return bs_obj.find('ul', attrs={"class":"baby-product-list"})

def get_product_items(product_list_obj):
    return product_list_obj.find_all('li', attrs={"class": "baby-product"})

def get_item_dict_list(page_idx, category_data):
    category_idx = category_data["category_idx"]
    page_uri = f"{URI}/{category_idx}?page={str(page_idx)}"

    bs_obj = get_page_bs_obj(page_uri)
    product_list = get_product_list(bs_obj)
    product_items = get_product_items(product_list)

    num_item = len(product_items)
    result_item_list = []

    for _, item in enumerate(product_items):
        name = item.find('div', attrs={"class": "name"}).get_text().strip()
        price = item.find('strong', attrs={"class": "price-value"}).get_text().strip()

        ### Check if item is on Discount
        base_price, discount_percentage = None, None
        if item.find('del', attrs={"class": "base-price"}) and item.find('span', attrs={"class": "discount-percentage"}):
            base_price = item.find('del', attrs={"class": "base-price"}).get_text().strip()
            discount_percentage = item.find('span', attrs={"class": "discount-percentage"}).get_text().strip()

        img_src = item.find('img').get("src")
        replaced_src = re.sub(r'^\/\/', '', img_src)
        
        result_item_list.append({ 
            "name": name, 
            "category": category_data["name"], 
            "price": price, 
            "base_price": base_price,
            "discount_percentage": discount_percentage,
            "img_src": replaced_src
            })

    return result_item_list

def save_item_list_dict_to_file(item_list_dict, filename):
    print(f"saving result into {filename}...")
    df = pd.DataFrame.from_dict(item_list_dict)
    df.to_csv(filename, index=False, header=False)

def crawl_single_category(page_to, category_data):
    item_dict_list = []
    for idx in range(1, page_to):
        print(f"crawling page... {idx}")
        item_dict_list.extend(get_item_dict_list(idx, category_data))

    save_item_list_dict_to_file(item_dict_list, category_data["result_filename"])


def run():
    category_list = [
        {"name": "과일", "category_idx": "194282", "result_filename": "fruits.csv"},
        {"name": "채소", "category_idx": "194432", "result_filename": "vegetables.csv"},
        {"name": "축산/계란", "category_idx": "194688", "result_filename": "eggs.csv"},
        {"name": "수산물/건어물", "category_idx": "194829", "result_filename": "fish.csv"},
        {"name": "과자/초콜릿/시리얼", "category_idx": "195266", "result_filename": "snack.csv"},
        {"name": "유제품/아이스크림", "category_idx": "195783", "result_filename": "dairy.csv"},
        {"name": "반찬/간편식/대용식", "category_idx": "432480", "result_filename": "instant.csv"},
        {"name": "냉장/냉동/간편요리", "category_idx": "225461", "result_filename": "frozen.csv"},
        {"name": "생수/음료", "category_idx": "195006", "result_filename": "drinks.csv"},
        {"name": "가루/조미료/오일", "category_idx": "195576", "result_filename": "condiment.csv"},
        {"name": "장/소스/드레싱/식초", "category_idx": "195694", "result_filename": "sauce.csv"},
        # {"name": "", "category_idx": "", "result_filename": ".csv"},
    ]
    end_page = 10

    for category in category_list:
        print(f"Begin Crawling {category.name} 카테고리...")
        crawl_single_category(end_page + 1, category)

run()