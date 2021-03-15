So you have a list of bricks from some MOC or something and you want to find out which ones are available from Vonado.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.

## Assumptions:
- You have a tab-delimited list of bricks. This can be either one Bricklink Item Number per line OR my typical format of BLItemNo, ElementId, PartName, ColorName, Qty.
- Python 3
- Running Linux or Mac OS X  [That's only if you're going to copy-paste the commands here; no reason this won't run on Windows]

## Getting started:
Clone the repo.
```
git clone https://github.com/chazlarson/vonado-bricks.git && cd vonado-bricks
```

Create and activate a virtual environment:
```
python3 -m venv vonado-bricks
source vonado-bricks/bin/activate
```

Copy the sample input file:
```
cp input.txt.sample input.txt
```

Run the script:
```
python vonado-bricks.py
```

The terminal output shows output with Bricklink ID and URL [or "Part Not Found":
```
 $ python vonado-bricks.py
2429 -  - Hinge Plate 1 x 4 Swivel Base : Part not found
2430 -  - Hinge Plate 1 x 4 Swivel Top : Part not found
2444 - 244426 - Plate, Modified 2 x 2 with Pin Hole : Part not found
2540 : https://www.vonado.com/plate-1x2-w-stick-2540.html
2921 : https://www.vonado.com/1x1-technic-changeover-catch-2921-28917.html
3004 : https://www.vonado.com/brick-1x2-3004.html
3007 - 6037390 - Brick 2 x 8 : Part not found
3020 : https://www.vonado.com/plate-2x4-3020.html
3023 : https://www.vonado.com/plate-1x2-3023.html
```

It also writes an `output.csv` that contains more information:
```
 $ cat output.csv
2429		Hinge Plate 1 x 4 Swivel Base	Black	1
2430		Hinge Plate 1 x 4 Swivel Top	Black	1
2540	4140588	Plate, Modified 1 x 2 with Handle on Side - Free Ends	Black	1	https://www.vonado.com/plate-1x2-w-stick-2540.html
2921	6170566	Brick, Modified 1 x 1 with Handle	Black	1	https://www.vonado.com/1x1-technic-changeover-catch-2921-28917.html
3004	4211088	Brick 1 x 2	Dark Bluish Gray	1	https://www.vonado.com/brick-1x2-3004.html
3020	4211065	Plate 2 x 4	Dark Bluish Gray	1	https://www.vonado.com/plate-2x4-3020.html
3023	4211063	Plate 1 x 2	Dark Bluish Gray	1	https://www.vonado.com/plate-1x2-3023.html
```

## Notes:

This script invokes a search just like the search field on the Vonado website.  If there are results returned, it then looks through them for a result where the part URL contains the Bricklink ID (without additional numbers) and does not contain "moc".  For example, if you're searching for "3004" you'll get these results:
- https://www.vonado.com/brick-1x2-3004.html
- https://www.vonado.com/cavity-w-leads-30046.html
- https://www.vonado.com/window-1x2x2-2-3-with-rounded-top-30044.html
- https://www.vonado.com/cavity-w-iron-lattice-30045.html
- https://www.vonado.com/plate-1x4-w-rev-hook-30043.html
- https://www.vonado.com/moc-30043-land-rover-defender-110.html

You only want the first, so a match is considered: "contains the bricklink ID, preceded by a dash, followed by a dash or period"

In this specific case, the "moc" filter is redundant, but it could be that soem moc will have the same number as a part, so belt-and-suspenders.

This means that "Part not found" doesn't *necessarily* mean the part isn't on Vonado, but the script will cut down the number of parts you need to search for manually.

For example:
```
2444 - 244426 - Plate, Modified 2 x 2 with Pin Hole : Part not found
```
That part *is* on Vonado:
https://www.vonado.com/plate-2x2-one-hule-4-8-10247.html

But the URL doesn't contain the BLID [or really anything one could use to match them], so it shows up here as "not found"

Currently no attention is paid to color.  If you have two colors of the part in your list:
```
4162	5210651	Tile 1 x 8	Dark Bluish Gray	1
4162	4211481	Tile 1 x 8	Light Bluish Gray	1
```
You'll get two lines in the output (and two rows in the csv):
```
...
4162 : https://www.vonado.com/flat-tile-1x8-4162.html
4162 : https://www.vonado.com/flat-tile-1x8-4162.html
...
```

Then the possible pain point is that this list will imply it's available at Vonado but you'll go there and find out it's not avaiable in Light Bluish Grey or whatever.

## Roadmap

- Calc how many lots you need to buy (should be trivial if all parts are in lots of ten but I don't know that to be true)
- Make the input file parsing a little more robust.
- Verify color availability
- Add parts to a shopping cart
