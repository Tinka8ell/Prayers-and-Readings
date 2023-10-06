#
cd ~/BibleExtract
source .venv/bin/activate
python GetBibleVersions.py MSG NLT NIVUK > log.txt 2> err.txt
