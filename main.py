# -*- coding: cp1252 -*-
import pygame, sys, random
from pygame.locals import *

pygame.init()

config = open('config.txt','r')
highscoreFile = open('highscore.txt','r')

WINDOWSIZE = (WINDOWWIDTH,WINDOWHEIGHT) = (int(config.readline()),int(config.readline()))

screen = pygame.display.set_mode(WINDOWSIZE)
pygame.display.set_caption("Zombies")

airDarkImage = pygame.image.load("Images\\airDark.png").convert()
grassImage = pygame.image.load("Images\\grass.png").convert()
flowersRedImage = pygame.image.load("Images\\flowersRed.png").convert()
flowersBlueImage = pygame.image.load("Images\\flowersBlue.png").convert()
flowersWhiteImage = pygame.image.load("Images\\flowersWhite.png").convert()
dirtImage = pygame.image.load("Images\\dirt.png").convert()
stoneImage = pygame.image.load("Images\\stone.png").convert()

bulletImage = pygame.image.load("Images\\bullet.png")

zombieRightImage = pygame.image.load("Images\\zombieRight.png")
zombieLeftImage = pygame.image.load("Images\\zombieLeft.png")

playerRightImage = pygame.image.load("Images\\playerRight.png")
playerLeftImage = pygame.image.load("Images\\playerLeft.png")

playerImage = playerRightImage

FPS = 30
clock = pygame.time.Clock()
playing = False

score = 0
highscore = highscoreFile.readline()
playerHealth = 100
playerStamina = 100

highscoreFile.close()

blockSize = 16

fontBig = pygame.font.SysFont(None, 48)
font = pygame.font.SysFont(None, 24)
TEXTCOLOR = (0,0,0)

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class block(object):
    image = airDarkImage
    size = blockSize
    name = "block"
    blockID = 0
    collidable = False

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.Rect = ((self.x * 16,self.y * 16),(16,16))

    def draw(self,screen,x,y):
        self.screen = screen
        self.x =x
        self.y = y
        self.screen.blit(self.image,(self.x,self.y))

class blockGrass(block):
    image = grassImage
    name = "Grass"
    blockID = 1

class blockFlowersRed(block):
    image = flowersRedImage
    name = "Red Flowers"
    blockID = 2

class blockFlowersBlue(block):
    image = flowersBlueImage
    name = "Blue Flowers"
    blockID = 3

class blockFlowersWhite(block):
    image = flowersWhiteImage
    name = "White Flowers"
    blockID = 4

class blockDirt(block):
    image = dirtImage
    name = "Dirt"
    blockID = 5
    

class blockStone(block):
    image = stoneImage
    name = "Stone"
    blockID = 6
    collidable = True

class bullet(object):
    
    image = bulletImage
    name = "Bullet"
    speed = 8

    def __init__(self,startX,startY,direction,damage):
        self.startX = startX
        self.startY = startY
        self.Rect = pygame.Rect((startX,startY),(1,1))

        self.damage = damage

        self.direction = direction

    def move(self):

        if self.direction == "left":
            self.Rect.move_ip(-1 * self.speed,0)
        
        elif self.direction == "right":
            self.Rect.move_ip(self.speed,0)

        elif self.direction == "up":
            self.Rect.move_ip(0,-1 * self.speed)

        elif self.direction == "down":
            self.Rect.move_ip(0,self.speed)
    
    def draw(self,x,y):
        screen.blit(self.image,(x,y))

class zombie(object):

    image = zombieLeftImage
    name = "Zombie"
    speed = 1
    direction = "n"
    health = 0
    collidedBlock = (0,0)

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.Rect = pygame.Rect((self.x,self.y),(16,16))

        self.health = 0

    def findPlayer(self,playerX,playerY):

        if playerX < self.Rect.left and playerY < self.Rect.top:
            self.Rect.move_ip(-1 * self.speed, -1 * self.speed)
            self.image = zombieLeftImage

        elif playerX > self.Rect.left and playerY > self.Rect.top:
            self.Rect.move_ip(self.speed,self.speed)
            self.image = zombieRightImage

        elif playerX < self.Rect.left and playerY > self.Rect.top:
            self.Rect.move_ip(-1 * self.speed,self.speed)
            self.image = zombieLeftImage

        elif playerX > self.Rect.left and playerY < self.Rect.top:
            self.Rect.move_ip(self.speed,-1 * self.speed)
            self.image = zombieRightImage

        elif playerX > self.Rect.left and playerY == self.Rect.top:
            self.Rect.move_ip(self.speed,0)
            self.image = zombieRightImage

        elif playerX < self.Rect.left and playerY == self.Rect.top:
            self.Rect.move_ip(-1 * self.speed,0)
            self.image = zombieLeftImage

        elif playerX == self.Rect.left and playerY > self.Rect.top:
            self.Rect.move_ip(0,self.speed)

        elif playerX == self.Rect.left and playerY < self.Rect.top:
            self.Rect.move_ip(0,-1 * self.speed)

    def draw(self,drawX,drawY):
        screen.blit(self.image,(drawX,drawY))
        

grid = []
gridLength = int(config.readline())
gridHeight = int(config.readline())

bullets = []
zombies = []

ticksSinceSpawn = 0
ticksSinceShot = 0

config.close()



grid = []
bullets = []
zombies = []

ticksSinceSpawn = 0
ticksSinceShot = 0

score = 0
playerHealth = 100

currentWave = 1
maxZombies = 20
zombiesSpawned = maxZombies
    
cameraRect = pygame.Rect((0,0),(WINDOWWIDTH + 32,WINDOWHEIGHT + 32))

playerRect = pygame.Rect((gridLength * 8,gridHeight * 8),(16,16))
playerMoveRate = 2
playerUp = False
playerDown = False
playerLeft = False
playerRight = False
currentWeapon = "Pistol"
bulletDamage = 1
ticksTillShot = 30

def drawMap((x, y), xsize, ysize):
    xmin = (x - xsize//2) // 16
    xmax = (x + xsize//2) // 16
    ymin = (y - ysize//2) // 16
    ymax = (y + ysize//2) // 16
    try:
        for xtile in xrange(xmin, xmax):
            for ytile in xrange(ymin, ymax):
                grid[xtile][ytile].draw(screen,((xtile * 16 + (WINDOWWIDTH / 2 - 16)) - playerRect.left),((ytile * 16) - playerRect.top + (WINDOWHEIGHT / 2 - 16)))
    except:
        pass

def movePlayer(Rect,rectX,rectY):
    
    collisionRect = pygame.Rect((Rect.left + rectX, Rect.top + rectY),(16,16))

    x,y = collisionRect.center
    x = x // 16
    y = y // 16
    
    for xTile in xrange(x - 1,x + 1):
        for yTile in xrange(y-  1,y + 1):
           if grid[xTile][yTile].collidable:    
                if collisionRect.colliderect(grid[xTile][yTile].Rect):
                    return True
                    del collisionRect

def playerCollideEntities():
    for z in zombies[:]:
        if playerRect.colliderect(z.Rect):
            return True

        else:
            return False

def moveZombie(Rect,rectX,rectY):
    
    collisionRect = pygame.Rect((Rect.left + rectX, Rect.top + rectY),(16,16))

    x,y = collisionRect.center
    x = x // 16
    y = y // 16
    
    for xTile in xrange(x - 1,x + 1):
        for yTile in xrange(y-  1,y + 1):
           if grid[xTile][yTile].collidable:    
                if collisionRect.colliderect(grid[xTile][yTile].Rect):
                    return True
                    del collisionRect

def zombieGetBlockCollided(Rect,rectx,recty):
    collisionRect = pygame.Rect((Rect.left + rectX, Rect.top + rectY),(16,16))

    x,y = collisionRect.center
    x = x // 16
    y = y // 16
    
    for xTile in xrange(x - 1,x + 1):
        for yTile in xrange(y-  1,y + 1):
           if grid[xTile][yTile].collidable:    
                if collisionRect.colliderect(grid[xTile][yTile].Rect):
                    return (xTile,Ytile)
                    del collisionRect

def bulletGetCollided(Rect,rectX,rectY):
    
    collisionRect = pygame.Rect((Rect.left + rectX, Rect.top + rectY),(1,1))

    x,y = collisionRect.center
    x = x // 16
    y = y // 16
    
    for xTile in xrange(x - 1,x + 1):
        for yTile in xrange(y-  1,y + 1):
           if grid[xTile][yTile].collidable:    
                if collisionRect.colliderect(grid[xTile][yTile].Rect):
                    return True
                    del collisionRect

while True:

    screen.fill((255,0,0))
    
    drawText("Chained Undead",fontBig,screen,WINDOWWIDTH /4, WINDOWHEIGHT/ 4)
    drawText("Press Space To Play",fontBig,screen,WINDOWWIDTH /4,WINDOWHEIGHT  /3)
    drawText("Your HighScore is: " + highscore,fontBig,screen,WINDOWWIDTH / 4,WINDOWHEIGHT / 2)
    drawText(("Chained Undead © 2013 Josh Steffen"),fontBig,screen,0,WINDOWHEIGHT / 1.5)

    for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: 
                    pygame.quit()
                    sys.exit()
                if event.key == K_SPACE:
                    screen.fill((255,0,0))
                    drawText("Generating Map...",fontBig,screen,WINDOWWIDTH/4,WINDOWHEIGHT/3)
                    pygame.display.update()

                    grid = []

                    bullets = []
                    zombies = []

                    ticksSinceSpawn = 0
                    ticksSinceShot = 0

                    grid = []
                    bullets = []
                    zombies = []

                    ticksSinceSpawn = 0
                    ticksSinceShot = 0

                    score = 0
                    playerHealth = 100
                    currentWeapon = "Pistol"
                    bulletDamage = 1
                    ticksTillShot = 30
                    money = 0
                    playerHasRifle = False
                    playerHasSMG  = False

                    currentWave = 1
                    maxZombies = 10
                    zombiesLeft = maxZombies
                    zombiesSpawned = 0
                    ticksTillSpawn = 90

                    selectedButton = 1
                    
                    for x in xrange(gridLength):
                        grid.append([])
                        for y in xrange(gridHeight):
                            randomBlock = random.randint(1,1000)
                            if randomBlock <= 900:
                                grid[x].append(blockGrass(x,y))
                            if randomBlock >= 901 and randomBlock <= 932:
                                grid[x].append(blockFlowersRed(x,y))
                            if randomBlock >= 933 and randomBlock <= 966:
                                grid[x].append(blockFlowersBlue(x,y))
                            if randomBlock >= 967 and randomBlock <= 1000:
                                grid[x].append(blockFlowersWhite(x,y))

                    for x in xrange(gridLength):
                        grid.append([])
                        for y in xrange(gridHeight):
                            randomHouse = random.randint(1,2000)
                            if randomHouse == 2000:
                                try:
                                    grid[x][y] = blockStone(x,y)
                                    grid[x + 1][y] = blockStone(x + 1,y)
                                    grid[x + 2][y] = blockStone(x + 2,y)
                                    grid[x + 3][y] = blockStone(x + 3,y)
            
                                    grid[x][y + 1] = blockStone(x,y + 1)
                                    grid[x + 1][y + 1] = blockDirt(x + 1,y + 1)
                                    grid[x + 2][y + 1] = blockDirt(x + 2,y + 1)
                                    grid[x + 3][y + 1] = blockStone(x + 3,y + 1)
            
                                    grid[x][y + 2] = blockStone(x,y + 2)
                                    grid[x + 1][y + 2] = blockDirt(x + 1,y + 2)
                                    grid[x + 2][y + 2] = blockDirt(x + 2,y + 2)
                                    grid[x + 3][y + 2] = blockDirt(x + 3,y + 2)

                                    grid[x][y + 3] = blockStone(x,y + 3)
                                    grid[x + 1][y + 3] = blockStone(x + 1,y + 3)
                                    grid[x + 2][y + 3] = blockStone(x + 2,y + 3)
                                    grid[x + 3][y + 3] = blockStone(x + 3,y + 3)
                
                                except:
                                    pass
                    playing = True

                

    
    pygame.display.update()
    clock.tick(FPS)
                  
    while playing:

        for event in pygame.event.get():

            if event.type == QUIT:

                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    pygame.quit()
                    sys.exit()

                if event.key == K_UP:

                    playerUp = True
                    playerDown = False

                if event.key == K_DOWN:

                    playerUp = False
                    playerDown = True

                if event.key == K_LEFT:
                
                    playerLeft = True
                    playerRight = False

                if event.key == K_RIGHT:

                    playerLeft = False
                    playerRight = True

                if event.key == K_w:

                    if ticksSinceShot >= ticksTillShot:
                        ticksSinceShot = 0
                        bullets.append(bullet(playerRect.left + 8,playerRect.top - 2,"up", bulletDamage))


                if event.key == K_s:

                    if ticksSinceShot >= ticksTillShot:
                        ticksSinceShot = 0
                        bullets.append(bullet(playerRect.left + 8,playerRect.bottom + 2,"down", bulletDamage))

                if event.key == K_a:

                    if ticksSinceShot >= ticksTillShot:
                        ticksSinceShot = 0
                        bullets.append(bullet(playerRect.left - 2,playerRect.top + 8,"left", bulletDamage))
                        playerImage = playerLeftImage

                if event.key == K_d:
                
                    if ticksSinceShot >= ticksTillShot:
                        ticksSinceShot = 0
                        bullets.append(bullet(playerRect.right + 2,playerRect.top + 8,"right", bulletDamage))
                        playerImage = playerRightImage

                if event.key == K_LSHIFT:
                    if  playerStamina > 0:
                        playerMoveRate = 4

                    else:
                        playerMoveRate = 2

                if event.key == K_1:
                    currentWeapon = "Pistol"
                    bulletDamage = 1
                    ticksTillShot = 30

                if event.key == K_2 and playerHasRifle == True:
                    currentWeapon = "Rifle"
                    bulletDamage = 3
                    ticksTillShot = 60

                if event.key == K_3 and playerHasSMG == True:
                    currentWeapon = "SMG"
                    bulletDamage = 1
                    ticksTillShot = 5
               
            if event.type == KEYUP:

                if event.key == K_UP:

                    playerUp = False

                if event.key == K_DOWN:

                    playerDown = False

                if event.key == K_LEFT:
                
                    playerLeft = False

                if event.key == K_RIGHT:

                    playerRight = False

                if event.key == K_LSHIFT:

                    playerMoveRate = 2

        screen.fill((0,0,0))  
                            
    
        if playerUp and not(movePlayer(playerRect,0,-1 * playerMoveRate)):
            
            playerRect.move_ip(0,-1 * playerMoveRate)
            if playerMoveRate == 4:
                playerStamina -= 3
                if playerStamina <= 0:
                    playerMoveRate = 2

        if playerDown and not(movePlayer(playerRect,0,8)):

            playerRect.move_ip(0,1 * playerMoveRate)
            if playerMoveRate == 4:
                playerStamina -= 3
                if playerStamina <= 0:
                    playerMoveRate = 2

        if playerLeft and not(movePlayer(playerRect,-1 * playerMoveRate,0)):

            playerRect.move_ip(-1 * playerMoveRate,0)
            playerImage = playerLeftImage
            if playerMoveRate == 4:
                playerStamina -= 3
                if playerStamina <= 0:
                    playerMoveRate = 2

        if playerRight and not(movePlayer(playerRect,8,0)):

            playerRect.move_ip(1 * playerMoveRate,0)
            playerImage = playerRightImage
            if playerMoveRate == 4:
                playerStamina -= 3
                if playerStamina <= 0:
                    playerMoveRate = 2
    
        cameraRect.center = playerRect.center

        drawMap(cameraRect.center,WINDOWWIDTH + 64, WINDOWHEIGHT + 64)
    
        screen.blit(playerImage,(WINDOWWIDTH / 2 - 16,WINDOWHEIGHT / 2 - 16))

        for b in bullets[:]:            
            if cameraRect.colliderect(b.Rect):
                b.move()
                b.draw(b.Rect.left + (WINDOWWIDTH / 2 - 16) - playerRect.left,(b.Rect.top ) - playerRect.top + (WINDOWHEIGHT / 2 - 16))
            elif bulletGetCollided(b.Rect,0,0):
                del b
            else:
                del b
        
        currentZombie = 0
        for z in zombies[:]:
            if not(moveZombie(z.Rect,0,6)):
                z.findPlayer(playerRect.left,playerRect.top)
            z.draw(z.Rect.left + (WINDOWWIDTH / 2 - 16) - playerRect.left,(z.Rect.top ) - playerRect.top + (WINDOWHEIGHT / 2 - 16))
            if z.Rect.colliderect(playerRect):
                playerHealth -= 1
            try:
                for b in bullets[:]:
                    if zombies[currentZombie].Rect.colliderect(b.Rect):
                        del b
                        zombies[currentZombie].health += bulletDamage
                        if zombies[currentZombie].health >= 20:
                            del zombies[currentZombie]
                            score += 100
                            money += 10
                            zombiesLeft -= 1
            except:
                pass

            
        if playerHealth <= 0:
            try:
                if score > int(highscore):
                    highscoreFile = open('highscore.txt','w+')
                    highscore = str(score)
                    highscoreFile.write(highscore)
                    highscoreFile.close()
            except:
                highscoreFile = open('highscore.txt','w+')
                highscore = str(score)
                highscoreFile.write(highscore)
                highscoreFile.close()
                pass
            playing = False
            break

        if ticksSinceSpawn >= ticksTillSpawn and maxZombies > zombiesSpawned:
            ticksSinceSpawn = 0
            zombiesSpawned += 1
            randomSpawn  = random.randint(1,8)

            if randomSpawn == 1:
                zombies.append(zombie(cameraRect.left,cameraRect.top))

            if randomSpawn == 2:
                zombies.append(zombie(cameraRect.left + (cameraRect.right - cameraRect.left),cameraRect.top))

            if randomSpawn == 3:
                zombies.append(zombie(cameraRect.right,cameraRect.top))

            if randomSpawn == 4:
                zombies.append(zombie(cameraRect.left,cameraRect.top + (cameraRect.bottom - cameraRect.top)))

            if randomSpawn == 5:
                zombies.append(zombie(cameraRect.right,cameraRect.top + (cameraRect.bottom - cameraRect.top)))

            if randomSpawn == 6:
                zombies.append(zombie(cameraRect.left,cameraRect.bottom))

            if randomSpawn == 7:
                zombies.append(zombie(cameraRect.left + (cameraRect.right - cameraRect.left),cameraRect.bottom))

            if randomSpawn == 8:
                zombies.append(zombie(cameraRect.right,cameraRect.bottom))

        drawText("Health:",font,screen,16,16)
        pygame.draw.rect(screen,(255,0,0),Rect((80,16),(playerHealth,16)))
        drawText("Stamina:",font,screen,16,40)
        pygame.draw.rect(screen,(0,255,0),Rect((96,40),(playerStamina,16)))
        drawText("Score: " + str(score),font,screen,16,64)
        drawText("Current Weapon: " + currentWeapon,font,screen,16,88)
        drawText("Wave: " + str(currentWave), font,screen,16,112)
        drawText("Zombies Left: " + str(zombiesLeft),font,screen,16,136)
    
        ticksSinceSpawn += 1
        ticksSinceShot += 1
       
        if playerStamina < 100:
            playerStamina += 1

        if zombiesLeft == 0:
            shopping = True
            while shopping:
                screen.fill((255,0,0))
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

                    if event.type == KEYDOWN:

                        if event.key == K_ESCAPE:
                            shopping = False
                            break
                        
                        if event.key == K_UP:
                            if selectedButton != 1:
                                selectedButton -= 1
                            else:
                                selectedButton = 2

                        if event.key == K_DOWN:
                            if selectedButton != 2:
                                selectedButton += 1
                            else:
                                selectedButton = 1

                        if event.key == K_SPACE:
                            if selectedButton == 1 and playerHasRifle == False and money >= 200:
                                playerHasRifle = True
                                money -= 200
                            if selectedButton == 2 and playerHasSMG == False and money >= 500:
                                playerHasSMG = True
                                money -= 500
                
                drawText("The Shop",font,screen,WINDOWWIDTH/2,16)
                drawText("Money: " + str(money),font,screen,16,64)
                if selectedButton != 1:
                    pygame.draw.rect(screen,(128,128,128),Rect((16,88),(100,24)))
                else:
                    pygame.draw.rect(screen,(255,255,255),Rect((16,88),(100,24)))
                drawText("Rifle $200",font,screen,16,88)
                if selectedButton != 2:
                    pygame.draw.rect(screen,(128,128,128),Rect((16,112),(100,24)))
                else:
                    pygame.draw.rect(screen,(255,255,255),Rect((16,112),(100,24)))
                drawText("SMG $500",font,screen,16,112)
                
                pygame.display.update()
                clock.tick(FPS)
                        
            currentWave += 1
            maxZombies += 5
            zombiesLeft = maxZombies
            ticksTillSpawn -= 2
            zombiesSpawned = 0
                 
        pygame.display.update()
        clock.tick(FPS)
