#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import requests
from bs4 import BeautifulSoup

ryogoID = "20ECA17OGAV5O"
baseURL = "https://www.amazon.co.jp"

desc = 'Amazonの欲しいものリストからセール中の本をリストアップするスクリプト'
parser = argparse.ArgumentParser(description = desc)
parser.add_argument('--wishlist_id',
                    default = ryogoID,
                    help = '欲しいものリストのID')
parser.add_argument('--discount_ratio',
                    type = int,
                    default = 20,
                    help = '最低値下げ率．この値以下の本は表示しない')
opts = parser.parse_args()


next_ref = "/wishlist/" + opts.wishlist_id

while next_ref is not None:
    res = requests.get(baseURL + next_ref)
    if res.status_code != 200:
        print("Error? -- Status Code = {}".format(res.status_code))
        # TODO: We should retry here.
        break
    
    tree = BeautifulSoup(res.content, 'lxml')
    book_elms = tree.find_all('li', class_="a-spacing-none g-item-sortable")

    for elm in book_elms:
        price_drop = elm.find('div', class_="a-row itemPriceDrop")
        if price_drop is None:
            continue
        
        drop_rate = price_drop.find('span', class_="a-text-bold").string.strip()
        # '価格がdd%下がりました'のdd. つまり，4文字目から%までの数字文字列
        dd_ratio = int(drop_rate[3: drop_rate.find('%', 3)])
        if dd_ratio < opts.discount_ratio:
            continue
        
        book_info = elm.find('a', class_="a-link-normal")
        price = elm.find('span', class_="a-offscreen").string
        title = book_info['title']
        url   = baseURL + book_info['href']

        txt_out = "{} ==>>\n\tprice = {}\n\ttitle = {}\n\tURL   = {}"
        print(txt_out.format(drop_rate, price, title, url))

    see_cls = "a-size-base a-link-nav-icon a-js g-visible-no-js wl-see-more"
    see_more = tree.find('a', class_=see_cls)
    if see_more is None: # no more books in the wishlist.
        break
    next_ref = see_more['href']

print("\n\nchecking wishlist done.")
