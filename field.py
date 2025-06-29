# field.py

import pygame
from constants import WHITE, FIELD_GREEN, FIELD_RECT
import game_state

def draw_field(surface):
    surface.fill(WHITE)

    zoom = game_state.zoom
    offset = game_state.offset

    # Transformar el campo
    transformed_field = pygame.Rect(
        FIELD_RECT.left * zoom + offset.x,
        FIELD_RECT.top * zoom + offset.y,
        FIELD_RECT.width * zoom,
        FIELD_RECT.height * zoom
    )

    # Fondo verde del campo
    pygame.draw.rect(surface, FIELD_GREEN, transformed_field)

    # Línea de mitad de cancha
    mid_x = transformed_field.left + transformed_field.width // 2
    pygame.draw.line(surface, WHITE, (mid_x, transformed_field.top), (mid_x, transformed_field.bottom), 3)

    # Círculo central
    center_circle_radius = 100 * zoom
    pygame.draw.circle(surface, WHITE, transformed_field.center, int(center_circle_radius), 2)

    # Arcos
    goal_width = 10 * zoom
    goal_height = 100 * zoom
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

    # Área grande (16.5 metros reales aprox → 200 en escala)
    area_width = 200 * zoom
    area_height = 400 * zoom
    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.left,
        transformed_field.centery - area_height // 2,
        area_width,
        area_height
    ))
    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.right - area_width,
        transformed_field.centery - area_height // 2,
        area_width,
        area_height
    ))

    # Área chica (5.5 metros reales aprox → 60 en escala)
    small_area_width = 60 * zoom
    small_area_height = 200 * zoom
    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.left,
        transformed_field.centery - small_area_height // 2,
        small_area_width,
        small_area_height
    ))
    pygame.draw.rect(surface, WHITE, pygame.Rect(
        transformed_field.right - small_area_width,
        transformed_field.centery - small_area_height // 2,
        small_area_width,
        small_area_height
    ))
