"""
This project is based on https://github.com/kevinunger/snake-Q-Learning. We modified the code to fit our needs.
We modified the parameters to fit our needs and added a few more parameters to the code.
We added the detailed explanation of the code.
"""
import numpy as np
import sys
from collections import defaultdict
import pickle
from time import sleep, time
import os
#os.environ['SDL_AUDIODRIVER'] = 'dummy'

if sys.argv[1] == "p":
    mode = "play"
if sys.argv[1] == "t":
    mode = "train"

if mode == "play":
    import snake
else:
    import snake_headless

rewardAlive = -1
rewardKill =  -10000
rewardScore = 50000000

alpha = 0.1
alphaD = 1
#alpha --> learning rate
#alphaD --> decay factor of the learning rate

gamma = 0.9
#discount factor

if mode == "play":
    e = 0.0001
    ed = 1
    emin = 0.0001
else:
    e = 0.9
    ed = 1.3
    emin = 0.0001

#e --> randomness, epsilon-greedy exploration
#ed --> decay factor of e



try:
    with open(r"C:\Users\DELL\Downloads\snake-Q-Learning-master\snake-Q-Learning-master\Q\Q.pickle", "rb") as file:
        Q = defaultdict(lambda: [0,0,0,0], pickle.load(file))
except:
    Q = defaultdict(lambda: [0,0,0,0])  #(UP,LEFT,DOWN,RIGHT)
"""
After training, the Q table is saved in a file called "Q.pickle".
<class 'dict'>
{'100010_0000_0000_0': [5416578.8755799215, 2692306.287212638, 2809514.3964385553, 2712410.7568099964], 
None: [5060518.899457691, 0, 0, 0], 
'100010_0000_0000_3': [1643862.5238455818, 1792078.2683447453, 1974082.6886699896, 5216994.966730276], 
'100010_0000_0000_1': [5232276.226739913, 2489500.4830415635, 2208105.307493244, 2483271.6072267178], 
"""
lastMoves = ""
def paramsToState(params):
    """
    Takes the parameters of the game (food position, snake position, snake body, score, ...) 
    and returns a string representing the state of the game.
    This string is used as a key in the Q-learning table.
    
    The state string is composed of 4 parts:
    1. relativeFoodPosition: where is the food relative to the snake body
    2. screenDanger: is the snake near the edge of the screen
    3. bodyDanger: is the snake body near to bite itself
    4. direction: which direction is the snake moving
    """
    global lastMoves

    ################# relativeFoodPosition (where is the food relative to the snake body) ###################
    relativeFoodPostion = [0,0,0,0,0,0]
        
    if (params["food_pos"][0] - params["snake_pos"][0]) > 0:        #foodRight
        relativeFoodPostion[0] = 1
    if (params["food_pos"][0] - params["snake_pos"][0]) < 0 :       #foodLeft
        relativeFoodPostion[1] = 1
    if ((params["food_pos"][0] - params["snake_pos"][0]) == 0):     #foodXMiddle
        relativeFoodPostion[2] = 1

    if (params["food_pos"][1] - params["snake_pos"][1]) > 0:        #foodDown
        relativeFoodPostion[3] = 1
    if (params["food_pos"][1] - params["snake_pos"][1]) < 0 :       #foodTop
       relativeFoodPostion[4] = 1
    if ((params["food_pos"][1] - params["snake_pos"][1]) == 0):     #foodYMiddle
        relativeFoodPostion[5] = 1

    rFP = ""                        #als String concatenated
    for x in relativeFoodPostion:
        rFP += str(x)

    ################# ScreenDanger (at the edge of the screen?) ###################

    screenDanger = [0,0,0,0]
    if(params["screenSizeX"] - params["snake_pos"][0] == 10):                               #dangerRight
        screenDanger[0] = 1
    if(params["screenSizeX"] - params["snake_pos"][0] == params["screenSizeX"]):            #dangerLeft
        screenDanger[1] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == 10):                               #dangerBottom
        screenDanger[2] = 1
    if(params["screenSizeY"] - params["snake_pos"][1] == params["screenSizeY"]):            #dangerTop
        screenDanger[3] = 1

    sD = ""                        #als String concatenated
    for x in screenDanger:
        sD += str(x)

    ################# Danger Body (is body reachable to bite?) ###################

    snake_body = []
    skip = 0
    for pos in params["snake_body"]:                # ignore the first 4 body parts
        if (skip > 3):
             snake_body.append(pos)
        skip+=1
    
    bodyDanger = [0,0,0,0]
    for bodyPart in snake_body:
        #print(bodyPart)
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == 10 ):  #BodyPartUp
            bodyDanger[0] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 0 and params["snake_pos"][1] - bodyPart[1] == -10 ): #BodypartDown
            bodyDanger[1] = 1
        if(params["snake_pos"][0] - bodyPart[0] == 10 and params["snake_pos"][1] - bodyPart[1] == 0 ):  #BodyPartLeft
            bodyDanger[2] = 1
        if(params["snake_pos"][0] - bodyPart[0] == -10 and params["snake_pos"][1] - bodyPart[1] == 0 ): #BodypartRight
            bodyDanger[3] = 1
            

    bD = ""                        #as String concatenated
    for x in bodyDanger:
        bD += str(x)

    direction = ""
    dx = params["snake_body"][1][0] - params["snake_body"][0][0]
    dy = params["snake_body"][1][1] - params["snake_body"][0][1]

    if dx == -10 and dy == 0:
        #Moving right
        direction="0"
    if dx == 10 and dy == 0:
        #Moving left
        direction="1"
    if dx == 0 and dy == 10:
        #Moving up
        direction="2"
    if dx == 0 and dy == -10:
        #Moving down
        direction="3"


    #state = xxxxxx_xxxx_xxxx_xx
    #state contains where the food is relative to the snake, if a screen edge is near, 
    #if a body part is near and the direction the snake took

    state = rFP + "_" + sD + "_" + bD + "_" + direction
    return state

oldState = None
oldAction = None
gameCounter = 0
gameScores = []

def emulate(params):
    """
    This function is the "brain" of the snake game. It makes decisions based on the current state of the game.
    It uses a Q-table to determine the best action to take.

    The Q-table is a dictionary, where the keys are states and the values are lists of 4 numbers, each representing the reward for taking a certain action (up, left, down, right) in that state.

    The function takes in a dictionary of parameters, which includes the current state of the snake, the food position, and other relevant information.

    It returns the action to take, which is one of 'U', 'L', 'D', 'R'.
    """

    global oldState
    global oldAction

    # Convert the parameters to a state string
    state = paramsToState(params)

    # Get the estimated reward for each action in this state
    estReward = Q[state]

    # Get the previous reward for the previous state
    prevReward = Q[oldState]

    # Get the index of the previous action
    index = 0
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3
    

    # Calculate the reward for this move. The reward is negative and decreases the longer the snake takes to eat the food. 
    # The reward is reset to 0 when the snake eats the food.
    reward = (0 -params["moveSinceScore"]) / 50

    # Update the previous reward for the previous state
    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (reward + gamma * max(estReward) )

    # Update the Q-table with the new reward
    Q[oldState] = prevReward

    # Update the old state and old action
    oldState = state
    basedOnQ = np.random.choice([True, False], p=[1-e,e])

    # Based on the Q-table, choose an action
    if basedOnQ == False:
        # Random choice based on e (decreases over time with ed)
        choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
        oldAction = choice
        return choice
    else:
        # Choose the action with the highest estimated reward
        if estReward[0] > estReward[1] and estReward[0] > estReward[2] and estReward[0] > estReward[3]:
            oldAction = 'U'
            return 'U'
        if estReward[1] > estReward[0] and estReward[1] > estReward[2] and estReward[1] > estReward[3]:
            oldAction = 'L'
            return 'L'
        if estReward[2] > estReward[0] and estReward[2] > estReward[1] and estReward[2] > estReward[3]:
            oldAction = 'D'
            return 'D'
        if estReward[3] > estReward[0] and estReward[3] > estReward[1] and estReward[3] > estReward[2]:
            oldAction = 'R'
            return 'R'
        else:
            # If all rewards are equal, choose a random action
            choice = np.random.choice(['U','L','D','R'], p=[0.25, 0.25,0.25,0.25])
            oldAction = choice
            return choice
        

gameCounter = []
gameCounter = 0
start = 0 
end = 0

    
def onGameOver(score, moves):
    """
    This is a callback function that is called whenever the snake runs into itself or the border.
    It's responsible for updating the Q-table of the previous state (the state that led to the game over).
    :param score: The score of the game that just ended.
    :param moves: The number of moves that the snake made in the game that just ended.
    """

    # Append the score of the game to the list of scores
    gameScores.append(score)

    # Update the Q-table of the previous state (state which lead to gameOver)
    prevReward = Q[oldState]

    # If the snake didn't make any moves, the Q value of the previous state is just the reward for the game over
    if oldAction == None:
        index = 0
    # Otherwise, the Q value of the previous state is the reward for the game over plus the discounted Q value of the next state
    else:
        if oldAction == 'U':
            index = 0
        if oldAction == 'L':
            index = 1
        if oldAction == 'D':
            index = 2
        if oldAction == 'R':
            index = 3

        # Update the Q value of the previous state
        prevReward[index] = (1 - alpha) * prevReward[index] + \
                            alpha * rewardKill
    """
Why This Update is Important
When the snake dies, the agent needs to learn that the action taken in the previous state led to a bad outcome.
By updating the Q-value with a large negative reward (rewardKill), the agent associates the previous state-action pair with a high penalty.
Over time, the agent will learn to avoid actions that lead to losing the game.
    """
    # Update the Q table with the new reward
    # Save the updated Q value of the previous state
    Q[oldState] = prevReward

    # Reset the old state and old action
    oldState = None
    oldAction = None

    # Save the Q table as a pickle every 200 games
    if gameCounter % 200 == 0:
        with open(r"C:\Users\DELL\Downloads\snake-Q-Learning-master\snake-Q-Learning-master\Q\Q.pickle","wb" ) as file:
            pickle.dump(dict(Q), file)
        print("+++++++++ Pickle saved +++++++++")

    # Print some stats every 100 games
    if gameCounter % 100 == 1:
        end = time()
        timeD = end - start
        print (str(gameCounter)+ " : " + "\t" + 'meanScore: ' +  str(np.mean(gameScores[-100:])) + "| HighScore: " + str(np.max(gameScores)) + \
              '| moves: ' + str(np.mean(moves[-100:])) + "| time for 10 games: " + str(round(timeD*10)/100))
        start = time()

    # Print the hyperparameters every 100 games
    if gameCounter % 100 == 0:
        print ("a:", alpha)
        print ("e:", e)
        print ("g:", gamma)

    # Decrease the learning rate and the randomness over time
    if gameCounter % 100 == 0:
        alpha = alpha * alphaD
        if e > emin:
            e = e / ed

    # Increment the game counter
    gameCounter += 1



def onScore(params):
    """
    This function gets called when the snake scores a point (eats the food).
    It updates the Q table with the new reward for the previous state and action.
    It also saves the new state as the old state to be used in the next iteration.
    """
    global oldState
    global oldAction
    global gameCounter

    # Convert the parameters to a state string
    state = paramsToState(params)

    # Get the estimated reward for each action in this state
    estReward = Q[state]

    # Get the previous reward for the previous state
    prevReward = Q[oldState]

    # Get the index of the previous action
    if oldAction == 'U':
        index = 0
    if oldAction == 'L':
        index = 1
    if oldAction == 'D':
        index = 2
    if oldAction == 'R':
        index = 3

    # Update the previous reward for the previous state using the Q-learning formula:
    # Q(s, a) <- Q(s, a) + alpha * [reward(s, a) + gamma * max(Q(s', a')) - Q(s, a)]
    prevReward[index] = (1 - alpha) * prevReward[index] + \
                      alpha * (rewardScore + gamma * max(estReward) )

    # Save the updated Q value of the previous state
    Q[oldState] = prevReward



if mode == "play":
    snake.main(emulate, onGameOver, onScore)
else:
    snake_headless.main(emulate, onGameOver, onScore)

