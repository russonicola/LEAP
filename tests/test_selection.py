"""
    Unit test for selection operators.
"""
import random
from math import nan

from leap_ec.individual import Individual
from leap_ec.decoder import IdentityDecoder
from leap_ec.binary_rep.problems import MaxOnes
from leap_ec.real_rep.problems import SpheroidProblem
import leap_ec.ops as ops



def test_naive_cyclic_selection():
    """ Test of the naive deterministic cyclic selection """
    pop = [Individual([0, 0], decoder=IdentityDecoder(), problem=MaxOnes()),
           Individual([0, 1], decoder=IdentityDecoder(), problem=MaxOnes())]

    # This selection operator will deterministically cycle through the
    # given population
    selector = ops.naive_cyclic_selection(pop)

    selected = next(selector)
    assert selected.genome == [0, 0]

    selected = next(selector)
    assert selected.genome == [0, 1]

    # And now we cycle back to the first individual
    selected = next(selector)
    assert selected.genome == [0, 0]



def test_cyclic_selection():
    """ Test of the deterministic cyclic selection """

    # Set seed so that we get consistent test results.  I.e., it is possible
    # by happenstance for some tests to fail even though they're actually ok.
    # E.g., the cyclic selection tests will test if the test_sequence
    # shuffles between a complete cycle, but there's a chance that the same
    # test_sequence may come up in the random shuffle, so the test will fail.
    # However, if we set a random seed ahead of time, then we can control for
    # those pathological scenarios.
    random.seed(123)

    # We're just going to use integers for the population as that's
    # sufficient for testing this selection operator; we don't want to get in
    # the weeds with comparing individuals for test_sequence equivalency
    # testing.
    pop = list(range(4))

    # This selection operator will deterministically cycle through the
    # given population
    selector = ops.cyclic_selection(pop)

    # first cycle should be the same order as we started
    first_iteration = [next(selector) for _ in range(len(pop))]

    assert pop == first_iteration

    # the second iteration should be shuffled
    second_iteration = [next(selector) for _ in range(len(pop))]

    assert pop != second_iteration



def test_truncation_selection():
    """ Basic truncation selection test"""
    pop = [Individual([0, 0, 0], decoder=IdentityDecoder(), problem=MaxOnes()),
           Individual([0, 0, 1], decoder=IdentityDecoder(), problem=MaxOnes()),
           Individual([1, 1, 0], decoder=IdentityDecoder(), problem=MaxOnes()),
           Individual([1, 1, 1], decoder=IdentityDecoder(), problem=MaxOnes())]

    # We first need to evaluate all the individuals so that truncation
    # selection has fitnesses to compare
    pop = Individual.evaluate_population(pop)

    truncated = ops.truncation_selection(pop, 2)

    assert len(truncated) == 2

    # Just to make sure, check that the two best individuals from the
    # original population are in the selected population
    assert pop[2] in truncated
    assert pop[3] in truncated


def test_truncation_parents_selection():
    """ Test (mu + lambda), i.e., parents competing with offspring

    Create parent and offspring populations such that each has an "best" individual that will be selected by
    truncation selection.
    """
    parents = [Individual([0, 0, 0], decoder=IdentityDecoder(), problem=MaxOnes()),
               Individual([1, 1, 0], decoder=IdentityDecoder(), problem=MaxOnes())]

    parents = Individual.evaluate_population(parents)

    offspring = [Individual([0, 0, 1], decoder=IdentityDecoder(), problem=MaxOnes()),
                 Individual([1, 1, 1], decoder=IdentityDecoder(), problem=MaxOnes())]
    offspring = Individual.evaluate_population(offspring)

    truncated = ops.truncation_selection(offspring, 2, parents=parents)

    assert len(truncated) == 2

    assert parents[1] in truncated
    assert offspring[1] in truncated


def test_tournament_selection():
    """ This simple binary tournament_selection selection """
    # Make a population where binary tournament_selection has an obvious
    # reproducible choice
    pop = [Individual([0, 0, 0], decoder=IdentityDecoder(), problem=MaxOnes()),
           Individual([1, 1, 1], decoder=IdentityDecoder(), problem=MaxOnes())]

    # We first need to evaluate all the individuals so that truncation
    # selection has fitnesses to compare
    pop = Individual.evaluate_population(pop)

    best = next(ops.tournament_selection(pop))
    pass

    # This assert will sometimes not work because it's possible to select the
    # same individual more than once, and that includes scenarios where the
    # worst of two individuals is selected twice, which can happen about 25%
    # of the time. assert pop[1] == best



def test_tournament_selection_with_nan():
    """ This simple binary tournament_selection selection to test NaN behavior
    """
    # Make a population where binary tournament_selection has an obvious
    # reproducible choice
    problem = MaxOnes()
    pop = [Individual([0, 0, 0], decoder=IdentityDecoder(), problem=problem),
           Individual([1, 1, 1], decoder=IdentityDecoder(), problem=problem)]

    # We first need to evaluate all the individuals so that truncation
    # selection has fitnesses to compare
    pop = Individual.evaluate_population(pop)

    # Now set the "best" to NaN
    pop[1].fitness = nan

    best = ops.truncation_selection(pop, size=1)

    assert pop[0] == best[0]

    # Ok, now do this for _minimization_
    decoder = IdentityDecoder()
    problem = SpheroidProblem(maximize=False)

    pop = []

    pop.append(Individual([0], problem=problem, decoder=decoder))
    pop.append(Individual([1], problem=problem, decoder=decoder))

    pop = Individual.evaluate_population(pop)

    # First *normal* selection should yield the 0 as the "best"
    best = ops.truncation_selection(pop, size=1)
    assert pop[0] == best[0]

    # But now let's set that best to a NaN, which *should* force the other
    # individual to be selected.
    pop[0].fitness = nan

    best = ops.truncation_selection(pop, size=1)
    assert pop[1] == best[0]
