#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@created: 21.03.2016
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com

import os
import re
import urllib2
import math
import time
# from lxml import html
# from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def find_item(regexp, source):
    item = re.findall(regexp, source, re.S)
    if item:
        return item[0]
    return ""

def scrap_streets(settings):
    '''
    '''
    results = []
    with open(settings["streets_file"], "w") as fh:

        page_url = settings["streets_page"]
        print(page_url)
        try:
            # page = urllib2.urlopen(page_url).read().decode("windows-1251")
            
            driver.get(page_url)
            page = driver.page_source
            driver.close()
        except:
            print("No such page")
            return []
        data = re.findall("\[\"(.*?)\",(\d+),(\d+)\]", page, re.S|re.M)
          
        for x in data:
            s = "%s\t%s\t%s\n" % (x[0], x[1], x[2])
            fh.write(s.encode("utf-8"))
            results.append((x[0].encode("utf-8"), int(x[1]), int(x[2])))
    return results


def check_expected(page, street_name):
    _street_name = street_name.replace("(", "\(")
    _street_name = _street_name.replace(")", "\)")
    _street_name = _street_name.replace(".", "\.")
    items = re.findall("<div class=\"cssHouseHead\">(.*?)<!-- cssHousehead -->", page, re.S|re.M)
    raw_items = items[::]
    if not street_name in ["Жертв революции пл."]:
        items = [x for x in items if street_name.lower() in x.lower()]
    items = list(set(items))
    rg = "title.>.*?%s.*?(\d+) до.*?</div>" % _street_name
    n_items = find_item(rg, page)
    if street_name in ["Пулковское отд. пос. Шушары"]:
        return True
    if not n_items:
        print rg
        print "Please, manually check page w/o hits"
        # raw_input("Please, manually check page w/o hits")
        return False
    if not items:
        print raw_items
    print "Found:", len(items), "expected", n_items
    if "линия ВО" in street_name and len(items)-int(n_items) < 3:
        return True
    if len(items)-int(n_items) < 2:
        return True
    if not n_items or len(items) != int(n_items):
        # raw_input("Not equal!")
        return False
    return True


def parse(page, results, fh):

    items = re.findall("<div class=\"cssHouseHead\">(.*?)<!-- cssHousehead -->", page, re.S|re.M)
    items = list(set(items))

    print "Parsed and found:", len(items)
    for item in items:

        address = find_item("<div class=\"address\">(.*?)</div>", item).split('<br>')

        address = [x for x in address if "<" in x]

        address = [re.sub("<.*?>", "", x, re.S|re.M) for x in address]
        authors = find_item("Архитекторы\:</td>(.*?)</tr>", item)

        # print authors

        authors = re.findall("<a href=\"(.*?)\">(.*?)</a>", authors, re.S|re.M)

        # print authors

        # raw_input("?")


        build_year = find_item("Год постройки\:</td>(.*?)</tr>", item)
        build_year = find_item(">(.*?)</td>", build_year)

        style = find_item("Стиль\:</td>(.*?)</tr>", item)
        style = re.sub("<.*?>", " ", style, re.S|re.M)
        style = re.sub("\s+", " ", style, re.S|re.M)
        style = style.strip()

        views = find_item("<a class=\"imb_eye\".*?>(\d+)</a>", item)
        comments = find_item("<a class=\"imb_comm\".*?>(\d+)</a>", item)
        link = find_item("<a class=\"imb_more\".*?href=\"(.*?)\"", item)
        link = link.split("?")[0]

        title = find_item("<h2>(.*?)</h2>", item)
        title = re.sub("<.*?>", " ", title, re.S|re.M)
        title = re.sub("\s+", " ", title, re.S|re.M)
        title = title.strip()

        title = re.sub("&quot;", '"', title)

        r = {
            "title": title,
            "image": find_item("><img src=\"(.*?)\?", item),
            "address": address,
            "authors_links": [x[0] for x in authors],
            "authors_names": [x[1] for x in authors],
            "build_year": build_year,
            "style": style,
            "views": views,
            "comments": comments,
            "link": link,
        }

        for address in r["address"][::]:

            address = address

            print address

            street, home = address.split(",")

            data = [
                r["title"], 
                r["image"], 
                address, 
                street.strip(),
                home.strip(),
                ",".join(r["authors_links"]), 
                ",".join(r["authors_names"]),
                r["build_year"],
                r["style"],
                r["views"],
                r["comments"],
                r["link"],
            ]

            results.append(data)

            fh.write("%s\n" % "\t".join(data))
    return results




def scrap_street(settings, sid, fh):
    '''
    '''
    results = []

    dump_fh = open("data%s.html" % sid, "a")
       
    page_url = settings["street_page"] % (sid, 1)
    print(page_url)
    try:
        # page = urllib2.urlopen(page_url).read().decode("windows-1251").encode("utf-8")
        # page = opener.open(page_url).read().decode("windows-1251").encode("utf-8")
        driver.get(page_url)
        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#m_footer")))
        page = driver.page_source.encode("utf-8")
        assert page
        dump_fh.write(page)
        # driver.close()

    except Exception, e:
        print e
        raw_input("No such page")
        dump_fh.close()
        return results

    results = parse(page, results, fh)

    n_items = find_item("<div class=\"title\">.*?(\d+) до.*?</div>", page)
    
    if n_items:
        pages = int(math.ceil(1.*int(n_items)/10))
    else:
        pages = 1

    if pages == 1:
        dump_fh.close()
        return results

    for page in xrange(2,pages+1):
        page_url = settings["street_page"] % (sid, page)
        print page_url
        try:
            # page = urllib2.urlopen(page_url).read().decode("windows-1251").encode("utf-8")
            # page = opener.open(page_url).read().decode("windows-1251").encode("utf-8")
            
            driver.get(page_url)
            time.sleep(5)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#m_footer")))

            page = driver.page_source.encode("utf-8")
            assert page
            # driver.close()

            dump_fh.write(page)
        except Exception, e:
            print e
            raw_input("No such page")

        results = parse(page, results, fh)
    
    dump_fh.close()
    return results
    

def my_proxy(PROXY_HOST,PROXY_PORT,driver_path):
    fp = webdriver.FirefoxProfile()
    # Direct = 0, Manual = 1, PAC = 2, AUTODETECT = 4, SYSTEM = 5
    print PROXY_PORT
    print PROXY_HOST
    fp.set_preference("network.proxy.type", 1)
    fp.set_preference("network.proxy.http",PROXY_HOST)
    fp.set_preference("network.proxy.http_port",int(PROXY_PORT))
    fp.set_preference("general.useragent.override","whater_useragent")
    fp.update_preferences()
    return  webdriver.PhantomJS(executable_path=driver_path, firefox_profile=fp)

if __name__ == '__main__':

    settings = {
        "streets_page": "http://www.citywalls.ru/select_street.html",
        "street_page": "http://www.citywalls.ru/search-street%s-page%s.html",
        "streets_file": "streets.txt",
        "houses_file": "houses.txt",
    }

    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    driver_path = "/Users/akomissarov/Downloads/phantomjs-1.9.8-macosx/bin/phantomjs"
    driver_path = "/home/akomissarov/libs/phantomjs/bin/phantomjs" #  --proxy=:8080

    PROXY_HOST = '221.178.181.107'
    PROXY_PORT = 80

    service_args = [
#        '--proxy=%s:%s' % (PROXY_HOST, PROXY_PORT),
 #       '--proxy-type=HTTP',
    ]

    # driver = my_proxy(PROXY_HOST,PROXY_PORT,driver_path)
    # driver = webdriver.PhantomJS(executable_path=driver_path, service_args=service_args)


    if not os.path.isfile(settings["streets_file"]):
        results = scrap_streets(settings)
    else:
        with open(settings["streets_file"]) as fh:
            results = [x.strip().split("\t") for x in fh]

    os.unlink("houses.txt")
    with open("houses.txt", "w") as fh:
        fh.write("%s\n" % "\t".join(["title", "image", "address", "street", "home", "authors_links", "authors_names", "build_year", "style", "views", "comments", "link"]))

    i = 0
    while results:
        street_name, sid, x = results.pop(0)
        i += 1
        file_name = "data%s.html" % sid
        if not os.path.isfile(file_name) or os.stat(file_name).st_size == 0:
            print "No such file"
            print i, street_name, "total:", len(results), file_name
            with open(settings["houses_file"], "a") as fh:
                scrap_street(settings, sid, fh)
            results.insert(0, [street_name, sid, x])
        else:
            print "File found"
            print i, street_name, "total:", len(results), "SKIPPED", file_name
            with open(file_name) as fh:
                page = fh.read()
            if check_expected(page, street_name):
                with open(settings["houses_file"], "a") as fh:
                    parse(page, [], fh)
            else:
                # exit()
                print i, street_name, "total:", len(results), file_name, "RETAKE"
                os.unlink(file_name)
                with open(settings["houses_file"], "a") as fh:
                    scrap_street(settings, sid, fh)
                results.insert(0, [street_name, sid, x])
        
