from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import re
from bs4 import BeautifulSoup

infile = open("input.txt", "r")
outfile = open('output.csv', 'w', newline='')
fileWriter = csv.writer(outfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

for aline in infile:
    values = aline.split('\t')
    try:

        blID = values[0]
        elementID = ""
        partName = ""
        partColor = ""
        partQty = ""

        if len(values) > 1:
            elementID = values[1]
            partName = values[2]
            partColor = values[3]
            partQty = values[4].rstrip()
        
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
            fileWriter.writerow([blID, elementID, partName, partColor, partQty])
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
                            fileWriter.writerow([blID, elementID, partName, partColor, partQty, link])

                if not found:
                    print(f"{blID} - {elementID} - {partName} : Part not found")
                    fileWriter.writerow([blID, elementID, partName, partColor, partQty])

infile.close()
outfile.close()
