#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
import numpy.random as rnd
import numpy as np
from scipy import stats
import os
import json
import operator
import pandas as pd
from fractions import Fraction

import itertools

from poll import *


# # Helper functions

# In[2]:


def traverse(qid_dict, paths, subtree, edges, current_index):
    for [parent, alt, next_qid] in paths:
        if parent == current_index:
            subtree.append(qid_dict[next_qid])
            edges.append([parent, alt, next_qid])
            traverse(qid_dict, paths, subtree, edges, next_qid)
    
def findPath(qid_dict, paths, acc, node):
    my_paths = getPaths(paths, node)
    if my_paths==None:
        return map(lambda x: acc+[x], qid_dict[node]['answers'])
    else:
        results = []
        structure = qid_dict[node]
        for alt in structure['answers']:
            if alt not in map(lambda x: x[1], my_paths):
                results.append(acc+[alt])
        for path in my_paths:
            parent, alt, next_qid = path
            temp = findPath(qid_dict, paths, acc+[alt], next_qid) 
            results+= temp
        return results
            
def findProbabilities(qid_dict, paths, acc, node):
    my_paths = getPaths(paths, node)
    if my_paths==None:
        tuples = zip(qid_dict[node]['answers'], qid_dict[node]['probability'])
        return map(lambda x: acc+[x], tuples)
    else:
        results = []
        structure = qid_dict[node]
        tuples = zip(qid_dict[node]['answers'], qid_dict[node]['probability'])
        
        for alt, prob in tuples:
            if alt not in map(lambda x: x[1], my_paths):
                results.append(acc+[(alt, prob)])
                
        for path in my_paths:
            parent, alt, next_qid = path
            parent_node = qid_dict[parent]
            tuples = zip(parent_node['answers'], parent_node['probability'])
            match = ()
            for a, p in tuples:
                if a == alt:
                    match = (a, p)
            temp = findProbabilities(qid_dict, paths, acc+[match], next_qid) 
            results+= temp
            
        return results
    
def subtreePaths(qid_dict, paths, subtree):
    qids = map(lambda x: x['qid'],subtree)
    temp = map(lambda y: getPaths(paths, y), qids) #Find all paths starting with our qids
    matches = [x for x in temp if x != None]
    
    flattened = list(itertools.chain.from_iterable(matches))
    
    return flattened

def decorate(qid_dict, paths, subtree):
    flattened = subtreePaths(qid_dict, paths, subtree)
    
    if flattened == []:
        return
    
    parents, alts, children = zip(*flattened)    
    parent_children = (set(parents)&set(children)) #Intersection, find overlap
    
    all_parents = list(set(parents) | parent_children) #Union, remove duplicates
    leaves = set(children)-set(all_parents) #Difference, parents not in children

    # Decorate questions
    for child in leaves:
        qid_dict[child]['hasFollowUp'] = 'False'
    for parent in all_parents:
        qid_dict[parent]['hasFollowUp'] = 'True'
        
def getPaths(paths, parent):
    toReturn = []
    for [p, alt, child] in paths:
        if p == parent:
            toReturn.append([p,alt, child])

    if toReturn != []:
        return toReturn
    
def pathToAlt(qid_dict, paths):
    answers = {}
    for [parent, prev_alt, next_qid] in paths:
        answers[parent]=[]
        for alt in qid_dict[next_qid]['answers']:
            answers[parent].append(prev_alt+alt)
            print prev_alt+alt
            
    return answers

def weightedPathToKey(path):
    result = ''
    for (alt, prob) in path:
        result+=alt
    return result

def pathToKey(path):
    result = ''
    for alt in path:
        result+=alt
    return result


# In[3]:


#Chernoff bounds variables

def calculateBeta(n, lambd):
    beta = 2*np.exp(-2*np.power(lambd,2)*n)
    return beta

def calculateLambdaFromNBeta(n, beta):
    lambd = np.sqrt(np.log(2/beta)/(2*n))
    return lambd

def calculateLambdaFromAlphaEpsilon(alpha, epsilon):
    lambd = alpha/(1+(np.exp(epsilon)))/(np.exp(epsilon)-1)
    return lambd

def calculateAlpha(n, beta, epsilon):
    lambd = calculateLambdaFromNBeta(n, beta)
    alpha = (1+(np.exp(epsilon)))/(np.exp(epsilon)-1)*lambd
    return alpha

def calculateEpsilon(n, alpha, beta):
    lambd = calculateLambdaFromNBeta(n, beta)
    epsilon = ((-alpha/lambd)-1)/(1-(alpha/lambd))
    return epsilon


# In[4]:


def parsePoll(json_poll):
    #Parse to proper datatypes
    root_questions = json_poll['roots']
    follow_ups = json_poll['children']
    root_to_truth = {}

    #Convert from id to questions
    qid_dict = {}

    count = 0
    for root in root_questions:
        root['probability'] = map(lambda x: Fraction(x), root['probability']) #Convert String to Fraction
        qid_dict[root['qid']]= root
        root_to_truth[root['qid']] = Fraction(root['truth'])
        count+=1


    for followup in follow_ups:
        followup['probability'] = map(lambda x: Fraction(x), followup['probability']) #Convert String to Fraction
        qid_dict[followup['qid']] = followup
        
    #Find question order

    subtrees = {}
    edges = []
    question_paths = {}
    answer_prob = {}
    paths = json_poll['paths']

    for root in root_questions:
        qid = root['qid']
        subtrees[qid] = [root]
        traverse(qid_dict, paths, subtrees[qid], edges, qid)
        decorate(qid_dict, paths, subtrees[qid])

        question_paths[qid] = findPath(qid_dict, paths, [], qid)
        answer_prob[qid] = findProbabilities(qid_dict, paths, [], qid)
        
    
    #Construct transition matrix
    transition_matrix_subtree = {}
    path_probs = {}
    
    for tree in answer_prob.keys():
        coinflip = root_to_truth[tree]
        path_prob = {}

        for path in answer_prob[tree]:
            node_prob = 1
            path_string = weightedPathToKey(path)
            for alt, prob in path:
                 node_prob*=prob
            path_prob[path_string] = node_prob
        path_probs[tree] = path_prob

        matrix = {}
        for _from in path_prob.keys():
            column_keys = []
            siblings = len(path_prob.keys())
            p_a = (1-coinflip)*path_prob[_from] + coinflip #Random + truth
            p_other = (1-p_a)/(siblings-1)
            
            for _to in path_prob.keys():
                key = (_from, _to)
                column_keys.append(key)
                # Higher likelihood to stay on same value
                if _from == _to:
                    matrix[key] = p_a #Random + truth
                else:
                    matrix[key]= p_other #Only random

            cases = []
            for key in column_keys:
                cases.append(matrix[key])

            assert sum(cases)==1

        transition_matrix_subtree[tree] = matrix
    
    return {'matrices':transition_matrix_subtree,
            'subtrees':subtrees,
            'paths':question_paths,
            'weighted_paths':path_probs,
            'answer_probability':answer_prob,
            'lookup':qid_dict,
           }

