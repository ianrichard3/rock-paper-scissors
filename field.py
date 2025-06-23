# field.py

import pygame
from constants import WHITE, FIELD_GREEN, FIELD_RECT
import game_state

def draw_field(surface):
    surface.fill(WHITE)
    transformed_field = pygame.Rect(
        FIELD_RECT.left * game_state.zoom + game_state.offset.x,
        FIELD_RECT.top * game_state.zoom + game_state.offset.y,
        FIELD_RECT.width * game_state.zoom,
        FIELD_RECT.height * game_state.zoom
    )
    pygame.draw.rect(surface, FIELD_GREEN, transformed_field)

    goal_width = 10 * game_state.zoom
    goal_height = 100 * game_state.zoom

    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.left - goal_width,
        transformed_field.centery - goal_height // 2,
        goal_width,
        goal_height
    ))
    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.right,
        transformed_field.centery - goal_height // 2,
        goal_width,
        goal_height
    ))
