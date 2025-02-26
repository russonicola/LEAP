#!/usr/bin/env python3
"""
    This implements a simple Evolutionary Strategy (ES) system, and implements
    a very crude self-adaptive step-size mechanism to show how to use contexts.

"""
from toolz import pipe

from leap_ec.individual import Individual
from leap_ec.decoder import IdentityDecoder
from leap_ec.context import context

import leap_ec.ops as ops
from leap_ec.real_rep.problems import SpheroidProblem
from leap_ec.real_rep.initializers import create_real_vector
from leap_ec.real_rep.ops import mutate_gaussian
from leap_ec import util

BROOD_SIZE = 3  # how many offspring each parent will reproduce
MAX_GENERATIONS = 10


def print_population(population, generation):
    """ Convenience function for pretty printing a population that's
    associated with a given generation

    :param population:
    :param generation:
    :return: None
    """
    for individual in population:
        print(
            generation,
            context['leap']['std'],
            individual.genome,
            individual.fitness)


def anneal_std(generation):
    """ Cool down the step-size each generation.

    This tickles context['leap']['std']

    :param generation: current generation, which the callback always gives
    :return: new std
    """
    # .85 was an original annealing step size used by Hans-Paul Schwefel, though
    # this was in the context of the 1/5 success rule, which we've not
    # implemented here.
    # Handbook of EC, B1.3:2
    context['leap']['std'] *= .85


if __name__ == '__main__':
    # Define the real value bounds for initializing the population. In this case,
    # we define a genome of four bounds.

    # the (-5.12,5.12) was what was originally used for this problem in
    # Ken De Jong's 1975 dissertation, so was used for historical reasons.
    bounds = [(-5.12, 5.12), (-5.12, 5.12), (-5.12, 5.12), (-5.12, 5.12)]
    parents = Individual.create_population(5,
                                           initialize=create_real_vector(
                                               bounds),
                                           decoder=IdentityDecoder(),
                                           problem=SpheroidProblem(
                                               maximize=False))

    # Evaluate initial population
    parents = Individual.evaluate_population(parents)

    context['leap']['std'] = 2

    # We use the provided context, but we could roll our own if we
    # wanted to keep separate contexts.  E.g., island models may want to have
    # their own contexts.
    generation_counter = util.inc_generation(
        context=context, callbacks=(anneal_std,))

    # print initial, random population
    print_population(parents, generation=0)

    while generation_counter.generation() < MAX_GENERATIONS:
        offspring = pipe(parents,
                         ops.random_selection,
                         ops.clone,
                         mutate_gaussian(std=context['leap']['std']),
                         ops.evaluate,
                         ops.pool(
                             size=len(parents) * BROOD_SIZE),
                         # create the brood
                         ops.truncation_selection(size=len(parents),
                                                  parents=parents))  # mu + lambda

        parents = offspring

        generation_counter()  # increment to the next generation

        # Just to demonstrate that we can also get the current generation from
        # the context
        print_population(parents, context['leap']['generation'])
