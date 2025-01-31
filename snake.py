import pygame, sys, time, random
import numpy as np
from time import sleep
import os
#os.environ['SDL_AUDIODRIVER'] = 'dummy'

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
game_window = None

def newGame():
    """
    Resets all the parameters of the game to their initial values.
    This function is called at the start of each game and whenever the snake dies.
    """
    global snake_pos, food_pos, score, food_spawn, snake_body

    # Reset the position of the snake head
    init_pos_x = random.randrange(1, (screenSize['x']//10)) * 10
    init_pos_y = random.randrange(1, (screenSize['y']//10)) * 10
    snake_pos = [init_pos_x, init_pos_y]

    # Reset the snake body
    snake_body = [
        [init_pos_x, init_pos_y], 
        [init_pos_x-10, init_pos_y], 
        [init_pos_x-(2*10), init_pos_y]
    ]

    # Reset the position of the food
    food_pos = [
        random.randrange(1, (screenSize['x']//10)) * 10, 
        random.randrange(1, (screenSize['y']//10)) * 10
    ]
    food_spawn = True

    # Reset the score
    score = 0

def main(emulate, onGameOver, onScore):
    global game_window
    
    # Initialize all imported pygame modules and check for any errors
    check_errors = pygame.init()
    
    # pygame.init() returns a tuple, the second element indicates the number of errors
    if check_errors[1] > 0:
        # If there are any errors, exit the program with a status of -1
        sys.exit(-1)
    else:
        # Otherwise, the game was successfully initialized
        pass

    # Set the window title to 'Snake Eater'
    pygame.display.set_caption('Snake Eater')
    
    # Create a display surface for the game with specified dimensions
    game_window = pygame.display.set_mode((screenSize['x'], screenSize['y']))

    # Create a clock object to help control and manage the game's frame rate
    fps_controller = pygame.time.Clock()

    # Call the main game loop with the necessary parameters
    mainGame(emulate, fps_controller, onGameOver, onScore)


moveCounter = 0
moves = []
moveSinceScore = 0

def mainGame(emulate, fps_controller, onGameOver, onScore):
    global moveCounter, moves, moveSinceScore
    global food_pos, food_spawn, snake_body, snake_pos, score, colors, screenSize, direction, change_to
    global game_window
    
    # Initialize move counter at the start of the game
    moveCounter = 0
    
    # Main game loop
    while True:
        # Process all events that have occurred
        for event in pygame.event.get():
            # If the QUIT event is triggered, exit the game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # If a key is pressed down
            elif event.type == pygame.KEYDOWN:
                # Change direction based on key pressed
                if event.key == pygame.K_UP or event.key == ord('w'):
                    change_to = 'UP'
                if event.key == pygame.K_DOWN or event.key == ord('s'):
                    change_to = 'DOWN'
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    change_to = 'LEFT'
                if event.key == pygame.K_RIGHT or event.key == ord('d'):
                    change_to = 'RIGHT'
                # If ESC is pressed, post a QUIT event to exit the game
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

#below is the same as the code in snake_headless.py

        # Calculate the difference between the food position and snake head
        diff = [snake_pos[0] - food_pos[0], snake_pos[1] - food_pos[1]]
        diff = abs(diff[0] + diff[1])
        
        # Parameters to pass to the emulate function
        params = {
            'food_pos': food_pos, 
            'snake_pos': snake_pos,
            'snake_body': snake_body,
            'score': score,
            'diff': diff,
            'screenSizeX': screenSize['x'],
            'screenSizeY': screenSize['y'],
            'moveSinceScore': moveSinceScore
        }

        # Call emulate function to determine the direction to move
        choosenDirection = emulate(params)

        # Update direction and move counters based on chosen direction
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

        # Ensure snake can't instantly move in the opposite direction
        if change_to == 'UP' and direction != 'DOWN':
            direction = 'UP'
        if change_to == 'DOWN' and direction != 'UP':
            direction = 'DOWN'
        if change_to == 'LEFT' and direction != 'RIGHT':
            direction = 'LEFT'
        if change_to == 'RIGHT' and direction != 'LEFT':
            direction = 'RIGHT'

        # Move the snake in the current direction
        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        # Snake grows if it eats food
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            moveSinceScore = 0
            onScore(params)
            food_spawn = False
        else:
            # Remove last part of snake body if no food eaten
            snake_body.pop()

        # Spawn new food if not already present
        if not food_spawn:
            food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]
            # Ensure food doesn't spawn inside the snake's body
            for x in snake_body:
                while (food_pos == x):
                    food_pos = [random.randrange(1, (screenSize['x']//10)) * 10, random.randrange(1, (screenSize['y']//10)) * 10]

        food_spawn = True

#below is different from the code in snake_headless.py
        # Clear game window by filling it with black color
        game_window.fill(colors['black'])

        # Draw the snake on the game window
        for index, pos in enumerate(snake_body):
            # Draw the snake head in dark green
            if(index > 0):
                pygame.draw.rect(game_window, colors['green'], pygame.Rect(pos[0], pos[1], 10, 10))
            else:
                pygame.draw.rect(game_window, colors['darkGreen'], pygame.Rect(pos[0], pos[1], 10, 10))

        # Draw the food on the game window
        pygame.draw.rect(game_window, colors['red'], pygame.Rect(food_pos[0], food_pos[1], 10, 10))

        # Check game over conditions
        # Snake collides with walls
        if snake_pos[0] < 0 or snake_pos[0] > screenSize['x']-10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)
        if snake_pos[1] < 0 or snake_pos[1] > screenSize['y']-10:
            game_over(emulate, colors, score, game_window, screenSize, onGameOver)

        # Snake collides with itself
        for block in snake_body[1:]:
            if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
                game_over(emulate, colors, score, game_window, screenSize, onGameOver)

        # Update the game display after drawing the snake and food
        pygame.display.update()

        # Control the frame rate of the game
        fps_controller.tick(FPS)

# Game Over
def game_over(emulate, colors, score, game_window, screenSize, onGameOver):
    """
    This function is called when the snake game is over. It resets the game state
    and calls the onGameOver callback function.

    :param emulate: The emulate function from the qlearning module.
    :param colors: A dictionary of colors.
    :param score: The score of the game that just ended.
    :param game_window: The game window to draw on.
    :param screenSize: A dictionary containing the size of the game window.
    :param onGameOver: The onGameOver callback function to call.
    """

    # Reset the move counter and call the onGameOver callback function
    global moves, moveCounter
    moveCounter = 0
    onGameOver(score, moves)
#all the code mentioned pygame is different from the code in snake_headless.py
    # Fill the game window with black and update the display
    game_window.fill(colors['black'])
    pygame.display.flip()

    # Call the newGame function to reset the game state
    newGame()
