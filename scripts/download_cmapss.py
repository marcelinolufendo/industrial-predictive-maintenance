"""
Download NASA C-MAPSS dataset.

The dataset is available at:
https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository

Manual steps:
1. Go to: https://data.nasa.gov/Aerospace/CMAPSS-Jet-Engine-Simulated-Data/ff5v-kuh6
2. Download: CMAPSSData.zip
3. Extract the .txt files into data/raw/

Expected files:
  data/raw/train_FD001.txt
  data/raw/train_FD002.txt
  data/raw/train_FD003.txt
  data/raw/train_FD004.txt
  data/raw/test_FD001.txt
  data/raw/RUL_FD001.txt
"""

print(__doc__)
