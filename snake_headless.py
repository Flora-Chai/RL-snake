import pygame, sys, time, random
import numpy as np
from time import sleep
import os

#os.environ['SDL_AUDIODRIVER'] = 'dummy'
#Headless version for training that disables fps limit and graphics

screenSize = {'x': 500,'y':500}
FPS = 100
direction = 'RIGHT'
change_to = direction
colors = {
    'black': pygame.Color(0, 0, 0), 
    'white': pygame.Color(255, 255, 255), 
    'red': pygame.Color(255, 0, 0), 
    'green':pygame.Color(0, 255, 0), 
    'darkGreen':pygame.Color(50, 200, 50), 
    'blue': pygame.Color(0, 0, 255)
}


init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10 
init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10
snake_pos = [init_pos_x, init_pos_y]
snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
#food_pos = [20,30]

score = 0
food_spawn = True


def newGame():
    """
    Resets all the parameters of the game to their initial values.

    This function is called at the start of each game and whenever the snake dies.
    """
    global snake_pos, food_pos, score, food_spawn, snake_body

    # Reset the position of the snake head
    # Choose a random x and y position for the snake head, making sure
    # it's not right at the edge of the screen
    init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10 
    init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10

    snake_pos = [init_pos_x, init_pos_y]

    # Reset the snake body
    # The snake body is a list of coordinates, where each element is the
    # position of the snake's segment
    snake_body = [[init_pos_x, init_pos_y], [init_pos_x-10, init_pos_y], [init_pos_x-(2*10), init_pos_y]]

    # Reset the position of the food
    # Choose a random x and y position for the food, making sure
    # it's not right at the edge of the screen
    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

    # Reset the flag to indicate that the food should spawn
    food_spawn = True

    # Reset the score
    score = 0

def main(emulate, onGameOver, onScore):
    """
    This is the main entry point of the game. It calls the mainGame function
    which contains the game loop. The game loop processes all events, updates
    the game state, and draws the game.

    First, it checks for errors encountered when initialising pygame. If any
    errors occur, it prints a message and exits the game.
    """
    # Checks for errors encountered
    check_errors = pygame.init()
    # pygame.init() example output -> (6, 0)
    # second number in tuple gives number of errors
    if check_errors[1] > 0:
        # If any errors occur, print a message and exit the game
        print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
        sys.exit(-1)
    else:
        # No errors encountered, print a success message
        print('[+] Game successfully initialised')
        pass


    # Call the mainGame function which contains the game loop
    mainGame(emulate, onGameOver, onScore)


moveCounter = 0
moves = []
moveSinceScore = 0

def mainGame(emulate, onGameOver, onScore):
    """
    This is the main game loop. It calls the emulate function from the qlearning
    module to determine the direction to move the snake. The emulate function
    takes in a dictionary of parameters, which includes the current state of the
    snake, the food position, and other relevant information. The direction is
    then determined based on the output of the emulate function.

    The game loop also checks for game over conditions and calls the
    game_over function if any of them are met. The game_over function resets the
    game state and calls the onGameOver callback function.

    The game loop also keeps track of the number of moves since the last food
    spawn and resets it to 0 when food is spawned. The number of moves since the
    last food spawn is passed to the onScore callback function when food is
    spawned.
    """
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to

    moveCounter = 0
    while True:
        # Calculate the difference between the food position and snake head
        # This is used as a parameter to the emulate function
        diff = [snake_pos[0] - food_pos[0], snake_pos[1] - food_pos[1]]
        diff = abs(diff[0] + diff[1])

        # Create a dictionary of parameters to pass to the emulate function
        params = {
            'food_pos': food_pos, 
            'snake_pos': snake_pos,
            'snake_body': snake_body,
            'score': score,
            'diff':diff,
            'screenSizeX': screenSize['x'],
            'screenSizeY': screenSize['y'],
            'moveSinceScore': moveSinceScore
        }

        # Call the emulate function to determine the direction to move
        choosenDirection = emulate(params)

        # Update the move counter and move list
        if choosenDirection == 'U':
            change_to = 'UP'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'D':
            change_to = 'DOWN'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'L':
            change_to = 'LEFT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1
        if choosenDirection == 'R':
            change_to = 'RIGHT'
            moveCounter += 1
            moves.append(moveCounter)
            moveSinceScore += 1

        # Making sure the snake cannot move in the opposite direction instantaneously
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Move the snake
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))

        # Check if the snake has eaten food
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            moveSinceScore = 0
            onScore(params)
            food_spawn = False
        else:
            snake_body.pop()

        # Spawn food on the screen
        if not food_spawn:
            food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
            for x in snake_body:    #when food spawns in snake body --> new position
                while (food_pos  == x):
                    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

        food_spawn = True

        # Game Over conditions
        # Getting out of bounds
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y']-10:
            game_over(emulate, colors, score, screenSize, onGameOver)

        # Touching the snake body
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, screenSize, onGameOver)
                
# Game Over
def game_over(emulate, colors, score, screenSize, onGameOver):
    """
    This function is called when the snake runs into a wall or its own body,
    which marks the end of the game. When this happens, the score of the game
    is passed to the onGameOver callback function, which is defined in the
    qlearning module. The newGame function is then called to reset the game
    state.

    :param emulate: The emulate function from the qlearning module.
    :param colors: A dictionary of colors.
    :param score: The score of the game that just ended.
    :param screenSize: A dictionary containing the size of the game window.
    :param onGameOver: The onGameOver callback function to call.
    """
    # Reset the move counter
    global moves, moveCounter
    moveCounter = 0
    
    # Call the onGameOver callback function
    onGameOver(score, moves)
    
    # Reset the game state
    newGame()
