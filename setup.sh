# Set up Bible Extract directory
cp ~/Prayers-and-Readings/requirements.txt .
cp ~/Prayers-and-Readings/UpdateBibles.sh .
cp ~/Prayers-and-Readings/src/Bible*.py .
cp ~/Prayers-and-Readings/src/GetBibleVersions.py .
cp ~/Prayers-and-Readings/src/WebTree.py .
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
