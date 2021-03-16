from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import re
from bs4 import BeautifulSoup
from detect_delimiter import detect

infile = open("input.txt", "r")
outfile = open('output.txt', 'w', newline='')

SKU_Quantity = 10

firstline = infile.readline()

delim = detect(firstline)

if delim is None:
    delim = ','

fileWriter = csv.writer(outfile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)

headers = firstline.split(delim)

columncount = len(headers)

# Get rid of the linefeed at the end
headers[columncount-1] = headers[columncount-1].rstrip()

if columncount == 1:
    headers.append("Color")
    headers.append("Quantity")

headers.append("lotCount")
headers.append("unit_price")
headers.append("total_price")
headers.append("link")

fileWriter.writerow(headers)

for aline in infile:
    values = aline.split(delim)
    try:

        blID = values[0].rstrip()
        partColor = "0"
        partQty = 0

        if len(values) > 1:
            partColor = values[1]
            partQty = int(values[2].rstrip())

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
            print(f"{blID} : Part not found")
            fileWriter.writerow([blID, partColor, partQty])
        else:
            tags = res.findAll("a", {"class": ["product photo product-item-photo"]})
            if len(tags) > 0:
                found = False

                for tag in tags:
                    link = tag['href']
                    if re.search(f"-{blID}[\.\-]", link, re.IGNORECASE):
                        if "moc" not in link:
                            found = True
                            lotCount = partQty//SKU_Quantity

                            if partQty%SKU_Quantity > 0:
                                lotCount = lotCount + 1

                            print(f"{blID} : {link}")

                            req2 = Request(url=link, headers=headers) 
                            html2 = urlopen(req)
                            res2 = BeautifulSoup(html2.read(),"html5lib")

                            price_tag = res2.find("span", {"class": "price-wrapper"})
                            unit_price = float(price_tag['data-price-amount'])
                            total_price = lotCount * unit_price
                            
                            fileWriter.writerow([blID, partColor, partQty, lotCount, unit_price, total_price, link])

                if not found:
                    print(f"{blID} : Part not found")
                    fileWriter.writerow([blID, partColor, partQty])

infile.close()
outfile.close()

