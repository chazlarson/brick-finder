#!/bin/bash

clear
echo "Setting up virtual environment"
python3 -m venv vonado-brick-test-env
source vonado-brick-test-env/bin/activate

clear
echo "Installing requirements"
pip install -r requirements.txt

clear
echo "running minimal file"
echo "input file:"
cat input-minimal.txt.sample
echo "Running script:"
python vonado-bricks.py -i input-minimal.txt.sample
echo "output file:"
cat input-minimal.txt-output.txt
cp app.log input-minimal.txt.log

echo "running Rebrickable csv"
echo "input file:"
cat input.txt.sample
echo "Running script:"
python vonado-bricks.py -i input.txt.sample
echo "output file:"
cat input.txt-output.txt
cp app.log input.txt.log

echo "running Bricklink XML"
echo "input file:"
cat input.xml.sample
echo "Running script:"
python vonado-bricks.py -i input.xml.sample
echo "output file:"
cat input.xml-output.txt
cp app.log input.xml.log

echo "cleaning up"
rm -fr vonado-brick-test-env
rm -f input*-output.txt
