@echo off

cls
echo Setting up virtual environment
python -m venv vonado-brick-test-env
vonado-brick-test-env/bin/activate

cls
echo Installing requirements
pip install -r requirements.txt

cls
echo running minimal file
echo input file:
type input-minimal.txt.sample
echo Running script:
python vonado-bricks.py -i input-minimal.txt.sample
echo output file:
type input-minimal.txt-output.txt

echo .
echo .
echo running Rebrickable csv
echo input file:
type input.txt.sample
echo Running script:
python vonado-bricks.py -i input.txt.sample
echo output file:
type input.txt-output.txt

echo .
echo .
echo running Bricklink XML
echo input file:
type input.xml.sample
echo Running script:
python vonado-bricks.py -i input.xml.sample
echo output file:
type input.xml-output.txt

echo .
echo .
echo cleaning up
rmdir /S /Q vonado-brick-test-env
del input*-output.txt
