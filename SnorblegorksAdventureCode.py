#Eddie Lowe
#Python Module Project
#Works with Python 3.4.2 and Pygame 1.9.2

import pygame, sys, math, time, random, os, copy
from pygame.locals import*

pygame.init()

#constants
if os.path.exists('save_games'):
    saveGameFile = 'save_games/save_file.txt'
else:
    saveGameFile = 'save_file.txt'

windowWidth = 600
windowHeight = 600
FPS = 180

blue =      (  0, 100, 255)
green =     (  0, 155,   0)
stoneCol =  (155, 155, 155)
brickCol =  (150,  25,  14)
insideBG =  (105, 105, 105)
red =       (255,   0,   0)
yellow =    (255, 255,   0)
white =     (255, 255, 255)
black =     (  0,   0,   0)
gold =      (212, 175,  55)

fpsClock = pygame.time.Clock()
    
displaySurf = pygame.display.set_mode((windowWidth, windowHeight))

#load sound effects
pygame.mixer.init(frequency = 22050, size = -16, channels = 2, buffer = 4096)

#if we can't find the sound file, we set it to a string to tell the user which is missing
sfxScorePoints = 'sfxScorePoints (Sounds/points.ogg)'
sfxJump = 'sfxJump (Sounds/jump.ogg)'
sfxDeath = 'sfxDeath (Sounds/lose.ogg)'

if os.path.exists('Sounds/points.ogg'):
    sfxScorePoints = pygame.mixer.Sound('Sounds/points.ogg')

if os.path.exists('Sounds/jump.ogg'):
    sfxJump = pygame.mixer.Sound('Sounds/jump.ogg')

if os.path.exists('Sounds/lose.ogg'):
    sfxDeath = pygame.mixer.Sound('Sounds/lose.ogg')
    
#used to scale the font sizes based on display size
fontFactor = windowHeight / 600

titleFont = pygame.font.Font('freesansbold.ttf', math.floor(55 * fontFactor))
titleFont.set_bold(True)

GOFont = pygame.font.Font('freesansbold.ttf', math.floor(40 * fontFactor))

menuFont = pygame.font.Font('freesansbold.ttf', math.floor(25 * fontFactor))

UIFont = pygame.font.Font('freesansbold.ttf', math.floor(15 * fontFactor))

popupFont = pygame.font.Font('freesansbold.ttf', math.floor(10 * fontFactor))
popupFont.set_bold(True)


#define game object sizes relative to screen size
playerSize = int(windowWidth / 20)
lifeSize = int(playerSize * 3/4)

enemyHeight = math.ceil(windowWidth / 24)
enemyWidth = math.ceil(windowWidth / 16)

platformWidth = math.floor(windowWidth / 12)

playerMoveDistance = math.ceil(windowWidth / 600)
enemyMoveDistance = math.ceil(windowWidth / 600)


def main():
    
    global levels, lives, score, last1UP, currentLevel
    
    global playerImages, playerWalkingRight, playerWalkingLeft, lifeImg
    
    global enemyWalkerLeftImg, enemyWalkerRightImg, enemyStanderImg, enemyShooterImg, enemyFlierLeftImg,\
           enemyFlierRightImg, projectileImg

    #The variables defined in this function are the variables that should only be reset at the
    #beginning of a new game. They won't change when a level is reset or when loading into a
    #new level

    levels = readLevelFile('levels.txt')
    
    if os.path.exists(saveGameFile) == False:
        createNewSaveGameData()

    else:
        readSaveGameData()

   
    playerImages = {'faceRight': loadSprite('Sprites\player.png', playerSize, playerSize),
                    'jumpRight': loadSprite('Sprites\player_jump.png', playerSize, playerSize),
                    'fallRight': loadSprite('Sprites\player_fall.png', playerSize, playerSize),
                    'dead': loadSprite('Sprites\player_dead.png', playerSize, playerSize)}
    
    playerImages['faceLeft'] = pygame.transform.flip(playerImages['faceRight'], True, False)
    playerImages['jumpLeft'] = pygame.transform.flip(playerImages['jumpRight'], True, False)
    playerImages['fallLeft'] = pygame.transform.flip(playerImages['fallRight'], True, False)      

    #look for the folder of every walking sprite
    try:
        playerWalkImgs = os.listdir('Sprites\player_walk')
        playerWalkingRight = []
        playerWalkingLeft = []
        
        for imgNum in range(len(playerWalkImgs)):        
            playerWalkingRight.append(loadSprite('Sprites\player_walk\\' + playerWalkImgs[imgNum], playerSize, playerSize))
                                      
            playerWalkingLeft.append(pygame.transform.flip(playerWalkingRight[imgNum], True, False))

    #if folder can't be found, load a red square instead
    except:
        missingSprite = pygame.Surface((int(playerSize), int(playerSize)))
        missingSprite.fill(red)
        
        playerWalkingRight = [missingSprite]
        playerWalkingLeft = [missingSprite]
        
    enemyWalkerLeftImg = [loadSprite('Sprites\enemy_walker_1.png', enemyWidth, enemyHeight),
                          loadSprite('Sprites\enemy_walker_2.png', enemyWidth, enemyHeight),]

    enemyWalkerRightImg = [pygame.transform.flip(enemyWalkerLeftImg[0], True, False),
                           pygame.transform.flip(enemyWalkerLeftImg[1], True, False)]

    enemyStanderImg = [loadSprite('Sprites\enemy_stander.png', enemyWidth, enemyHeight)]

    enemyShooterImg = [loadSprite('Sprites\enemy_shooter_1.png', enemyWidth, enemyHeight),
                       loadSprite('Sprites\enemy_shooter_2.png', enemyWidth, enemyHeight),]

    enemyFlierLeftImg = [loadSprite('Sprites\enemy_flier_1.png', enemyWidth, enemyHeight),
                         loadSprite('Sprites\enemy_flier_2.png', enemyWidth, enemyHeight)]
    
    enemyFlierRightImg = [pygame.transform.flip(enemyFlierLeftImg[0], True, False),
                          pygame.transform.flip(enemyFlierLeftImg[1], True, False)]

    projectileImg = loadSprite('Sprites\shooter_projectile.png', enemyWidth/2, enemyHeight/2)

    lifeImg = loadSprite('Sprites\player_UI.png', lifeSize, lifeSize)

    while True:
        mainMenu()
        runGame()


def readLevelFile(filename):
    
    #check the level file exists
    assert os.path.exists(filename), 'cannot find the level file. Please ensure that it is present and named "levels.txt"'

    #extract data from the file
    file = open(filename, 'r')
    content = file.readlines()
    file.close()

    #split the data up by level
    levels = []

    levelRows = []
    thisLevel = []

    for lineNum in range(len(content)):
        
    #readlines() adds a '\n' to the end of each line, we remove that here otherwise it
    #leaves a blank column at the end of the level
        line = content[lineNum].rstrip('\n')

    #';' is used as a comment mark in the level file, so we ignore those lines
        if ';' in line:
            line = line[:line.find(';')]

    #finds the end of the line
        if line != '':
            levelRows.append(line)

    #if the entire line is blank, we have reached the end of the current level we're looking at
        elif line == '' and len(levelRows) > 0:
            levelLength = len(levelRows[0])

            #checks if any of the rows are different lengths...
            for row in levelRows:
                if len(row) > levelLength:
                    levelLength = len(row)

            #then makes them the same length by adding blank spaces to the end of shorter rows
            for row in levelRows:
                rowIndex = levelRows.index(row)
                if len(levelRows[rowIndex]) < levelLength:
                    levelRows[rowIndex] = row + ('-' * (levelLength - len(levelRows[rowIndex])))
      
        #convert our lines into x, y coordinates in the mapObj list
        #we create an empty list for each row
            for x in range(levelLength):
                thisLevel.append([])

            for y in range(len(levelRows)):
                for x in range(levelLength):
                    thisLevel[x].append(levelRows[y][x])


        #check each x,y coordinate and check what's supposed to be there
        #and populate the lists for each object with the coordinates
            platforms = []
            blanks = []
            grassBlocks = []
            stoneBlocks = []
            finish = []
            standers = []
            walkers = []
            fliers = []
            shooters = []
            playerStart = (0, 0)
            location = 'outside'

            for x in range(levelLength):
                for y in range(len(thisLevel[x])):
                    if thisLevel[x][y] == 'p':
                        playerStart = (x, y)
                        
                    if thisLevel[x][y] == '+':
                        platforms.append((x, y))
                        
                    if thisLevel[x][y] == '#':
                        stoneBlocks.append((x, y))
                        location = 'inside'
                        
                    if thisLevel[x][y] == 'x':
                        grassBlocks.append((x, y))
                        location = 'outside'
                        
                    if thisLevel[x][y] == '0':
                        finish.append((x, y))
                        
                    if thisLevel[x][y] == 'e':
                        standers.append((x, y))
                        
                    if thisLevel[x][y] == 'w':
                        walkers.append((x, y))
                        
                    if thisLevel[x][y] == 'f':
                        fliers.append((x, y))
                        
                    if thisLevel[x][y] == 's':
                        shooters.append((x, y))
                        
                    if thisLevel[x][y] == 'E':
                        standers.append((x, y))
                        platforms.append((x, y))

            #a dictionary containing level data
                #length and height are the dimensions of the level
                #everything else stores coordinate which we use later to draw objects onto the screen
                        
            level = {'length': levelLength,
                     'height': len(levelRows),
                     'playerStart': playerStart,
                     
                     'platforms': platforms,
                     'grassBlocks': grassBlocks,
                     'stoneBlocks': stoneBlocks,
                     'finish': finish,
                     'standers': standers,
                     'walkers': walkers,
                     'fliers': fliers,
                     'shooters': shooters,
                     
                     'location': location}

            if level['height'] <= 1:
                print('Level', len(levels) + 1, 'isn\'t tall enough, it must be at least 2 blocks tall')
                level = []

            if level['finish'] == []:
                print('Level', len(levels) + 1, 'Doesn\'t have any finish points, please check the level file')
                level = []

        #levels is a list containing every level in the data file
            if level != []:
                levels.append(level)

        #reset the variables, then do the next level
            levelRows = []
            thisLevel = []
            
    return levels


def createNewSaveGameData():
    global currentLevel, lives, score, last1UP
    
    score = 0
    last1UP = 0
    lives = 6
    currentLevel = 0


def editSaveGameData():
    '''updates the save file with current information'''

    file = open(saveGameFile, 'w')

    for data in [currentLevel, lives, score, last1UP]:
        file.write(str(data) + '\n')

    file.close()


def readSaveGameData():
    global currentLevel, lives, score, last1UP
    
    saveGameData = open(saveGameFile, 'r')
    dataList = saveGameData.readlines()
    saveGameData.close()
    
    currentLevel = int(dataList[0])
    lives = int(dataList[1])
    score = int(dataList[2])
    last1UP = int(dataList[3])

    if currentLevel + 1 > len(levels):
        gameComplete()


def loadSprite(filePath, width, height):
    '''look for the specified image on file. If it can't be found, load a red square instead'''
    
    try:
        sprite = pygame.transform.scale(pygame.image.load(filePath), (int(width), int(height)))

    except:
        sprite = pygame.Surface((int(width), int(height)))
        sprite.fill(red)

    return sprite
                                             

def findDeadEnemySprite(deadEnemy):
    '''takes the index of the enemy and finds out which type of enemy it is
Then loads the correct death sprite'''

    width = enemies[deadEnemy]['rect'].width
    height = enemies[deadEnemy]['rect'].height
    
    if deadEnemy in standers:
        sprite = loadSprite('Sprites\enemy_stander_dead.png', width, height)
        
    elif deadEnemy in fliers:
        sprite = loadSprite('Sprites\enemy_flier_dead.png', width, height)
        
    elif deadEnemy in walkers:
        sprite = loadSprite('Sprites\enemy_walker_dead.png', width, height)
        
    elif deadEnemy in shooters:
        sprite = loadSprite('Sprites\enemy_shooter_dead.png', width, height)
        
    return sprite


def mainMenu():
    '''shows upon running the program, completing the game, or running out of lives'''

    #set button constants
    buttonWidth = windowWidth / 3
    buttonHeight = windowHeight / 10

    saveFileExists = False

    newGameButton = pygame.Rect(windowWidth/2 - buttonWidth/2, windowHeight * 5/8 - buttonHeight/2,
                                buttonWidth, buttonHeight)

    quitGameButton = pygame.Rect(newGameButton.x, (windowHeight * 6/8) - buttonHeight/2,
                                 buttonWidth, buttonHeight)

    #create title and player character image
    title = titleFont.render('SNORBLEGORK\'S', True, gold)
    title2 = titleFont.render('ADVENTURE', True, gold)

    titleRect = title.get_rect()
    title2Rect = title2.get_rect()

    titleRect.center = (windowWidth/2, windowHeight * 2/8)
    title2Rect.midleft = (titleRect.x, windowHeight * 3/8)

    playerImgSize = (titleRect.width - title2Rect.width) * 3/8
    
    playerImg = pygame.transform.scale(playerImages['jumpRight'], (int(playerImgSize), int(playerImgSize)))

    playerImgRect = playerImg.get_rect()

    playerImgRect.midtop = (title2Rect.x + title2Rect.width + (titleRect.width - title2Rect.width)/2 , title2Rect.y)

    while True:

        #draw background and title
        platformHeight = math.ceil(windowHeight / 7)
        
        displaySurf.fill(blue)
        ground = pygame.draw.rect(displaySurf, green, (0, windowHeight - platformHeight, windowWidth, platformHeight))
        pygame.draw.line(displaySurf, black, (0, ground.y), (windowWidth, ground.y))

        displaySurf.blit(title, titleRect)
        displaySurf.blit(title2, title2Rect)
        displaySurf.blit(playerImg, playerImgRect)

        mouseX, mouseY = pygame.mouse.get_pos()

        #draw a continue button if there is a save game file
        if os.path.exists(saveGameFile):
            saveFileExists = True
            
            continueButton = pygame.Rect(newGameButton.x, (windowHeight * 5/8) - buttonHeight/2,
                                 buttonWidth, buttonHeight)

            newGameButton.y = windowHeight * 4/8 - buttonHeight/2
            
            buttonList = [newGameButton, quitGameButton, continueButton]
            
        else:
            buttonList = [newGameButton, quitGameButton]

        #draw buttons    
        for button in buttonList:
            
            if button.collidepoint((mouseX, mouseY)):
                buttonColour = gold
            else:
                buttonColour = white

            pygame.draw.rect(displaySurf, buttonColour, (button), 2)

            #create the text for each button
            if button == newGameButton:
                buttonText = menuFont.render('New Game', True, buttonColour)
                
            elif button == quitGameButton:
                buttonText = menuFont.render('Quit', True, buttonColour)

            elif saveFileExists:
                if button == continueButton:
                    buttonText = menuFont.render('Continue', True, buttonColour)

            textRect = buttonText.get_rect()
            textRect.center = button.center

            displaySurf.blit(buttonText, textRect)

        #event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                quitGame()
    
            if event.type == MOUSEBUTTONDOWN:
                if newGameButton.collidepoint((mouseX, mouseY)):
                    createNewSaveGameData()
                    return
                
                elif quitGameButton.collidepoint((mouseX, mouseY)):
                    quitGame()

                elif saveFileExists:
                    if continueButton.collidepoint((mouseX, mouseY)):
                        return

        pygame.display.update()
        fpsClock.tick(FPS)
    

def preLevelScreen():
    
    global playerRect, jumpCounter, falling
    
    waitTime = time.time()
    while time.time() - waitTime <= 1.5:

        #draw the pre level screen
        displaySurf.fill(black)
        
        levelNumber = GOFont.render('LEVEL %s' % (currentLevel + 1), True, white)
        levelNumberRect = levelNumber.get_rect()
        levelNumberRect.center = (windowWidth/2, windowHeight/2)

        livesText = UIFont.render(' x %s' % lives, True, gold)
        livesTextRect = livesText.get_rect()
        livesTextRect.center = (windowWidth * 17/32, windowHeight * 3/5)
        
        livesImgRect = pygame.Rect(windowWidth * 15/32 - lifeSize/2, livesTextRect.centery - lifeSize/2, lifeSize, lifeSize)
    
        displaySurf.blit(levelNumber, levelNumberRect)
        displaySurf.blit(livesText, livesTextRect)
        displaySurf.blit(lifeImg, livesImgRect)
        
        pygame.display.update()
        fpsClock.tick(FPS)


def runGame():
    global cameraX, jumping, jumpCounter, maxJumpCounter, currentPlat, framesFallen, playerRect
    global score, lives, last1UP, FPS
    global moveLeft, moveRight, canMoveLeft, canMoveRight, currentLevel, finishPoint, playerAtFinish
    global enemies, clouds, platforms, enemyCollision, frameCount
    global deadEnemyAnimation, timer, killMultiplier, combo, lastTimerChange, last1UP
    global standers, walkers, fliers, popups, playerImage, falling, shooters, projectiles
    global platformHeight, maximumJumpHeight

#recover data from save file
    editSaveGameData()
    readSaveGameData()
    
    platformHeight = math.ceil(windowHeight / levels[currentLevel]['height'])

    maximumJumpHeight = math.ceil(windowHeight / (levels[currentLevel]['height'] - 1))
    
#These variables all change throughout the course of playing the level

    #uninteractable decoration
    clouds = []
    deadEnemyAnimation = []
    popups = []

    #enemies
    standers = []
    walkers = []
    fliers = []
    shooters = []
    projectiles = []
    enemies = []

    for enemy in [(standers, 'standers'), (walkers, 'walkers'), (fliers, 'fliers'), (shooters, 'shooters')]:
        populateEnemyLists(enemy)

    #platforms
    platforms = []
    finishPoint = []

    #camera variables
    cameraX = 0
    cameraSlack = 0

    #player movement variables
    moveLeft = False
    moveRight = False
    canMoveLeft = False
    canMoveRight = False
    
    #currentPlat = platformHeight

    playerStartX = levels[currentLevel]['playerStart'][0] * platformWidth
    playerStartY = (levels[currentLevel]['playerStart'][1] + 1) * platformHeight - playerSize
    
    playerRect = pygame.Rect(playerStartX, playerStartY, playerSize, playerSize)
    playerImage = playerImages['faceRight']
    playerFacing = 'Right'
    walkingIndex = 1

    #set jumpCounter to FPS means it takes 1 second to complete a full jump
    maxJumpCounter = FPS
    jumpCounter = maxJumpCounter
    jumping = False
    falling = False
    framesFallen = 0

    #enemy collision variables
    enemyCollision = False
    killMultiplier = 1
    combo = False

    #non-player related variables
    timer = 300
    frameCount = 0
    playerAtFinish = False

    #shows number of lives and level number on the screen before each level
    preLevelScreen()
    
    lastTimerChange = time.time()
    pygame.event.clear()

   
    while True:

        #check the player death conditions
        if playerRect.y >= windowHeight or enemyCollision == True or timer <= 0:
            #the loseLife function returns True if the player has no lives left
            lives -= 1
            playerImage = playerImages['dead']

            jumping = False
            falling = False
            jumpCounter = 0
            deathStartLoc = playerRect.y

            pygame.time.wait(550)
            playSFX(sfxDeath)
            pygame.time.wait(450)

            while playerRect.y < windowHeight:
                drawGame()

                #the player flies into the air (to the normal jump height) then continues to fall until
                #they are off the screen
                playerRect.y = jump(jumpCounter, deathStartLoc)
                jumpCounter += 1
                
                pygame.display.update()
                fpsClock.tick(FPS)

            if lives <= 0:
                gameOverScreen()
            else:
                runGame()
                
        platforms = []
        finishPoint = []
        
        timer = countdownTimer(timer)

        drawGame()
        moveEnemies(enemies)
        
        if playerAtFinish == True:
            levelComplete()

    #Main event loop
        for event in pygame.event.get():
            if event.type == QUIT:
                quitGame()
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quitGame()
                    
                if (event.key == K_SPACE or event.key == K_UP) and (jumping == False and falling == False):
                    jumping = True
                    playSFX(sfxJump)
                    
                if event.key == K_RIGHT:
                    moveRight = True
                    moveLeft = False
                    
                elif event.key == K_LEFT:
                    moveRight = False
                    moveLeft = True
                    
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moveRight = False
                    
                if event.key == K_LEFT:
                    moveLeft = False

    #We calculate what image we should be using for the player
        #walking right or left
        if moveRight == True or moveLeft == True:
            if frameCount % 10 == 0:
                
                walkingIndex += 1
                if walkingIndex >= len(playerWalkingRight):
                    walkingIndex = 0
                    
                if moveRight == True and moveLeft == False:
                    playerFacing = 'Right'
                    playerImage = playerWalkingRight[walkingIndex - 1]
                    
                elif moveRight == False and moveLeft == True:
                    playerFacing = 'Left'
                    playerImage = playerWalkingLeft[walkingIndex - 1]


        #jumping or falling
        if jumping == True or falling == True:
            
            walkingIndex = 1
            if jumping == True:
                if playerFacing == 'Right':
                    playerImage = playerImages['jumpRight']
                    
                elif playerFacing == 'Left':
                    playerImage = playerImages['jumpLeft']
                    
            elif falling == True:
                if playerFacing == 'Right':
                    playerImage = playerImages['fallRight']
                    
                elif playerFacing == 'Left':
                    playerImage = playerImages['fallLeft']
                    
            jumpCounter += 1
            playerRect.y = jump(jumpCounter, currentPlat)
            

        #standing still
        if moveRight == False and moveLeft == False and jumping == False and falling == False:
            
            walkingIndex = 1
            if playerFacing == 'Right':
                playerImage = playerImages['faceRight']
                
            elif playerFacing == 'Left':
                playerImage = playerImages['faceLeft']

    #looks at what the player is touching                      
     
        playerSides = {'top':       pygame.Rect(playerRect.x + 2, playerRect.y, playerRect.width - 4, 1),
                       'bottom':    pygame.Rect(playerRect.x + 2, playerRect.y + playerRect.height, playerRect.width - 4, 1),
                       'left':      pygame.Rect(playerRect.x, playerRect.y + 3, 1, playerRect.height * 3/4),
                       'right':     pygame.Rect(playerRect.x + playerRect.width - 1, playerRect.y + 3, 1, playerRect.height * 3/4)}
        
        checkPlatformCollision(playerSides, platforms)
        
        for e in enemies:
        
            for p in playerSides.values():
                
                if e['hitbox'].colliderect(p):
                    
                    if p == playerSides['bottom']:

                        playSFX(sfxScorePoints)
                                            
                        enemyIndex = enemies.index(e)
                        deadEnemyAnimation.append({'rect': e['rect'],
                                                   'surface': findDeadEnemySprite(enemyIndex)})

                        #if the player bounces on multiple enemy's head without touching the floor, they gain
                        #a bonus to their score
                        if combo == True:
                            killMultiplier += 1    
                        else:
                            killMultiplier = 1

                        #check which enemy we collided with    
                        for enemyType in [standers, walkers, fliers, shooters]:
                            for i in range(len(enemyType)):

                                #we remove the enemy from the enemy list then change the indices of every
                                #value after the one we removed.  Otherwise the index list and enemy list don't
                                #match up anymore
                                if enemyType[i-1] > enemyIndex:
                                    enemyType[i-1] -= 1

                                #change the value in the index list so that it doesn't correspond to an entry
                                #in the enemy list anymore
                                elif enemyType[i-1] == enemyIndex:
                                    enemyType[i-1] = -1

                        #adds the the player score            
                        createScorePopUp(50 * killMultiplier, e['rect'])
                        score += 50 * killMultiplier
                        popup1UPLoc = copy.copy(e['rect'])
                        checkFor1UP(score, popup1UPLoc)

                        enemies.remove(e)

                        #resets the jump variables, so that the player bounces off the enemy
                        jumpCounter = 0
                        currentPlat = playerRect.y + playerRect.height
                        combo = True
                        jumping = True

                    #if any part of the player other than the bottom touches an enemy, the player dies
                    else:
                        enemyCollision = True

        
        #projectile collision
        for projectile in projectiles:
            projHitbox = projectile['rect'].inflate(-(projectile['rect'].width / 5), -(projectile['rect'].height / 5))
            
            for p in playerSides.values():
                if projHitbox.colliderect(p):

                    #bounces off the top of a projectile and kills it
                    if p == playerSides['bottom']:
                        playSFX(sfxScorePoints)
                        
                        deadEnemyAnimation.append({'rect': projectile['rect'],
                                                   'surface': projectileImg})
                        projectiles.remove(projectile)
                        
                        jumpCounter = 0
                        currentPlat = playerRect.y + playerRect.height
                        jumping = True

                    #player dies if any other part of the projectile touches them
                    else:
                        enemyCollision = True

    #draws score and 1up popups onto the screen (which are calculated in the calcPlayerHitbox variable)
        drawPopups(popups)

    #move the player / screen
        if moveRight == True and canMoveRight == True:

            #moves the player image
            if playerRect.x < windowWidth/2 or cameraX >= (levels[currentLevel]['length'] * platformWidth) - windowWidth:
                playerRect.x += playerMoveDistance

            #moves the camera position and the non-player objects on screen    
            else:
                cameraX += playerMoveDistance

                moveScreen(-playerMoveDistance)

            #cameraSlack is used to figure out whether we should move the camera or the player image
            #is keeps track of how far away the player is from the center of the screen
            if cameraSlack < 0:
                cameraSlack += playerMoveDistance
                if cameraSlack > 0:
                    cameraSlack -= playerMoveDistance
            
        elif moveLeft == True and canMoveLeft == True:
            
            if cameraX < windowWidth / 2 or cameraSlack <= -(windowWidth/2) or playerRect.x > windowWidth/2:
                playerRect.x -= playerMoveDistance
                
            else:
                cameraX -= playerMoveDistance
                cameraSlack -= playerMoveDistance
                
                moveScreen(playerMoveDistance)                

        #frameCount is used to keep track of how often enemies should move or change sprite
        frameCount += 1
    
        pygame.display.update()
        fpsClock.tick(FPS)


def drawGame():
    ''' draws everything onto the screen'''
    
    #changes the background of the level depending on whether it's an 'inside' or 'outside' level
    if levels[currentLevel]['location'] == 'inside':
        displaySurf.fill(insideBG)
        
    elif levels[currentLevel]['location'] == 'outside':
        displaySurf.fill(blue)
        
        sun = pygame.draw.rect(displaySurf,yellow, (windowWidth *(3/4), windowHeight*(1/5), 50, 50))
        sunOutline = pygame.draw.rect(displaySurf, black, (sun), 1)
        drawClouds(cameraX, clouds)


    #draw the blocks that the player can stand on
    for i in [('grassBlocks', green), ('platforms', brickCol), ('stoneBlocks', stoneCol), ('finish', gold)]:
        drawPlatforms(i)


    #draw the enemies onto the screen
    for obj in enemies:
        if obj['rect'].x <= windowWidth:
            
            enemySprite = obj['spriteList'][obj['animationIndex']]

            displaySurf.blit(enemySprite, obj['rect'])

            
    #draws the enemies who are in mid-death animation     
    for enemy in deadEnemyAnimation:
        if enemy['rect'].y <= windowHeight + 2:
            enemy['rect'].y += 2
            displaySurf.blit(enemy['surface'], enemy['rect'])

    #draws projectiles onto the screen
    for proj in projectiles:
        p = proj['rect']

        #remove a projectile if it hits a platform...
        for platform in platforms:
            if platform.colliderect(p):
                projectiles.remove(proj)

        #...or if it goes off the edge of the screen        
        if p.x + p.width < 0:
            projectiles.remove(proj)
            
        else:   
            displaySurf.blit(projectileImg, p)

    displaySurf.blit(playerImage, playerRect)

    #display lives in UI
    
    #if the player has more than 5 lives, we display the amount of lives as a number
    if lives > 5:
        livesText = UIFont.render('  x %s' % lives, True, gold)
        livesTextRect = livesText.get_rect()
        livesTextRect.topleft = (windowWidth*2/30, windowHeight/30)
        
        livesImgRect = pygame.Rect(windowWidth/30, livesTextRect.centery - lifeSize/2, 15, 15)

        displaySurf.blit(lifeImg, livesImgRect)

    #if they have less than or exactly 5 lives, we display an image for each life
    else:
        livesText = UIFont.render('Lives:', True, gold)
        livesTextRect = livesText.get_rect()
        livesTextRect.topleft = (windowWidth/30, windowHeight/30)
        
        for life in range(lives):
            livesImgRect = pygame.Rect((lifeSize * life + livesTextRect.x + livesTextRect.width * 6/5),
                                       livesTextRect.centery - lifeSize/2, 15, 15)
            displaySurf.blit(lifeImg, livesImgRect)
            
    displaySurf.blit(livesText, livesTextRect)

    #create score in UI
    scoreText = UIFont.render('Score: %s' % score, True, gold)
    scoreRect = scoreText.get_rect()
    scoreRect.midtop = (windowWidth/2, windowHeight/30)
    
    displaySurf.blit(scoreText, scoreRect)
    
    #create timer in UI
    timerText = UIFont.render('Time: %s' % timer, True, gold)
    timerRect = timerText.get_rect()
    timerRect.topright = (windowWidth * (29/30), windowHeight/30)
    
    displaySurf.blit(timerText, timerRect)


def drawPlatforms(block):
    global finishPoint, platforms

    blockType = block[0]
    colour = block[1]

    #set size of each platform type
    if blockType == 'grassBlocks' or blockType == 'stoneBlocks':
        blockHeight = platformHeight + 1
    else:
        blockHeight = windowHeight / 30

    #draw each platform onto the screen       
    for obj in levels[currentLevel][blockType]:
        x = obj[0] * platformWidth - cameraX
        y = obj[1] * platformHeight

        if x <= windowWidth and x >= - platformWidth:
            rect = pygame.draw.rect(displaySurf, colour, (x, y, platformWidth, blockHeight))
            platforms.append(rect)

            if blockType == 'finish':
                finishPoint.append(rect)

            #draws outline around platforms
            if (obj[0] - 1, obj[1]) not in levels[currentLevel][blockType]:
                pygame.draw.line(displaySurf, black, (x, y), (x, y + blockHeight - 1))
                
            if (obj[0] + 1, obj[1]) not in levels[currentLevel][blockType]:
                pygame.draw.line(displaySurf, black, (x + platformWidth, y), (x + platformWidth, y + blockHeight - 1))
                
            if (obj[0], obj[1] - 1) not in levels[currentLevel][blockType] or blockType == 'platforms':
                pygame.draw.line(displaySurf, black, (x, y), (x + platformWidth, y))

            if (obj[0], obj[1] + 1) not in levels[currentLevel][blockType] or blockType == 'platforms':
                pygame.draw.line(displaySurf, black, (x, y + blockHeight - 1), (x + platformWidth, y + blockHeight - 1))

            
def drawClouds(cameraX, clouds):
    
    #generate clouds if there aren't enough
    while len(clouds) < 8:

        #start the game with 1 cloud on the screen
        if len(clouds) < 1:
            x = random.randint(cameraX + int(windowWidth/2), cameraX + windowWidth)

        #generate the rest of the clouds just off the screen
        else:
            x = random.randint(cameraX + windowWidth, cameraX + int(windowWidth * 2))
            
        y = random.randint(-int(windowHeight/25),(int(windowHeight * (2/5))))
        
        cloudSize = random.randint(int(windowHeight / 40), int(windowHeight / 15))
        
        clouds.append({'x': x,
                       'y': y,
                       'centerHeight': 2*(cloudSize/5),
                       'size': cloudSize,
                       'centerY': (y - (2*(cloudSize/5)) + 1)})

    #draw the clouds onto the screen    
    for c in clouds:

        #remove the cloud if it moves more than half a screen off the left hand side of the screen
        if c['x'] <= cameraX - math.ceil(windowWidth/2):
            clouds.remove(c)
            continue

        pygame.draw.rect(displaySurf, white, (c['x'] - cameraX, c['y'], c['size'] * 3, c['size']))
        pygame.draw.rect(displaySurf, black, (c['x'] - cameraX, c['y'], c['size'] * 3, c['size']), 1)
        pygame.draw.rect(displaySurf, white, (c['x'] + c['size'] - cameraX, c['centerY'], c['size'], c['centerHeight']))
        pygame.draw.rect(displaySurf, black, (c['x'] + c['size'] - cameraX, c['centerY'], c['size'], c['centerHeight']), 1)
        pygame.draw.rect(displaySurf, white, (c['x'] + c['size'] - cameraX + 1, c['centerY'] + 2, c['size'] - 2, c['centerHeight']))


def drawPopups(popups):
    
    for i in popups:
        i['popupRect'].center = i['rect'].center
        displaySurf.blit(i['popupText'], i['popupRect'])

        #move popup upwards
        if frameCount % 4 == 0:
            i['rect'].y -= 1

        #delete popup after a time
        if frameCount - i['startFrame'] >= FPS:
            popups.remove(i)


def moveEnemies(enemies):

    if frameCount % (FPS / 90) == 0:

    #move projectiles
        for i in range(len(projectiles) - 1, -1, -1):
            projectiles[i]['rect'].x -= enemyMoveDistance

    #move enemies
        for i in range(len(enemies) - 1, -1, -1):
            
            e = enemies[i]

    # Walkers
            if i in walkers:

            #reset our collision variables
                leftCollisions = False
                rightCollisions = False
                botCollisions = False
                
            #create rects for each side on the enemy so we can calculate if it walks into something
                leftSide = pygame.Rect(e['rect'].x, e['rect'].y+4, 1, e['rect'].height-5)
                rightSide = pygame.Rect(e['rect'].x + (e['rect'].width*6/7), e['rect'].y+4, 1, e['rect'].height-5)
                botSide = pygame.Rect(e['rect'].x+1, e['rect'].y + e['rect'].height, e['rect'].width-2, 1)
                
            #check for platform collisions
                for plat in platforms:
                    
                    if plat.colliderect(leftSide):
                        leftCollisions = True
                    if plat.colliderect(rightSide):
                        rightCollisions = True

                    #checks if the enemy is standing on a platform
                    if plat.colliderect(botSide):
                        botCollisions = True

                #if the walker is currently moving left
                                #only starts moving if it is just off the right side of the screen
                if e['direction'] == 'left' and e['rect'].x - (e['rect'].width / 2) <= windowWidth:

                    #keep moving left if no collision
                    if leftCollisions == False:
                        e['rect'].x -= enemyMoveDistance

                    #change direction and sprite to face right if it collides with a wall 
                    elif leftCollisions == True:
                        e['direction'] = 'right'
                        e['spriteList'] = enemyWalkerRightImg
                        
                #moving right
                elif e['direction'] == 'right':

                    #no collisions, keep moving
                    if rightCollisions == False:
                        e['rect'].x += enemyMoveDistance

                    #collision, turn around    
                    elif rightCollisions == True:
                        e['direction'] = 'left'
                        e['spriteList'] = enemyWalkerLeftImg
                        
                #falls down if not touching the floor
                if botCollisions == False and e['rect'].x + 5 <= windowWidth:
                    e['rect'].y += enemyMoveDistance * 2

    # Fliers      
            if i in fliers:

                #'left' is really 'up'
                if e['direction'] == 'left':
                    e['rect'].y -= enemyMoveDistance

                    #once maximum height reached, start moving down
                    if (e['startingY'] - e['rect'].y >= platformHeight) or (e['rect'].y <= 0):
                        e['direction'] = 'right'

                #'right' is 'down'        
                elif e['direction'] == 'right':
                    e['rect'].y += enemyMoveDistance

                    #start going up again once it's done a full loop
                    if e['rect'].y >= e['startingY']:
                        e['direction'] = 'left'

                #flier turns to always face the player
                if e['rect'].x <= playerRect.x:
                    e['spriteList'] = enemyFlierRightImg
                    
                elif e['rect'].x >= playerRect.x:
                    e['spriteList'] = enemyFlierLeftImg

    # Shooters
            #creates a projectile periodically
            if frameCount % (FPS * 3) == 0 and i in shooters and e['rect'].x <= windowWidth * 2:
                
                e['shooting'] = True
                projectiles.append({'rect': pygame.Rect(e['rect'].x, e['rect'].y + e['rect'].height * 3/4,
                                            projectileImg.get_width(), projectileImg.get_height())})

        #we update the hitbox of every enemy, incase it moved
            e['hitbox'] = e['rect'].inflate(-(e['rect'].width * 1/5), -(e['rect'].height * 1/5))

    #cycle through the enemy's animation list
    if frameCount % (FPS / 2) == 0:
        for i in enemies:
            i['animationIndex'] += 1
            if i['animationIndex'] >= len(i['spriteList']):
                i['animationIndex'] = 0
            
    return enemies


def moveScreen(moveDistance):
    for listsToMove in [enemies, popups, deadEnemyAnimation, projectiles]:
        for obj in listsToMove:
            obj['rect'].x += moveDistance
    

def checkPlatformCollision(playerSides, platforms):
    
    global jumping, falling, jumpCounter, currentPlat, canMoveLeft, canMoveRight, finishPoint,\
           playerAtFinish, combo

    #keeps track of the rect that the player is currently standing on
    currentPlatRect = platforms[0]

    #resets player movement variables
    canMoveLeft = True
    canMoveRight = True
             
    for i in platforms:

    #checks if there are platforms blocking the player from moving left or right
        if i.colliderect(playerSides['left']) or i.colliderect(playerSides['right']):
            if i.colliderect(playerSides['left']):
                canMoveLeft = False
                
            elif i.colliderect(playerSides['right']):
                canMoveRight = False

    #stops the player moving off the edge of the level        
        if playerRect.x <= 0:
            canMoveLeft = False
            
        if playerRect.x >= windowWidth - playerRect.width:
            canMoveRight = False
          
    #stops the player from jumping through the celing        
        if i.colliderect(playerSides['top']):
            jumping = False
            playerRect.y = i.y + i.height
            jumpCounter = maxJumpCounter - jumpCounter                
            return
          
        elif i.colliderect(playerSides['bottom']) and (jumpCounter >= maxJumpCounter / 2 or jumpCounter == 0):
        #reset jumping variables and update current platform data when the player
        #is on the floor
            currentPlat = i.y
            currentPlatRect = i
            playerRect.y = currentPlat - playerRect.height
            combo = False
            jumping = False
            falling = False
            jumpCounter = 0

    #check if the player is at the finish point
    for end in finishPoint:
        if end.collidepoint((playerRect.centerx, playerRect.y + playerRect.height)):
            playerAtFinish = True

    #checks if the player should be falling
    if not currentPlatRect.colliderect(playerSides['bottom']) and (jumping == False and falling == False):

        #for falling, we set the player to be at the apex of a jump, where the apex is their current position
        jumpCounter = maxJumpCounter / 2
        currentPlat = playerRect.y + playerRect.height + maximumJumpHeight
        falling = True


def countdownTimer(timer):
    '''update timer once per second'''
    
    global lastTimerChange

    if time.time() - lastTimerChange >= 1:
        lastTimerChange = time.time()
        timer -= 1
        
    return timer


def checkFor1UP(score, rect):
    global lives, last1UP
    
    if score - last1UP >= 1000:
        newLives = []
        
        scoreCheck = math.floor(score/1000)
        last1UPRoundDown = math.floor(last1UP/1000)

        #we compare the current score (scoreCheck) to the last time to player earned a 1UP (last)
        #the player earns 1 life for each 1000 points earned.  So by dividing the above values by 1000, we're left
        #with the number of lives the player has earned
        numOfLives = scoreCheck - last1UPRoundDown
        lives += numOfLives

        #add lives to player life count
        while numOfLives > 0:
            newLives.append(1)
            numOfLives -= 1
            
        last1UP = scoreCheck * 1000

        #creates a popup for each life gained
        popupRect = rect
        for newLife in newLives:
            popupRect.y -= 10
            createScorePopUp('1UP', rect)
            
    return lives, last1UP


def createScorePopUp(pointsEarned, location):

    #change global to input
    global popups

    #start location of the popup, which will rise over time
    start = (location.x, location.y)
    startFrame = frameCount

    #create the visible popup
    scoreInc = popupFont.render(str(pointsEarned), True, gold)
    scoreRect = scoreInc.get_rect()

    newPopup = {'startLoc': start,
                'startFrame': startFrame,
                'popupText': scoreInc,
                'popupRect': scoreRect,
                'rect': pygame.Rect(location.x, location.y, location.width, location.height)}

    popups.append(newPopup)


def playSFX(sfx):
    
    try:
        sfx.play()
    except:
        print('SFX not found:', sfx)


def jump(currentJumpStage, jumpStartLoc):
    '''calculates by how much the players Y position should be changes based on the current jump stage'''
    global framesFallen

    #the extra amount we add to the player Y position if they are falling
    #reset each time we call this function since we use the 'frameFallen' variable to recalculate
    fallAmount = 0

    #if the player has completed a full jump cycle but is still in the air, they are falling
    if currentJumpStage >= maxJumpCounter + 1:
        
        #don't let currentJumpStage get higher than this, otherwise the player will start
        #rising again, since the jump cycle is based on a sine wave
        currentJumpStage = maxJumpCounter + 1

        #calculate amount to add to player Y position when falling
        framesFallen += 1
        sineWave = math.sin((math.pi/float(maxJumpCounter)) * (maxJumpCounter - 1))
        fallAmount = -(sineWave * maximumJumpHeight * framesFallen)
        
    else:
        #reset the frames fallen varaible
        framesFallen = 0

    #main jump calculation

    #calculates the position on the sine wave the player is currently on    
    sineWave = math.sin((math.pi/float(maxJumpCounter)) * currentJumpStage)

    #convert this to a pixel value by multiplying by the maximum jumpHeight                
    jumpHeight = sineWave * maximumJumpHeight

    #if the player is falling (aka. past the end of the sine wave) we add the extra pixels that
    #they need to fall
    jumpHeight += fallAmount

    return (windowHeight - playerRect.height) - (windowHeight - jumpStartLoc) - jumpHeight
        
        
def populateEnemyLists(enemy):
    global enemies

    indexList = enemy[0]
    enemyType = enemy[1]

    #skips the function if there are none of the specified enemy type in this level
    if len(levels[currentLevel][enemyType]) == 0:
        return
    
    else:
        for obj in levels[currentLevel][enemyType]:

        #load sprites and set y position (height above block)
            if enemyType == 'fliers':
                spriteList = enemyFlierLeftImg
                
                j = platformHeight / 2
                
            elif enemyType == 'shooters':
                spriteList = enemyShooterImg
                
                j = platformHeight - enemyHeight * 2
                
            else:
                if enemyType == 'standers':
                    spriteList = enemyStanderImg
                    
                elif enemyType == 'walkers':
                    spriteList = enemyWalkerLeftImg
                    
                j = platformHeight - enemyHeight


            #animation index runs through spriteList and changes the image used    
            newEnemy =  {'spriteList': spriteList,
                         'animationIndex': 0,
                         'startingX': obj[0] * platformWidth + ((platformWidth - spriteList[0].get_width()) / 2),
                         'startingY': (obj[1]) * platformHeight + j,
                         'direction': 'left'}

            width = spriteList[len(spriteList) - 1].get_width()
            height= spriteList[len(spriteList) - 1].get_height()

            #create rect used for enemy placement
            newEnemy['rect'] = pygame.Rect(newEnemy['startingX'], newEnemy['startingY'], width, height)

            #and hitbox used for collision detection
            newEnemy['hitbox'] = newEnemy['rect'].inflate(-(newEnemy['rect'].width * 1/5), -(newEnemy['rect'].height * 1/5))

            if enemyType == 'shooters':
                newEnemy['shooting'] = False
            
            enemies.append(newEnemy)
            indexList.append(enemies.index(newEnemy))


def levelComplete():
    global currentLevel, timer, score
    
    completeText = GOFont.render('Level Complete', True, gold)
    completeRect = completeText.get_rect()
    completeRect.center = (windowWidth/2, windowHeight/2)
    displaySurf.blit(completeText, completeRect)
    
    pygame.display.update()

    #create a copy of timer, because we change timer below
    scoreCountDelay = timer
    
    pygame.time.wait(500)

    #add remaining time to score
    while timer > 0:
        displaySurf.blit(completeText, completeRect)
        
        timer -= 1
        score += 1
        checkFor1UP(score, playerRect)
        
        drawGame()
        
        pygame.display.update()
        
        fpsClock.tick(scoreCountDelay / 2)
        
    pygame.time.wait(1000)
    
    currentLevel += 1

    #check whether this was the last level or not
    if currentLevel >= len(levels):
        gameComplete()
    else:
        runGame()


def gameComplete():

    os.remove(saveGameFile)
    
    texts = []
    rects = []
    
    displaySurf.fill(gold)
    
    texts.append(GOFont.render('Congratulations!', True, white))
    texts.append(GOFont.render('Snorblegork has successfully', True, white))
    texts.append(GOFont.render('finished his mission on Earth!', True, white))
    texts.append(GOFont.render('', True, white))
    texts.append(GOFont.render('Press any key to', True, white))
    texts.append(GOFont.render('return to the menu', True, white))
    
    for i in range(len(texts)):
        rects.append(texts[i].get_rect())
        rects[i].center = (windowWidth/2, windowHeight * ((i+1)/(len(texts) + 2)))
        
        displaySurf.blit(texts[i], rects[i])
        
    pygame.display.update()
    pygame.event.clear()
    pygame.time.wait(750)

    #press any key to exit
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quitGame()
                
            if event.type == KEYDOWN:
                main()


def gameOverScreen():
    '''shows when the player dies with 0 lives left'''

    os.remove(saveGameFile)
    
    displaySurf.fill(black)
    
    gameOverText = GOFont.render('GAME OVER', True, red)
    gameOverRect = gameOverText.get_rect()
    gameOverRect.center = (windowWidth/2, windowHeight/2)
    
    displaySurf.blit(gameOverText, gameOverRect)
    
    pygame.display.update()
    pygame.time.wait(2000)
    
    main()
                        
   
def quitGame():
    pygame.quit()
    sys.exit()

main()

      
