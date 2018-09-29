#! /usr/bin/env python

##############################################################################
#
#   LEAP - Library for Evolutionary Algorithms in Python
#   Copyright (C) 2004  Jeffrey K. Bassett
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################

import sys
#sys.path.insert(0,'..')
import string
import copy
import random
import math
import numpy

import LEAP
import LEAP.Exec
from ruleInterp import *
#import cRuleFuncs


#############################################################################
#
# InterpolatingRuleInterp
#
#    This is an alternate rule interpreter for Pitt approach systems.
# When none of the rules match exactly, instead of picking a nearby rule to
# fire, an output is generated by interpolating between the outputs of several
# nearby rules.
#
#############################################################################
class InterpolatingRuleInterp(RuleInterp):
    """
    Rule interpreter for Pitt approach style rule learning.  
    Rules take the form: input_pairs, memory_pairs, output, memory
    """

    def execute(self, input):
        raise NotImplementedError



#############################################################################
#
# pyInterpolatingRuleInterp
#
#############################################################################
class pyInterpolatingRuleInterp(InterpolatingRuleInterp):
    """
    A python implementation of InterpolatingRuleInterp.
    """

    def __init__(self, ruleset, numInputs, numOutputs, initMem=[],
                 priorityMetric = None):  # priorityMetric is ignored
        # For now we'll make things simple.  One input only.
        assert(numInputs == 1)
        assert(numOutputs == 1)
        assert(initMem == [])

        self.numInputs = numInputs
        self.numOutputs = numOutputs
        self.memRegs = initMem
        self.numMemory = len(initMem)

        self.numConditions = self.numInputs + self.numMemory
        self.numActions = self.numOutputs + self.numMemory

        self.ruleset = ruleset
        assert(len(ruleset) > 0)
        for r in ruleset:
            assert(r[0] == r[1])


    def execute(self, input):
        """
        Calculate interpolated output value based on nearby rules.
        Python version.
        """
        assert(len(input) == 1)
        #return numpy.interp(input, self.xp, self.fp)

        Inf = float('inf')
        maxLower = -Inf
        minUpper = Inf
        upper = None
        lower = None

        x = input[0]
        for r in self.ruleset:
            if (r[0] >= x) and (r[0] < minUpper):
                upper = r
                minUpper = r[0]
            elif (r[0] <= x) and (r[0] > maxLower):
                lower = r
                maxLower = r[0]

        if lower == None:
            output = [upper[2]]
        elif upper == None:
            output = [lower[2]]
        elif lower == upper:
            output = [lower[2]]
        else:
            x1 = lower[0]
            x2 = upper[0]
            y1 = lower[2]
            y2 = upper[2]
            output = [(y2-y1) * (x-x1) / (x2-x1) + y1]

        return output



#############################################################################
#
# cInterpolatingRuleInterp
#
#############################################################################
#class cInterpolatingRuleInterp(InterpolatingRuleInterp):
#    """
#    A C implementation of InterpolatingRuleInterp.  Optimized for speed.
#    """
#
#    def __init__(self, ruleset, numInputs, numOutputs, initMem=[],
#                 priorityMetric=ExecInterpolate.PERIMETER):
#        if priorityMetric not in range(ExecInterpolate.numPriorityMetrics):
#            raise ValueError, "Illegal value for priorityMetric"
#
#        #print ruleset
#        self.addr = cRuleFuncs.cInit(ruleset, numInputs, numOutputs, initMem,
#                                     priorityMetric)
#
#
#    def __del__(self):
#        cRuleFuncs.cDel(self.addr)
#        return None
#
#
#    def execute(self, input):
#        output = cRuleFuncs.cExecute(self.addr, input)
#        return output



#############################################################################
#
# makeMap
#
#############################################################################
def makeMap(interp):
    f = open("map.dat", "w")
    res = 0.0025
    y = 0.0
    while y <= 1.0:
        x = 0.0
        while x <= 1.0:
            if interp.execute([x, y]) == [1]:
                f.write(str(x) + " " + str(y) + "\n")
            x += res
        y += res
    f.close()



#############################################################################
#
# test
#
#############################################################################
def test():
    """
    Test the rule interpreter.
    """
    ruleset = [[0.0, 0.0, 4.0],
               [1.0, 1.0, 0.0],
               [2.0, 2.0, 2.0],
               [3.0, 3.0, 4.0]]

    numInputs = 1
    numOutputs = 1
    initMem = []

    # Test the python version
    pyInterp = pyInterpolatingRuleInterp(ruleset, numInputs, numOutputs,initMem)

    output = pyInterp.execute([-0.5])
    output += pyInterp.execute([0.5])
    output += pyInterp.execute([1.5])
    output += pyInterp.execute([2.5])
    output += pyInterp.execute([2.75])
    output += pyInterp.execute([3.5])

    print " output =", output
    assert(output == [4.0, 2.0, 1.0, 3.0, 3.5, 4.0])

    # Test the C version
#    pyOutput = output
#    cInterp = cInterpolatingRuleInterp(ruleset, numInputs, numOutputs, initMem)
#
#    output = cInterp.execute([1])
#    output += cInterp.execute([1])
#    output += cInterp.execute([0])
#    output += cInterp.execute([1])
#
#    print " output =", output
#    assert(output == pyOutput)


#    print "Writing map file..."
#    makeMap(interp)

    print "Passed"


if __name__ == '__main__':
    test()
    #test2()

