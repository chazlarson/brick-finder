So you have a list of bricks from some MOC or something and you want to find out which ones are available from Webricks or Vonado.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.  It's pretty brittle and works for me.

## Assumptions:
- You have a list of bricks in one of the following formats:
  - Rebrickable CSV
  - Bricklink XML
  - One Bricklink part ID per line [with a header row]
- Python 3
- Running Mac OS X [or probably Linux; I haven't seen the selenium setup work there]
- Rebrickable API Key

## Getting started:
Clone the repo.
```
git clone https://github.com/chazlarson/vonado-bricks.git && cd vonado-bricks
```

Create an environment file at `.env`:
```
RB_API_KEY=BINGBANGBOING
BROWSER=firefox
```

Available [not necessarily working] settings for `BROWSER` are:
```
  chrome
  chromium
  firefox
  msie
  edge
```

Selenium setup:

Mac OS X: 
- Install the browser matching the setting in `.env`
  - only `chrome` and `firefox` working presently

Linux: 
- TBD

Windows: 
- TBD

There's a `quick-test.sh` that will run through the rest of this for all three sample input files [it creates and deletes the venv] if you just want to watch it.  

The sample input file contains a few different cases:
```
Part,Color,Quantity
32064a,4,81 # part not available on webrick, available on vonado with correct color
32064a,5,9  # part not available on webrick, available on vonado but not in the requested color
63965,0,40  # part available on webrick in the wrong color; not available from vonado in correct color, either
2444,0,17   # part available on webrick under alternate mold
4732,72,2   # part not available on either
```

Create and activate a virtual environment:
```
python3 -m venv vonado-bricks
source vonado-bricks/bin/activate
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


====== WebDriver manager ======
Current firefox version is 89.0.2
Get LATEST driver version for 89.0.2
Driver [/Users/chazlarson/.wdm/drivers/geckodriver/macos/v0.29.1/geckodriver] found in cache


================
Processing input.txt.sample
================
1/5 - 32064a : https://www.vonado.com/brick-1x2-with-cross-hole-32064.html - Color 4 (21) : True
2/5 - 32064a : https://www.vonado.com/brick-1x2-with-cross-hole-32064.html - Color 5 (221) : False
3/5 - 63965 : https://www.webrick.com/stick-6m-w-flange-63965.html - Color 0 (26) : False
4/5 - 2444 : https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html - Color 0 (26) : True
5/5 - 4732 : Part not found: Bracket 8 x 2 x 1 1/3
```

It also writes a csv that contains more information:
```
$ cat input.txt-output.csv
Part,Color,Quantity,root,LEGOColor,lots,unit,total,link,available,color_available
32064a,4,81,32064,21,9,0.8,7.2,https://www.vonado.com/brick-1x2-with-cross-hole-32064.html,True,True
32064a,5,9,32064,221,1,0.8,0.8,https://www.vonado.com/brick-1x2-with-cross-hole-32064.html,True,False
63965,0,40,63965,26,40,0.03,1.2,https://www.webrick.com/stick-6m-w-flange-63965.html,True,False
2444,0,17,2444,26,17,0.07,1.1900000000000002,https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html,True,True
4732,72,2,4732,199,0,0,0,,False,False
```

## Notes:

This script invokes a search just like the search field on the Webricks [and posibly Vonado] website.  If there are results returned, it then looks through them for a result where the part URL contains the Bricklink ID (without additional numbers) and does not contain "moc".  For example, if you're searching for "3004" you'll get these results:
- https://www.vonado.com/brick-1x2-3004.html
- https://www.vonado.com/cavity-w-leads-30046.html
- https://www.vonado.com/window-1x2x2-2-3-with-rounded-top-30044.html
- https://www.vonado.com/cavity-w-iron-lattice-30045.html
- https://www.vonado.com/plate-1x4-w-rev-hook-30043.html
- https://www.vonado.com/moc-30043-land-rover-defender-110.html

You only want the first, so a match is considered: "contains the bricklink ID, preceded by a dash, followed by a dash or period"

In this specific case, the "moc" filter is redundant, but it could be that some MOC will have the same number as a part, so belt-and-suspenders.

If a part is not found on Webricks, then Vonado is searched.
If a part is found on Webricks, but not in the desired color, then Vonado is searched and the part info is only updated if the color is found on Vonado.

Webricks is searched first because parts are sold by the each there.  Vonado is always lots of 10.

The script grabs the alternate molds from rebrickable for each part and searches for those as well.  This *should* mean that a "Part not found" truly means it is not found on either Webricks or Vonado.

Color is checked by loading the page via selenium and looking for a color swatch that contains the Lego color number. I'm assuming that the input file contains rebrickable color numbers.

## Future possibilities

- support for other sites
  - ~~webrick [looks to be same site backend as Vonado]~~
  - AliExpress [extracting results will be fragile]
- ~~local database to store alternate part numbers~~ [not needed, loaded on the fly]
- support for exported BrickLink wanted list XML
- ~~Verify color availability [will require loading the page via selenium since the chart appears to be loaded by JS; also hampered by remarks above about vagary in color names and numbers]~~
- Add parts to a shopping cart
- Read and/or produce Excel docs
- ~~Calc how many lots you need to buy (should be trivial if all parts are in lots of ten but I don't know that to be true)~~
- ~~Make the input file parsing a little more robust.~~ Now uses Rebrickable CSV as default.
- ~~Calc ballpark cost~~
