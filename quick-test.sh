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
cp input-minimal.txt.sample input.txt
echo "input file:"
cat input.txt
echo "Running script:"
python vonado-bricks.py
echo "output file:"
cat output.txt

echo "running standard file"
cp input.txt.sample input.txt
echo "input file:"
cat input.txt
echo "Running script:"
python vonado-bricks.py
echo "output file:"
cat output.txt

echo "cleaning up"
rm -fr vonado-brick-test-env
rm -f input.txt
rm -f output.txt
