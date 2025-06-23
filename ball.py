# ball.py
import pygame
from constants import BLACK, FRICTION, FIELD_RECT
import game_state

class Ball:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.radius = 10
        self.color = BLACK
        self.velocity = pygame.Vector2(0, 0)

    def update(self):
        self.position += self.velocity
        self.velocity *= FRICTION
        # Colisiones con bordes
        if self.position.x < FIELD_RECT.left + self.radius:
            self.position.x = FIELD_RECT.left + self.radius
            self.velocity.x *= -1
        elif self.position.x > FIELD_RECT.right - self.radius:
            self.position.x = FIELD_RECT.right - self.radius
            self.velocity.x *= -1
        if self.position.y < FIELD_RECT.top + self.radius:
            self.position.y = FIELD_RECT.top + self.radius
            self.velocity.y *= -1
        elif self.position.y > FIELD_RECT.bottom - self.radius:
            self.position.y = FIELD_RECT.bottom - self.radius
            self.velocity.y *= -1

    def draw(self, surface):
        transformed_pos = self.position * game_state.zoom + game_state.offset
        pygame.draw.circle(surface, self.color, (int(transformed_pos.x), int(transformed_pos.y)), int(self.radius * game_state.zoom))
