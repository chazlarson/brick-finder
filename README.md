So you have a list of bricks from some MOC or something and you want to find out which ones are available from Vonado.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.  It's pretty brittle and works for me.

## Assumptions:
- You have a list of bricks in one of the following formats:
  - Rebrickable CSV
  - Bricklink XML
  - One Bricklink part ID per line [with a header row]
- Python 3
- Running Linux or Mac OS X  [That's only if you're going to copy-paste the commands here; no reason this won't run on Windows]

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

Run the script:
```
python vonado-bricks.py -i input.txt.sample
```

The terminal output shows output with Bricklink ID and URL [or "Part Not Found":
```
 $ python vonado-bricks.py -i input.txt.sample
3030 : https://www.vonado.com/plate-4x10-3030.html
63965 : https://www.vonado.com/stick-6m-w-flange-63965.html
3005 : https://www.vonado.com/brick-1x1-3005.html
3005 : https://www.vonado.com/brick-1x1-3005.html
2444 : Part not found
```

It also writes an `output.txt` that contains more information:
```
 $ cat output.txt
Part,Color,Quantity,lots,unit,total,link
3030,0,12,2,2.91,5.82,https://www.vonado.com/plate-4x10-3030.html
63965,0,40,4,0.27,1.08,https://www.vonado.com/stick-6m-w-flange-63965.html
3005,0,6,1,0.36,0.36,https://www.vonado.com/brick-1x1-3005.html
3005,1,8,1,0.36,0.36,https://www.vonado.com/brick-1x1-3005.html
2444,0,17
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

In this specific case, the "moc" filter is redundant, but it could be that some MOC will have the same number as a part, so belt-and-suspenders.

This means that "Part not found" doesn't *necessarily* mean the part isn't on Vonado, but the script will cut down the number of parts you need to search for manually.

For example:
```
2444 : Part not found
```
That part *is* on Vonado:
https://www.vonado.com/plate-2x2-one-hule-4-8-10247.html

But the URL doesn't contain the Bricklink ID [or really anything one could use to match them], so it shows up here as "not found"

Currently no attention is paid to color.  If you have two colors of the part in your list:
```
4162	0	1
4162	1	1
```
You'll get two lines in the output (and two rows in the output file):
```
...
4162 : https://www.vonado.com/flat-tile-1x8-4162.html
4162 : https://www.vonado.com/flat-tile-1x8-4162.html
...
```

Then the possible pain point is that this list will imply it's available at Vonado but you'll go there and find out it's not avaiable in Light Bluish Grey or whatever.

Color is tricky.  Vonado *seems* to use LEGO color IDs and Bricklink/Rebrickable color names:

For example:

![image](https://user-images.githubusercontent.com/3865541/111374320-f4ffeb00-866a-11eb-9e6d-eae511fa42fb.png)

Two names and four numbers for the same color:

![image](https://user-images.githubusercontent.com/3865541/111374636-588a1880-866b-11eb-8151-08167ca001d3.png)

Source: https://rebrickable.com/colors/

## Future possibilities

- support for exported BrickLink wanted list XML
- Verify color availability [will require loading the page via selenium since the chart appears to be loaded by JS; also hampered by remarks above about vagary in color names and numbers]
- Add parts to a shopping cart
- Read and/or produce Excel docs
- ~~Calc how many lots you need to buy (should be trivial if all parts are in lots of ten but I don't know that to be true)~~
- ~~Make the input file parsing a little more robust.~~ Now uses Rebrickable CSV as default.
- ~~Calc ballpark cost~~
