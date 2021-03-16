So you have a list of bricks from some MOC or something and you want to find out which ones are available from Vonado.

There's a lot of them, so all the clicking is a pain.

This dumb script can help.  It's pretty brittle and works for me.

ATENTION - BREAKING CHANGE: 
The default input format is now Rebrickable CSV.  My goofy private format is retired for now.

## Assumptions:
- You have a list of bricks in Rebrickable CSV format. [It can also be a list of one Bricklink ID per line]
- Python 3
- Running Linux or Mac OS X  [That's only if you're going to copy-paste the commands here; no reason this won't run on Windows]

## Getting started:
Clone the repo.
```
git clone https://github.com/chazlarson/vonado-bricks.git && cd vonado-bricks
```

There's a `quick-test.sh` that will run through the rest of this for both sample input files [it creates and deletes the venv] if you just want to watch it.

Create and activate a virtual environment:
```
python3 -m venv vonado-bricks
source vonado-bricks/bin/activate
```

install the requirements:
```
pip install -r requirements.txt
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
87994 : Part not found
30374 : Part not found
63965 : https://www.vonado.com/stick-6m-w-flange-63965.html
11090 : https://www.vonado.com/bar-holder-with-clip-11090.html
23443 : https://www.vonado.com/3-2-shaft-w-3-2-hole-23443.html
99781 : https://www.vonado.com/angular-plate-1-5-top-1x2-1-2-99781.html
99780 : https://www.vonado.com/angular-plate-1-5-bot-1x2-1-2-99780.html
10201 : Part not found
```

It also writes an `output.txt` that contains more information:
```
 $ cat output.txt
Part,Color,Quantity,lotCount,unit_price,total_price,link
87994,0,2
30374,0,2
63965,0,4,1,0.27,0.27,https://www.vonado.com/stick-6m-w-flange-63965.html
11090,0,2,1,0.27,0.27,https://www.vonado.com/bar-holder-with-clip-11090.html
23443,0,2,1,0.36,0.36,https://www.vonado.com/3-2-shaft-w-3-2-hole-23443.html
99781,0,7,1,0.55,0.55,https://www.vonado.com/angular-plate-1-5-top-1x2-1-2-99781.html
99780,0,3,1,0.55,0.55,https://www.vonado.com/angular-plate-1-5-bot-1x2-1-2-99780.html
10201,0,2
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
