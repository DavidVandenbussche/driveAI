import pygame
import os 
import math
import sys
#import neat

SCREEN_WIDHT = 1244
SCREEN_HEIGHT = 1016
SCREEN = pygame.display.set_mode((SCREEN_WIDHT,SCREEN_HEIGHT))

TRACK = pygame.image.load(os.path.join("Assets","track.png"))

class Car(pygame.sprite.Sprite):
    def __init__(self): # init function
        super().__init__() # initialise the parent class
        self.original_image = pygame.image.load(os.path.join("Assets","car.png")) # load the original image of the car
        self.image = self.original_image # set the image display on the screen equal to the original_image
        self.rect = self.image.get_rect(center=(490,820)) # specify the rectangle of the image
        self.drive_state = False # True when the car drives
        self.vel_vector = pygame.math.Vector2(1.3,0) # velocity of the car
        self.angle = 0 # useful for the steering
        self.rotation_vel = 5 # rotation velocity
        self.direction = 0 # -1 when we turn left and 1 when we turn right
        self.alive = True # when the car starts it's alive, be careful to start on the road! usef for collisions

    def update(self): # function to update the car when called, the car can drive and rotate
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):  # for the inout of the neural network: the distance to the edge of the track
            self.radar(radar_angle)
        self.collision()

    def drive(self):
        if self.drive_state:
            self.rect.center += self.vel_vector * 6 # increment the center of the car image by the velocity vector, simulating the car driving

    def collision(self):
        length = 40 # distance betzeen the center of the car and the collision point
        # creation of two collisions points
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # death on collision
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255): # when any collision point touches the green color  
             self.alive = False

        # drawing collision points
        # pygame.draw.circle(SCREEN, (0,255,0,0), collision_point_right, 4)
        # pygame.draw.circle(SCREEN, (0,255,0,0), collision_point_left, 4)               

    def rotate(self):
        if self.direction == 1:
            self.angle -= self.rotation_vel # making it turn clockwise ie to the right
            self.vel_vector.rotate_ip(self.rotation_vel) # changing also the velocity vector with rotate in place function
        if self.direction == -1:
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1) # scaling down the original_image
        self.rect = self.image.get_rect(center=self.rect.center) # getting the rectangle of the car image

    def radar(self, radar_angle):
        length = 0 # length of the radar
        x = int(self.rect.center[0])
        y = int(self.rect.center[1]) # x and y the center of the car

        while not SCREEN.get_at((x,y)) == pygame.Color(2, 105, 31, 255) and length < 200: # RGBA colors 2,105,31,255 green
            length +=1
            # now calculating the end point of the radar
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # Draw radar
        # pygame.draw.line(SCREEN, (255,255,255,255), self.rect.center, (x,y), 1) # draw a line that connects the center of the car with the end point of the radar
        # pygame.draw.circle(SCREEN, (0,255 ,0 ,0 ), (x,y), 3)


car = pygame.sprite.GroupSingle(Car()) # "Group container that holds a single sprite." Single sprite image here. The sprite object is an instance of the class Car

def eval_genomes(): # main loop of the game, evaluating the fitness of all the cars to then select the best ones
    run = True
    while run:
        for event in pygame.event.get(): # this block is to quit the pygame window when we click on the red cross
            if event.type == pygame.QUIT:
                pygame.exit()
                sys.exit()
        
        SCREEN.blit(TRACK,(0,0)) # blit = display, displaying the track image on the screen

        # User input
        user_input = pygame.key.get_pressed() # the key which is pressed on the keyboard
        if sum(pygame.key.get_pressed()) <= 1: # when no keys are pressed
            car.sprite.drive_state = False # the car doesn't move
            car.sprite.direction = 0 # not turning when no keys are pressed

        # Drive
        if user_input[pygame.K_UP]: # the car drives if we press the up arrow
            car.sprite.drive_state = True

        # Steer
        if user_input[pygame.K_RIGHT]:
            car.sprite.direction = 1
        if user_input[pygame.K_LEFT]:
            car.sprite.direction = -1


        # Update
        car.draw(SCREEN) # draw the car on the screen window
        car.update() # update the car
        pygame.display.update() # update the display

eval_genomes() # finally we make a call the the loop function




