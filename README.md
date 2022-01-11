Webrick's site has changed with the addition of "brick source", which breaks my scraping code.  Webrick disabled for the time being.

So you have a list of bricks from some MOC or something and you want to find out which ones are available from Webricks, Vonado, or your local Dollar Tree.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.  It works for me and is fairly brittle given that it's scraping websites.

## Assumptions:
- You have a list of bricks in one of the following formats:
  - Rebrickable CSV or XML
  - BrickLink Wanted List XML
  - One part ID per line [with a header row]
- Python 3
  - https://www.python.org/
- git
  - https://git-scm.com/download
- Rebrickable API Key [free]
  - https://rebrickable.com/api/
- Running Mac OS X, Linux, Windows

## Getting started:
I'm assuming that you can get [Python 3](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed on your own.

This script runs in the terminal or command prompt.  Below, everything that `looks like this` can be copy-pasted into your terminal or command prompt to do that step.  The Windows stuff is pretty standard, but it does see far less testing than Linux or OS X, so if issues come up don't hesitate to let me know so I can adjust this doc.

1. Clone the repo and cd to that dir.
```
git clone https://github.com/chazlarson/brick-finder.git && cd brick-finder
```

<details>
  <summary>Windows</summary>
  <br />

  ```
  git clone https://github.com/chazlarson/brick-finder.git
  cd brick-finder
  ```
</details>

2. Copy the example `.env` file:
```
cp .env.example .env
```
<details>
  <summary>Windows</summary>
  <br />

  ```
  copy .env.example .env
  ```
</details>

3. Edit `.env` to insert your rebrickable API key:
```
nano .env
```
<details>
  <summary>Windows</summary>
  <br />

  ```
  notepad .env
  ```
</details>

```
RB_API_KEY=BINGBANGBOING
PRIMARY=webrick
DOLLAR_TREE_ENABLED=True
```
Available settings for `PRIMARY` are:
```
  webrick [anything else here will search Vonado first]
```

> There's a `quick-test.sh` [or `quick-test.bat`]  that will run through the process for four sample input files [it creates and deletes the venv] if you want to watch it run as a test at this point.  Note that if you want to check the log for the logic behind the results below, make sure `PRIMARY=webrick`; you will see that these "not found here but found there" test cases are assuming webrick is being searched first.

There are four sample input files:
```
input-minimal.txt.sample    # simple list of part numbers, no color or quantity
input.txt.sample            # Rebrickable inventory csv
input.xml.sample            # Rebrickable inventory xml
input.bricklink.xml.sample  # Bricklink Wanted List XML [Primary difference to RB XML is in the color numbers]
```

The sample input files contain a few different cases [as of this writing; things may change].  Of course, the color-related details don't apply to the minimal case.

```
Part,Color,Quantity
30150,84,81   # part not available on webrick, available on vonado with correct color
6060,70,9     # part not available on webrick, available on vonado but not in the requested color
10169,70,40   # part available on webrick in the wrong color; not available from vonado in correct color, either
15573,28,17   # part available on webrick under alternate mold
4732,72,2     # part not available on either
30374,9999,1  # Part requested in "Any Color"
3648,19,22    # Rebrickable doesn't recognize this part, Bricklink does
```


1. Create and activate a virtual environment:
```
python3 -m venv brick-finder
source brick-finder/bin/activate
```

<details>
  <summary>Windows</summary>
  <br />

  ```
  python -m venv brick-finder
  brick-finder\Scripts\activate
  ```
</details>

5. install the requirements:
```
pip install -r requirements.txt
```

6. Run the script:
```
python brick-finder.py -i input.txt.sample
```
Of course, you can replace `input.txt.sample` with the downloaded inventory file you are interested it.

If the input file is a Bricklink Wanted List XML, you need to specify `-l True` to tell the script that the input file contains Bricklink color numbers.
```
python brick-finder.py -i input.bricklink.xml.sample -l True
```

The terminal output shows Bricklink ID, URL, color status [or "Part Not Found":
```
$ python brick-finder.py -i input.txt.sample

================
Processing input.txt.sample
================
================
Processing input.txt.sample
================
1/7 - 30150 : https://www.vonado.com/box-3x4-30150.html - Color 84 (312) (Medium Dark Flesh) available: True
2/7 - 6060 : https://www.vonado.com/brick-w-arch-1x1x3-1-3-15967.html - Color 70 (192) (Reddish Brown) available: False
3/7 - 10169 : https://www.webrick.com/mini-sack-w-3-2-shaft-10169.html - Color 70 (192) (Reddish Brown) available: False
4/7 - 15573 : https://www.webrick.com/plate-1x2-w-1-knob-3794.html - Color 28 (138) (Dark Tan) available: True
5/7 - 4732 : Part not found: Bracket 8 x 2 x 1 1/3
6/7 - 3666 : https://www.webrick.com/plate-1x6-3666.html - Color 312 (Medium Dark Flesh) used for 'Any Color': True
7/7 - 3648 : https://www.webrick.com/gear-wheel-z24-3648.html - Color 19 (5) (Tan) available: True
```

It also writes an output file that contains more information:
```
 $ cat input.txt-output.txt
Part,Color,Quantity,root,LEGOColor,lots,priceColor,priceColorName,unit,total,name,link,available,color_available
30150,84,81,30150,312,9,312,Medium Dark Flesh,5.73,51.57000000000001,Box / Crate with Handholds,https://www.vonado.com/box-3x4-30150.html,True,True
6060,70,9,6060,192,1,192,Reddish Brown,0,0,Brick Arch 1 x 6 x 3 1/3 Curved Top,https://www.vonado.com/brick-w-arch-1x1x3-1-3-15967.html,True,False
10169,70,40,10169,192,40,192,Reddish Brown,0,0,Bag / Sack with Handle,https://www.webrick.com/mini-sack-w-3-2-shaft-10169.html,True,False
15573,28,17,15573,138,17,138,Dark Tan,0.03,0.51,Plate Special 1 x 2 with 1 Stud with Groove and Inside Stud Holder (Jumper),https://www.webrick.com/plate-1x2-w-1-knob-3794.html,True,True
4732,72,2,4732,199,0,72,Dark Bluish Gray,0,0,Bracket 8 x 2 x 1 1/3,,False,False
3666,9999,15,3666,9999,15,312,Medium Dark Flesh,0.08,1.2,Plate 1 x 6,https://www.webrick.com/plate-1x6-3666.html,True,True
3648,19,22,3648,5,22,5,Tan,0.1,2.2,"LEGO Technic, Gear 24 Tooth (2nd Version - 1 Axle Hole) [Technic, Gear]",https://www.webrick.com/gear-wheel-z24-3648.html,True,True
```
Columns:

| Column | Meaning |
| :--- | :--- |
| Part | Part number as it came from the source |
| Color | Color number as it came from the source |
| Quantity | Part quantity as it came from the source |
| root | Root part number as determined by the script; this is the part number without any printing, mold, or design variation |
| LEGOColor | The Lego color number corresponding to the supplied color|
| lots | Count of lots required [mostly for Vonado at this point, since they sell parts in lots of 10] |
| priceColor | Color number used for pricing [mostly interesting in the "Any Color" case, or if the input file uses Bricklink colors] |
| priceColorName | Name of the pricing color |
| unit | unit cost|
| total | total cost [unit cost * lots] |
| name | Name of part |
| link | Link to store page |
| available | Is this part available at all? |
| color_available | Is this part available in the right color? |


There's also a log file that gets recreated with each run, `app.log`:
```
root - INFO - -- Begin loop for part 30150 quantity 81 in color 84 ---
root - INFO - Begin check for 30150 in color 84 (312)
root - INFO - part not found in correct color; checking Webrick for: 30150 as 30150
root - INFO - part not found in correct color; checking Webrick for: 30150 as 439795
root - INFO - part not found in correct color; checking Vonado for: 30150 as 30150
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 49
root - INFO - Don't have the color yet, and this is the desired color
root - INFO - Found instance of 30150.
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 6060 quantity 9 in color 70 ---
root - INFO - Begin check for 6060 in color 70 (192)
root - INFO - part not found in correct color; checking Webrick for: 6060 as 6060
root - INFO - part not found in correct color; checking Webrick for: 6060 as 218471
root - INFO - part not found in correct color; checking Webrick for: 6060 as 15967
root - INFO - part not found in correct color; checking Webrick for: 6060 as 30935
root - INFO - part not found in correct color; checking Vonado for: 6060 as 6060
root - INFO - part not found in correct color; checking Vonado for: 6060 as 218471
root - INFO - part not found in correct color; checking Vonado for: 6060 as 15967
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 49
root - INFO - Found instance of 6060.
root - INFO - part not found in correct color; checking Vonado for: 6060 as 30935
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 10169 quantity 40 in color 70 ---
root - INFO - Begin check for 10169 in color 70 (192)
root - INFO - part not found in correct color; checking Webrick for: 10169 as 10169
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 9
root - INFO - Found instance of 10169.
root - INFO - part not found in correct color; checking Webrick for: 10169 as 739003
root - INFO - part not found in correct color; checking Webrick for: 10169 as 17833
root - INFO - part not found in correct color; checking Vonado for: 10169 as 10169
root - INFO - part not found in correct color; checking Vonado for: 10169 as 739003
root - INFO - part not found in correct color; checking Vonado for: 10169 as 17833
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 15573 quantity 17 in color 28 ---
root - INFO - Begin check for 15573 in color 28 (138)
root - INFO - part not found in correct color; checking Webrick for: 15573 as 15573
root - INFO - part not found in correct color; checking Webrick for: 15573 as 3794a
root - INFO - part not found in correct color; checking Webrick for: 15573 as 3794b
root - INFO - part not found in correct color; checking Webrick for: 15573 as 3794
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 21
root - INFO - Don't have the color yet, and this is the desired color
root - INFO - Found instance of 15573.
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 4732 quantity 2 in color 72 ---
root - INFO - Begin check for 4732 in color 72 (199)
root - INFO - part not found in correct color; checking Webrick for: 4732 as 4732
root - INFO - part not found in correct color; checking Webrick for: 4732 as 716610
root - INFO - part not found in correct color; checking Vonado for: 4732 as 4732
root - INFO - part not found in correct color; checking Vonado for: 4732 as 716610
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 3666 quantity 15 in color 9999 ---
root - INFO - Begin check for 3666 in color 9999 (9999)
root - INFO - part not found in correct color; checking Webrick for: 3666 as 3666
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 52
root - INFO - new low price: 0.09 for 1.
root - INFO - new low price: 0.08 for 312.
root - INFO - Found instance of 3666.
root - INFO - --- Done ---
root - INFO - -- Begin loop for part 3648 quantity 22 in color 19 ---
root - INFO - Rebrickable doesn't recognize part 3648
root - INFO - Bricklink recognizes part 3648
root - INFO - Bricklink alternates found for part 3648
root - INFO - Begin check for 3648 in color 19 (5)
root - INFO - part not found in correct color; checking Webrick for: 3648 as 3648
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 50
root - INFO - Don't have the color yet, and this is the desired color
root - INFO - Found instance of 3648.
root - INFO - --- Done ---
```

## Dollar Tree bricks:
Dollar Tree stores in the US carry "Make-it" brand clone bricks in a limited number of parts and colors.  

For system bricks, there are three different SKUs in-store, with the following contents:

| Brick | Name | SKU 1 [48 for $1] | SKU 2 [48 for $1] | SKU 3  [100 for $1] |
| :--- | :--- | :--- | :--- | :--- |
| 2456 | 2x6 brick | 6 |  |  |
| 3001 | 2x4 brick | 10 | 2 | 16 |
| 3002 | 2x3 brick |  | 3 | 16 |
| 3003 | 2x2 brick | 6 | 5 | 16 |
| 3010 | 1x4 brick | 6 | 3 | 16 |
| 3004 | 1x2 brick |  | 3 | 16 |
| 3005 | 1x1 brick |  |  | 20 |
| 3020 | 2x4 plate | 5 | 6 |  |
| 3021 | 2x3 plate |  | 3 |  |
| 3022 | 2x2 plate | 5 | 9 |  |
| 3666 | 1x6 plate | 5 |  |  |
| 3710 | 1x4 plate | 5 | 8 |  |
| 3023 | 1x2 plate |  | 6 |  |
<!-- | 3795 | 2x6 plate |  |  |  | -->
<!-- | 3024 | 1x1 plate |  |  |  | -->

SKU 1 and 2 are typically available in-store in a variety of colors.  This tool only accounts for the online colors until I'm able to come up with a comprehensive list of the in-store colors.  SKU 3 is evenly divided into grey, green, blue, and brown.

Online the SKU 2 product shows somewhat different colors if you're buying individually [black, white, red, blue, yellow, green] or by the case [blue, gray, green, red, yellow].  Brown and other colors are typically available in-store, but aren't listed in this tool yet.

The tool also knows about the 32x32 baseplates in blue, brown, gray, and green.

In-store there are also a variety of bags of windows and plants and the like. Those may be added here at some point, but they're pretty ;limited.  For example, there's a bag of "Roofs" which is 4 2x8 plates and 4 6x8 plates for $1.  That's 12.5 cents per brick, which isn't bad, but they're only in reddish brown.  Also, in the "Plants" bag there's a 1x1 "bush" that doesn't have a Lego equivalent and in the "Windows and Doors"  pack there are 1x4x3 window frames that don't exactly match a Lego part as well.

If "DOLLAR_TREE_ENABLED" is set to true in your env, these parts will be called out as available at Dollar Tree and the web search won't get run.

Note that this will throw off pricing, since these bricks are priced individually even though they're not available individually. Future plans are to track how many packages are needed, combining all the Dollar Tree bricks.  For example, if you need 25 2x4 bricks, 8 1x6 plates, and 10 2x4 plates in blue, you need three of the one Dollar Tree bag for a total of $3 rather than 43 individual bricks for 86 cents.

## Notes:

This script invokes a search just like the search field on Webricks and Vonado [sequence depends on the `PRIMARY` setting] website.  If there are results returned, it then looks through them for a result where the part URL contains the part ID (without additional numbers) and does not contain "moc".  For example, if you're searching for "3004" you'll get these results:
- https://www.vonado.com/brick-1x2-3004.html
- https://www.vonado.com/cavity-w-leads-30046.html
- https://www.vonado.com/window-1x2x2-2-3-with-rounded-top-30044.html
- https://www.vonado.com/cavity-w-iron-lattice-30045.html
- https://www.vonado.com/plate-1x4-w-rev-hook-30043.html
- https://www.vonado.com/moc-30043-land-rover-defender-110.html

You only want the first, so a match is considered: "contains the part ID, preceded by a dash, followed by a dash or period"

In this specific case, the "moc" filter is redundant, but it could be that some MOC will have the same number as a part, so we explicitly skip them.

If a part is not found on the first site [webrick or vonado], then the other is searched.
If a part is found on the first site, but not in the desired color, then the second is searched and the part info is only updated if the color is found on the second site.

You may want to search Webricks first because parts are sold by the each there.  Vonado parts are always lots of 10.  Personally I typically order from Vonado since I like building up the stock of spares.

The script grabs the alternate molds and IDs from rebrickable for each part and searches for those as well.  If rebrickable doesn't recognize the part, it searches bricklink for the part and any alternates.  This *should* mean that a "Part not found" truly means it is not found on either Webricks or Vonado.

# Color checking:

Vonado and Webrick appear to use the same server software; there's a javascript tag in the page that contains a JSON object listing available colors and prices for the part.  This script finds that tag, then parses the JSON object to extract color information.  This is of course fragile, but it's the best we have.  A previous version of this script loaded the page through Selenium and dug through the swatch block; that was abandoned since it was slower and didn't provide pricing information.

Webrick, especially, seems to run into sporadic trouble building that JSON object of colors and prices [in this case that script tag contains a PHP error rather than valid JSON].  For this reason, the script tries 12 [twelve] times to load the page and get a valid piece of color-listing JSON.  If that fails, there will be a note to this effect in the console output and the color availability will be "False". 

I haven't seen this happen with Vonado, at least not with the frequency that it happens with Webrick.

In the "Any Color" case, it loops through all the colors in which the part is available and picks the first one with the lowest price.  More often than not this is white since usually all the colors are the same price and white is the first color listed, if it is listed.  The log above shows a part where white *wasn't* the cheapest.

# Edge cases

There may be some oddball parts I'm not handling well; one old example was:
https://www.vonado.com/flat-tile-1x2-3069-trans-clear.html

That page has been removed, but it used to have no color chart, and no lot size.  The title of the page listed just one color, and pricing was in line with a lot of 10 of 1x2 plates, so it wasn't exactly clear what to do with that.  At the time it was the only result for 3069 1x2 tile on either site.  It seems like now Vonado ]at least] has this part in multiple colors.

## Roadmap

Features
- web UI
- ~~Support Dollar Tree~~
  - Merge Dollar Tree SKU quantities [you have to buy a bag of 48 assorted bricks, you can't buy just one 2x4 brick]
  - Expand Dollar Tree part availability list [add standard window, roof, etc bags]
  - include bricks in prepackaged sets
- compare against your own spares collection
  - Maybe based on a rebrickable parts list?
- support for other sites
  - ~~webrick [looks to be same site backend as Vonado]~~
  - AliExpress [extracting results will be even more fragile; maybe focus on specific stores]
  - GoBricks [may be a non-starter since it doesn't appear to use common part or color numbers]
- Add parts to a shopping cart [seems dicey, need to manage login state]
- Read and/or produce Excel docs
- ~~support for exported BrickLink wanted list XML~~
- ~~search for alternate brick IDs and molds~~
- ~~local database to store alternate part numbers~~ [not needed, loaded on the fly]
- ~~Verify color availability [will require loading the page via selenium since the chart appears to be loaded by JS; also hampered by remarks above about vagary in color names and numbers]~~
- ~~Calc how many lots you need to buy~~
- ~~Make the input file parsing a little more robust.~~ Now uses Rebrickable CSV as default.
- ~~Calc ballpark cost~~
- ~~account for varying prices per part~~
- ~~pick the cheapest color for "Any Color" parts~~

Tech Debt:
- refactor into modules
