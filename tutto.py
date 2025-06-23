import pygame
import sys
import math

pygame.init()

# Configuración inicial
WIDTH, HEIGHT = 1100, 700
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trayectoria por arrastre")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Colores
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
BLACK = (0, 0, 0)
FIELD_GREEN = (34, 139, 34)
CONE_COLOR = (0, 255, 0, 80)

STEP_DISTANCE = 4
FRICTION = 0.98
MAX_DISTANCE = 700

zoom = 0.25
offset = pygame.Vector2(0, 0)
moving_camera = False
last_mouse_pos = None
ball_paused = False


FIELD_RECT = pygame.Rect(0, 0, 2000, 1500)

MAX_KICK_POWER = 16
turn_active = False

class Player:
    def __init__(self, x, y, color=BLUE):
        self.position = pygame.Vector2(x, y)
        self.radius = 20
        self.color = color
        self.kick_power = 0
        self.kick_direction = pygame.Vector2(0, 0)
        self.setting_kick = False
        self.raw_path = []
        self.path = []
        self.saved_path = []
        self.moving = False
        self.drawing = False
        self.current_step = 0
        self.last_mouse_pos = None
        self.facing_direction = pygame.Vector2(1, 0)
        self.current_distance = 0

    def handle_event(self, event, mouse_pos):
        if turn_active:
            return

        world_mouse = (pygame.Vector2(mouse_pos) - offset) / zoom
        if event.type == pygame.MOUSEBUTTONDOWN:
            distance = (world_mouse - self.position).length()
            if event.button == 1 and distance < self.radius:
                self.drawing = True
                self.raw_path = []
                self.path = []
                self.last_mouse_pos = world_mouse
                self.current_distance = 0
            elif event.button == 3 and distance < self.radius:
                self.setting_kick = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.setting_kick = False
            if event.button == 1:
                self.drawing = False
                if len(self.raw_path) >= 2:
                    self.path = self.interpolate_path(self.raw_path, STEP_DISTANCE)
                    self.saved_path = list(self.path)

    def update(self, ball, others):
        if self.setting_kick:
            mouse_world = (pygame.Vector2(pygame.mouse.get_pos()) - offset) / zoom
            direction = mouse_world - self.position
            if direction.length() > 0:
                self.kick_direction = direction.normalize()
                self.kick_power = min(direction.length() / 10, MAX_KICK_POWER)

        if self.drawing:
            current_mouse = (pygame.Vector2(pygame.mouse.get_pos()) - offset) / zoom
            delta = current_mouse - self.last_mouse_pos if self.last_mouse_pos else pygame.Vector2(0, 0)
            distance = delta.length()
            if distance >= 2 and self.current_distance + distance <= MAX_DISTANCE:
                self.raw_path.append(current_mouse)
                self.last_mouse_pos = current_mouse
                self.current_distance += distance

        if self.moving and self.saved_path:
            if self.current_step < len(self.saved_path):
                next_pos = pygame.Vector2(self.saved_path[self.current_step])
                direction = next_pos - self.position
                if direction.length() > 0:
                    self.facing_direction = direction.normalize()
                self.position = next_pos
                self.current_step += 1
            else:
                self.moving = False

        offset_vec = ball.position - self.position
        distance = offset_vec.length()
        if distance < self.radius + ball.radius and distance != 0:
            normal = offset_vec.normalize()
            overlap = self.radius + ball.radius - distance
            ball.position += normal * overlap
            if self.kick_power > 0 and self.kick_direction.length() > 0:
                ball.velocity = self.kick_direction * self.kick_power
            else:
                ball.velocity = ball.velocity.reflect(normal) * 0.8

        for other in others:
            if other is not self:
                diff = self.position - other.position
                dist = diff.length()
                if dist < self.radius * 2 and dist != 0:
                    overlap = self.radius * 2 - dist
                    push = diff.normalize() * (overlap / 2)
                    self.position += push
                    other.position -= push

    def draw(self, surface):
        transformed_pos = self.position * zoom + offset
        if len(self.raw_path) >= 2:
            transformed_path = [(p * zoom + offset) for p in self.raw_path]
            pygame.draw.lines(surface, RED, False, transformed_path, 3)
        pygame.draw.circle(surface, self.color, (int(transformed_pos.x), int(transformed_pos.y)), int(self.radius * zoom))

        if self.kick_direction.length() > 0:
            end_pos = self.position + self.kick_direction * self.kick_power * 3
            pygame.draw.line(surface, BLACK, self.position * zoom + offset, end_pos * zoom + offset, 2)

        self.draw_cone(surface, transformed_pos, self.facing_direction)

    def draw_cone(self, surface, position, direction, length=40, angle_width=40):
        if direction.length() == 0:
            return
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        half_angle = angle_width / 2
        left = direction.rotate(-half_angle).normalize() * length * zoom + position
        right = direction.rotate(angle_width).normalize() * length * zoom + position
        pygame.draw.polygon(cone_surface, CONE_COLOR, [position, left, right])
        surface.blit(cone_surface, (0, 0))

    def interpolate_path(self, points, step_distance):
        if len(points) < 2:
            return points
        interpolated = []
        for i in range(len(points) - 1):
            p1 = pygame.Vector2(points[i])
            p2 = pygame.Vector2(points[i + 1])
            segment = p2 - p1
            distance = segment.length()
            steps = max(1, int(distance // step_distance))
            for j in range(steps):
                interpolated.append(p1 + segment * (j / steps))
        interpolated.append(pygame.Vector2(points[-1]))
        return interpolated


class Ball:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.radius = 10
        self.color = BLACK
        self.velocity = pygame.Vector2(0, 0)

    def update(self):
        self.position += self.velocity
        self.velocity *= FRICTION

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
        transformed_pos = self.position * zoom + offset
        pygame.draw.circle(surface, self.color, (int(transformed_pos.x), int(transformed_pos.y)), int(self.radius * zoom))

players = [Player(300 + (i % 4) * 80, 300 + (i // 4) * 100) for i in range(11)]
ball = Ball(FIELD_RECT.centerx, FIELD_RECT.centery)

button_rect = pygame.Rect(WIDTH - 170, HEIGHT - 80, 150, 60)

def draw_field(surface):
    surface.fill(WHITE)
    transformed_field = pygame.Rect(FIELD_RECT.left * zoom + offset.x, FIELD_RECT.top * zoom + offset.y, FIELD_RECT.width * zoom, FIELD_RECT.height * zoom)
    pygame.draw.rect(surface, FIELD_GREEN, transformed_field)
    goal_width = 10 * zoom
    goal_height = 100 * zoom
    pygame.draw.rect(surface, WHITE, pygame.Rect(transformed_field.left - goal_width, transformed_field.centery - goal_height//2, goal_width, goal_height))
    pygame.draw.rect(surface, WHITE, pygame.Rect(transformed_field.right, transformed_field.centery - goal_height//2, goal_width, goal_height))

def draw_button():
    color = GREEN if not turn_active else (150, 150, 150)
    pygame.draw.rect(screen, color, button_rect)
    text = font.render("Ejecutar", True, WHITE)
    screen.blit(text, (button_rect.x + 20, button_rect.y + 15))

while True:
    draw_field(screen)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
                moving_camera = True
                last_mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            elif event.button == 4:
                mouse_world_before = (pygame.Vector2(mouse_pos) - offset) / zoom
                zoom *= 1.1
                offset = pygame.Vector2(mouse_pos) - mouse_world_before * zoom
            elif event.button == 5:
                mouse_world_before = (pygame.Vector2(mouse_pos) - offset) / zoom
                zoom /= 1.1
                offset = pygame.Vector2(mouse_pos) - mouse_world_before * zoom

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                moving_camera = False
            elif button_rect.collidepoint(event.pos) and not turn_active:
                any_movement = False
                for player in players:
                    if player.saved_path:
                        player.moving = True
                        player.current_step = 0
                        any_movement = True
                if any_movement:
                    turn_active = True
                    ball_paused = False
                    ball.velocity = ball.stored_velocity if hasattr(ball, 'stored_velocity') else pygame.Vector2(0, 0)

        if event.type == pygame.MOUSEMOTION:
            if moving_camera and last_mouse_pos:
                current_mouse = pygame.Vector2(event.pos)
                delta = current_mouse - last_mouse_pos
                offset += delta
                last_mouse_pos = current_mouse

        for player in players:
            player.handle_event(event, mouse_pos)

    if not ball_paused:
        ball.update()

    # Verificamos estados solo una vez
    all_players_stopped = all(not p.moving for p in players)
    ball_stopped = ball.velocity.length_squared() < 0.01
    all_stopped = all_players_stopped and ball_stopped

    # Pausar pelota si los jugadores ya se detuvieron, pero la pelota aún no
    if turn_active and all_players_stopped and not ball_paused:
        ball_paused = True
        ball.stored_velocity = ball.velocity
        ball.velocity = pygame.Vector2(0, 0)

    # Finalizar el turno si todo (jugadores y pelota) se detuvo
    if turn_active and all_stopped:
        turn_active = False
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
    draw_button()
    pygame.display.flip()
    clock.tick(FPS)
