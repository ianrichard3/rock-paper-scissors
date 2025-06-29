# ui.py

import pygame
from constants import GREEN, WHITE, BLUE, RED
import game_state

def draw_button(surface, button_rect, font):
    # Color del botón según el estado del juego
    if game_state.turn_active:
        color = (150, 150, 150)  # Gris cuando se está ejecutando
    elif game_state.waiting_to_execute:
        color = GREEN  # Verde cuando se espera ejecución
    elif game_state.planning_team == 0:
        color = BLUE  # Azul para Plan A
    else:
        color = RED  # Rojo para Plan B

    pygame.draw.rect(surface, color, button_rect)

    # Texto del botón según el estado del juego
    if game_state.turn_active:
        label = "Ejecutando..."
    elif game_state.waiting_to_execute:
        label = "Ejecutar Jugadas"
    elif game_state.planning_team == 0:
        label = "Terminar Plan A"
    else:
        label = "Terminar Plan B"

    text = font.render(label, True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    surface.blit(text, text_rect)
