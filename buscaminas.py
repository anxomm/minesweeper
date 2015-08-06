#====================================
#     ---------IMPORTS---------
#====================================
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
import random
import time
#====================================
#    ---------CONSTANTS---------
#====================================
WIDTH_SCREEN = 600
HEIGHT_SCREEN = 450
FPS = 60

#====================================
#  --------FUNCTIONS/CLASSES--------
#====================================

#==================FUNCTIONS
def create_coordinates(pos_start_width, pos_start_height, n_box_width, n_box_height):
    group_coordinates = []
    x = pos_start_width
    y = pos_start_height

    for column in range(n_box_height):
        for row in range(n_box_width):
            group_coordinates.append((x, y))
            x += 16
        x = pos_start_width
        y += 16

    return group_coordinates


def create_coordinates_mines(group_coordinates, n_mines):
    pos_mines = []
    for mine in range(n_mines):
        position = group_coordinates[random.randrange(len(group_coordinates))]
        pos_mines.append(position)
        group_coordinates.remove(position)
    return pos_mines


def create_coordinates_numbers(group_coordinates, pos_mines):
    pos_boxes = []
    for coordinate in group_coordinates:
        number = 0
        if (coordinate[0]-16, coordinate[1]-16) in pos_mines:  # Up-Right
            number += 1
        if (coordinate[0], coordinate[1]-16) in pos_mines:  # Up
            number += 1
        if (coordinate[0]+16, coordinate[1]-16) in pos_mines:  # Up-Left
            number += 1
        if (coordinate[0]-16, coordinate[1]) in pos_mines:  # Right
            number += 1
        if (coordinate[0]+16, coordinate[1]) in pos_mines:  # Left
            number += 1
        if (coordinate[0]-16, coordinate[1]+16) in pos_mines:  # Down-Right
            number += 1
        if (coordinate[0], coordinate[1]+16) in pos_mines:  # Down
            number += 1
        if (coordinate[0]+16, coordinate[1]+16) in pos_mines:  # Down-Left
            number += 1

        if number != 0:
            pos_boxes.append((str(number), coordinate))
            group_coordinates.remove(coordinate)
            number = 0

    return pos_boxes


def create_coordinates_spaces(group_coordinates):
    pos_spaces = []
    for coordinate in group_coordinates:
        pos_spaces.append(coordinate)
    return pos_spaces


def update_table(standard_image, group_mines, group_numbers, group_spaces):
    #-Mines
    for mine in group_mines:
        if mine.mode == True:
            DISPLAYSURF.blit(mine.image, (mine.pos))
        elif mine.image != mine.original_image:  # Blit the box with a flag
            DISPLAYSURF.blit(mine.image, (mine.pos))
        else:
            DISPLAYSURF.blit(standard_image, (mine.pos))

    #-Numbers
    for number in group_numbers:
        if number.mode == True:
            DISPLAYSURF.blit(number.image, (number.pos))
        elif number.image != number.original_image:
            DISPLAYSURF.blit(number.image, (number.pos))
        else:
            DISPLAYSURF.blit(standard_image, (number.pos))

    #-Spaces
    for space in group_spaces:
        if space.mode == True:
            DISPLAYSURF.blit(space.image, (space.pos))
        elif space.image != space.original_image:
            DISPLAYSURF.blit(space.image, (space.pos))
        else:
            DISPLAYSURF.blit(standard_image, (space.pos))


def search_box(group_mines, group_numbers, group_spaces, position):
    for mine in group_mines:
        if (position[0] >= mine.pos[0] and position[0] <= mine.pos[0]+15) and (position[1] >= mine.pos[1] and position[1] <= mine.pos[1]+15):
            return mine

    for number in group_numbers:
        if (position[0] >= number.pos[0] and position[0] <= number.pos[0]+15) and (position[1] >= number.pos[1] and position[1] <= number.pos[1]+15):
            return number

    for space in group_spaces:
        if (position[0] >= space.pos[0] and position[0] <= space.pos[0]+15) and (position[1] >= space.pos[1] and position[1] <= space.pos[1]+15):
            return space


def end_game(n_mines, box, group_mines):
    if box.name == "mine" and box.mode == True:
        box.image = pygame.image.load("graphics/box_mine_fail.png")
        end = "lose"
        for mine in group_mines:
            mine.mode = True
        return end

    counter = 0
    for mine in group_mines:
        if mine.image != mine.original_image:
            counter += 1
    if counter == n_mines:  # All mines are with the flag, the player knows where are all the mines
        end = "win"
        return end


def new_game():
    time_start = time.time()
    counter_mines = 100

    group_coordinates = create_coordinates(12.5, 53.25, 36, 24)

    group_mines = pygame.sprite.Group()
    pos_mines = create_coordinates_mines(group_coordinates, counter_mines)
    for coordinate in pos_mines:
        mine = Box("mine", coordinate)
        group_mines.add(mine)

    group_numbers = pygame.sprite.Group()
    pos_numbers = create_coordinates_numbers(group_coordinates, pos_mines) # [(number, coordinate), (number, coordinate), ...]
    for coordinate in pos_numbers:
        number = coordinate[0]
        coordinate_number = coordinate[1]
        number_box = Box(number, coordinate_number)
        number_box.name = "number"
        group_numbers.add(number_box)

    group_spaces = pygame.sprite.Group()
    pos_spaces = create_coordinates_spaces(group_coordinates)
    for coordinate in pos_spaces:
        group_spaces.add(Box("space", coordinate))

    return time_start, 0, counter_mines, group_mines, group_numbers, group_spaces, pos_spaces


def boxes_next_to(position):
    list_boxes_next_to = []
    list_boxes_next_to.append(search_box(group_mines, group_numbers, group_spaces, (position[0]+16, position[1])))
    list_boxes_next_to.append(search_box(group_mines, group_numbers, group_spaces, (position[0]-16, position[1])))
    list_boxes_next_to.append(search_box(group_mines, group_numbers, group_spaces, (position[0], position[1]-16)))
    list_boxes_next_to.append(search_box(group_mines, group_numbers, group_spaces, (position[0], position[1]+16)))
    for box in list_boxes_next_to:
        if box == None:
            list_boxes_next_to.remove(box)

    return list_boxes_next_to


def show_spaces(box_space, pos_spaces):
    list_spaces = [box_space]
    for space in list_spaces:
        boxes_next = boxes_next_to(space.pos)
        for box in boxes_next:
            if box.name == "space" and box not in list_spaces:
                box.mode = True
                list_spaces.append(box)
            elif box.name == "number":
                box.mode = True


#==================CLASSES
class Box(pygame.sprite.Sprite):
    def __init__(self, name, position):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image = pygame.image.load("graphics/box_" + name + ".png")
        self.original_image = self.image  # Change when you put a flag in the box (left click)

        self.pos = position
        self.mode = False  # False if it's hidden, True if is clear


#====================================
#      ----------BODY----------
#====================================
#------------------Initialize
pygame.init()
DISPLAYSURF = pygame.display.set_mode((WIDTH_SCREEN, HEIGHT_SCREEN))
pygame.display.set_caption("Buscaminas")
fps_clock = pygame.time.Clock()

#------------------Create boxes and time
box_flag_image = pygame.image.load("graphics/box_flag.png")
box_standard_image = pygame.image.load("graphics/box_standard.png")

all_mines = 100
time_start, time_finish, counter_mines, group_mines, group_numbers, group_spaces, pos_spaces = new_game()

#------------------Font
font = pygame.font.Font("Market_Deco.TTF", 30)

#------------------Others
counter_end_game = None

#====================================
#     -----------LOOP-----------
#====================================
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == MOUSEBUTTONDOWN:
            if (event.pos[0] >= 200 and event.pos[0] <= 335) and (event.pos[1] >= 12 and event.pos[1] <= 39):  # Create new game
                time_start, time_finish, counter_mines, group_mines, group_numbers, group_spaces, pos_spaces = new_game()
                counter_end_game = None

            if counter_end_game == None:  # If you don't lose or win
                box_pressed = search_box(group_mines, group_numbers, group_spaces, event.pos)
                try:
                    if box_pressed.mode == False:  # Press in a box
                        if pygame.mouse.get_pressed()[0] and box_pressed.image == box_pressed.original_image:  # If the box hasn't got a flag
                            box_pressed.mode = True
                            if box_pressed.name == "space":
                                show_spaces(box_pressed, pos_spaces)

                        elif pygame.mouse.get_pressed()[2]:  # Put or remove a flag
                            if box_pressed.image == box_pressed.original_image:
                                box_pressed.image = pygame.image.load("graphics/box_flag.png")
                                counter_mines -= 1
                            else:
                                counter_mines += 1
                                box_pressed.image = box_pressed.original_image

                    #------------------End game
                    if end_game(all_mines, box_pressed, group_mines) == "win":
                        counter_end_game = "win"
                        time_finish = int(time.time()-time_start)
                    elif end_game(90, box_pressed, group_mines) == "lose":
                        time_finish = int(time.time()-time_start)
                        counter_end_game = "lose"

                except AttributeError:  # When you don't press a box
                    pass

    #================================UPDATE============================
    #------------------Surface
    DISPLAYSURF.fill((0, 0, 0, 255))

    #------------------Table
    pygame.draw.rect(DISPLAYSURF, pygame.Color(150, 150, 150), pygame.Rect(10, 50, 580, 390))
    update_table(box_standard_image, group_mines, group_numbers, group_spaces)

    #------------------Counters and bars
    #___Bars
    bar_counters = pygame.gfxdraw.rectangle(DISPLAYSURF, (10, 10, 580, 30), (255, 255, 255, 255))
    stuffed_counters = pygame.gfxdraw.box(DISPLAYSURF, (11, 11, 579, 29), (100, 100, 100, 255))

    #___Text
    #-Time
    if counter_end_game == None:
        time_now = int(time.time()-time_start)
        if time_now > 999999:
            time_now = 999999
    else:
        time_now = time_finish

    text_time = font.render("TIME:" + str(time_now), True, (0, 0, 0, 255))
    DISPLAYSURF.blit(text_time, (30, 10))

    #-Mines
    text_mines = font.render("MINES:" + str(counter_mines), True, (0, 0, 0, 255))
    DISPLAYSURF.blit(text_mines, (460, 10))

    #-New Game
    bar_new_game = pygame.gfxdraw.rectangle(DISPLAYSURF, (199, 11, 137, 29), (0, 0, 0, 255))
    stuffed_new_game = pygame.gfxdraw.box(DISPLAYSURF, (200, 12, 135, 27), (200, 200, 200, 255))
    text_new_game = font.render("NEW GAME", True, (0, 0, 0, 255))
    DISPLAYSURF.blit(text_new_game, (200, 10))

    #------------------End of the game
    if counter_end_game == "win":
        text_win = font.render("WIN!!", True, (255, 200, 0, 255))
        DISPLAYSURF.blit(text_win, ((WIDTH_SCREEN+text_win.get_rect()[2])//3, (HEIGHT_SCREEN+text_win.get_rect()[3])//2))
    elif counter_end_game == "lose":
        text_lose = font.render("You lose...", True, (255, 0, 0, 255))
        DISPLAYSURF.blit(text_lose, ((WIDTH_SCREEN+text_lose.get_rect()[2])//4, (HEIGHT_SCREEN+text_lose.get_rect()[3])//2))

    #------------------Update, FPS
    pygame.display.update()
    fps_clock.tick(FPS)


# Al pulsar en un espacio que se muestren todas las casillas vacías (hasta llegar a un número)  ** HECHO
# Poner a funcionar new_game() ** HECHO
# Poner a funcionar end_game() ** HECHO