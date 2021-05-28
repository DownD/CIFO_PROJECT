from random import randint, uniform, sample, random


def template_co(p1, p2):
    """[summary]

    Args:
        p1 ([type]): [description]
        p2 ([type]): [description]

    Returns:
        [type]: [description]
    """

    return offspring1, offspring2

def single_point_co(p1, p2):
    """Implementation of single point crossover.

    Args:
        p1 (Individual): First parent for crossover.
        p2 (Individual): Second parent for crossover.

    Returns:
        Individuals: Two offspring, resulting from the crossover.
    """
    co_point = randint(1, len(p1)-2)

    offspring1 = p1[:co_point] + p2[co_point:]
    offspring2 = p2[:co_point] + p1[co_point:]

    return offspring1, offspring2
    
def cycle_co(p1, p2):
    # Offspring placeholders - None values make it easy to debug for errors
    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p1)
    # While there are still None values in offspring, get the first index of
    # None and start a "cycle" according to the cycle crossover method
    while None in offspring1:
        index = offspring1.index(None)
        # alternate parents between cycles beginning on second cycle
        if index != 0:
            p1, p2 = p2, p1
        val1 = p1[index]
        val2 = p2[index]

        while val1 != val2:
            offspring1[index] = p1[index]
            offspring2[index] = p2[index]
            val2 = p2[index]
            index = p1.index(val2)
        # In case last values share the same index, fill them in each offspring
        offspring1[index] = p1[index]
        offspring2[index] = p2[index]

    return offspring1, offspring2


def multiple_point_fitness_co(p1,p2):
    p1_fitness = int(p1.fitness)
    p2_fitness = int(p2.fitness)
    sum_fitness = p1_fitness+p2_fitness

    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p1)
    for i in range(len(p1)):
        r1 = uniform(0,sum_fitness)
        r2 = uniform(0,sum_fitness)

        if r1>p1_fitness:
            offspring1[i] = p2[i]
        else:
            offspring1[i] = p1[i]

        if r2>p1_fitness:
            offspring2[i] = p2[i]
        else:
            offspring2[i] = p1[i]
    
    return offspring1,offspring2

        


def arithmetic_co(p1, p2):
    # Offspring placeholders - None values make it easy to debug for errors
    offspring1 = [None] * len(p1)
    offspring2 = [None] * len(p1)
    # Set a value for alpha between 0 and 1
    alpha = uniform(0,1)
    # Take weighted sum of two parents, invert alpha for second offspring
    for i in range(len(p1)):
        offspring1[i] = p1[i] * alpha + (1 - alpha) * p2[i]
        offspring2[i] = p2[i] * alpha + (1 - alpha) * p1[i]

    return offspring1, offspring2

def pmx_co(p1, p2):
    # Sample 2 random co points
    co_points = sample(range(len(p1)), 2)
    co_points.sort()

    def PMX(x, y):
        # Create placeholder for offspring
        o = [None] * len(x)

        # Copy co segment into offspring
        o[co_points[0]:co_points[1]] = x[co_points[0]:co_points[1]]

        # Find set of values not in offspring from co segment in P2
        z = set(y[co_points[0]:co_points[1]]) - set(x[co_points[0]:co_points[1]])

        # Map values in set to corresponding position in offspring
        for i in z:
            temp = i
            index = y.index(x[y.index(temp)])
            while o[index] != None:
                temp = index
                index = y.index(x[temp])
            o[index] = i
        
        while None in o:
            index = o.index(None)
            o[index] = y[index]
        return o

    o1, o2 = (
        PMX(p1, p2),
        PMX(p2, p1)
    )

    return o1, o2



if __name__ == '__main__':
    import charles

    charles.Individual.evaluate = lambda x: sum(x)
    p1 = charles.Individual(representation=[1,2,3,4,0,0,0,0,0])
    p2 = charles.Individual(representation=[-9,-3,-7,-8,-2,-6,-5,-1,-4])
    print(p1.fitness)
    print(p2.fitness)


    print(multiple_point_fitness_co(p1, p2))