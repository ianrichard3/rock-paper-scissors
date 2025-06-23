import pygame
import sys
from constants import *
import game_state
from player import Player
from ball import Ball
from field import draw_field
from ui import draw_button

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trayectoria por arrastre")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

players = [Player(300 + (i % 4) * 80, 300 + (i // 4) * 100) for i in range(11)]
ball = Ball(FIELD_RECT.centerx, FIELD_RECT.centery)

button_rect = pygame.Rect(WIDTH - 170, HEIGHT - 80, 150, 60)


while True:
    draw_field(screen)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                game_state.moving_camera = True
                game_state.last_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            elif event.button == 4:  # Zoom in
                mouse_world_before = (pygame.Vector2(mouse_pos) - game_state.offset) / game_state.zoom
                game_state.zoom *= 1.1
                game_state.offset = pygame.Vector2(mouse_pos) - mouse_world_before * game_state.zoom
            elif event.button == 5:  # Zoom out
                mouse_world_before = (pygame.Vector2(mouse_pos) - game_state.offset) / game_state.zoom
                game_state.zoom /= 1.1
                game_state.offset = pygame.Vector2(mouse_pos) - mouse_world_before * game_state.zoom


        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                game_state.moving_camera = False
            elif button_rect.collidepoint(event.pos) and not game_state.turn_active:
                any_movement = False
                for player in players:
                    if player.saved_path:
                        player.moving = True
                        player.current_step = 0
                        any_movement = True
                if any_movement:
                    game_state.turn_active = True
                    game_state.ball_paused = False
                    ball.velocity = ball.stored_velocity if hasattr(ball, 'stored_velocity') else pygame.Vector2(0, 0)

        if event.type == pygame.MOUSEMOTION:
            if game_state.moving_camera and game_state.last_mouse_pos:
                current_mouse = pygame.Vector2(event.pos)
                delta = current_mouse - game_state.last_mouse_pos
                game_state.offset += delta
                game_state.last_mouse_pos = current_mouse

        for player in players:
            player.handle_event(event, mouse_pos)

    if not game_state.ball_paused:
        ball.update()

    # Verificamos estados solo una vez
    all_players_stopped = all(not p.moving for p in players)
    ball_stopped = ball.velocity.length_squared() < 0.01
    all_stopped = all_players_stopped and ball_stopped

    # Pausar pelota si los jugadores ya se detuvieron, pero la pelota aún no
    if game_state.turn_active and all_players_stopped and not game_state.ball_paused:
        game_state.ball_paused = True
        ball.stored_velocity = ball.velocity
        ball.velocity = pygame.Vector2(0, 0)

    # Finalizar el turno si todo (jugadores y pelota) se detuvo
    if game_state.turn_active and all_stopped:
        game_state.turn_active = False
        for player in players:
            player.path = []
            player.raw_path = []
            player.saved_path = []
            player.kick_direction = pygame.Vector2(0, 0)
            player.kick_power = 0


    for player in players:
        player.update(ball, players)
        player.draw(screen)

    ball.draw(screen)
    draw_button(screen, button_rect, font)
    pygame.display.flip()
    clock.tick(FPS)
