# game_state.py
import pygame

zoom = 0.25
offset = pygame.Vector2(0, 0)
moving_camera = False
last_mouse_pos = None
turn_active = False
ball_paused = False
planning_team = 0
waiting_to_execute = False  # Espera de confirmación antes de ejecutar
