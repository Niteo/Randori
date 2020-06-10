#!/usr/bin/env python
# coding: utf-8

import unittest
import json
from fractions import Fraction

def addsToOne(probabilities):
    testFrac= sum([prob for (_,prob) in probabilities])
    return testFrac.denominator == 1 and testFrac.numerator == 1

class Poll:
    roots = []
    children = []
    paths = []
    
    def __init__(self):
        self.roots = [] #(Question, factor representing the initial 'coinflip')
        self.children = [] #Question
        self.paths = [] # (Root, alt, child) 
    
    def addRoot(self, question, coinflip):
        self.roots.append((question, coinflip))
        
    def addChild(self, question):
        self.children.append(question)
        
    def addPath(self, root, alt, child):
        if(alt in root.getAnswers()):
            self.paths.append((root, alt, child))
            
    def removePath(self, root, alt, child):
        if((root, alt, child) in self.paths):
            self.paths.remove((root, alt, child))
        
    def __str__(self):
        return str(self.toJSON())
    
    def toDict(self):
        (question, truth) = map(list, zip(*self.roots)) #Unzip the tuples into separate lists        
        
        # Generate unique ids only for use in JSON
        count = 0
        questions = question + self.children
        
        for q in questions:
            q.setQid(count)
            count+=1
        
        structure = {
            'roots':map(lambda q: q.toDict(), question),
            'children':map(lambda q: q.toDict(), self.children),
            'paths':map(lambda (parent, alt, child): (parent.qid, alt, child.qid), self.paths), 
            'truth':map(lambda x: str(x), truth)
            }
        
        return structure
    
    def toJSON(self):
        return json.dumps(self.toDict())

class Question:
    # answer: (string, probability)
    answers = []
    questionText = ''
    qid = None

    def __init__(self, text, answers):
        
        if addsToOne(answers):
            self.answers = answers
            self.questionText = text
            self.children = []

    def addAnswer(self, answer):
        self.answers.append(answer)
        
    def removeAnswer(self, answer):
        self.answers.pop(answer, None)
        
    def getAnswers(self):
        (alts, probabilities) = map(list, zip(*self.answers))
        return alts
    
    def setQid(self, qid):
        self.qid = qid
    
    def toDict(self):
        (alts, probability) = map(list, zip(*self.answers))
        return {'question': self.questionText, 
                'answers':alts,
                'probability':map(lambda x: str(x),probability)
               }

class Test(unittest.TestCase):
    def testAddCondition(self):
        # Test add condition
        poll = Poll()
        rq = Question('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
        fq = Question('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
        
        poll.addRoot(rq, Fraction(1,2))
        poll.addChild(fq)
        poll.addPath(rq, 'b', fq)

        assert map(lambda x: rq in x, poll.paths)
        assert map(lambda x: 'b' in x, poll.paths)
        assert len(poll.paths)==1

        # Test that conditions without existing answers aren't added
        poll.addPath(rq, 'doesnt exist', fq)
        assert len(poll.paths)==1  

    def testRemoveCondition(self):
        poll = Poll()
        rq = Question('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
        fq = Question('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
        
        poll.addRoot(rq, Fraction(1,2))
        poll.addChild(fq)
        poll.addPath(rq, 'b', fq)

        assert len(poll.paths)==1

        # Test remove condition
        poll.removePath(rq, 'b', fq)
        assert (rq,'b', fq) not in poll.paths
        assert len(poll.paths)==0


        # Test remove from empty
        poll.removePath(rq, 'b', fq)
        assert len(poll.paths)==0
        
    def testPollStruct(self):
        poll = Poll()
        rq = Question('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
        fq = Question('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])

        assert Poll.roots == []
        poll.addRoot(rq, Fraction(1,2))
        assert lambda (x, y): x in Poll.roots
        
        poll.addChild(fq)
        poll.addPath(rq, 'b', fq)

    def testTraverse(self):
        poll = Poll()
        rq= Question('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
        fqa=Question('Question 2', [('d', Fraction(1,2)), ('e', Fraction(1,2))])
        fqb=Question('Question 3', [('f', Fraction(1,2)), ('g', Fraction(1,2))])
        fqc=Question('Question 4', [('h', Fraction(1,2)), ('i', Fraction(1,2))])
        poll.addRoot(rq, Fraction(1,2))
        
        poll.addChild(fqa)
        poll.addChild(fqb)
        poll.addChild(fqc)
        
        poll.addPath(rq, 'a', fqa)
        poll.addPath(rq, 'b',fqb)
        poll.addPath(rq, 'c',fqc)
        
        assert len(poll.children)==3
        jsonPoll = poll.toDict()
        assert len(jsonPoll['paths'])==3
        assert 'a' in map(lambda (x,y,z): y,jsonPoll['paths'])
        assert 'b' in map(lambda (x,y,z): y,jsonPoll['paths'])
        assert 'c' in map(lambda (x,y,z): y,jsonPoll['paths'])
        assert not 'd' in map(lambda (x,y,z): y,jsonPoll['paths'])

unittest.main(argv=[''], verbosity=2, exit=False)

