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
    result_item_list, result_prod_img_src_list = [], []

    # 한 페이지에 포함된 60개 상품 iterate
    for _, item in enumerate(product_items):
        product_id = item.get('id')
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
            "product_id": product_id,
            "category": category_data["name"], 
            "price": price, 
            "base_price": base_price,
            "discount_percentage": discount_percentage,
            "img_src": replaced_src
            })

        ### TODO
        # https://www.coupang.com/vp/products/{prodcut_id}로 가서 img_src 긁어오기
        bs_obj = get_page_bs_obj(f"https://www.coupang.com/vp/products/{product_id}")

        # Thumbnail 가져오기
        prod_img_list = bs_obj.find_all('div', attrs={"class": "prod-image__item"})
        for _, prod_img in enumerate(prod_img_list):
            img_element = prod_img.find('img')
            if (img_element == -1): continue
            small_img_src = re.sub(r'^\/\/', '', img_element.get("data-src"))

            ## replace img size: 48x48ex => 492x492ex
            large_img_src = re.sub(r'48x48ex', '492x492ex', small_img_src)
            result_prod_img_src_list.append({ "product_id": product_id, "name": name, "img_src": large_img_src})

        # detail 가져오기 - deprecated
        # print(bs_obj.find('div', attrs={"class": "productDetail"}))
        # detail_img_list = bs_obj.find_all('div', attrs={"class": "type-IMAGE_NO_SPACE"}) 
        # print(detail_img_list)
        # for idx, detail_img in enumerate(detail_img_list):
        #     img_element = detail_img.find('img')
        #     if (img_element == -1): continue
        #     img_src = re.sub(r'^\/\/', '', img_element.get('src'))
        #     print(img_src)
        #     result_detail_img_src_list.append({ "product_id": product_id, "name": name, "in_page_idx": idx + 1, "img_src": img_src })
            
        #################

    return result_item_list, result_prod_img_src_list

def save_list_dict_to_file(list_dict, filename):
    print(f"saving result into {filename}...")
    df = pd.DataFrame.from_dict(list_dict)
    df.to_csv(filename, index=False, header=False)

def crawl_single_category(page_to, category_data):
    item_dict_list, img_src_dict_list = [], []
    for idx in range(1, page_to):
        print(f"crawling page... {idx}")
        item_list, img_src_list = get_item_dict_list(idx, category_data)
        item_dict_list.extend(item_list)
        img_src_dict_list.extend(img_src_list)

    save_list_dict_to_file(item_dict_list, category_data["result_filename"])
    save_list_dict_to_file(img_src_dict_list, category_data["product_img_filename"])


def run():
    category_list = [
        {"name": "과일", "category_idx": "194282", "result_filename": "fruits.csv", "product_img_filename": "fruits_prod_img.csv"},
        {"name": "채소", "category_idx": "194432", "result_filename": "vegetables.csv", "product_img_filename": "vegetables_prod_img.csv"},
        {"name": "축산/계란", "category_idx": "194688", "result_filename": "eggs.csv", "product_img_filename": "eggs_prod_img.csv"},
        {"name": "수산물/건어물", "category_idx": "194829", "result_filename": "fish.csv", "product_img_filename": "fish_prod_img.csv"},
        {"name": "과자/초콜릿/시리얼", "category_idx": "195266", "result_filename": "snack.csv", "product_img_filename": "snack_prod_img.csv"},
        {"name": "유제품/아이스크림", "category_idx": "195783", "result_filename": "dairy.csv", "product_img_filename": "dairy_prod_img.csv"},
        {"name": "반찬/간편식/대용식", "category_idx": "432480", "result_filename": "instant.csv","product_img_filename": "instant_prod_img.csv"},
        {"name": "냉장/냉동/간편요리", "category_idx": "225461", "result_filename": "frozen.csv", "product_img_filename": "frozen_prod_img.csv"},
        {"name": "생수/음료", "category_idx": "195006", "result_filename": "drinks.csv", "product_img_filename": "drinks_prod_img.csv"},
        {"name": "가루/조미료/오일", "category_idx": "195576", "result_filename": "condiment.csv", "product_img_filename": "condiment_prod_img.csv"},
        {"name": "장/소스/드레싱/식초", "category_idx": "195694", "result_filename": "sauce.csv", "product_img_filename": "sauce_prod_img.csv"},
        # {"name": "", "category_idx": "", "result_filename": ".csv"},
    ]
    end_page = 10

    for category in category_list:
        print(f"Begin Crawling { category.get('name') } 카테고리...")
        crawl_single_category(end_page + 1, category)

run()