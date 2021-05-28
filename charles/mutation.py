from random import randint, sample, uniform, random
import numpy as np

def template_mutation(individual):
    """[summary]

    Args:
        individual ([type]): [description]

    Returns:
        [type]: [description]
    """
    return individual


def binary_mutation(individual):
    """Binary muation for a GA individual

    Args:
        individual (Individual): A GA individual from charles libray.py

    Raises:
        Exception: When individual is not binary encoded.py

    Returns:
        Individual: Mutated Individual
    """
    mut_point = random.randint(0, len(individual) - 1)

    if individual[mut_point] == 0:
        individual[mut_point] = 1
    elif individual[mut_point] == 1:
        individual[mut_point] = 0
    else:
        raise Exception(
            f"Trying to do binary mutation on {individual}. But it's not binary."
        )

    return individual


def swap_mutation(individual):
    # Get two mutation points
    mut_points = sample(range(len(individual)), 2)
    # Rename to shorten variable name
    i = individual

    i[mut_points[0]], i[mut_points[1]] = i[mut_points[1]], i[mut_points[0]]

    return i

def inversion_mutation(individual):
    i = individual
    # Position of the start and end of substring
    mut_points = sample(range(len(i)), 2)
    # This method assumes that the second point is after (on the right of) the first one
    # Sort the list
    mut_points.sort()
    # Invert for the mutation
    i[mut_points[0]:mut_points[1]] = i[mut_points[0]:mut_points[1]][::-1]

    return i

def float_mutation_multiply(individual):
    i = individual
    for value in range(len(i)):
        val = random()
        if val>0.78:
            i[value] = i[value]* uniform(-2,2)
    return i

def float_mutation_replace(individual):
    i = individual
    for value in range(len(i)):
        val = random()
        if val>0.78:
            i[value] = uniform(-2,2)
    return i
    
if __name__ == '__main__':
    i1 = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18]

    print(float_mutation(i1))