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
cat output.txt

echo "running Rebrickable csv"
echo "input file:"
cat input.txt.sample
echo "Running script:"
python vonado-bricks.py -i input.txt.sample
echo "output file:"
cat output.txt

echo "running Bricklink XML"
echo "input file:"
cat input.xml.sample
echo "Running script:"
python vonado-bricks.py -i input.xml.sample
echo "output file:"
cat output.txt

echo "cleaning up"
rm -fr vonado-brick-test-env
rm -f output.txt
