import pygame
class Robot:
    robot_img_up = pygame.image.load("images/up_robot.png")
    robot_img_down = pygame.image.load("images/down_robot.png")
    robot_img_left = pygame.image.load("images/left_robot.png")
    robot_img_right = pygame.image.load("images/right_robot.png")
    robot_img_up_right = pygame.image.load("images/up_right_robot.png")
    robot_img_up_left = pygame.image.load("images/up_left_robot.png")
    robot_img_down_right = pygame.image.load("images/down_right_robot.png")
    robot_img_down_left = pygame.image.load("images/down_left_robot.png")

# Resize if needed
    robot_imgs = [robot_img_up, robot_img_down, robot_img_left, robot_img_right,
              robot_img_up_right, robot_img_up_left, robot_img_down_right, robot_img_down_left]
