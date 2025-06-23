# player.py
import pygame
from constants import RED, BLUE, MAX_DISTANCE, STEP_DISTANCE, MAX_KICK_POWER, CONE_COLOR, WIDTH, HEIGHT, BLACK
import game_state

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
        if game_state.turn_active:
            return

        world_mouse = (pygame.Vector2(mouse_pos) - game_state.offset) / game_state.zoom
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
            mouse_world = (pygame.Vector2(pygame.mouse.get_pos()) - game_state.offset) / game_state.zoom
            direction = mouse_world - self.position
            if direction.length() > 0:
                self.kick_direction = direction.normalize()
                self.kick_power = min(direction.length() / 10, MAX_KICK_POWER)

        if self.drawing:
            current_mouse = (pygame.Vector2(pygame.mouse.get_pos()) - game_state.offset) / game_state.zoom
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
        transformed_pos = self.position * game_state.zoom + game_state.offset
        if len(self.raw_path) >= 2:
            transformed_path = [(p * game_state.zoom + game_state.offset) for p in self.raw_path]
            pygame.draw.lines(surface, RED, False, transformed_path, 3)
        pygame.draw.circle(surface, self.color, (int(transformed_pos.x), int(transformed_pos.y)), int(self.radius * game_state.zoom))

        if self.kick_direction.length() > 0:
            end_pos = self.position + self.kick_direction * self.kick_power * 3
            pygame.draw.line(surface, BLACK, self.position * game_state.zoom + game_state.offset, end_pos * game_state.zoom + game_state.offset, 2)

        self.draw_cone(surface, transformed_pos, self.facing_direction)


    def draw_cone(self, surface, position, direction, length=40, angle_width=40):
        # (misma lógica)
        if direction.length() == 0:
            return
        cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        half_angle = angle_width / 2
        left = direction.rotate(-half_angle).normalize() * length * game_state.zoom + position
        right = direction.rotate(angle_width).normalize() * length * game_state.zoom + position
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
