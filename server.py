from flask import Flask
import matplotlib.pyplot as plt
import numpy.random as rnd
import numpy as np
from scipy import stats
import os
import json
import operator
import pandas as pd
import seaborn as sns

app = Flask(__name__)


# Annotated functions
@app.route('/get')
def getPoll():
    return {}

@app.route('/create')
def setPoll():
    return {}

@app.route('/collect')
def getResults():
    return {}

#Run server
if __name__ == "__main__":
    app.run()

