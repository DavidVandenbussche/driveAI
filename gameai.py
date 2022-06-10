import pygame
import os
import math
import sys
import neat


####
'''
Pour créer une map lancer GIMP, pinceau pixel noir, taille 1920 1080 et commencer la course a 490px 820px, 
changeable dans get_rect(center = ...)
Ensuite exporter sous (pour extension png) et changer le nom ddans TRACK, noms pris : mapi (i dans [1,5] par difficulté)
''' 
####


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

TRACK = pygame.image.load(os.path.join("Assets","map2.png"))


class Car(pygame.sprite.Sprite):
    def __init__(self): # init function
        super().__init__() # initialise the parent class
        self.original_image = pygame.image.load(os.path.join("Assets","car.png")) # load the original image of the car
        self.image = self.original_image # set the image display on the screen equal to the original_image
        self.rect = self.image.get_rect(center=(490,820)) # specify the rectangle of the image
        self.vel_vector = pygame.math.Vector2(0.7,0) # velocity of the car
        self.angle = 0 # useful for the steering
        self.rotation_vel = 5 # rotation velocity
        self.direction = 0 # -1 when we turn left and 1 when we turn right
        self.alive = True # when the car starts it's alive, be careful to start on the road! usef for collisions
        self.radars = [] # list to store all the information collected by by the radars

    def update(self): # function to update the car when called, the car can drive and rotate
        self.radars.clear() # we only want to the most up to date data within the radar list
        self.drive()
        self.rotate()
        for radar_angle in (-60, -30, 0, 30, 60):  # for the inout of the neural network: the distance to the edge of the track
            self.radar(radar_angle)
        self.collision()
        self.data()

    def drive(self):
        self.rect.center += self.vel_vector * 6 # increment the center of the car image by the velocity vector, simulating the car driving

    def collision(self):
        length = 40 # distance between the center of the car and the collision point, then creation of two collisions points
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # death on collision
        if SCREEN.get_at(collision_point_right) == pygame.Color(255, 255, 255, 255) or SCREEN.get_at(collision_point_left) == pygame.Color(255, 255, 255, 255): # when any collision point touches the green color  
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

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.05) # scaling down the original_image
        self.rect = self.image.get_rect(center=self.rect.center) # getting the rectangle of the car image

    def radar(self, radar_angle):
        length = 0 # length of the radar
        x = int(self.rect.center[0])
        y = int(self.rect.center[1]) # x and y the center of the car

        while not SCREEN.get_at((x,y)) == pygame.Color(255, 255, 255, 255) and length < 200: # RGBA colors 
            length += 1 # now calculating the end point of the radar
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # Draw radar
        #pygame.draw.line(SCREEN, (2,105,31,255), self.rect.center, (x,y), 1) # draw a line that connects the center of the car with the end point of the radar
        #pygame.draw.circle(SCREEN, (0,255 ,0 ,0 ), (x,y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2) + math.pow(self.rect.center[1] - y, 2))) # dist between the center of the car and the tip of a radar

        self.radars.append([radar_angle, dist]) # store the information in the radars list

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input 

def remove(index): # removing the car that runs outside of the track, each car is indexed so takes an index as an argument
    cars.pop(index) # remove the car
    ge.pop(index) # remove the genome
    nets.pop(index) # remove the neural network


def eval_genomes(genomes, config): # main loop of the game, evaluating the fitness of all the cars to then select the best ones
    global cars, ge, nets # global variables

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car())) # add a group single container to the car list that store the car object
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config) 
        nets.append(net) # append neat alg
        genome.fitness = 0 # initial fitness of each car

    run = True
    while run:
        for event in pygame.event.get(): # this block is to quit the pygame window when we click on the red cross
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        SCREEN.blit(TRACK, (0, 0)) # blit = display, displaying the track image on the screen

        if len(cars) == 0:
            break # if no more cars break the loop

        for i, car in enumerate(cars):
            ge[i].fitness += 1 # increment the fitness score to all the cars runing
            if not car.sprite.alive:
                remove(i) # remove the car that goes into the grass

        for i, car in enumerate(cars): # determine how each individual car drives, with the outpu of the neural network not the arrow keys
            output = nets[i].activate(car.sprite.data()) # output created by an activation function which takes in argument the data generated by the cars radars, gives a list of 2 elements  between -1 and 1
            if output[0] > 0.7:
                car.sprite.direction = 1 # then the car turns right
            if output[1] > 0.7:
                car.sprite.direction = -1 # turns left
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0 # straight forward

        # Update
        for car in cars:
            car.draw(SCREEN) # draw the car on the screen window
            car.update() # update the car
        pygame.display.update() # update the display

        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_ESCAPE]:
            sys.exit()

# Setup the NEAT neural network
def run(config_path):
    global pop 
    config = neat.config.Config( # default values for neat alg
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    # helpful statistics
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50) # eval function and number of generations of cars that we want to iterate through

if __name__ == '__main__': #run the program if the file is executed directly and not imported
    local_dir = os.path.dirname(__file__) # specify the path to the local directory
    config_path = os.path.join(local_dir, 'config.txt') # create the path to the configuration file
    run(config_path)

