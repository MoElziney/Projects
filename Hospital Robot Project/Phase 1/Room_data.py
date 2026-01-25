import pygame

class Room_data:

    WIDTH=700
    BORDER_THICKNESS=10
    HEIGHT=700
    DOOR=60

    def __init__(self, width, border,height,door):
        self.WIDTH = width
        self.BORDER_THICKNESS = border
        self.HEIGHT=height
        self.DOOR=door
    first_floor_struct=[
    pygame.Rect(0, 0, WIDTH, BORDER_THICKNESS),  # Top
    pygame.Rect(0, 0, BORDER_THICKNESS, HEIGHT),  # Left
    pygame.Rect(0, HEIGHT - BORDER_THICKNESS, WIDTH, BORDER_THICKNESS),  # Bottom
    pygame.Rect(WIDTH - BORDER_THICKNESS, 0, BORDER_THICKNESS, HEIGHT), # Right
    pygame.Rect(WIDTH/4, 0, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH/4, HEIGHT/4 + DOOR, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH/4, HEIGHT/2 + 2*DOOR, BORDER_THICKNESS, HEIGHT/5), # wall vertical
    pygame.Rect(0, HEIGHT/4+DOOR, WIDTH/4, BORDER_THICKNESS), # wall horizontal
    pygame.Rect(0, 2*(HEIGHT/4+DOOR), WIDTH/4, BORDER_THICKNESS), # wall horizontal

    pygame.Rect(WIDTH*3/4,0, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/4 + DOOR, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/2 + 2*DOOR, BORDER_THICKNESS, HEIGHT/5), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/4+DOOR, WIDTH/4, BORDER_THICKNESS), # wall horizontal
    pygame.Rect(WIDTH*3/4, 2*(HEIGHT/4+DOOR), WIDTH/4, BORDER_THICKNESS) # wall horizontal
    ]
    obj_obstacles_first_floor=[
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (100, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-100, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (100, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-100, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (100, 2*BORDER_THICKNESS+2*HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-100, 2*BORDER_THICKNESS+2*HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (50, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (8*WIDTH/10, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (50, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (8*WIDTH/10, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (50, 2*BORDER_THICKNESS+2*HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/room_chair.png"), (30, 30), (8*WIDTH/10,2*BORDER_THICKNESS+2*HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/counter_1.png"), (90, 50), (WIDTH/2,BORDER_THICKNESS+20)],

    ]
    emergency_floor_struct=[
    pygame.Rect(0, 0, WIDTH, BORDER_THICKNESS),  # Top
    pygame.Rect(0, 0, BORDER_THICKNESS, HEIGHT),  # Left
    pygame.Rect(0, HEIGHT - BORDER_THICKNESS, WIDTH, BORDER_THICKNESS),  # Bottom
    pygame.Rect(WIDTH - BORDER_THICKNESS, 0, BORDER_THICKNESS, HEIGHT), # Right
    pygame.Rect(WIDTH/4, HEIGHT/4 + DOOR, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH/4, HEIGHT/2 + 2*DOOR, BORDER_THICKNESS, HEIGHT/5), # wall vertical
    pygame.Rect(0, HEIGHT/4+DOOR, WIDTH/4, BORDER_THICKNESS), # wall horizontal
    pygame.Rect(0, 2*(HEIGHT/4+DOOR), WIDTH/4, BORDER_THICKNESS), # wall horizontal

    pygame.Rect(WIDTH/2, HEIGHT/4+DOOR, WIDTH/2, BORDER_THICKNESS), # wall horizontal
    ]
    obj_obstacles_emergency_floor=[
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (100, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (150, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (200, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-100, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-150, BORDER_THICKNESS)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-200, BORDER_THICKNESS)],

        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (100, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-200, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-250, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-150, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/bed.png"), (50, 80), (WIDTH-100, 2*BORDER_THICKNESS+HEIGHT//3)],
        [pygame.image.load("Robotics/images/obj_obstacles/counter_1.png"), (90, 50), (50, 2*BORDER_THICKNESS+2*HEIGHT//3)],
        
        [pygame.image.load("Robotics/images/obj_obstacles/counter_2.png"), (90, 50), (5*WIDTH/6,5*HEIGHT/6)],

    ]

    
