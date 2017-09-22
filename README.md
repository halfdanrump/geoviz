# geoviz
This repository will contain the work I have done on geospatial data analysis and visualization. I presented some of what I have made at [PyCon JP 2017](https://pycon.jp/2017/en/schedule/presentation/57/). The talk was recorded and there's a [link to the video here](https://www.youtube.com/watch?v=Yd5oEIBFQ_E&feature=youtu.be). 

## Setup
1. Install requirements: `pip install --upgrade -r requirements.txt`
2. Create folder for storing temporary files and cached data: `mkdir ~/geotmp`. If you want to put the folder somewhere else, you can edit `lib/config.py`

## Notebooks
I've collected the notebooks that I made and placed them in the repository root. The notebooks use code that is placed in `./lib/`.

### Cityblocks.ipynb
This notebook shows how to calculate city blocks for a given area. My definition of city blocks is "blocks of land that occupy space in the city and are encapsulated by roads on every side". There's probably a more correct word for that, so feel free to make suggestions :). 


