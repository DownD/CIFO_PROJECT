from random import seed, uniform
from snakeGame import SnakeGame, SnakeGraphics
from charles import mutation,selection,search,crossover
from charles import charles_multithread as charles
from copy import deepcopy
import copy,time
import numpy as np
#import keras
from keras.models import Sequential
from keras.layers import Dense, Input
from operator import  attrgetter
import matplotlib.pyplot as plt
import pickle
import os


MAX_STEPS_OPERATING = 50 #Maximum time of steps per agent
NUM_SIM_PER_FITNESS = 5 #Number of simulation per fitness
seed()

#Hyper-parameters
GA_SETTINGS = {
    "crossover":(crossover.multiple_point_fitness_co,0.7),                    #Crossover algorithm and percentage
    "mutation":(mutation.float_mutation_multiply,0.09),             #Mutation algorithm and percentage
    "population_size":200,                                          #Population size
    "selection":selection.fps,                               #Selection algorithm
    "elitism":(True,0.04),                                          #Elitism and percentage of individuals to keep
    "simulation_per_fitness":NUM_SIM_PER_FITNESS,                   #Number of games to be run per individual
    "generations":110,                                               #Number of generations
    "name_folder":"test_7"                                          #Folder name to store statistics
}


#Model of the network
def buildModel():
    model = Sequential()
    model.add(Dense(5, input_shape=(6,), activation="relu"))
    model.add(Dense(3, activation="softmax"))
    model.compile(loss='mse',optimizer="adam",metrics=['acc'])
    return model

#Transform a numpy matrix into an 1-d array
def flatten(matrix):
    weights_shape = []

    #Flatten
    flatten_weights = []
    for weight in matrix:
        flatten_weights.extend(list(weight.flatten()))
        weights_shape.append(weight.shape)

    return weights_shape,flatten_weights

#Transform an 1-d array into a numpy matrix
def reshape(arr,weights_shape):
    orig_form = []
    curr_index = 0
    for shape in weights_shape:
        if len(shape) == 1:
            end_index = curr_index + shape[0]
        else:
            end_index = curr_index + shape[0]*shape[1]
        orig_form.append(np.array(arr[curr_index:end_index],dtype=np.float32).reshape(shape))
        curr_index = end_index
    return orig_form


#Build the model
model = buildModel()
model_shape,weights_flatten = flatten(model.get_weights())
indiv_size = 0

#Determine the size from the model
indiv_size = len(weights_flatten)

#Statistical Information
best_indivs_fitness = []
avg_indivs_fitness = []
time_per_gen = []
time_per_gen.append(time.time())


def get_neighbours(self):
    return self.representation


#Fitness function
def fitness(self):
    #Since the function is run in multiple threads a new model need to created multiple times

    #Build model and set weights
    model = buildModel()
    weights = reshape(self.representation,model_shape)
    model.set_weights(weights)

    steps = 0
    score = 0
    subtract_score = 0
    
    #Run the game multiple times
    for i in range(NUM_SIM_PER_FITNESS):
        s = SnakeGame(gridSize=(40,30))
        this_steps = 0

        #Run until game is over or maximum number of steps reached 
        while this_steps<MAX_STEPS_OPERATING*(s.getScore()+1) and s.isGameOver() == False:
            positions = [None] * 3

            features_values = []

            #Possible positions
            positions[0] = s.getFrontPos()
            positions[1] = s.getLeftPos()
            positions[2] = s.getRightPos()

            for pos in positions:
                features_values.append(int(s.posIsGameOver(pos)))
                features_values.append(s.getDistanceToFood(food_Pos=s.foodPos,pos=pos))

            converted_values = np.asarray(features_values)
            converted_values = np.atleast_2d(converted_values)
            
            val = model.predict_step(converted_values) #much faster then predict
            result = np.argmax(val) #Get best neuron

            if(result == 0):
                s.moveFront__()
            elif(result == 1):
                s.moveLeft__()
            elif(result == 2):
                s.moveRight__()
            else:
                raise Exception("No possible move")

            this_steps+=1
        if s.isGameOver() == True and s.getScore()>=1:
            subtract_score += 50
        
        score+=s.getScore()
        steps+=this_steps

    #Average all numbers
    score/=NUM_SIM_PER_FITNESS
    steps/=NUM_SIM_PER_FITNESS
    subtract_score/=NUM_SIM_PER_FITNESS

    #Calculate fitness
    final_score = score*100 + steps - subtract_score

    print("Score:",score,"Subtract Score",subtract_score," Steps:",steps," Fitness:",final_score)
    return final_score


#Generate a list of random weights
def getRandomWeights(size):
    return {uniform(-0.5, 0.5) for i in range(size)}




#Store generation information
def new_gen_feedback(pop):
    best_indivs_fitness.append(max(ind.fitness for ind in pop))
    avg_indivs_fitness.append(sum(ind.fitness for ind in pop)/len(pop))
    curr = time.time()
    time_per_gen.append(curr)
    
    #Benchamrk generation process time
    print("Time to process:",curr - time_per_gen[len(time_per_gen)-2])


    
# Monkey patching
charles.Individual.evaluate = fitness
charles.Individual.get_neighbours = get_neighbours

if __name__ == '__main__':
    init = time.time()
    os.mkdir("stats/"+GA_SETTINGS["name_folder"]+"/")

    #Load current weights
    #pop_weights = []
    #with open("all_pop.weights","r") as f:
    #    for line in f:
    #        float_vals = []
    #        vals = line.rstrip()[1:-1].split(", ")
    #        for val in vals:
    #            float_vals.append(float(val))
    #        pop_weights.append(float_vals)

    pop = charles.Population(
        size=GA_SETTINGS["population_size"],
        optim="max",
        #representations=pop_weights,
        valid_set=getRandomWeights(indiv_size*30),
        sol_size=indiv_size,
        replacement=False,
    )


    pop.evolve(
        gens=GA_SETTINGS["generations"],
        select=GA_SETTINGS["selection"],
        crossover= GA_SETTINGS["crossover"][0],
        mutate=GA_SETTINGS["mutation"][0],
        co_p=GA_SETTINGS["crossover"][1],
        mu_p=GA_SETTINGS["mutation"][1],
        elitism=GA_SETTINGS["elitism"][0],
        elitism_pct = GA_SETTINGS["elitism"][1],
        feedback_new_gen=new_gen_feedback,
        n_thread=6 #Number of threads, dependant on the number of logical cores of each system for best performance
    )



    indiv = max(pop, key=attrgetter("fitness")) #Best individual
    #pickle.dump(indiv.representation, open('best_indiv.txt', 'wb')) #Store best individual
    
    
    #Store population by sorted fitness
    with open("all_pop.weights","w") as f:
        indivs = sorted(pop.individuals, key=attrgetter("fitness"))
        for i in indivs:
            f.write(str(i.representation)+"\n")
    
    #Store statsitical information about the run
    with open("stats/"+GA_SETTINGS["name_folder"]+"/stats.txt","w") as f:
        for i in range(len(best_indivs_fitness)):
            f.write("Generation=" + str(i))
            f.write("\nBest Fitness=" + str(best_indivs_fitness[i]))
            f.write("\nAverage Fitness=" + str(avg_indivs_fitness[i]))
            f.write("\nTime Process=" + str(time_per_gen[i+1]-time_per_gen[i]))


    #Statistical information for the graphs
    txt = ""
    txt+="Selection: " + GA_SETTINGS["selection"].__name__+"\n"
    txt+="Crossover: " + GA_SETTINGS["crossover"][0].__name__+"\n"
    txt+="Crossover Pct: " + str(GA_SETTINGS["crossover"][1])+"\n"
    txt+="Mutation: " + GA_SETTINGS["mutation"][0].__name__+"\n"
    txt+="Mutation Pct: " + str(GA_SETTINGS["mutation"][1])+"\n"
    txt+="N simulations: " + str(GA_SETTINGS["simulation_per_fitness"])+"\n"
    txt+="Population Size: " + str(GA_SETTINGS["population_size"])+"\n"
    txt+="Generations: " + str(GA_SETTINGS["generations"])+"\n"
    txt+="Using elitism: " + str(GA_SETTINGS["elitism"][0])+"\n"
    if(GA_SETTINGS["elitism"][0] == True):
        txt+="Elitism pct: " + str(GA_SETTINGS["elitism"][1])+"\n"


    fig, ax = plt.subplots(2)
    fig.suptitle('Statisctical graph')
    ax[0].plot(range(len(best_indivs_fitness)),best_indivs_fitness,label='Best Agent')
    ax[0].set_title("Best Agent Fitness")

    ax[1].plot(range(len(best_indivs_fitness)),avg_indivs_fitness,label='Average Agent')
    ax[1].set_title("Average Agent Fitness")

    fig.tight_layout(h_pad=2.0)
    fig.subplots_adjust(left=0.35)
    fig.text(0.02,0.35, txt, fontsize=9)
    plt.savefig('stats/'+GA_SETTINGS["name_folder"]+'/stats.png')
    print("Time:",(time.time()-init)/60,"minutes")


