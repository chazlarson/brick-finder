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

## Getting started:
Clone the repo.
```
git clone https://github.com/chazlarson/vonado-bricks.git && cd vonado-bricks
```

There's a `quick-test.sh` that will run through the rest of this for all three sample input files [it creates and deletes the venv] if you just want to watch it.

Create and activate a virtual environment:
```
python3 -m venv vonado-bricks
source vonado-bricks/bin/activate
```

install the requirements:
```
pip install -r requirements.txt
```

INSTALL SOME SELENIUM STUFF TO BE FILLED IN SOON

Run the script:
```
python vonado-bricks.py -i input.txt.sample
```

The terminal output shows output with Bricklink ID, URL, color status [or "Part Not Found":
```
 $ python vonado-bricks.py -i input.txt.sample
1/6 - 3030 : https://www.webrick.com/plate-4x10-3030.html - Color 0 (26) : True
2/6 - 63965 : https://www.vonado.com/stick-6m-w-flange-63965.html - Color 0 (26) : True
3/6 - 3005 : https://www.webrick.com/brick-1x1-3005.html - Color 0 (26) : True
4/6 - 3005 : https://www.webrick.com/brick-1x1-3005.html - Color 1 (23) : True
5/6 - 2444 : https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html - Color 0 (26) : True
6/6 - 41769 : https://www.webrick.com/right-plate-2x4-w-angle-41769.html - Color 72 (199) : False
```

It also writes a csv that contains more information:
```
 $ cat input.txt-output.csv
Part,Color,Quantity,root,LEGOColor,lots,unit,total,link,available,color_available
3030,0,12,3030,26,12,0.73,8.76,https://www.webrick.com/plate-4x10-3030.html,True,True
63965,0,40,63965,26,4,0.27,1.08,https://www.vonado.com/stick-6m-w-flange-63965.html,True,True
3005,0,6,3005,26,6,0.04,0.24,https://www.webrick.com/brick-1x1-3005.html,True,True
3005,1,8,3005,23,8,0.04,0.32,https://www.webrick.com/brick-1x1-3005.html,True,True
2444,0,17,2444,26,17,0.07,1.1900000000000002,https://www.webrick.com/plate-2x2-one-hule-4-8-10247.html,True,True
41769,72,47,41769,199,47,0.08,3.7600000000000002,https://www.webrick.com/right-plate-2x4-w-angle-41769.html,True,False
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

The script grabs the alternate molds from rebrickable for each part and searches for those as well.  This *should* mean that a "Part not found" truly m,eans it is not found on either Webricks or Vonado.

Color is checked by loading the page via selenium and looking for a color swatch that contains the lego color number. I'm assuming that the input file contains rebrickable color numbers.

If a part is not found on Webricks, then Vonado is searched.
If a part is found on Webricks, but not in the desired color, then Vonado is searched and the part i is only updated if the color is found on Vonado.

I search Webricks first because parts are sold by the each there.  Vonado is always lots of 10.

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
