from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.error import URLError
import csv
import json
import logging
import os
import re
from pathlib import PurePath
from bs4 import BeautifulSoup
from detect_delimiter import detect
import argparse
import xml.etree.cElementTree as ET
from xml.dom.minidom import parseString
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
USE_SELENIUM =  os.getenv('USE_SELENIUM')

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

partList = []
web_driver = None

if USE_SELENIUM:
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
        logging.error(f"Exception while creating webdriver: {ex}")
        print(f"cannot initialize {os.getenv('BROWSER')} browser option:")
        print(f"{ex}")
        exit()

def rebrickableColorToLEGO(colornum):
    """
    Get the LEGO equivalent to a rebrickable color number if it exists
    :param colornum:
    :return:
    """
    if colornum < 0:
        return colornum
    
    try:
        return color_data[colornum]['Lego']
    except:
        return colornum

def isColorAvailable(partURL, colornum):

    if colornum > -1:
        web_driver.get(partURL)
        delay = 60 # seconds
        myElem = None
        try:
            available_colors=web_driver.find_elements_by_class_name("swatch-option")
    
            for i in available_colors:
                title = i.get_attribute('aria-label')
                logging.info(f"checking {title} for: {colornum}")
                if title.startswith(f"{colornum}-"):
                    logging.info(f"Found it")
                    return True

        except TimeoutException:
            print("Could not get color information.  This may be because the page load timed out or because the page is for a single color.")

        except Exception as ex:
            print(f"{ex}")
    
    logging.info(f"Nope")
    return False 

def countFileLines(file_path):
    # open file in read mode
    with open(file_path, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    return count

def countXMLTags(file_path):
    with open(file_path, 'r') as xml_file:
        data = xml_file.read()
        dom = parseString(data)
        return len(dom.getElementsByTagName('ITEM'))

class Part:

    def __init__(self, partID, partColor, partQty):
        rb_part = get_rebrickable_details(partID)
        self._ID = partID
        self._rootID = getPartRoot(partID)
        self._altIDs = rb_part['altIDs']
        self._color = partColor
        self._LEGOColor = rebrickableColorToLEGO(partColor)
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
wbPos = 0 if os.getenv('PRIMARY') == 'webrick' else 99 

vendors.append(Vendor('Vonado', 'https://www.vonado.com/catalogsearch/result/?q=', 10))
vendors.insert(wbPos, Vendor('Webrick', 'https://www.webrick.com/catalogsearch/result/?q=', 1))

class Color:

    ID = -1
    label = "None"
    price = 0

    def __init__(self, ID, label):
        self.ID = ID
        self.label = label
  
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
    alternates.append(partNum)
    partName = 'Unknown'

    try:
        headers = {'Accept': 'application/json', 'Authorization': 'key ' + RB_API_KEY}
        reg_url = f"https://rebrickable.com/api/v3/lego/parts/{partNum}/"
        req = Request(url=reg_url, headers=headers) 
        resp = urlopen(req)
        partData = json.loads(resp.read())
        partName = partData['name']
        alternates = partData['molds']
        alternates.insert(0, rootID)
    except HTTPError as e:
        print(f"Rebrickable doesn't recognize part {partNum}")

    except URLError:
        print(f"{partNum} : Server down or incorrect domain")

    details['name'] = partName
    alternates = list(dict.fromkeys(alternates))
    details['altIDs'] = alternates
    return details

def get_rebrickable_colors():
    colorData = {}
    
    try:
        headers = {'Accept': 'application/json', 'Authorization': 'key ' + RB_API_KEY}
        reg_url = f"https://rebrickable.com/api/v3/lego/colors/"
        req = Request(url=reg_url, headers=headers) 
        resp = urlopen(req)
        colorData = json.loads(resp.read())
        allColors = colorData["results"]
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
    except HTTPError as e:
        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print(f"Colors : Server down or incorrect domain")

    return colorData

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

def getColorDataOutOfPage(res2):
    colorswatches = {}

    script = res2.find_all('script')
    for scr in script:
        if scr.text.__contains__('data-role=swatch-options'):
            try:
                colorswatches = json.loads(scr.text)
            except Exception as ex:
                logging.error(f"Could not find color information in page: {ex}")
            break

    return colorswatches

def firstLevelCheck(thePart, doublecheck=False):
    logging.info(f"---------------------------------------------------")
    logging.info(f"Begin check for {thePart.ID} in color {thePart.color} ({thePart.LEGOColor}) ")
    partQty = thePart.qty

    for vnd in vendors:
        for partNum in thePart.altIDs:
            if not thePart.available:
                logging.info(f"part not found yet; checking {vnd.name} for: {thePart.ID} as {partNum}")
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
                    reg_url = vnd.searchURL + partNum
                    req = Request(url=reg_url, headers=headers) 
                    html = urlopen(req)

                    res = BeautifulSoup(html.read(),"html5lib")

                    tags = res.findAll("div", {"class": "message notice"})
                    # the appearance of this means no results.
                    
                    if len(tags) == 0:
                        tags = res.findAll("a", {"class": ["product photo product-item-photo"]})
                        for tag in tags:
                            if not thePart.available:
                                link = tag['href']
                                if re.search(f"-{partNum}[\.\-]", link, re.IGNORECASE):
                                    if "moc" not in link:
                                        # we've found the right search result; get the part page
                                        colorList = []
                                        swatch_dict = {}
                                        idx = 0
                                        req2 = Request(url=link, headers=headers) 
                                        html2 = urlopen(req2)
                                        res2 = BeautifulSoup(html2.read(),"html5lib")
                                        try:
                                            price_tag = res2.find("span", {"class": "price-wrapper"})
                                            unit_price = float(price_tag['data-price-amount'])
                                        except Exception as ex:
                                            logging.error(f"Error while getting base price: {ex}")
                                            unit_price=0

                                        total_price = 0
                                        hasColor = False

                                        lotCount = partQty//vnd.skuQty

                                        if partQty%vnd.skuQty > 0:
                                            lotCount = lotCount + 1

                                        if USE_SELENIUM:
                                            logging.info(f"checking {link} for: {thePart.LEGOColor} with selenium")
                                            hasColor = isColorAvailable(link, thePart.LEGOColor)
                                            logging.info(f"hasColor: {hasColor}")

                                        else:    
                                            logging.info(f"extracting color data from page via script tags")
                                            while len(swatch_dict) == 0 and idx < 6:
                                                idx = idx + 1
                                                logging.info(f"color data retrieval attempt: {idx}")
                                                if html2 is None:
                                                    req2 = Request(url=link, headers=headers) 
                                                    html2 = urlopen(req2)
                                                    res2 = BeautifulSoup(html2.read(),"html5lib")

                                                swatch_dict = getColorDataOutOfPage(res2)
                                                if len(swatch_dict) == 0:
                                                    logging.info(f"Didn't find any color data")
                                                
                                            if len(swatch_dict) > 0:
                                                unit_price = 0
                                                hasColor = False

                                                a = swatch_dict["[data-role=swatch-options]"]["Magento_Swatches/js/swatch-renderer"]["jsonConfig"]
                                                prices = a["optionPrices"]
                                                c = a["attributes"]
                                                for item in c.items():
                                                    j = item[1]
                                                    if type(j) is dict:
                                                        if j["position"] == '0':
                                                            # this contains the list of colors
                                                            colors = j['options']
                                                            logging.info(f"swatches found: {len(colors)}")
                                                            for color in colors:
                                                                if len(color["products"]) > 0 and color["id"] is not None:
                                                                    # it's used for this part
                                                                    product = color["products"][0]
                                                                    # split label on '-'
                                                                    parts = color["label"].split('-')
                                                                    this = Color(parts[0], parts[1])
                                                                    this.price = prices[product]["finalPrice"]["amount"]
                                                                    colorList.append(this)

                                                for color in colorList:
                                                    hasColor = hasColor or int(color.ID) == int(thePart.LEGOColor)
                                                    if hasColor and total_price == 0:
                                                        # pull pricing for this color
                                                        unit_price = color.price
                                            else:
                                                logging.error(f"Could not find color information in page after {idx} tries.")
                                                print(f"No color data for {partNum} after {idx} tries.")

                                        total_price = lotCount * unit_price

                                        if (not doublecheck) or (hasColor and doublecheck):
                                            logging.info(f"Found instance of {thePart.ID}.")
                                            if doublecheck:
                                                logging.info(f"Previous instance was wrong color.")
                                            thePart.colorAvailable = hasColor
                                            thePart.available = True
                                            thePart.lotCount = lotCount
                                            thePart.unit_price = unit_price
                                            thePart.total_price = total_price
                                            thePart.link = link

                except HTTPError as he:
                    logging.error(f"HTTPError: {he} on {reg_url}")

                except URLError as ue:

                    logging.error(f"URLError: {ue} on {reg_url}")
                    print(f"{thePart.ID} : Server down or incorrect domain")

                    
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
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color {thePart.color} ({thePart.LEGOColor}) available: {thePart.colorAvailable}"

    print(outputString)

def writeResults(thePartList, file_name, headers, delim):

    p = PurePath(file_name)
    output_name=f"{p.root}{p.stem}-output.txt"

    with open(output_name, 'wt') as csv_file:
        wr = csv.writer(csv_file, delimiter=delim)
        wr.writerow(list(headers))
        for part in thePartList:
            wr.writerow(list(part))
 
def handleResults(thePart, idx, ct):
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
    parser = argparse.ArgumentParser(description='vonado-bricks')
    parser.add_argument('-i','--input', help='Input file name',required=True)
    # parser.add_argument('-r','--rb-api', help='Rebrickable API key',required=True)
    # parser.add_argument('-b','--browser', help='Browser to use',required=True, choices=['chrome', 'firefox', 'edge'])
    # parser.add_argument('-p','--primary', help='Site to search first',required=True, choices=['webrick', 'vonado'])
    args = parser.parse_args()
    processFile(args.input)
    if web_driver is not None:
       web_driver.close()
