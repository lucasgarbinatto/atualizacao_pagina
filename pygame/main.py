import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top Down GTA II Style Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game settings
PLAYER_SIZE = 30
CAR_SIZE = 40
NPC_SIZE = 25
BUILDING_SIZE = 80
PLAYER_SPEED = 3
CAR_SPEED = 5
NPC_SPEED = 1

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.in_car = False
        self.car = None
        
    def update(self, keys, buildings):
        # Store previous position for collision rollback
        prev_x, prev_y = self.rect.x, self.rect.y
        
        if not self.in_car:
            # Walking movement with collision checking
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
                if self.check_building_collision(buildings):
                    self.rect.y = prev_y
            if keys[pygame.K_s]:
                self.rect.y += self.speed
                if self.check_building_collision(buildings):
                    self.rect.y = prev_y
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                if self.check_building_collision(buildings):
                    self.rect.x = prev_x
            if keys[pygame.K_d]:
                self.rect.x += self.speed
                if self.check_building_collision(buildings):
                    self.rect.x = prev_x
        else:
            # Car movement with collision checking
            car_prev_x, car_prev_y = self.car.rect.x, self.car.rect.y
            
            if keys[pygame.K_w]:
                self.car.rect.y -= CAR_SPEED
                if self.car.check_building_collision(buildings):
                    self.car.rect.y = car_prev_y
                else:
                    self.rect.center = self.car.rect.center
            if keys[pygame.K_s]:
                self.car.rect.y += CAR_SPEED
                if self.car.check_building_collision(buildings):
                    self.car.rect.y = car_prev_y
                else:
                    self.rect.center = self.car.rect.center
            if keys[pygame.K_a]:
                self.car.rect.x -= CAR_SPEED
                if self.car.check_building_collision(buildings):
                    self.car.rect.x = car_prev_x
                else:
                    self.rect.center = self.car.rect.center
            if keys[pygame.K_d]:
                self.car.rect.x += CAR_SPEED
                if self.car.check_building_collision(buildings):
                    self.car.rect.x = car_prev_x
                else:
                    self.rect.center = self.car.rect.center
    
    def check_building_collision(self, buildings):
        """Check if player collides with any building"""
        for building in buildings:
            if self.rect.colliderect(building.rect):
                return True
        return False
    
    def try_enter_car(self, cars):
        if not self.in_car:
            for car in cars:
                if self.rect.colliderect(car.rect):
                    self.in_car = True
                    self.car = car
                    car.occupied = True
                    break
    
    def exit_car(self):
        if self.in_car:
            self.in_car = False
            self.car.occupied = False
            self.car = None
    
    def draw(self, screen, camera_offset):
        if not self.in_car:
            draw_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
            pygame.draw.rect(screen, GREEN, (*draw_pos, PLAYER_SIZE, PLAYER_SIZE))

class Car:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, CAR_SIZE, CAR_SIZE)
        self.occupied = False
    
    def check_building_collision(self, buildings):
        """Check if car collides with any building"""
        for building in buildings:
            if self.rect.colliderect(building.rect):
                return True
        return False
    
    def draw(self, screen, camera_offset):
        draw_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        color = YELLOW if self.occupied else BLUE
        pygame.draw.rect(screen, color, (*draw_pos, CAR_SIZE, CAR_SIZE))

class NPC:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, NPC_SIZE, NPC_SIZE)
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.move_timer = 0
        self.alive = True
    
    def update(self, buildings):
        if not self.alive:
            return
        
        # Store previous position
        prev_x, prev_y = self.rect.x, self.rect.y
        
        self.move_timer += 1
        if self.move_timer > 60:  # Change direction every 60 frames
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.move_timer = 0
        
        # Move and check for building collisions
        self.rect.x += self.direction[0] * NPC_SPEED
        self.rect.y += self.direction[1] * NPC_SPEED
        
        # Check building collision and revert if needed
        if self.check_building_collision(buildings):
            self.rect.x, self.rect.y = prev_x, prev_y
            # Change direction when hitting a building
            self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
    
    def check_building_collision(self, buildings):
        """Check if NPC collides with any building"""
        for building in buildings:
            if self.rect.colliderect(building.rect):
                return True
        return False
    
    def draw(self, screen, camera_offset):
        if self.alive:
            draw_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
            pygame.draw.rect(screen, RED, (*draw_pos, NPC_SIZE, NPC_SIZE))

class Building:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BUILDING_SIZE, BUILDING_SIZE)
    
    def draw(self, screen, camera_offset):
        draw_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        pygame.draw.rect(screen, GRAY, (*draw_pos, BUILDING_SIZE, BUILDING_SIZE))
        pygame.draw.rect(screen, DARK_GRAY, (*draw_pos, BUILDING_SIZE, BUILDING_SIZE), 3)

class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.direction = direction
        self.speed = 8
    
    def update(self, buildings):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        
        # Check if bullet hits building and remove it
        for building in buildings:
            if self.rect.colliderect(building.rect):
                return True  # Signal to remove bullet
        return False
    
    def draw(self, screen, camera_offset):
        draw_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        pygame.draw.rect(screen, WHITE, (*draw_pos, 5, 5))

class Game:
    def __init__(self):
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.cars = []
        self.npcs = []
        self.buildings = []
        self.bullets = []
        self.camera_offset = [0, 0]
        
        # Generate world
        self.generate_world()
    
    def generate_world(self):
        # Create buildings first to avoid overlaps
        building_positions = []
        for _ in range(15):
            while True:
                x = random.randint(100, 1500)
                y = random.randint(100, 1100)
                new_building = pygame.Rect(x, y, BUILDING_SIZE, BUILDING_SIZE)
                
                # Check if building overlaps with player spawn or other buildings
                player_spawn = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 - 50, 100, 100)
                if not new_building.colliderect(player_spawn):
                    overlap = False
                    for pos in building_positions:
                        if new_building.colliderect(pos):
                            overlap = True
                            break
                    if not overlap:
                        building_positions.append(new_building)
                        self.buildings.append(Building(x, y))
                        break
        
        # Create cars avoiding buildings
        for _ in range(10):
            while True:
                x = random.randint(0, 1600)
                y = random.randint(0, 1200)
                car_rect = pygame.Rect(x, y, CAR_SIZE, CAR_SIZE)
                
                collision = False
                for building in self.buildings:
                    if car_rect.colliderect(building.rect):
                        collision = True
                        break
                
                if not collision:
                    self.cars.append(Car(x, y))
                    break
        
        # Create NPCs avoiding buildings
        for _ in range(20):
            while True:
                x = random.randint(0, 1600)
                y = random.randint(0, 1200)
                npc_rect = pygame.Rect(x, y, NPC_SIZE, NPC_SIZE)
                
                collision = False
                for building in self.buildings:
                    if npc_rect.colliderect(building.rect):
                        collision = True
                        break
                
                if not collision:
                    self.npcs.append(NPC(x, y))
                    break
    
    def update_camera(self):
        # Center camera on player
        target_x = self.player.rect.centerx - WIDTH // 2
        target_y = self.player.rect.centery - HEIGHT // 2
        
        # Smooth camera movement
        self.camera_offset[0] += (target_x - self.camera_offset[0]) * 0.1
        self.camera_offset[1] += (target_y - self.camera_offset[1]) * 0.1
    
    def handle_shooting(self, mouse_pos):
        # Calculate direction from player to mouse
        player_center = (self.player.rect.centerx - self.camera_offset[0], 
                        self.player.rect.centery - self.camera_offset[1])
        
        dx = mouse_pos[0] - player_center[0]
        dy = mouse_pos[1] - player_center[1]
        
        # Normalize direction
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            direction = (dx/distance, dy/distance)
            bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, direction)
            self.bullets.append(bullet)
    
    def check_collisions(self):
        # Check bullet-NPC collisions and bullet-building collisions
        for bullet in self.bullets[:]:
            # Check bullet-building collision
            if bullet.update(self.buildings):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            # Check bullet-NPC collision
            for npc in self.npcs:
                if bullet.rect.colliderect(npc.rect) and npc.alive:
                    npc.alive = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
        
        # Check car-NPC collisions (if player is driving)
        if self.player.in_car:
            for npc in self.npcs:
                if self.player.car.rect.colliderect(npc.rect) and npc.alive:
                    npc.alive = False
        
        # Remove bullets that are too far
        self.bullets = [bullet for bullet in self.bullets 
                       if abs(bullet.rect.x - self.player.rect.x) < 1000 and 
                          abs(bullet.rect.y - self.player.rect.y) < 1000]
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        if self.player.in_car:
                            self.player.exit_car()
                        else:
                            self.player.try_enter_car(self.cars)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_shooting(pygame.mouse.get_pos())
            
            # Get pressed keys
            keys = pygame.key.get_pressed()
            
            # Update game objects with building collision checking
            self.player.update(keys, self.buildings)
            
            for npc in self.npcs:
                npc.update(self.buildings)
            
            self.check_collisions()
            self.update_camera()
            
            # Draw everything
            screen.fill(BLACK)
            
            # Draw grid for streets
            for x in range(-100, 2000, 100):
                start_pos = (x - self.camera_offset[0], 0)
                end_pos = (x - self.camera_offset[0], HEIGHT)
                if -50 < start_pos[0] < WIDTH + 50:
                    pygame.draw.line(screen, DARK_GRAY, start_pos, end_pos, 2)
            
            for y in range(-100, 1500, 100):
                start_pos = (0, y - self.camera_offset[1])
                end_pos = (WIDTH, y - self.camera_offset[1])
                if -50 < start_pos[1] < HEIGHT + 50:
                    pygame.draw.line(screen, DARK_GRAY, start_pos, end_pos, 2)
            
            # Draw game objects
            for building in self.buildings:
                building.draw(screen, self.camera_offset)
            
            for car in self.cars:
                car.draw(screen, self.camera_offset)
            
            for npc in self.npcs:
                npc.draw(screen, self.camera_offset)
            
            for bullet in self.bullets:
                bullet.draw(screen, self.camera_offset)
            
            self.player.draw(screen, self.camera_offset)
            
            # Draw UI
            font = pygame.font.Font(None, 36)
            instructions = [
                "WASD: Move/Drive",
                "E: Enter/Exit Car",
                "Mouse: Shoot",
                f"In Car: {'Yes' if self.player.in_car else 'No'}"
            ]
            
            for i, instruction in enumerate(instructions):
                text = font.render(instruction, True, WHITE)
                screen.blit(text, (10, 10 + i * 30))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()
