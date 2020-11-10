#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, send_from_directory, request
import os
import json
import operator
import pandas as pd

import ast # Decode from unicode
import logic as lgc


# In[ ]:


file_name = 'respondent.html'
icon_name = 'favicon.ico'


# In[ ]:


app = Flask(__name__)


# In[ ]:


#Example JSON
_example_json_poll = {"children": [
{"answers": ["B+", "AB+", "O-", "A-", "Other"],
   "probability": ["1/5", "1/5", "1/5", "1/5", "1/5"],
   "qid": 1,
   "question": "Specify..."},
  {"answers": ["B-", "AB-"],
   "probability": ["3/4", "1/4"],
   "qid": 2,
   "question": "Specify further..."}],
 "paths": [[0, "Other", 1], [1, "Other", 2]],
 "roots": [{"answers": ["O+", "A+", "Other"],
   "probability": ["1/3", "1/3", "1/3"],
   "qid": 0,
   "truth": "1/2",
   "question": "Blood type?"}, 
   {"answers": ["A", "B", "C"],
   "probability": ["1/3", "1/3", "1/3"],
   "qid": 4,
   "truth": "3/4",
   "question": "Q2?"},
   {"answers": ["1", "2"],
   "probability": ["1/2", "1/2"],
   "qid": 3,   
   "truth": "1/3",
   "question": "1 or 2?"}],
 "order": [0, 4, 3]
}
_example_json_poll


# In[ ]:


# Helper functions and logic
json_poll = json.dumps(_example_json_poll)
poll_info = lgc.parsePoll(_example_json_poll)
subtrees=poll_info['subtrees']
matrices=poll_info['matrices']
lookup = poll_info['lookup']


# In[ ]:


responses =[]
result_filtered = {}


# In[ ]:


def results():
    # Parse responses
    lists_responses = {}
    for question in subtrees.keys():
        lists_responses[question] = map(lambda x: pathToKey(x[question]), responses)
    response_frame = pd.DataFrame(lists_responses)
    response_frequency = {}

    #Count occurences
    for question in subtrees.keys():
        response_frequency[question] = {}

        to_match = pd.unique(response_frame[question])
        for match in to_match:
            response_frequency[question][match] = len(response_frame[response_frame[question]==match])

    result_filtered['Respondents']=len(responses)

    #Filter with Bayes' theorem
    for question in response_frequency.keys():
        #P(True)
        p_true = Fraction(lookup[question]['truth'])
        result_filtered[lookup[question]['question']] = {}

        #Bayes' theorem: p(A|True) = p(True|A)*p(A) / p(True)
        for alternative in response_frequency[question].keys():
            transition = (alternative, alternative)
            #p(True|A), Probability of not changing answer
            p_true_given_a = matrices[question][transition]
            #p(A), Actual responses
            p_a = Fraction((response_frequency[question][alternative]),len(responses)) #Convert to %

            #p(A|True) = p(True|A)*p(A) / p(True)
            p_a_given_true = (p_true_given_a*p_a)/p_true

            # Save percentage and use on pop!
            true_a = float(p_a_given_true*p_true)*response_frequency[question][alternative]
            result_filtered[lookup[question]['question']][alternative] = true_a


# In[ ]:


# Annotated functions
@app.route('/')
def getHtml():
    return send_from_directory('.', file_name)

@app.route('/favicon.ico')
def getIcon():
    return send_from_directory('.', icon_name)


@app.route('/poll')
def getPoll():
    return json_poll

@app.route('/create')
def setPoll():
    return {}

@app.route('/results')
def showResults():
    return result_filtered

@app.route('/submit', methods=['POST'])
def getResults():
    content = request.json
    print content
    
    decoded = {}
    for key in content:
        decoded[int(key)]=content[key]
    
    responses.append(decoded)
    results()
    return ''


# In[ ]:


#Run server
if __name__ == "__main__":
    app.run()

