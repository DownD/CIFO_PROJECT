from random import shuffle, choice, sample, uniform,random
from operator import  attrgetter
from copy import deepcopy
import threading,math


#Improved evolve method to use multi-thread

def skip(pop):
    pass


class Individual:
    def __init__(
        self,
        representation=None,
        size=None,
        replacement=True,
        valid_set=[i for i in range(13)],
    ):
        if representation == None:
            if replacement == True:
                self.representation = [choice(valid_set) for i in range(size)]
            elif replacement == False:
                self.representation = sample(valid_set, size)
        else:
            self.representation = representation
        self.fitness = self.evaluate()

    def evaluate(self):
        raise Exception("You need to monkey patch the fitness path.")

    def get_neighbours(self, func, **kwargs):
        raise Exception("You need to monkey patch the neighbourhood function.")

    def index(self, value):
        return self.representation.index(value)

    def __len__(self):
        return len(self.representation)

    def __getitem__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"


class Population:
    def __init__(self, size, optim,representations=[], **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim

        print("Loading",len(representations),"old weights")
        for n in representations:
            self.individuals.append(Individual(representation=n))
        for _ in range(size-len(representations)):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"],
                    replacement=kwargs["replacement"],
                    valid_set=kwargs["valid_set"],
                )
            )

    def evolve(self, gens, select, crossover, mutate, co_p, mu_p, elitism,elitism_pct,feedback_new_gen=skip,n_thread=2):
        for gen in range(gens):
            new_pop = []
 
            if elitism == True:
                sort_indiv = sorted(self.individuals, key=attrgetter("fitness"))
                n_indiv = int(elitism_pct*len(self.individuals))
                if self.optim == "max":
                    elite = sort_indiv[-n_indiv:]
                    
                elif self.optim == "min":
                    elite = sort_indiv[:n_indiv]
                
                for el in elite:
                    #Recalculate fitness
                    new_pop.append(Individual(representation=el.representation))


            #Calculate the work to be done by each thread 
            curr_size = self.size-len(new_pop)
            pop_per_thread = int(curr_size/n_thread)
            thread_list = []

            #Create threads
            for i in range(n_thread-1):
                t = threading.Thread(target=self.__evolve_thread, args=(select, crossover, mutate, co_p, mu_p,pop_per_thread,new_pop))
                thread_list.append(t)
                t.start()

            #Also use the main thread to get new individuals
            self.__evolve_thread(select, crossover, mutate, co_p, mu_p,curr_size-pop_per_thread*(n_thread-1),new_pop)

            for t in thread_list:
                t.join()

            #Workarround for race conditions
            while len(new_pop) > self.size:
                new_pop.pop()

            #print(len(new_pop),self.size)

 
            self.individuals = new_pop

            print("Generation:",gen)
 
            if self.optim == "max":
                print(f'Best Individual: {max(self, key=attrgetter("fitness"))}')
            elif self.optim == "min":
                print(f'Best Individual: {min(self, key=attrgetter("fitness"))}')
            feedback_new_gen(self)
        
        return new_pop

    #Function to be run by multiple threads
    def __evolve_thread(self, select, crossover, mutate, co_p, mu_p,n,pop):  
        for i in range(math.ceil(n/2)):
            parent1, parent2 = select(self), select(self)
            # Crossover
            if random() < co_p:
                offspring1, offspring2 = crossover(parent1, parent2)
            else:
                offspring1, offspring2 = parent1.representation, parent2.representation
            # Mutation
            if random() < mu_p:
                offspring1 = mutate(offspring1)
            if random() < mu_p:
                offspring2 = mutate(offspring2)

            pop.append(Individual(representation=offspring1))
            if i*2<(n-1):
                pop.append(Individual(representation=offspring2))

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]

    def __repr__(self):
        return f"Population(size={len(self.individuals)}, individual_size={len(self.individuals[0])})"
