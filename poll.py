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
        
    def __str__(self):
        toRet = str(self.root)
        current = self.root
        
        toPop = list(self.root.children)
        loop=True
        while(loop):
            nextQ = toPop.pop(0)
            toRet += str(nextQ)
            
            if(len(nextQ.children)>0):
                toPop.append(list(nextQ.children))
            
            if(len(toPop)==0):
                loop=False

        return toRet


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
            self.children = []

    def addAnswer(self, answer):
        self.answers.append(answer)
        
    def removeAnswer(self, answer):
        self.answers.pop(answer, None)
    
    def addFollowUpQuestion(self, question, conditional=None):
        self.children.append(question)
    
    def removeFollowUpQuestion(self, question):
        self.children.pop(question, None)
        
    def __str__(self):
        toRet = 'Question: ' + self.questionText + '\n'
        toRet += '(Answer, Probability) : \n'
        for (ans, prob) in self.answers:
            toRet += '    ('+ans+', '+str(prob.numerator)+'/'+str(prob.denominator)+')\n'
        
        return toRet
        


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
        self.questionText = text
        self.answers = answers
        self.children = []
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
    rq = RootQuestion('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
    fq = ConditionalQuestion('Question', [('d', Fraction(1,3)), ('e', Fraction(1,3)), ('f', Fraction(1,3))])
    fq.addCondition((rq, 'b'))
    
    assert rq in fq.conditions.keys()
    assert 'b' in fq.conditions[rq]
    assert len(fq.conditions[rq])==1

    # Test that conditions without existing answers aren't added
    fq.addCondition((rq, 'doesnt exist'))
    assert len(fq.conditions[rq])==1
    
    
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

def testSetTruth():
    global rq
    rq = RootQuestion('','')
    rq.setTruth(999)
    assert rq.truth!=999
    rq.setTruth(10)
    assert rq.truth==10
    
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
    
def testTraverse():
    global qs, rq, fq
    
    qs = QuestionStruct()
    rq= RootQuestion('Root',[('a', Fraction(1,3)), ('b', Fraction(1,3)), ('c', Fraction(1,3))])
    qs.addRootQuestion(rq)
    rq.addFollowUpQuestion(ConditionalQuestion('Question 2', [('d', Fraction(1,2)), ('e', Fraction(1,2))]))
    rq.addFollowUpQuestion(ConditionalQuestion('Question 3', [('f', Fraction(1,2)), ('g', Fraction(1,2))]))
    rq.addFollowUpQuestion(ConditionalQuestion('Question 4', [('h', Fraction(1,2)), ('i', Fraction(1,2))]))
    
    assert len(rq.children)==3
    assert str(qs)=='Question: Root\n(Answer, Probability) : \n    (a, 1/3)\n    (b, 1/3)\n    (c, 1/3)\nQuestion: Question 2\n(Answer, Probability) : \n    (d, 1/2)\n    (e, 1/2)\nQuestion: Question 3\n(Answer, Probability) : \n    (f, 1/2)\n    (g, 1/2)\nQuestion: Question 4\n(Answer, Probability) : \n    (h, 1/2)\n    (i, 1/2)\n'


# In[8]:


testInheritance()
testAddCondition()
testRemoveCondition()
testSetTruth()
testStruct()
testTraverse()

