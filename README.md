So you have a list of bricks from some MOC or something and you want to find out which ones are available from Webricks or Vonado.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.  It's pretty brittle and works for me.

## Assumptions:
- You have a list of bricks in one of the following formats:
  - Rebrickable CSV or XML
  - One Bricklink part ID per line [with a header row]
- Python 3
  - https://www.python.org/
- git
  - https://git-scm.com/download
- Running Mac OS X, Linux, Windows
- Rebrickable API Key

## Getting started:
Clone the repo.
```
git clone https://github.com/chazlarson/vonado-bricks.git && cd vonado-bricks
```

Create an environment file at `.env`:
```
RB_API_KEY=BINGBANGBOING
PRIMARY=webrick
```
Available settings for `PRIMARY` are:
```
  webrick [anything else here will search Vonado first]
```

There's a `quick-test.sh` that will run through the rest of this for all three sample input files [it creates and deletes the venv] if you just want to watch it.  

The sample input file contains a few different cases:
```
Part,Color,Quantity
32064a,4,81  # part not available on webrick, available on vonado with correct color
32064a,5,9   # part not available on webrick, available on vonado but not in the requested color
63965,0,40   # part available on webrick in the wrong color; not available from vonado in correct color, either
2444,0,17    # part available on webrick under alternate mold
4732,72,2    # part not available on either
30374,9999,1 # Part requested in "Any Color"
```

Create and activate a virtual environment:
```
python3 -m venv vonado-bricks
source vonado-bricks/bin/activate
```
Windows?
```
python -m venv vonado-bricks
vonado-bricks\Scripts\activate
```

install the requirements:
```
pip install -r requirements.txt
```

Run the script:
```
python vonado-bricks.py -i input.txt.sample
```

The terminal output shows output with Bricklink ID, URL, color status [or "Part Not Found":
```
$ python vonado-bricks.py -i input.txt.sample

================
Processing input.txt.sample
================
1/6 - 32064a : https://www.vonado.com/brick-1x2-with-cross-hole-32064.html - Color 4 (21) (Red) available: True
2/6 - 32064a : https://www.vonado.com/brick-1x2-with-cross-hole-32064.html - Color 5 (221) (Dark Pink) available: False
3/6 - 63965 : https://www.webrick.com/stick-6m-w-flange-63965.html - Color 0 (26) (Black) available: False
4/6 - 2444 : https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html - Color 0 (26) (Black) available: False
5/6 - 4732 : Part not found: Bracket 8 x 2 x 1 1/3
6/6 - 3666 : https://www.webrick.com/plate-1x6-3666.html - Color 312 (Medium Dark Flesh) used for 'Any Color': True
```

It also writes a csv that contains more information:
```
$ cat input.txt-output.csv
Part,Color,Quantity,root,LEGOColor,lots,priceColor,priceColorName,unit,total,name,link,available,color_available
32064a,4,81,32064,21,9,21,Red,0.82,7.38,Technic Brick 1 x 2 with Axle Hole Type 1 [+ Opening] and Bottom Pin,https://www.vonado.com/brick-1x2-with-cross-hole-32064.html,True,True
32064a,5,9,32064,221,1,221,Dark Pink,0,0,Technic Brick 1 x 2 with Axle Hole Type 1 [+ Opening] and Bottom Pin,https://www.vonado.com/brick-1x2-with-cross-hole-32064.html,True,False
63965,0,40,63965,26,40,26,Black,0,0,Bar 6L with Stop Ring,https://www.webrick.com/stick-6m-w-flange-63965.html,True,False
2444,0,17,2444,26,17,26,Black,0,0,Plate Special 2 x 2 with 1 Pin Hole [Split Underside Ribs],https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html,True,False
4732,72,2,4732,199,0,72,Dark Bluish Gray,0,0,Bracket 8 x 2 x 1 1/3,,False,False
3666,9999,15,3666,9999,15,312,Medium Dark Flesh,0.08,1.2,Plate 1 x 6,https://www.webrick.com/plate-1x6-3666.html,True,True
```

There's also a log file that gets recreated with each run, `app.log`:
```
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 32064a in color 4 (21) 
root - INFO - part not found yet; checking Webrick for: 32064a as 32064
root - INFO - part not found yet; checking Webrick for: 32064a as 32064b
root - INFO - part not found yet; checking Webrick for: 32064a as 32064c
root - INFO - part not found yet; checking Vonado for: 32064a as 32064
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 49
root - INFO - Don't have the color yet, and this is the desired color
root - INFO - Found instance of 32064a.
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 32064a in color 5 (221) 
root - INFO - part not found yet; checking Webrick for: 32064a as 32064
root - INFO - part not found yet; checking Webrick for: 32064a as 32064b
root - INFO - part not found yet; checking Webrick for: 32064a as 32064c
root - INFO - part not found yet; checking Vonado for: 32064a as 32064
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 49
root - INFO - Found instance of 32064a.
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 63965 in color 0 (26) 
root - INFO - part not found yet; checking Webrick for: 63965 as 63965
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 1
root - INFO - Found instance of 63965.
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 2444 in color 0 (26) 
root - INFO - part not found yet; checking Webrick for: 2444 as 2444
root - INFO - part not found yet; checking Webrick for: 2444 as 10247
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - INFO - swatches found: 49
root - INFO - Found instance of 2444.
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 4732 in color 72 (199) 
root - INFO - part not found yet; checking Webrick for: 4732 as 4732
root - INFO - part not found yet; checking Vonado for: 4732 as 4732
root - INFO - ---------------------------------------------------
root - INFO - Begin check for 3666 in color 9999 (9999) 
root - INFO - part not found yet; checking Webrick for: 3666 as 3666
root - ERROR - Error while getting base price: 'NoneType' object is not subscriptable
root - INFO - extracting color data from page via script tags
root - INFO - color data retrieval attempt: 1
root - ERROR - Could not find color information in page: Expecting value: line 5 column 31 (char 130)
root - INFO - Didn't find any color data
root - INFO - color data retrieval attempt: 2
root - INFO - swatches found: 52
root - INFO - new low price: 0.09 for 1.
root - INFO - new low price: 0.08 for 312.
root - INFO - Found instance of 3666.
```

## Notes:

This script invokes a search just like the search field on Webricks and Vonado [sequence depends on the `PRIMARY` setting] website.  If there are results returned, it then looks through them for a result where the part URL contains the Bricklink ID (without additional numbers) and does not contain "moc".  For example, if you're searching for "3004" you'll get these results:
- https://www.vonado.com/brick-1x2-3004.html
- https://www.vonado.com/cavity-w-leads-30046.html
- https://www.vonado.com/window-1x2x2-2-3-with-rounded-top-30044.html
- https://www.vonado.com/cavity-w-iron-lattice-30045.html
- https://www.vonado.com/plate-1x4-w-rev-hook-30043.html
- https://www.vonado.com/moc-30043-land-rover-defender-110.html

You only want the first, so a match is considered: "contains the bricklink ID, preceded by a dash, followed by a dash or period"

In this specific case, the "moc" filter is redundant, but it could be that some MOC will have the same number as a part, so belt-and-suspenders.

If a part is not found on the first, then the other is searched.
If a part is found on the first, but not in the desired color, then the second is searched and the part info is only updated if the color is found on the second site.

You may want to search Webricks first because parts are sold by the each there.  Vonado parts are always lots of 10.  Personally I typically order from Vonado since I like building up the stock of spares.

The script grabs the alternate molds from rebrickable for each part and searches for those as well.  This *should* mean that a "Part not found" truly means it is not found on either Webricks or Vonado.

# Color checking:

Vonado and Webrick appear to use the same server software; there's a javascript tag in the page that contains a JSON object listing available colors and prices for the part.  This script finds that tag, then parses the JSON object to extract color information.  This is of course fragile, but it's the best we have.

Webrick, especially, seems to run into sporadic trouble building that JSON object [in this case that script tag contains a PHP error rather than valid JSON].  For this reason, the script tries 12 [twelve] times to load the page and get a valid piece of color-listing JSON.  If that fails, there will be a note to this effect in the console output and the color availability will be "False". 

I haven't seen this happen with Vonado, at least not with the frequency that it happens with Webrick.

In the "Any Color" case, it loops through all the colors that the part is available in and picks the first one with the lowest price.  More often than not this is white since usually all the colors are the same price and white is the first color listed, if it is listed.  The log above shows a part where white *wasn't* the cheapest.

# Edge cases

There are some oddball parts I'm not handling well; for example:
https://www.vonado.com/flat-tile-1x2-3069-trans-clear.html

That page has no color chart, and no lot size.  The title of the page seems to indicate it's just one color, and pricing is in line with a lot of 10 of 1x2 plates:
https://www.vonado.com/plate-1x2-3023.html

so it's not exactly clear what to do with that.  It is the only result for 3069 1x2 tile on either site as of this writing.

## Future possibilities

- support for other sites
  - ~~webrick [looks to be same site backend as Vonado]~~
  - AliExpress [extracting results will be fragile]
- support for exported BrickLink wanted list XML
- Add parts to a shopping cart
- Read and/or produce Excel docs
- ~~local database to store alternate part numbers~~ [not needed, loaded on the fly]
- ~~Verify color availability [will require loading the page via selenium since the chart appears to be loaded by JS; also hampered by remarks above about vagary in color names and numbers]~~
- ~~Calc how many lots you need to buy (should be trivial if all parts are in lots of ten but I don't know that to be true)~~
- ~~Make the input file parsing a little more robust.~~ Now uses Rebrickable CSV as default.
- ~~Calc ballpark cost~~
- ~~account for varying prices per part~~
- ~~pick the cheapest color for "Any Color" parts~~
