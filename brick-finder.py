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
from dotenv import load_dotenv

from dollartree import isDTBrick

load_dotenv()  # take environment variables from .env.

RB_API_KEY = os.getenv("RB_API_KEY")
PRIMARY = os.getenv("PRIMARY")
DOLLAR_TREE_ENABLED = os.getenv("DOLLAR_TREE_ENABLED")

logging.basicConfig(
    level=logging.DEBUG,
    filename="app.log",
    filemode="w",
    format="%(name)s - %(levelname)s - %(message)s",
)

partList = []
vendorCounts = {}
brickLinkColors = False


def colorToLEGO(colornum, brickLinkColors):
    if brickLinkColors:
        return bricklinkColorToLEGO(colornum)
    else:
        return rebrickableColorToLEGO(colornum)


def rebrickableColorToLEGO(colornum):
    """
    Get the LEGO equivalent to a rebrickable color number if it exists
    :param colornum:
    :return:
    """
    default = {"name": "Unknown", "Lego": colornum}

    if colornum < 0:
        return default

    try:
        return color_data[colornum]
    except Exception:
        return default


def bricklinkColorToLEGO(colornum):
    """
    Get the LEGO equivalent to a bricklink color number if it exists
    :param colornum:
    :return:
    """
    default = {"name": "Unknown", "Lego": colornum, "BrickLink": colornum}

    if colornum < 0:
        return default

    for color in color_data:
        if color_data[color]["BrickLink"] == colornum:
            return color_data[color]

    return default


def countFileLines(file_path):
    # open file in read mode
    with open(file_path, "r") as fp:
        for count, line in enumerate(fp):
            pass
    return count


def countXMLTags(file_path):
    with open(file_path, "r") as xml_file:
        data = xml_file.read()
        dom = parseString(data)
        return len(dom.getElementsByTagName("ITEM"))


class Color:

    _ID = -1
    _label = "Unknown"
    _price = 0

    def __init__(self, ID, label):
        self._ID = ID
        self._label = label

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, a):
        self._ID = a

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, a):
        self._label = a

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, a):
        self._price = a


class Part:
    def __init__(self, partID, partColor, partQty):
        rb_part = get_rebrickable_details(partID)
        rb_LegoColor = colorToLEGO(partColor, brickLinkColors)
        self._ID = partID
        self._rootID = getPartRoot(partID)
        self._altIDs = rb_part["altIDs"]
        self._qty = partQty
        self._color = Color(partColor, rb_LegoColor["name"])
        self._printed = partID.__contains__("pr")
        self._LEGOColor = Color(rb_LegoColor["Lego"], rb_LegoColor["name"])
        self._priceColor = Color(partColor, rb_LegoColor["name"])
        self._lotCount = 0
        self._unit_price = 0
        self._total_price = 0
        self._link = ""
        self._name = rb_part["name"]
        self._available = False
        self._colorAvailable = False

    def __iter__(self):
        return iter(
            [
                self._ID,
                self._color.ID,
                self._qty,
                self._rootID,
                self._LEGOColor.ID,
                self._lotCount,
                self._priceColor.ID,
                self._priceColor.label,
                self._unit_price,
                self._total_price,
                self._name,
                self._link,
                self._available,
                self._colorAvailable,
            ]
        )

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
    def printed(self):
        return self._printed

    @printed.setter
    def printed(self, a):
        self._printed = a

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, a):
        self._color = a

    @property
    def priceColor(self):
        return self._priceColor

    @priceColor.setter
    def priceColor(self, a):
        self._priceColor = a

    @property
    def priceColorLabel(self):
        return self._priceColorLabel

    @priceColorLabel.setter
    def priceColorLabel(self, a):
        self._priceColorLabel = a

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

    name = ""
    searchURL = ""
    skuQty = 1

    def __init__(self, name, searchURL, skuQty):
        self.name = name
        self.searchURL = searchURL
        self.skuQty = skuQty


vendors = []
wbPos = 0 if os.getenv("PRIMARY") == "webrick" else 99

vendors.append(
    Vendor("Vonado", "https://www.vonado.com/catalogsearch/result/?q=", 10)
)
vendorCounts["Vonado"] = 0
vendors.insert(
    wbPos,
    Vendor("Webrick", "https://www.webrick.com/catalogsearch/result/?q=", 1),
)
vendorCounts["Webrick"] = 0


def getPartRoot(partID):
    rootPartID = partID
    # Vonado doesn't use the letter at the end on something like 3070b
    # so we'll pull it off for search purposes.
    try:
        a, b = re.split(r"[a-z]", partID, 1, flags=re.I)
        rootPartID = a
    except Exception:
        rootPartID = partID

    return rootPartID


def get_rebrickable_details(partNum):
    rootID = getPartRoot(partNum)
    details = {}
    alternates = []
    alternates.append(rootID)
    alternates.append(partNum)
    partName = "Unknown"
    tryBrickLink = True

    try:
        headers = {
            "Accept": "application/json",
            "Authorization": "key " + RB_API_KEY,
        }
        reg_url = f"https://rebrickable.com/api/v3/lego/parts/{partNum}/"
        req = Request(url=reg_url, headers=headers)
        resp = urlopen(req)
        partData = json.loads(resp.read())
        partName = partData["name"]
        alternates = partData["molds"]
        alternates.insert(0, rootID)
        for alt in partData["external_ids"]:
            alternates = alternates + partData["external_ids"][alt]

        tryBrickLink = False
    except HTTPError:
        logging.info(f"Rebrickable doesn't recognize part {partNum}")
    except URLError:
        print(f"{partNum} : Server down or incorrect domain")

    if tryBrickLink:
        try:
            headers = {"User-Agent": "vonado-bricks"}
            reg_url = f"https://www.bricklink.com/v2/catalog/catalogitem.page?P={partNum}"
            req = Request(url=reg_url, headers=headers)
            html = urlopen(req)

            res = BeautifulSoup(html.read(), "html5lib")

            tags = res.findAll("section", {"id": "content"})

            # If there's one of those we got results
            if len(tags) > 0:
                logging.info(f"Bricklink recognizes part {partNum}")
                partName = res.findAll("title")[0].text
                # 'BrickLink - Part 3648 : LEGO Technic, Gear 24 Tooth (2nd Version - 1 Axle Hole) [Technic, Gear] - BrickLink Reference Catalog'
                partName = re.sub("BrickLink - Part .+ : ", "", partName)
                partName = re.sub(
                    " - BrickLink Reference Catalog", "", partName
                )
                # 'LEGO Technic, Gear 24 Tooth (2nd Version - 1 Axle Hole) [Technic, Gear]'
                # I'm sure this isn't brittle at all.

                tags = res.findAll("span")
                for tag in tags:
                    # gather any alternates
                    if tag.text.__contains__("Alternate Item No"):
                        logging.info(
                            f"Bricklink alternates found for part {partNum}"
                        )
                        # Item No: 4265c  Alternate Item No: 32123,  42136
                        parts = tag.text.split("Alternate Item No: ")
                        tempNums = parts[1].split(",")
                        altNums = []
                        # 32123,  42136
                        for thing in tempNums:
                            altNums.append(thing.lstrip())

                        uniques = set(altNums + alternates)
                        alternates = uniques

        except HTTPError:
            print(f"Bricklink doesn't recognize part {partNum}")

    details["name"] = partName
    alternates = list(dict.fromkeys(alternates))
    details["altIDs"] = alternates
    return details


def get_rebrickable_colors():
    colorData = {}

    try:
        headers = {
            "Accept": "application/json",
            "Authorization": "key " + RB_API_KEY,
        }
        reg_url = "https://rebrickable.com/api/v3/lego/colors/?page_size=200"
        req = Request(url=reg_url, headers=headers)
        resp = urlopen(req)
        tempData = json.loads(resp.read())
        allColors = tempData["results"]
        for color in allColors:
            sub = {}
            if color["id"] > -1:
                sub["name"] = color["name"]
                sub["Rebrickable"] = color["id"]
                try:
                    sub["Lego"] = color["external_ids"]["LEGO"]["ext_ids"][0]
                except KeyError:
                    sub["Lego"] = -1
                try:
                    sub["BrickLink"] = color["external_ids"]["BrickLink"][
                        "ext_ids"
                    ][0]
                except KeyError:
                    sub["BrickLink"] = -1
                if sub["Lego"] > -1:
                    colorData[color["id"]] = sub
    except HTTPError as e:
        print(f"{reg_url} : HTTPError")
        print(e)

    except URLError:

        print("Colors : Server down or incorrect domain")

    return colorData


color_data = get_rebrickable_colors()


def isXML(file_name):
    try:
        tree = ET.ElementTree(file=file_name)  # noqa: F841
        return True

    except ET.ParseError:
        return False


def getHeaders(firstline, delim):
    if len(firstline) == 0:
        headers = ["part"]
        headers.append("color")
        headers.append("qty")
    else:
        headers = firstline.split(delim)

        columncount = len(headers)

        # Get rid of the linefeed at the end
        headers[columncount - 1] = headers[columncount - 1].rstrip()

        if columncount == 4:
            if headers[3] == "Is Spare":
                headers.pop()

        if columncount == 1:
            headers.append("color")
            headers.append("qty")

    headers.append("root")
    headers.append("LEGOColor")
    headers.append("lots")
    headers.append("priceColor")
    headers.append("priceColorName")
    headers.append("unit")
    headers.append("total")
    headers.append("name")
    headers.append("link")
    headers.append("available")
    headers.append("color_available")

    return headers


def getColorDataOutOfPage(res2):
    colorswatches = {}

    script = res2.find_all("script")
    for scr in script:
        if scr.text.__contains__("data-role=swatch-options"):
            try:
                colorswatches = json.loads(scr.text)
            except Exception as ex:
                logging.error(
                    f"Could not find color information in page: {ex}"
                )
            break

    return colorswatches


def firstLevelCheck(thePart):  # noqa: C901
    logging.info(
        f"Begin check for {thePart.ID} in color {thePart.color.ID} ({thePart.LEGOColor.ID}) "
    )
    partQty = thePart.qty

    if DOLLAR_TREE_ENABLED and isDTBrick(thePart.ID, thePart.color.ID):
        logging.info(
            f"Dollar Tree carries {thePart.ID} in color {thePart.color.ID} ({thePart.LEGOColor.ID}) "
        )
        thePart.available = True
        thePart.colorAvailable = True
        thePart.lotCount = partQty // 1
        thePart.unit_price = round(1 / 48, 2)
        thePart.total_price = round(thePart.lotCount * thePart.unit_price, 2)
        thePart.link = "https://www.dollartree.com/make-it-blocks-assorted-building-blocks-48ct-packs/269130"

    for vnd in vendors:
        for partNum in thePart.altIDs:

            if not thePart.available or not thePart.colorAvailable:
                logging.info(
                    f"part not found in correct color; checking {vnd.name} for: {thePart.ID} as {partNum}"
                )
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"
                    }
                    reg_url = vnd.searchURL + partNum
                    req = Request(url=reg_url, headers=headers)
                    html = urlopen(req)

                    res = BeautifulSoup(html.read(), "html5lib")

                    tags = res.findAll("div", {"class": "message notice"})
                    # the appearance of this means no results.

                    if len(tags) == 0:
                        tags = res.findAll(
                            "a",
                            {"class": ["product photo product-item-photo"]},
                        )
                        for tag in tags:
                            if not thePart.available:
                                link = tag["href"]
                                if re.search(
                                    f"-{partNum}[.-]", link, re.IGNORECASE
                                ):
                                    if "moc" not in link:
                                        # we've found the right search result; get the part page
                                        colorList = []
                                        swatch_dict = {}
                                        idx = 0
                                        req2 = Request(
                                            url=link, headers=headers
                                        )
                                        html2 = urlopen(req2)
                                        res2 = BeautifulSoup(
                                            html2.read(), "html5lib"
                                        )
                                        try:
                                            price_tag = res2.find(
                                                "span",
                                                {"class": "price-wrapper"},
                                            )
                                            unit_price = float(
                                                price_tag["data-price-amount"]
                                            )
                                        except Exception as ex:
                                            logging.error(
                                                f"Error while getting base price: {ex}"
                                            )
                                            unit_price = 0

                                        total_price = 0
                                        foundColor = False
                                        priceColor = thePart.LEGOColor
                                        lotCount = partQty // vnd.skuQty

                                        if partQty % vnd.skuQty > 0:
                                            lotCount = lotCount + 1

                                        logging.info(
                                            "extracting color data from page via script tags"
                                        )
                                        while (
                                            len(swatch_dict) == 0 and idx < 12
                                        ):
                                            idx = idx + 1
                                            logging.info(
                                                f"color data retrieval attempt: {idx}"
                                            )
                                            if html2 is None:
                                                req2 = Request(
                                                    url=link, headers=headers
                                                )
                                                html2 = urlopen(req2)
                                                res2 = BeautifulSoup(
                                                    html2.read(), "html5lib"
                                                )

                                            swatch_dict = (
                                                getColorDataOutOfPage(res2)
                                            )
                                            if len(swatch_dict) == 0:
                                                logging.info(
                                                    "Didn't find any color data"
                                                )
                                                html2 = None

                                        if len(swatch_dict) > 0:
                                            unit_price = 0
                                            foundColor = False

                                            a = swatch_dict[
                                                "[data-role=swatch-options]"
                                            ][
                                                "Magento_Swatches/js/swatch-renderer"
                                            ][
                                                "jsonConfig"
                                            ]
                                            prices = a["optionPrices"]
                                            c = a["attributes"]
                                            for item in c.items():
                                                j = item[1]
                                                if type(j) is dict:
                                                    if j["position"] == "0":
                                                        # this contains the list of colors
                                                        colors = j["options"]
                                                        logging.info(
                                                            f"swatches found: {len(colors)}"
                                                        )
                                                        for color in colors:
                                                            if (
                                                                len(
                                                                    color[
                                                                        "products"
                                                                    ]
                                                                )
                                                                > 0
                                                                and color["id"]
                                                                is not None
                                                            ):
                                                                # it's used for this part
                                                                product = color[
                                                                    "products"
                                                                ][
                                                                    0
                                                                ]
                                                                # split label on '-'
                                                                # need to deal with "Trans-clear"
                                                                parts = color[
                                                                    "label"
                                                                ].split("-")
                                                                this = Color(
                                                                    parts[0],
                                                                    parts[1],
                                                                )
                                                                if (
                                                                    len(parts)
                                                                    == 3
                                                                ):
                                                                    this = Color(
                                                                        parts[
                                                                            0
                                                                        ],
                                                                        f"{parts[1]}-{parts[2]}",
                                                                    )
                                                                this.price = prices[
                                                                    product
                                                                ][
                                                                    "finalPrice"
                                                                ][
                                                                    "amount"
                                                                ]
                                                                colorList.append(
                                                                    this
                                                                )

                                            getCheapest = (
                                                int(thePart.color.ID) == 9999
                                            )
                                            if getCheapest and unit_price == 0:
                                                unit_price = 9999

                                            for color in colorList:
                                                if getCheapest:
                                                    if (
                                                        color.price
                                                        < unit_price
                                                    ):
                                                        logging.info(
                                                            f"new low price: {color.price} for {color.ID}."
                                                        )
                                                        unit_price = (
                                                            color.price
                                                        )
                                                        priceColor = Color(
                                                            color.ID,
                                                            color.label,
                                                        )
                                                        foundColor = True
                                                else:
                                                    isDesiredColor = int(
                                                        color.ID
                                                    ) == int(
                                                        thePart.LEGOColor.ID
                                                    )

                                                    if (
                                                        not foundColor
                                                    ) and isDesiredColor:
                                                        logging.info(
                                                            "Don't have the color yet, and this is the desired color"
                                                        )
                                                        unit_price = (
                                                            color.price
                                                        )
                                                        foundColor = True
                                        else:
                                            logging.error(
                                                f"Could not find color information in page after {idx} tries."
                                            )
                                            print(
                                                f"No color data for {partNum} after {idx} tries."
                                            )

                                        unit_price = round(unit_price, 2)
                                        total_price = round(
                                            lotCount * unit_price, 2
                                        )

                                        if (not thePart.available) or (
                                            foundColor and thePart.available
                                        ):
                                            logging.info(
                                                f"Found instance of {thePart.ID}."
                                            )
                                            vendorCounts[vnd.name] += 1
                                            if thePart.available:
                                                logging.info(
                                                    "Previous instance was wrong color."
                                                )
                                            thePart.colorAvailable = foundColor
                                            thePart.available = True
                                            thePart.priceColor = priceColor
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
    outputString = (
        f"{idx}/{ct} - {thePart.ID} : Part not found: {thePart.name}"
    )
    if thePart.available:
        if thePart.color.ID < 0:
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color not specified"
        elif thePart.color.ID == 9999:
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color {thePart.priceColor.ID} ({thePart.priceColor.label}) used for 'Any Color': {thePart.colorAvailable}"
        else:
            outputString = f"{idx}/{ct} - {thePart.ID} : {thePart.link} - Color {thePart.color.ID} ({thePart.LEGOColor.ID}) ({thePart.color.label}) available: {thePart.colorAvailable}"

    print(outputString)


def writeResults(thePartList, file_name, headers, delim):

    p = PurePath(file_name)
    output_name = f"./{p.stem}-output.txt"

    with open(output_name, "wt") as csv_file:
        wr = csv.writer(csv_file, delimiter=delim)
        wr.writerow(list(headers))
        for part in thePartList:
            wr.writerow(list(part))


def handleResults(thePart, idx, ct):
    reportResults(thePart, idx, ct)
    partList.append(thePart)


def processPart(partID, partColor, partQty, lineIdx, numLines):
    logging.info(
        f"-- Begin loop for part {partID} quantity {partQty} in color {partColor} ---"
    )

    if len(partID) == 0:
        logging.info("-- Bblank line found in input file ---")
    else:
        thePart = getPartInfo(partID, partColor, partQty)
        handleResults(thePart, lineIdx, numLines)

    logging.info("--- Done ---")


def processFile(file_name):

    print(f"\n\n================\nProcessing {file_name}\n================")

    firstline = ""

    delim = "\t"

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
            delim = ","

    if isXML(file_name):
        lineIdx = 0
        tree = ET.ElementTree(file=file_name)
        root = tree.getroot()

        # get the information via the children!
        for part in root.findall("ITEM"):
            lineIdx = lineIdx + 1
            partID = part.find("ITEMID").text
            try:
                partColor = int(part.find("COLOR").text)
            except Exception:
                partColor = 9999
                # If there's no color, default to ANY
            partQty = int(part.find("MINQTY").text)

            processPart(partID, partColor, partQty, lineIdx, numLines)

    else:
        lineIdx = 0

        for aline in infile:
            lineIdx = lineIdx + 1
            if len(aline) == 1:
                logging.info("-- Blank line found in input file ---")
                print(f"{lineIdx}/{numLines} - Blank line found in input file")
            else:
                values = aline.split(delim)

                partID = values[0].rstrip()
                partColor = -1
                partQty = 0

                if len(values) > 1:
                    partColor = int(values[1])
                    partQty = int(values[2].rstrip())

                processPart(partID, partColor, partQty, lineIdx, numLines)

        infile.close()

    totalParts = 0
    totalBricks = 0
    totalPrints = 0
    totalCost = 0
    foundParts = 0
    foundUnits = 0
    correctColorParts = 0
    correctColorBricks = 0

    for part in partList:
        totalParts += 1
        totalBricks += part.qty
        totalCost += part.total_price

        if part.printed:
            totalPrints += 1

        if part.available:
            foundParts += 1
            foundUnits += part.qty

        if part.colorAvailable:
            correctColorParts += 1
            correctColorBricks += part.qty

    print(f"\n\nFinished processing {file_name}:")
    print(f"Found {foundParts} of {totalParts} part types")
    for row in vendorCounts:
        if vendorCounts[row] > 0:
            print(f"{vendorCounts[row]} from {row}")
    print(
        f"Of these, {correctColorParts} of {foundParts} are available in the correct color"
    )
    if totalPrints > 0:
        print(
            f"List contains {totalPrints} printed parts; if shown as found they will likely not be printed"
        )
    print(
        f"Ballpark cost for {foundUnits} bricks of {foundParts} part types is {totalCost:.2f}"
    )

    headers = getHeaders(firstline, delim)

    writeResults(partList, file_name, headers, delim)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vonado-bricks")
    parser.add_argument("-i", "--input", help="Input file name", required=True)
    parser.add_argument(
        "-l", "--bricklink", help="XML is from Bricklink", required=False
    )
    args = parser.parse_args()
    try:
        brickLinkColors = bool(args.bricklink)
    except Exception:
        brickLinkColors = False
    processFile(args.input)
