from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import re
from bs4 import BeautifulSoup
from detect_delimiter import detect
import argparse
import xml.etree.cElementTree as ET

def isXML(file_name):
    try:
       tree = ET.ElementTree(file=file_name)
       return True

    except ET.ParseError as e:
       return False

def getHeaders(firstline, delim):
    if len(firstline) == 0:
        headers = ["Part"]
        headers.append("Color")
        headers.append("Qty")
        headers.append("lots")
        headers.append("unit")
        headers.append("total")
        headers.append("link")
    else:
        headers = firstline.split(delim)

        columncount = len(headers)

        # Get rid of the linefeed at the end
        headers[columncount-1] = headers[columncount-1].rstrip()

        if columncount == 1:
            headers.append("Color")
            headers.append("Qty")

        headers.append("lots")
        headers.append("unit")
        headers.append("total")
        headers.append("link")

    return headers

def getPartInfo(partID, partColor, partQty):
    partInfo = []
    # [partID, partColor, partQty, lotCount, unit_price, total_price, link]

    SKU_Quantity = 10

    partInfo.append(partID)
    partInfo.append(partColor)
    partInfo.append(partQty)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
        reg_url = "https://www.vonado.com/catalogsearch/result/?q=" + partID
        req = Request(url=reg_url, headers=headers) 
        html = urlopen(req)

    except HTTPError as e:

        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print(f"{partID} : Server down or incorrect domain")

    else:
        res = BeautifulSoup(html.read(),"html5lib")

        tags = res.findAll("div", {"class": "message notice"})
        
        if len(tags) == 0:
            tags = res.findAll("a", {"class": ["product photo product-item-photo"]})
            if len(tags) > 0:
                found = False

                for tag in tags:
                    link = tag['href']
                    if re.search(f"-{partID}[\.\-]", link, re.IGNORECASE):
                        if "moc" not in link:
                            found = True
                            lotCount = partQty//SKU_Quantity

                            if partQty%SKU_Quantity > 0:
                                lotCount = lotCount + 1

                            req2 = Request(url=link, headers=headers) 
                            html2 = urlopen(req)
                            res2 = BeautifulSoup(html2.read(),"html5lib")

                            price_tag = res2.find("span", {"class": "price-wrapper"})
                            unit_price = float(price_tag['data-price-amount'])
                            total_price = lotCount * unit_price

                            partInfo.append(lotCount)
                            partInfo.append(unit_price)
                            partInfo.append(total_price)
                            partInfo.append(link)

    return partInfo

def reportResults(partinfo):
    if len(partinfo) == 3:
        print(f"{partinfo[0]} : Part not found")
    else:
        print(f"{partinfo[0]} : {partinfo[-1]}")

def processFile(file_name):
    outfile = open('output.txt', 'w', newline='')

    firstline = ""

    delim = '\t'
    
    if isXML(file_name):
        firstline = ""
    else:
        infile = open(file_name, "r")
        firstline = infile.readline()

        delim = detect(firstline)

        if delim is None:
            delim = ','

    headers = getHeaders(firstline, delim)

    fileWriter = csv.writer(outfile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    fileWriter.writerow(headers)

    
    if isXML(file_name):
        tree = ET.ElementTree(file=file_name)
        root = tree.getroot()

        # get the information via the children!
        for part in root.findall('ITEM'):
            partID = part.find('ITEMID').text
            partColor = part.find('COLOR').text
            partQty = int(part.find('MINQTY').text)
            # print(f"Item ID: {itemID} - Color: {itemColor} - Qty: {itemQty}")

            partinfo = getPartInfo(partID, partColor, partQty)

            if len(partinfo) == 3:
                print(f"{partID} : Part not found")
            else:
                print(f"{partID} : {partinfo[-1]}")

            fileWriter.writerow(partinfo)
    else:
        for aline in infile:
            values = aline.split(delim)

            partID = values[0].rstrip()
            partColor = "0"
            partQty = 0

            if len(values) > 1:
                partColor = values[1]
                partQty = int(values[2].rstrip())

            partinfo = getPartInfo(partID, partColor, partQty)

            reportResults(partinfo)

            fileWriter.writerow(partinfo)

        infile.close()

    outfile.close()

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='program1 ')
   parser.add_argument('-i','--input', help='Input file name',required=True)
   args = parser.parse_args()
   processFile(args.input)
