from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import re
from bs4 import BeautifulSoup
import sqlite3

infile = open("input.txt", "r")
outfile = open('output.csv', 'w', newline='')
fileWriter = csv.writer(outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

SKU_Quantity = 10

for aline in infile:
    values = aline.split('\t')
    try:

        blID = values[0]
        elementID = ""
        partName = ""
        partColor = ""
        partQty = 0

        if len(values) > 1:
            elementID = values[1]
            partName = values[2]
            partColor = values[3]
            partQty = int(values[4].rstrip())

        lotCount = partQty//SKU_Quantity
        if partQty%SKU_Quantity > 0:
            lotCount = lotCount + 1
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        reg_url = "https://www.vonado.com/catalogsearch/result/?q=" + blID
        req = Request(url=reg_url, headers=headers) 
        html = urlopen(req)

    except HTTPError as e:

        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print(f"{blID} : Server down or incorrect domain")

    else:

        res = BeautifulSoup(html.read(),"html5lib")

        tags = res.findAll("div", {"class": "message notice"})
        
        if len(tags) > 0:
            print(f"{blID} - {elementID} - {partName} : Part not found")
            fileWriter.writerow([blID, elementID, partName, partColor, partQty, lotCount])
        else:
            tags = res.findAll("a", {"class": ["product photo product-item-photo"]})
            if len(tags) > 0:
                found = False

                for tag in tags:
                    link = tag['href']
                    if re.search(f"-{blID}[\.\-]", link, re.IGNORECASE):
                        if "moc" not in link:
                            found = True
                            print(f"{blID} : {link}")

                            req2 = Request(url=link, headers=headers) 
                            html2 = urlopen(req)
                            res2 = BeautifulSoup(html2.read(),"html5lib")

                            price_tag = res2.find("span", {"class": "price-wrapper"})
                            unit_price = float(price_tag['data-price-amount'])
                            total_price = lotCount * unit_price
                            
                            fileWriter.writerow([blID, elementID, partName, partColor, partQty, lotCount, unit_price, total_price, link])

                if not found:
                    print(f"{blID} - {elementID} - {partName} : Part not found")
                    fileWriter.writerow([blID, elementID, partName, partColor, partQty, lotCount])

infile.close()
outfile.close()

