@echo off

cls
echo Setting up virtual environment
python -m venv vonado-brick-test-env
vonado-brick-test-env/bin/activate

cls
echo Installing requirements
pip install -r requirements.txt

cls
echo -----------------------------------------
echo running minimal file
echo input file:
type input-minimal.txt.sample
echo Running script:
python vonado-bricks.py -i input-minimal.txt.sample
echo output file:
type input-minimal.txt-output.txt
copy app.log input-minimal.txt.log

echo .
echo .
echo -----------------------------------------
echo running Rebrickable csv
echo input file:
type input.txt.sample
echo Running script:
python vonado-bricks.py -i input.txt.sample
echo output file:
type input.txt-output.txt
copy app.log input.txt.log

echo .
echo .
echo -----------------------------------------
echo running Bricklink XML
echo input file:
type input.xml.sample
echo Running script:
python vonado-bricks.py -i input.xml.sample
echo output file:
type input.xml-output.txt
copy app.log input.xml.log

echo .
echo .
echo -----------------------------------------
echo running BrickLink Wanted List XML
echo input file:
type input.bricklink.xml.sample
echo Running script:
python vonado-bricks.py -i input.bricklink.xml.sample -l True
echo output file:
type input.bricklink.xml-output.txt
copy app.log input.bricklink.xml.log

echo "input file:"
cat input.bricklink.xml.sample
echo "Running script:"
python vonado-bricks.py -i input.bricklink.xml.sample -l True
echo "output file:"
cat input.bricklink.xml-output.txt
cp app.log input.bricklink.xml.log


echo .
echo .
echo -----------------------------------------
echo cleaning up
rmdir /S /Q vonado-brick-test-env
del input*-output.txt
