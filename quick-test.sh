#!/bin/bash

clear
echo "Setting up virtual environment"
python3 -m venv brick-finder-test-env
source brick-finder-test-env/bin/activate

echo "-----------------------------------------"
echo "Installing requirements"
pip install -r requirements.txt

clear
echo "-----------------------------------------"
echo "running minimal file"
echo "input file:"
cat input-minimal.txt.sample
echo "Running script:"
python brick-finder.py -i input-minimal.txt.sample
echo "output file:"
cat input-minimal.txt-output.txt
cp app.log input-minimal.txt.log

echo "-----------------------------------------"
echo "running Rebrickable csv"
echo "input file:"
cat input.txt.sample
echo "Running script:"
python brick-finder.py -i input.txt.sample
echo "output file:"
cat input.txt-output.txt
cp app.log input.txt.log

echo "-----------------------------------------"
echo "running Rebrickable XML"
echo "input file:"
cat input.xml.sample
echo "Running script:"
python brick-finder.py -i input.xml.sample
echo "output file:"
cat input.xml-output.txt
cp app.log input.xml.log

echo "-----------------------------------------"
echo "running BrickLink Wanted List XML"
echo "input file:"
cat input.bricklink.xml.sample
echo "Running script:"
python brick-finder.py -i input.bricklink.xml.sample -l True
echo "output file:"
cat input.bricklink.xml-output.txt
cp app.log input.bricklink.xml.log

echo "-----------------------------------------"
echo "cleaning up"
rm -fr brick-finder-test-env
rm -f input*-output.txt
