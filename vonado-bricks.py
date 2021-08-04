from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import json
import os
import re
from bs4 import BeautifulSoup
from detect_delimiter import detect
import argparse
import xml.etree.cElementTree as ET
from xml.dom.minidom import parseString
from sqlite3 import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOpts
from selenium.webdriver.firefox.options import Options as FirefoxOpts
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

RB_API_KEY = os.getenv('RB_API_KEY')

web_driver = None

try:
    if os.getenv('BROWSER') == 'chromium':
        chrome_options = ChromeOpts()
        chrome_options.add_argument("--headless")
        web_driver = webdriver.Chrome(ChromeDriverManager(chrome_type = ChromeType.CHROMIUM).install())

    if os.getenv('BROWSER') == 'firefox':
        firefox_options = FirefoxOpts()
        firefox_options.add_argument("--headless")
        web_driver = webdriver.Firefox(executable_path = GeckoDriverManager().install(), options=firefox_options)

    if os.getenv('BROWSER') == 'msie':
        web_driver = webdriver.Ie(IEDriverManager().install())

    if os.getenv('BROWSER') == 'edge':
        web_driver = webdriver.Edge(EdgeChromiumDriverManager().install())

    if web_driver == None:
        chrome_options = ChromeOpts()
        chrome_options.add_argument("--headless")
        web_driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
except Exception as ex:
    print(f"cannot initialize {os.getenv('BROWSER')} browser option:")
    print(f"{ex}")
    exit()

def create_outputWriter(file_name, delim):
    global outputWriter
    global outfile

    parts = file_name.split('.')
    parts.pop()
    dotstr="."
    output_name = dotstr.join(parts)
    output_name=f"{output_name}-output.csv"
    
    outfile = open(output_name, 'w', newline='')

    outputWriter = csv.writer(outfile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)

outputWriter = None
outfile = None
partList = []

def rebrickableToLEGO(colornum):
    """
    Get the LEGO equivalent to a rebrickable color number
    :param colornum:
    :return:
    """
    if colornum < 0:
        return colornum
    
    return color_data[colornum]['Lego']

def isColorAvailable(partURL, colornum):

    if colornum > -1:
        web_driver.get(partURL)
        delay = 30 # seconds
        try:
            myElem = WebDriverWait(web_driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'swatch-attribute')))

            available_colors=web_driver.find_elements_by_class_name("swatch-option")
    
            for i in available_colors:
                title = i.get_attribute('aria-label')
                if title.startswith(f"{colornum}-"):
                    return True

        except TimeoutException:
            print("Could not get color information.  This may be because the page load timed out or because the page is for a single color.")
    
    return False 

def countFileLines(file_path):
    # open file in read mode
    with open(file_path, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    return count

def countXMLTags(file_path):
    file = open(file_path,'r')
    data = file.read()
    file.close()
    dom = parseString(data)
    return len(dom.getElementsByTagName('ITEM'))

class Part:

    def __init__(self, partID, partColor, partQty):
        rb_part = get_rebrickable_details(partID)
        self._ID = partID
        self._rootID = getPartRoot(partID)
        self._altIDs = rb_part['altIDs']
        self._color = partColor
        self._LEGOColor = rebrickableToLEGO(partColor)
        self._qty = partQty
        self._lotCount = 0
        self._unit_price = 0
        self._total_price = 0
        self._link = ""
        self._name = rb_part['name']
        self._available = False
        self._colorAvailable = False

    def __iter__(self):
        return iter([self._ID, self._color, self._qty, self._rootID, self._LEGOColor,
                   self._lotCount, self._unit_price, self._total_price, self._link, self._available,
                   self._colorAvailable])

    @property
    def ID(self):
        return self._ID
       
    @ID.setter
    def ID(self, a):
        self._ID = a

    @property
    def rootID(self):
        return self._rootID
       
    @rootID.setter
    def rootID(self, a):
        self._rootID = a

    @property
    def altIDs(self):
        return self._altIDs
       
    @altIDs.setter
    def altIDs(self, a):
        self._altIDs = a

    @property
    def color(self):
        return self._color
       
    @color.setter
    def color(self, a):
        self._color = a

    @property
    def LEGOColor(self):
        return self._LEGOColor
       
    @LEGOColor.setter
    def LEGOColor(self, a):
        self._LEGOColor = a

    @property
    def qty(self):
        return self._qty
       
    @qty.setter
    def qty(self, a):
        self._qty = a

    @property
    def lotCount(self):
        return self._lotCount
       
    @lotCount.setter
    def lotCount(self, a):
        self._lotCount = a

    @property
    def unit_price(self):
        return self._unit_price
       
    @unit_price.setter
    def unit_price(self, a):
        self._unit_price = a

    @property
    def total_price(self):
        return self._total_price
       
    @total_price.setter
    def total_price(self, a):
        self._total_price = a

    @property
    def link(self):
        return self._link
       
    @link.setter
    def link(self, a):
        self._link = a

    @property
    def name(self):
        return self._name
       
    @name.setter
    def name(self, a):
        self._name = a

    @property
    def available(self):
        return self._available
       
    @available.setter
    def available(self, a):
        self._available = a

    @property
    def colorAvailable(self):
        return self._colorAvailable
       
    @colorAvailable.setter
    def colorAvailable(self, a):
        self._colorAvailable = a

class Vendor:

    name = ''
    searchURL = ''
    skuQty = 1

    def __init__(self, name, searchURL, skuQty):
        self.name = name
        self.searchURL = searchURL
        self.skuQty = skuQty

vendors = []
vendors.append(Vendor('Webrick', 'https://www.webrick.com/catalogsearch/result/?q=', 1))
vendors.append(Vendor('Vonado', 'https://www.vonado.com/catalogsearch/result/?q=', 10))
  
def getPartRoot(partID):
    rootPartID = partID
    # Vonado doesn't use the letter at the end on something like 3070b
    # so we'll pull it off for search purposes.
    try:
        a, b = re.split(r"[a-z]", partID, 1, flags=re.I)
        rootPartID = a
    except:
        rootPartID = partID
    
    return rootPartID

def get_rebrickable_details(partNum):
    rootID = getPartRoot(partNum)
    details = {}
    alternates = []
    alternates.append(rootID)
    partName = 'Unknown'

    try:
        headers = {'Accept': 'application/json', 'Authorization': 'key ' + RB_API_KEY}
        reg_url = f"https://rebrickable.com/api/v3/lego/parts/{partNum}/"
        req = Request(url=reg_url, headers=headers) 
        resp = urlopen(req)
    except HTTPError as e:
        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print(f"{partNum} : Server down or incorrect domain")

    else:
        partData = json.loads(resp.read())
        partName = partData['name']
        # "name": "Plate Special 2 x 2 with 1 Pin Hole [Split Underside Ribs]",
        alternates = partData['molds']
        alternates.insert(0, rootID)

    details['name'] = partName
    details['altIDs'] = alternates
    return details

def get_rebrickable_colors():
    # curl -X GET --header 'Accept: application/json' --header 'Authorization: key 8944defc013ca0ee31e05d4972824335' ''
    colorData = {}
    
    try:
        headers = {'Accept': 'application/json', 'Authorization': 'key ' + RB_API_KEY}
        reg_url = f"https://rebrickable.com/api/v3/lego/colors/"
        req = Request(url=reg_url, headers=headers) 
        resp = urlopen(req)
    except HTTPError as e:
        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print(f"Colors : Server down or incorrect domain")

    else:
        colorData = json.loads(resp.read())
        allColors = colorData["results"]
        # colorData["results"] is the array of colors
        # color["id"] is id
        # color["name"] is name
        # color["external_ids"]["LEGO"] is lego colorData
        # color["external_ids"]["LEGO"]["ext_ids"][0] is array we want element 0
        # want to build 
        # colorData = {
        #     0: {
        #         name: "Black"
        #         Lego: 26
        #     }
        # }
        for color in allColors:
            sub = {}
            if color['id'] > -1:
                sub['name'] = color["name"]
                try:
                    sub["Lego"] = color["external_ids"]["LEGO"]["ext_ids"][0]
                except KeyError:
                    sub["Lego"] = -1
                if sub["Lego"] > -1:
                    colorData[color['id']] = sub

    return colorData
        # {0: {'name': 'Black', 'Lego': 26}}

color_data = get_rebrickable_colors()

def isXML(file_name):
    try:
       tree = ET.ElementTree(file=file_name)
       return True

    except ET.ParseError as e:
       return False

def getHeaders(firstline, delim):
    if len(firstline) == 0:
        headers = ["part"]
        headers.append("root")
        headers.append("color")
        headers.append("LEGOColor")
        headers.append("qty")
        headers.append("lots")
        headers.append("unit")
        headers.append("total")
        headers.append("link")
        headers.append("available")
        headers.append("color_available")
    else:
        headers = firstline.split(delim)

        columncount = len(headers)

        # Get rid of the linefeed at the end
        headers[columncount-1] = headers[columncount-1].rstrip()

        if columncount == 1:
            headers.append("color")
            headers.append("qty")

        headers.append("root")
        headers.append("LEGOColor")
        headers.append("lots")
        headers.append("unit")
        headers.append("total")
        headers.append("link")
        headers.append("available")
        headers.append("color_available")

    return headers

def firstLevelCheck(thePart, doublecheck=False):
    # pass in partinfo, return partinfo
    partQty = thePart.qty

    for vnd in vendors:
        for partNum in thePart.altIDs:
            if not thePart.available:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
                    reg_url = vnd.searchURL + partNum
                    req = Request(url=reg_url, headers=headers) 
                    html = urlopen(req)

                except HTTPError as e:

                    print(f"{reg_url} : HTTPError")
                    print(e)

                except URLError:

                    print(f"{thePart.ID} : Server down or incorrect domain")

                else:
                    res = BeautifulSoup(html.read(),"html5lib")

                    tags = res.findAll("div", {"class": "message notice"})
                    
                    if len(tags) == 0:
                        tags = res.findAll("a", {"class": ["product photo product-item-photo"]})
                        if len(tags) > 0:
                            found = False

                            for tag in tags:
                                if not thePart.available:
                                    link = tag['href']
                                    if re.search(f"-{partNum}[\.\-]", link, re.IGNORECASE):
                                        if "moc" not in link:
                                            lotCount = partQty//vnd.skuQty

                                            if partQty%vnd.skuQty > 0:
                                                lotCount = lotCount + 1

                                            req2 = Request(url=link, headers=headers) 
                                            html2 = urlopen(req)
                                            res2 = BeautifulSoup(html2.read(),"html5lib")

                                            price_tag = res2.find("span", {"class": "price-wrapper"})
                                            unit_price = float(price_tag['data-price-amount'])
                                            total_price = lotCount * unit_price

                                            hasColor = isColorAvailable(link, thePart.LEGOColor)

                                            if (not doublecheck) or (hasColor and doublecheck):
                                                thePart.colorAvailable = hasColor
                                                thePart.available = True
                                                thePart.lotCount = lotCount
                                                thePart.unit_price = unit_price
                                                thePart.total_price = total_price
                                                thePart.link = link
                        
    return thePart

def getPartInfo(partID, partColor, partQty):

    thePart = Part(partID, partColor, partQty)

    thePart = firstLevelCheck(thePart)

    # TODO: Perhaps try searching Aliexpress:
    # https://www.aliexpress.com/af/6562.html
    
    return thePart

def reportResults(thePart, idx, ct):
    outputString = f"{idx}/{ct} - {thePart.ID} : Part not found: {thePart.name}"
    if thePart.available:
        if thePart.color < 0:
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color not specified"
        else:
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color {thePart.color} ({thePart.LEGOColor}) : {thePart.colorAvailable}"

    print(outputString)

def writeResults(thePartList, file_name, headers, delim):
    parts = file_name.split('.')
    parts.pop()
    dotstr="."
    output_name = dotstr.join(parts)
    output_name=f"{output_name}-output.csv"

    with open(output_name, 'wt') as csv_file:
        wr = csv.writer(csv_file, delimiter=delim)
        wr.writerow(list(headers))
        for part in thePartList:
            wr.writerow(list(part))
 
def handleResults(thePart, idx, ct):
    global partList
    reportResults(thePart, idx, ct)
    partList.append(thePart)

def processFile(file_name):

    print(f"\n\n================\nProcessing {file_name}\n================")

    firstline = ""

    delim = '\t'
    
    numLines = 0

    if isXML(file_name):
        firstline = ""
        numLines = countXMLTags(file_name)
    else:
        numLines = countFileLines(file_name)
        infile = open(file_name, "r")
        firstline = infile.readline()

        delim = detect(firstline)

        if delim is None:
            delim = ','

    
    if isXML(file_name):
        lineIdx = 0
        tree = ET.ElementTree(file=file_name)
        root = tree.getroot()

        # get the information via the children!
        for part in root.findall('ITEM'):
            lineIdx = lineIdx + 1
            partID = part.find('ITEMID').text
            try:
                partColor = int(part.find('COLOR').text)
            except:
                partColor = -1
                # This is probably not going to be found, as it's a sticker sheet or the like
            partQty = int(part.find('MINQTY').text)
            # print(f"Item ID: {itemID} - Color: {itemColor} - Qty: {itemQty}")

            thePart = getPartInfo(partID, partColor, partQty)

            handleResults(thePart, lineIdx, numLines)

    else:
        lineIdx = 0

        for aline in infile:
            lineIdx = lineIdx + 1
            values = aline.split(delim)

            partID = values[0].rstrip()
            partColor = -1
            partQty = 0

            if len(values) > 1:
                partColor = int(values[1])
                partQty = int(values[2].rstrip())

            thePart = getPartInfo(partID, partColor, partQty)

            handleResults(thePart, lineIdx, numLines)

        infile.close()

    headers = getHeaders(firstline, delim)
    
    writeResults(partList, file_name, headers, delim)

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description='program1 ')
   parser.add_argument('-i','--input', help='Input file name',required=True)
   args = parser.parse_args()
   processFile(args.input)
   web_driver.close()
