# Randori
Local Differential Privacy for All!

## Components:
- Backend Server (server.py)
- Poll Editor (editor.html)
- Respondent UI (respondent.html)
- Simulation Environment (simulation_environment.ipynb)

## Usage:
Required python libraries: flask, pandas, matplotlib, scipy, os, json, itertools, fractions, operator

If any library is missing, use pip install <library> before proceeding.

1) Start the server: python server.py
2) Let respondents visit <serverlocation>
3) Visit <serverlocation>/results to view the responses

## Notebook Installation:
Install jupyter notebook (required for Simulation Environment) for your OS using the instructions found at:

https://github.com/Niteo/miniconda-notebook

## Notebook dependencies:
 - python=2.7
 - ipywidgets=7.4.2
 - numpy=1.15.4
 - pandas=0.24.0
 - scipy=1.2.0
 - seaborn=0.7.0
 - flask=1.1.2
