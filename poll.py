#!/usr/bin/env python
# coding: utf-8

# In[1]:


import unittest
from fractions import Fraction


# In[2]:


def addsToOne(probabilities):
    testFrac= sum([prob for (_,prob) in probabilities])
    return testFrac.denominator == 1 and testFrac.numerator == 1


# In[3]:


class QuestionStruct:
    root = None
    
    def addRootQuestion(self, question):
        self.root = question;


# In[4]:


class Question:
    # answer: (string, probability)
    answers = []
    questionText = ''
    children = []

    def __init__(self, text, answers):
        
        if addsToOne(answers):
            self.answers = answers
            self.questionText = text

    def addAnswer(self, answer):
        self.answers.append(answer)
        
    def removeAnswer(self, answer):
        self.answers.pop(answer, None)
    
    def addFollowUpQuestion(self, question, conditional=None):
        self.children.append(question)
    
    def removeFollowUpQuestion(self, question):
        self.children.pop(question, None)
        


# In[5]:


class RootQuestion(Question):
    truth = 50

    def setTruth(self, t):
        if(t>= 0 and t<=100):
            self.truth = t


# In[6]:


class ConditionalQuestion(Question):
    # Parent : answer alts
    conditions = {}
    
    def __init__(self, text, answers):
        Question(text, answers)
        self.conditions = {}
    
    def addCondition(self, cond):
        (parent, answer) = cond
        
        # Only add if answer exists, don't match probability
        if(answer in [ans for (ans,prob) in parent.answers]):
            # Check if list already is created
            try:
                answers = self.conditions[parent]
                if(answer not in answers):
                    self.conditions[parent].append(answer)
            except:
                self.conditions[parent]=[answer]
        
    def removeCondition(self, c):
        (parent, answer) = c
        #Check that parent exist before accessing
        if(parent in self.conditions):
            #Get the list of answers that trigger the question
            answers = self.conditions[parent]
            if(answer in answers):
                answers.remove(answer)
            # Remove key if no follow-ups exist
            if len(answers)==0:
                self.conditions.pop(parent)


# In[7]:


# Test cases
rq = None
fq = None
cq = None
qs = None

def testInheritance():
    assert issubclass(RootQuestion, Question)
    assert issubclass(ConditionalQuestion, Question)
    
def testAddCondition():
    # Test add condition
    global rq, fq
    rq= RootQuestion('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
    fq = ConditionalQuestion('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
    fq.addCondition((rq, 'b'))
    
    assert rq in fq.conditions.keys()
    assert 'b' in fq.conditions[rq]
    assert len(fq.conditions[rq])==1

    # Test that conditions without existing answers aren't added
    fq.addCondition((rq, 'doesnt exist'))
    assert len(fq.conditions[rq])==1
    
    #Cleanup
    rq=fq=qs=None

    
def testRemoveCondition():
    global rq, fq
    rq = RootQuestion('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
    fq = ConditionalQuestion('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
    fq.addCondition((rq, 'b'))
    assert len(fq.conditions[rq])==1
    assert len(fq.conditions.keys())==1
    
    # Test remove condition
    fq.removeCondition((rq, 'b'))
    assert rq not in fq.conditions.keys()
    assert len(fq.conditions.keys())==0
    

    # Test remove from empty
    fq.removeCondition((rq, 'b'))
    assert len(fq.conditions.keys())==0
    
    #Cleanup
    rq=fq=qs=None
    
def testSetTruth():
    global rq
    rq = RootQuestion('','')
    rq.setTruth(999)
    assert rq.truth!=999
    rq.setTruth(10)
    assert rq.truth==10
    
    #Cleanup
    rq=fq=qs=None
    
def testStruct():
    global qs, rq, fq
    qs = QuestionStruct()
    rq = RootQuestion('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
    fq = ConditionalQuestion('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
    
    assert qs.root == None
    qs.addRootQuestion(rq)
    assert qs.root == rq

    rq.addFollowUpQuestion(fq)
    fq.addCondition((rq, 'b'))
    
    #Cleanup
    rq=fq=qs=None


# In[8]:


testInheritance()
testAddCondition()
testRemoveCondition()
testSetTruth()
testStruct()

