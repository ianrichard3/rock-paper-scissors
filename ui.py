# ui.py

import pygame
from constants import GREEN, WHITE  
import game_state

def draw_button(surface, button_rect, font):
    color = GREEN if not game_state.turn_active else (150, 150, 150)
    pygame.draw.rect(surface, color, button_rect)
    text = font.render("Ejecutar", True, WHITE)
    surface.blit(text, (button_rect.x + 20, button_rect.y + 15))
