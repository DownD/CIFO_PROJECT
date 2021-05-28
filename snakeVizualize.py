from keras.models import Sequential
from keras.layers import Dense, Input
from snakeGame import SnakeGraphics, SnakeGame
from snakeTraining import reshape, buildModel, flatten
import time, copy
import numpy as np
import pickle



snakeGraphics = SnakeGraphics()
model = buildModel()
model_shape,weights_flatten = flatten(model.get_weights())

def nextMove(game,this_model,step):
    s = game
    positions = [None]*3#[copy.deepcopy(s) for x in range(3)]
    features_values = []


    positions[0] = s.getFrontPos()
    positions[1] = s.getLeftPos()
    positions[2] = s.getRightPos()
    

    for pos in positions:
        features_values.append(int(s.posIsGameOver(pos)))
        features_values.append(s.getDistanceToFood(food_Pos=s.foodPos,pos=pos))
    
    converted_values = np.asarray(features_values)
    converted_values = np.atleast_2d(converted_values)
    #t1 = time.time()
    val = model.predict_step(converted_values) #much faster then predict
    result = np.argmax(val)

    if(result == 0):
        s.moveFront__()
    elif(result == 1):
        s.moveLeft__()
    elif(result == 2):
        s.moveRight__()
    else:
        raise Exception("No possible move")
    return result



#weights_flatten = pickle.load(open('best_indiv.txt', 'rb'))

#Load all trained weights
pop_weights = []
with open("all_pop.weights","r") as f:
    for line in f:
        float_vals = []
        vals = line.rstrip()[1:-1].split(", ")
        for val in vals:
            float_vals.append(float(val))
        pop_weights.append(float_vals)

weights_flatten = pop_weights[-1]
weights = reshape(weights_flatten,model_shape)
model.set_weights(weights)


steps = 0
while True:
    print("Move updated->",nextMove(snakeGraphics.game,model,steps))
    snakeGraphics.updateNoMove()
    snakeGraphics.draw()
    steps+=1
    time.sleep(0.1)
