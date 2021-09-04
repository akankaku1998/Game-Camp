import turtle
from turtle import Screen, Turtle
import winsound
from flask import Flask, render_template
import pygame
from pygame.locals import *
import random
import sys
import time
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

#main code for flappy bird
@app.route('/flappy/')
def flappy():
  FPS = 40
  SCREENWIDTH =750
  SCREENHEIGHT = 534
  SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
  GROUNDY = SCREENHEIGHT * 0.9
  GAME_SPRITES = {}
  GAME_SOUNDS = {}
  PLAYER = 'static/bird.png'
  BACKGROUND = 'static/background.jpeg'
  PIPE = 'static/pipe.png'

  def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
  
    basex = 0
    while True:
      for event in pygame.event.get():
        # if user clicks on cross button, close the game
        if event.type == QUIT or (event.type==KEYDOWN and event.key == K_ESCAPE):
          pygame.quit()
          sys.exit()

        # If the user presses space or up key, start the game for them
        elif event.type==KEYDOWN and (event.key==K_SPACE or event.key == K_UP):
          return
        else:
          SCREEN.blit(GAME_SPRITES['background'], (0, 0))    
          SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))    
          SCREEN.blit(GAME_SPRITES['message'], (0,0))    
          SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))    
          pygame.display.update()
          FPSCLOCK.tick(FPS)

  def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
      {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
      {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
      {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
      {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping


    while True:
      for event in pygame.event.get():
          if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
          if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
              if playery > 0:
                playerVelY = playerFlapAccv
                playerFlapped = True
                GAME_SOUNDS['wing'].play()


      crashTest = isCollide(playerx, playery, upperPipes, lowerPipes) # This function will return true if the player is crashed
      if crashTest:
        return     

      #check for score
      playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
      for pipe in upperPipes:
        pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
        if pipeMidPos<= playerMidPos < pipeMidPos +4:
          score +=1
          print(f"Your score is {score}") 
          GAME_SOUNDS['point'].play()


      if playerVelY <playerMaxVelY and not playerFlapped:
        playerVelY += playerAccY

      if playerFlapped:
        playerFlapped = False            
      playerHeight = GAME_SPRITES['player'].get_height()
      playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

      # move pipes to the left
      for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
        upperPipe['x'] += pipeVelX
        lowerPipe['x'] += pipeVelX

      # Add a new pipe when the first is about to cross the leftmost part of the screen
      if 0<upperPipes[0]['x']<5:
        newpipe = getRandomPipe()
        upperPipes.append(newpipe[0])
        lowerPipes.append(newpipe[1])

      # if the pipe is out of the screen, remove it
      if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
        upperPipes.pop(0)
        lowerPipes.pop(0)
    
      # Lets blit our sprites now
      SCREEN.blit(GAME_SPRITES['background'], (0, 0))
      for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
        SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
        SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

      SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
      SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
      myDigits = [int(x) for x in list(str(score))]
      width = 0
      for digit in myDigits:
        width += GAME_SPRITES['numbers'][digit].get_width()
      Xoffset = (SCREENWIDTH - width)/2

      for digit in myDigits:
        SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
        Xoffset += GAME_SPRITES['numbers'][digit].get_width()
      pygame.display.update()
      FPSCLOCK.tick(FPS)

  def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 25  or playery<0:
      GAME_SOUNDS['hit'].play()
      return True
    
    for pipe in upperPipes:
      pipeHeight = GAME_SPRITES['pipe'][0].get_height()
      if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in lowerPipes:
      if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
        GAME_SOUNDS['hit'].play()
        return True

    return False

  def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT/3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
      {'x': pipeX, 'y': -y1}, #upper Pipe
      {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe


  if __name__ == "__main__":
    # This will be the main point from where our game will start
    pygame.init() # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')
    GAME_SPRITES['numbers'] = ( 
      pygame.image.load('static/0.png').convert_alpha(),
      pygame.image.load('static/1.png').convert_alpha(),
      pygame.image.load('static/2.png').convert_alpha(),
      pygame.image.load('static/3.png').convert_alpha(),
      pygame.image.load('static/4.png').convert_alpha(),
      pygame.image.load('static/5.png').convert_alpha(),
      pygame.image.load('static/6.png').convert_alpha(),
      pygame.image.load('static/7.png').convert_alpha(),
      pygame.image.load('static/8.png').convert_alpha(),
      pygame.image.load('static/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] =pygame.image.load('static/message.png').convert_alpha()
    GAME_SPRITES['base'] =pygame.image.load('static/base.png').convert_alpha()
    GAME_SPRITES['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
    pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('wing.wav')

    GAME_SPRITES['background'] = pygame.image.load('static/background.jpeg').convert()
    GAME_SPRITES['player'] = pygame.image.load('static/bird.png').convert_alpha()

    count = 1
    while count!=0:
      welcomeScreen() # Shows welcome screen to the user until he presses a button
      mainGame() # This is the main game function
      count -= 1
  return render_template('final.html')

#main code for snake game
@app.route('/snake/')
def snake():
  from snake import Snake
  from food import Food
  from score_snake import Score

  screen = Screen()
  user_input = screen.textinput(title="PONG GAME", prompt="ENTER ANY ALPHABET TO START THE GAME")
  game_start = False
  screen.setup(width=600, height=600)
  screen.bgcolor("black")
  screen.title("MY SNAKE GAME")
  screen.tracer(0)

  snake = Snake()
  food = Food()
  score = Score()

  screen.listen()
  screen.onkey(snake.up, "Up")
  screen.onkey(snake.down, "Down")
  screen.onkey(snake.left, "Left")
  screen.onkey(snake.right, "Right")

  if user_input:
    game_start = True
  while game_start:
    screen.update()
    time.sleep(0.15)
    snake.move()

    if snake.head.distance(food) < 15:
      winsound.PlaySound("snakehit.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
      food.random_food()
      snake.extend()
      score.update_score()

    if snake.head.xcor() > 280 or snake.head.xcor() < -280 or snake.head.ycor() > 280 or snake.head.ycor() < -280:
      winsound.PlaySound("hit.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
      game_start = False
      score.game_over()

    for segment in snake.segments[1:]:
      if snake.head.distance(segment) < 10:
        winsound.PlaySound("hit.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
        game_start = False
        score.game_over()

  screen.exitonclick()
  return render_template('final.html')

#main code for pong game
@app.route('/pong/')
def pong():
  from paddle import Paddle
  from ball import Ball
  from score_pong import Score

  screen = Screen()
  screen.bgcolor("black")
  screen.setup(width=800, height=600)
  screen.title("PONG GAME")
  screen.tracer(0)
  user_input = screen.textinput(title="PONG GAME", prompt="ENTER ANY ALPHABET TO START THE GAME")
  game_start = False

  paddle_r = Paddle((350, 0))
  paddle_l = Paddle((-350, 0))
  ball = Ball()
  score = Score()

  screen.listen()
  screen.onkey(paddle_r.go_up, "Up")
  screen.onkey(paddle_r.go_down, "Down")
  screen.onkey(paddle_l.go_up, "w")
  screen.onkey(paddle_l.go_down, "s")

  if user_input:
    game_start = True
  while game_start:
    time.sleep(ball.move_speed)
    screen.update()
    ball.move()

    if ball.ycor() > 280 or ball.ycor() < -280:
      ball.bounce_y()

    if (ball.distance(paddle_r) < 50 and ball.xcor() > 320) or (ball.distance(paddle_l) < 50 and ball.xcor() > -320):
      ball.bounce_x()

    if ball.xcor() > 380:
      winsound.PlaySound("point.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
      ball.center()
      score.point_l()
      score.update_score()

    if ball.xcor() < -380:
      winsound.PlaySound("point.wav", winsound.SND_ASYNC | winsound.SND_ALIAS )
      ball.center()
      score.point_r()
      score.update_score()

    if score.score_r == 10 or score.score_l == 10:
      ball.stop()
      game_start = False

  screen.clear()
  turtle.bgcolor("black")
  turtle.penup()
  turtle.color("white")
  turtle.hideturtle()
  if score.score_r == 10:
    turtle.write("RIGHT WIN!!", True, align="center", font=("Arial", 50, "normal"))
  else:
    turtle.write("Left WIN!!", True, align="center", font=("Arial", 50, "normal"))

  screen.exitonclick()
  return render_template('final.html')

#main code for race game
@app.route('/race/')
def race():
  screen = Screen()
  screen.setup(width=500, height=400)
  user_input = screen.textinput(title="Make Your Bet", prompt="Which turtle will win the race?\nColors: red, blue, yellow, green, purple\nEnter a color:")
  race_start = False

  turtle_list = []
  x = -230
  y = -80
  color = ["red", "blue", "yellow", "green", "purple"]
  for i in range(0, 5):
    k = Turtle(shape="turtle")
    k.penup()
    k.color(color[i])
    k.goto(x, y)
    y += 30
    turtle_list.append(k)


  def display_result(msg):
    turtle.color("black")
    turtle.goto(-100, 0)
    turtle.write(msg, True, align="left")

      

  if user_input:
    race_start = True


  while race_start:
    for turtle in turtle_list:
      if turtle.xcor() > -x:
        race_start = False
        screen.clear()
        win = turtle.pencolor()
        if win == user_input:
          msg = f"You've won! The {win} turtle is the winner!"
        else:
          msg = f"You've lost! The {win} turtle is the winner!"
        display_result(msg)
      turtle.forward(random.randint(0, 10))
  screen.exitonclick()
  return render_template('final.html')

#main code for car crossing game
@app.route('/car-crossing/')
def car_crossing():
  from player import Player
  from car_manager import CarManager
  from score_car_crossing import Score

  screen = Screen()
  screen.setup(width=600, height=600)
  screen.tracer(0)
  user_input = screen.textinput(title="CAR CROSSING GAME", prompt="ENTER ANY ALPHABET TO START THE GAME")
  game_start = False

  player = Player()
  car_manager = CarManager()
  score = Score()


  screen.listen()
  screen.onkey(player.go_up,"space")

  if user_input:
    game_start = True
  count = 0
  while game_start:
    time.sleep(0.1)
    screen.update()

    count += 1
    if count == 6:
      car_manager.create()
      count = 0
    car_manager.move()

    for car in car_manager.cars:
      if car.distance(player) < 20:
        game_start = False
        score.game_over()

    if player.ycor() > 280:
      player.start_again()
      car_manager.level_up()
      score.update_level()


  screen.exitonclick()
  return render_template('final.html')

if __name__ == '__main__':
  app.run(debug=True, port=8000)