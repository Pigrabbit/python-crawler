import requests
from bs4 import BeautifulSoup

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
HEADER = {'User-Agent': USER_AGENT}
URI = "https://www.coupang.com/np/categories/194282?page="

def get_page_bs_obj(uri):
    data = requests.get(uri, headers=HEADER)
    bs_obj = BeautifulSoup(data.content, "html.parser")
    return bs_obj

def get_product_list(bs_obj):
    return bs_obj.find('ul', attrs={"class":"baby-product-list"})

def get_product_items(product_list_obj):
    return product_list_obj.find_all('li', attrs={"class": "baby-product"})

def crawl_single_page(idx):
    page_uri = URI + str(idx)
    bs_obj = get_page_bs_obj(page_uri)
    product_list = get_product_list(bs_obj)
    prodcut_items = get_product_items(product_list)
    print(len(prodcut_items))

    return []

idx = list(range(1, 11))

for i in idx:
    crawl_single_page(i)
