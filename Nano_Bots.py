import pygame, sys, random, math, colorsys, os
import asyncio


# Initialize pygame
pygame.init()

# Constants
info = pygame.display.Info()
DISPLAY_WIDTH = info.current_w
DISPLAY_HEIGHT = info.current_h

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

COLORS = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'grey': (128, 128, 128),
    'blue': (0, 0, 255),
    'dark blue' : (0, 0, 128),
    'cyan': (0, 255, 255),
    'green': (0, 255, 0),
    'dark green': (0, 100, 0),
    'lime': (173, 255, 47),
    'red': (255, 0, 0),
    'dark red': (100, 0, 0),
    'orange': (255, 128, 0),
    'brown': (165, 42, 42),
    'yellow': (255, 255, 0),
    'gold': (255, 215, 0),
    'pink': (255, 105, 180),
    'purple': (128, 0, 128),
    'indigo': (75, 0, 130),
    'magenta': (255, 0, 255),
}

# Define the initial high scores
initial_high_scores = {
    "chain gun": 0,
    "grape shot": 0,
    "laser": 0,
    "blaster": 0,
    "missile": 0,
    "grenade": 0,
    "cannon": 0
}

# Create the text file only if it doesn't exist
if not os.path.exists('high_scores.txt'):
    with open('high_scores.txt', 'w') as file:
        for weapon, score in initial_high_scores.items():
            file.write(f'{weapon}:{score}\n')

# Load font
font = pygame.font.Font('quantum.ttf', 24)
font_big = pygame.font.Font('quantum.ttf', 36)

# Set up the display
display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("NanoBots")

# Set up the clock and FPS
clock = pygame.time.Clock() 
FPS = 60

class Player:
    def __init__(self, x, y, radius, speed):
        self.position = pygame.math.Vector2(x, y)

        self.radius = radius
        self.speed = speed
        self.lives = 2
        self.circle_color = COLORS['white']
        self.line_color = COLORS['white']
        self.current_weapon = 'chain gun'
        self.ammo = 200
        self.max_ammo = 200
        self.reload_time = 0.8
        self.shot_delay = 0.0
        self.last_shot_time = 0
        self.num_projectiles = 1
        self.spread_angle = 0
        self.projectile_velocity = 10
        self.turret_angle = 0
        self.laser_length = 350
        self.laser_active = False
        self.laser_damage = 100
        self.initial_hue = 0.6  
        self.hue_shift_speed = 0.005 
        self.current_hue_offset = 0
        self.max_laser_ammo = 4  
        self.laser_ammo = self.max_laser_ammo
        self.laser_ammo_regen_time = 3  
        self.laser_usage_rate = 1.5  
        self.laser_regen_rate = 1 
        self.laser_depleted = False
        self.depletion_time = 0
        

    def switch_weapon(self, weapon_type):
        self.current_weapon = weapon_type
        if weapon_type == 'chain gun':
            self.ammo = 200
            self.max_ammo = 200
            self.reload_time = 1.2
            self.shot_delay = 0.0  
            
        elif weapon_type == 'grape shot':
            self.ammo = 12
            self.max_ammo = 12
            self.reload_time = 2.0
            self.shot_delay = 0.2  
            self.num_projectiles = 6 
            self.projectile_velocity = 12
            self.spread_angle = 15
            #self.projectile_velocity = 12
        elif weapon_type == 'laser':
            self.ammo = 50
            self.max_ammo = 50
            self.reload_time = 2.0
            self.shot_delay = 0.1
            self.num_projectiles = 1 
        elif weapon_type == 'missile':
            self.ammo = 20
            self.max_ammo = 20
            self.reload_time = 3.0
            self.shot_delay = 0.1
            self.num_projectiles = 1 
            self.projectile_damage = 20
        elif weapon_type == 'grenade':
            self.ammo = 15
            self.max_ammo = 15
            self.reload_time = 3.0
            self.shot_delay = 0.1
            self.num_projectiles = 1 
        elif weapon_type == 'cannon':
            self.ammo = 1
            self.max_ammo = 1
            self.reload_time = 1.5
            self.shot_delay = 0.0
            self.num_projectiles = 1
            self.projectile_damage = 120  # Set projectile damage 
        elif weapon_type == 'blaster':
            self.ammo = 20
            self.max_ammo = 20
            self.reload_time = 1.0
            self.shot_delay = 0.1
            #self.projectile_velocity = 12
            #self.projectile_damage = 100
        elif weapon_type == 'firethrower':
            self.ammo = 50
            self.max_ammo = 50
            self.reload_time = 2.0
            self.shot_delay = 0.1
            self.projectile_velocity = 5
            self.projectile_damage = 10


    def fire_chain_gun(self, mouse_x, mouse_y, projectiles):
        # Calculate the direction from the player to the mouse position
        direction = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y).normalize()
        
        # Calculate the positions for the two projectiles
        offset = direction.rotate(90) * 2  # 4 pixels apart, so 2 pixel offset on each side
        projectile1 = Projectile(self.position.x + offset.x, self.position.y + offset.y, mouse_x, mouse_y, self.current_weapon)
        projectile2 = Projectile(self.position.x - offset.x, self.position.y - offset.y, mouse_x, mouse_y, self.current_weapon)
        projectiles.add(projectile1, projectile2)
        self.ammo -= 2  # Decrement ammo by 2

    def fire_grape_shot(self, mouse_x, mouse_y, projectiles):
        base_direction = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y).normalize()
        base_angle = base_direction.angle_to(pygame.math.Vector2(1, 0))

        for i in range(self.num_projectiles):
            angle_offset = -self.spread_angle / 2 + i * (self.spread_angle / (self.num_projectiles - 1))
            projectile_direction = base_direction.rotate(angle_offset).normalize()

            projectile = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, self.current_weapon)
            projectile.velocity = projectile_direction * self.projectile_velocity
            projectile.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            projectiles.add(projectile)

        self.ammo -= 1  # Decrement ammo by 1

    

    def fire_laser(self, mouse_x, mouse_y):
        if self.laser_ammo > 0:
            self.laser_active = True
            self.laser_direction = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y).normalize()

    def stop_laser(self):
        self.laser_active = False

    def fire_missile(self, mouse_x, mouse_y, projectiles):
    # Create the missile projectile
        missile = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, 'missile', self.turret_angle)
        missile.radius = 8  # Set the length of the missile line
        projectiles.add(missile)
        self.ammo -= 1  # Decrement ammo by 1

    def fire_grenade(self, mouse_x, mouse_y, projectiles):
        # Create the grenade projectile
        grenade = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, 'grenade')
        grenade.radius = 3  # Set the size of the grenade projectile
        projectiles.add(grenade)
        self.ammo -= 1  # Decrement ammo by 1

    def fire_cannon(self, mouse_x, mouse_y, projectiles):
        # Create the cannonball projectile with persist_hits=True
        cannonball = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, 'cannon', persist_hits=True)
        cannonball.projectile_damage = self.projectile_damage  # Set the projectile damage
        cannonball.radius = 4  # Set the size of the cannonball projectile
        projectiles.add(cannonball)
        self.ammo -= 1  # Decrement ammo by 1

    def fire_blaster(self, mouse_x, mouse_y, projectiles):
        # Create the blaster projectile with the turret angle
        blaster_projectile = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, 'blaster')
        blaster_projectile.angle = self.turret_angle  # Set the angle
        projectiles.add(blaster_projectile)
        self.ammo -= 1  # Decrement ammo by 1
    
    def fire_firethrower(self, mouse_x, mouse_y, projectiles):
        # Create the firethrower projectile
        firethrower_projectile = Projectile(self.position.x, self.position.y, mouse_x, mouse_y, 'firethrower')
        projectiles.add(firethrower_projectile)
        self.ammo -= 1  # Decrement ammo by 1
        
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.position.y - self.radius - self.speed > 0:
            self.position.y -= self.speed
        if keys[pygame.K_s] and self.position.y + self.radius + self.speed < DISPLAY_HEIGHT:
            self.position.y += self.speed
        if keys[pygame.K_a] and self.position.x - self.radius - self.speed > 0:
            self.position.x -= self.speed
        if keys[pygame.K_d] and self.position.x + self.radius + self.speed < DISPLAY_WIDTH:
            self.position.x += self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.circle_color, (int(self.position.x), int(self.position.y)), self.radius, 3)
        self.draw_turret(surface)

    def draw_turret(self, surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y)
        
        if direction.length() != 0:  # Check if direction length is not zero
            direction = direction.normalize()
            self.turret_angle = direction.angle_to(pygame.math.Vector2(1, 0))

        if self.current_weapon == 'chain gun':
            offset = direction.rotate(90) * 2  
            end_pos1 = self.position + direction * 4 
            end_pos2 = self.position + direction * 4 
            end_pos3 = self.position + direction * 15 - direction * 2  
            end_pos4 = self.position + direction * 15 - direction * 2  

            pygame.draw.line(surface, self.line_color, self.position + offset, end_pos1 + offset, 3)  
            pygame.draw.line(surface, self.line_color, self.position - offset, end_pos2 - offset, 3)  
            pygame.draw.line(surface, self.line_color, self.position + offset - direction * 2, end_pos3 + offset, 2)  
            pygame.draw.line(surface, self.line_color, self.position - offset - direction * 2, end_pos4 - offset, 2)  

        else:
            end_pos = self.position + direction * 12  
            pygame.draw.line(surface, self.line_color, self.position, end_pos, 3)

            if self.current_weapon in ['blaster', 'laser']:
                draw_weapon_shape_1(surface, end_pos, direction, 'laser', 4, 0, 0)
            elif self.current_weapon in ['missile', 'grenade']:
                draw_weapon_shape_1(surface, end_pos, direction, self.current_weapon, 3, 3, 4)  
            elif self.current_weapon == 'cannon':
                draw_weapon_shape_2(surface, end_pos, direction, self.current_weapon, 11, 4, 0.75)  
            elif self.current_weapon == 'grape shot':
                draw_weapon_shape_3(surface, end_pos, direction, self.current_weapon, 2, 6, 10, 0.001, 2)  


    def draw_laser(self, surface):
        if self.laser_active and self.current_weapon == 'laser':
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.position.x, mouse_y - self.position.y).normalize()
            laser_end = self.position + direction * self.laser_length
            closest_distance = self.laser_length
            for bot in bots:
                if line_intersects_circle(self.position, laser_end, bot.position, bot.size):
                    distance = self.position.distance_to(bot.position) - bot.size
                    if distance < closest_distance:
                        closest_distance = distance
            adjusted_laser_end = self.position + direction * closest_distance
            
            # Draw laser with dynamic rainbow colors
            for i in range(int(closest_distance)):
                hue = (self.initial_hue + (self.current_hue_offset + i * self.hue_shift_speed)) % 1
                color = tuple(int(j * 255) for j in colorsys.hsv_to_rgb(hue, 1, 1))
                segment_start = self.position + direction * i
                segment_end = self.position + direction * (i + 1)
                pygame.draw.line(surface, color, segment_start, segment_end, 3)
            
            # Update hue offset for dynamic change
            self.current_hue_offset = (self.current_hue_offset + self.hue_shift_speed) % 1

    def update_laser_ammo(self):
        current_time = pygame.time.get_ticks()

        if self.laser_active and self.current_weapon == 'laser':
            self.laser_ammo -= self.laser_usage_rate * (clock.get_time() / 1000)
            if self.laser_ammo <= 0:
                self.laser_ammo = 0
                self.laser_depleted = True
                self.depletion_time = current_time
                self.stop_laser()
        else:
            if self.laser_depleted:
                if current_time - self.depletion_time >= 1000:
                    self.laser_ammo += self.laser_regen_rate * (clock.get_time() / 1000)
                    if self.laser_ammo >= self.max_laser_ammo:
                        self.laser_ammo = self.max_laser_ammo
                        self.laser_depleted = False
            else:
                self.laser_ammo += self.laser_regen_rate * (clock.get_time() / 1000)
                if self.laser_ammo >= self.max_laser_ammo:
                    self.laser_ammo = self.max_laser_ammo

    def reset_position(self):
        self.position = pygame.math.Vector2(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2)

    def update(self, enemies, bots):
        self.position += self.velocity
        self.rect.center = self.position
        self.update_color()
            
        if not (0 <= self.position.x <= DISPLAY_WIDTH and 0 <= self.position.y <= DISPLAY_HEIGHT):
            self.kill()

# def update_projectile(projectile):
#         distance_traveled = projectile.position.distance_to(pygame.math.Vector2(projectile.start_x, projectile.start_y))
#         if distance_traveled > 100:
#             projectile.projectile_damage = 0
#         elif distance_traveled > 40:
#             projectile.projectile_damage /= 4
#         elif distance_traveled > 20:
#             projectile.projectile_damage /= 2

def generate_fragments(grenade):
    fragments = []
    for i in range(20):  # 20 fragments
        angle = i * (360 / 20)  # Divide the circle by 20
        direction = pygame.math.Vector2(1, 0).rotate(angle).normalize()
        fragment = Projectile(grenade.position.x, grenade.position.y, grenade.position.x + direction.x, grenade.position.y + direction.y, 'fragment')
        fragment.radius = 1  # Set the size of the fragments
        fragment.projectile_damage = 0  # Set the damage of the fragments to 0
        fragment.velocity = direction * 6  # Set the velocity of the fragments
        fragment.is_visual = True  # Custom attribute to mark fragments as visual-only
        fragments.append(fragment)
    return fragments

def line_intersects_circle(start, end, circle_center, circle_radius):
    d = end - start
    f = start - circle_center
    a = d.dot(d)
    b = 2 * f.dot(d)
    c = f.dot(f) - circle_radius ** 2
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return False
    discriminant = math.sqrt(discriminant)
    t1 = (-b - discriminant) / (2 * a)
    t2 = (-b + discriminant) / (2 * a)
    if (0 <= t1 <= 1) or (0 <= t2 <= 1):
        return True
    return False

def draw_laser_ammo_bar(surface, player):
    bar_width = 700  
    bar_height = 10
    bar_x = DISPLAY_WIDTH // 2 - 350  
    bar_y = 50  # Place at the top of the screen

    # Draw the white hollow rectangle
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)

    # Calculate the red line width based on the player's laser ammo percentage
    ammo_percentage = player.laser_ammo / player.max_laser_ammo
    red_line_width = int(bar_width * ammo_percentage)

    # Draw the red line centered in the rectangle
    pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y + 1, red_line_width, bar_height - 2))

def draw_hollow_circle(surface, position, radius, color=(0, 0, 255)):
    pygame.draw.circle(surface, color, position, radius)


def create_explosion(x, y, explosions, weapon_type=None):
    initial_radius = 5 if weapon_type != 'missile' else 10
    max_radius = 10 if weapon_type != 'missile' else 20
    explosion = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)  # Create surface based on max_radius
    pygame.draw.circle(explosion, (255, 0, 0), (max_radius, max_radius), max_radius)  # Draw the initial filled circle
    explosion_rect = explosion.get_rect(center=(x, y))
    start_time = pygame.time.get_ticks()
    initial_duration = 50  # Time in milliseconds for the initial filled circle
    expansion_duration = 150  # Time in milliseconds for the hollow circle to expand
    hold_duration = 50  # Time in milliseconds to hold the hollow circle at max radius
    initial_hue = random.random()  # Random initial hue value between 0 and 1

    # Pre-calculate a set of colors for the rainbow effect
    num_colors = 100
    colors = [tuple(int(i * 255) for i in colorsys.hsv_to_rgb((initial_hue + (j / num_colors)) % 1, 1, 1)) for j in range(num_colors)]

    def update_explosion():
        nonlocal start_time, explosion_rect, initial_hue
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        explosion.fill((0, 0, 0, 0))  # Clear the image

        if elapsed_time < initial_duration:
            # First phase: display the filled circle for the initial duration
            radius = initial_radius
            pygame.draw.circle(explosion, (255, 0, 0), (max_radius, max_radius), initial_radius)  # Redraw the filled circle
        elif elapsed_time < initial_duration + expansion_duration:
            # Second phase: expand the hollow circle
            progress = (elapsed_time - initial_duration) / expansion_duration
            radius = initial_radius + (max_radius - initial_radius) * progress  # Expand from initial_radius to max_radius
            color_index = int(progress * (num_colors - 1))  # Get the color index based on progress
            color = colors[color_index]
            pygame.draw.circle(explosion, color, (max_radius, max_radius), int(radius), 2)  # Draw the hollow circle with a 2-pixel border
        elif elapsed_time < initial_duration + expansion_duration + hold_duration:
            # Third phase: hold the hollow circle at max radius
            radius = max_radius
            color = colors[-1]  # Use the last color in the list
            pygame.draw.circle(explosion, color, (max_radius, max_radius), radius, 2)  # Draw the hollow circle with a 2-pixel border
        else:
            # End of explosion: remove the explosion
            explosions.remove((explosion, explosion_rect, update_explosion))
            return

        # Update the explosion's rect to keep it centered
        explosion_rect.size = (max_radius * 2, max_radius * 2)
        explosion_rect.center = (x, y)

    explosions.append((explosion, explosion_rect, update_explosion))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, weapon_type, angle = 0, persist_hits=False):
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.target_x = target_x
        self.target_y = target_y
        self.weapon_type = weapon_type
        self.radius = 1  # Default radius, can be changed based on weapon type
        self.color = (255, 255, 255)  # Default color, can be changed based on weapon type
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.color_index = 63
        self.creation_time = pygame.time.get_ticks()
        self.original_update = self.update
        # if self.weapon_type == 'firework':
        #     self.update = self.custom_update
        self.persist_hits = persist_hits
        self.active = True
        self.position = pygame.math.Vector2(x, y)
        self.initial_position = self.position.copy()  
        # self.projectile_damage = 1
        # self.initial_damage = self.projectile_damage

        # Initialize weapon-specific attributes
        self.initialize_weapon()

        # Update image and rect based on the new radius
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))

        # Failsafe for projectile_velocity
        if not hasattr(self, 'projectile_velocity'):
            self.projectile_velocity = 10  # Default velocity

        # Calculate velocity
        direction = pygame.math.Vector2(target_x - x, target_y - y)
        self.velocity = direction.normalize() * self.projectile_velocity if direction.length() != 0 else pygame.math.Vector2(1, 0) * self.projectile_velocity

        # Initialize color transition
        self.hue = 0  # Start with red

        # Initialize timer for grenade explosion
        self.creation_time = pygame.time.get_ticks()


    def custom_update(self):
        if pygame.time.get_ticks() - self.creation_time > 1000:
            self.kill()
        else:
            self.original_update()


    def hsv_to_rgb(self, h, s, v):
        return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

    def update_color(self):
        self.color = rainbow_colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(rainbow_colors)  # Cycle through the colors
        self.image.fill((0, 0, 0, 0))  # Clear the image
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

    def initialize_weapon(self):
        if self.weapon_type == 'chain gun':
            self.chain_gun()
        elif self.weapon_type == 'grape shot':  
            self.grape_shot()
        elif self.weapon_type == 'laser':
            self.laser()
        elif self.weapon_type == 'missile':
            self.missile()
        elif self.weapon_type == 'grenade':
            self.grenade()
        elif self.weapon_type == 'cannon':
            self.cannon()
        elif self.weapon_type == 'blaster':  
            self.blaster()
        #elif self.weapon_type == 'firethrower':  
            #self.firethrower()

    def chain_gun(self):

        self.projectile_damage = 1
 
        self.projectile_velocity = 10
        self.hue = 0  # Initialize hue for rainbow effect
        self.color_index =63

    def blaster(self):
       
        self.projectile_damage = 10
        self.color_index = 70
        self.projectile_velocity = 14
        self.color = (255, 0, 0)  # Set color for blaster projectiles
        self.radius = 2.5
        self.angle = 0
        
    def grape_shot(self):

        self.projectile_damage = 3
        
        self.color_index = 75
        #self.projectile_velocity = 20
        
        
    def laser(self):
        self.max_ammo = 50
        self.ammo = 50
        self.projectile_damage = 10
        self.reload_time = 2.0
        self.shot_delay = 0.1
        self.projectile_velocity = 15
        self.color = (0, 255, 0)  # Set color for laser projectiles

    def missile(self):

        self.projectile_damage = 15
        self.color_index = 75
        
        self.projectile_velocity = 12
        self.color = (0, 0, 255)  # Set color for missile projectiles
        self.radius = 8  # Set the length of the missile line

    def grenade(self):

        self.projectile_damage = 20
        self.color_index = 31
        self.projectile_velocity = 8
        self.color = (255, 165, 0)  # Set color for grenade projectiles
        self.radius = 3

    def cannon(self):
        #self.max_ammo = 5
        #self.ammo = 5
        #self.projectile_damage = 500
        self.reload_time = 5.0
        self.shot_delay = 1.5
        self.projectile_velocity = 13
        self.color = (128, 0, 128)  # Set color for cannon projectiles
        self.radius = 5  
    def firethrower(self):
        self.max_ammo = 50
        self.ammo = 50
        self.projectile_damage = 10
        self.reload_time = 2.0
        self.shot_delay = 0.1
        self.projectile_velocity = 5  # Slightly slower than laser
        self.color = (255, 165, 0)  # Set color for firethrower projectiles (orange)

    #cannon logic 
    def move(self):
        # update projectile position based on velocity
        self.position += self.velocity
        self.rect.center = self.position
        
    def check_collision(self, bots):
        if self.active:
            hit_bots = []
            for bot in bots:
                if self.collides_with(bot):
                    hit_bots.append(bot)
            if hit_bots:
                self.handle_hits(hit_bots)
                if not self.persist_hits:
                    self.active = False

    def collides_with(self, bot):
        return pygame.sprite.collide_circle(self, bot)  # Adjust collision detection as needed

    def handle_hits(self, bots):
        hit_bots = []
        for bot in bots:
            if self.collides_with(bot):
                hit_bots.append(bot)
        for bot in hit_bots:
            self.apply_damage(bot)

    def apply_damage(self, bot):
        global score
        if self.weapon_type == 'cannon':
            if self.projectile_damage > bot.health:
                self.projectile_damage -= bot.health
                new_bots = bot.explode(round_number)  # Handle bot explosion
                bots.add(new_bots)
                if bot.size > 10:
                    score += 1
                bots.remove(bot)
            else:
                bot.health -= self.projectile_damage
                create_explosion(self.position.x, self.position.y, explosions)
                self.projectile_damage = 0
                self.kill()  # Remove projectile when its damage is zero
                
    def update(self):
        self.position += self.velocity
        self.rect.center = self.position
        self.update_color()  # Update the color

        # Remove projectiles that go off-screen
        if not (0 <= self.position.x <= DISPLAY_WIDTH and 0 <= self.position.y <= DISPLAY_HEIGHT):
            self.kill()

        # Handle blaster projectiles as lines
        if self.weapon_type == 'blaster':
            self.image = pygame.Surface((self.radius * 10, 2), pygame.SRCALPHA)
            pygame.draw.line(self.image, self.color, (0, 1), (self.radius * 10, 2), 8)  # Draw the blaster line
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(center=self.position)

        # Rotate the missile to face the turret direction and draw the triangle
        if self.weapon_type == 'missile':
            self.image = pygame.Surface((self.radius * 2, self.radius), pygame.SRCALPHA)
            pygame.draw.line(self.image, self.color, (self.radius, self.radius // 2), (self.radius * 2, self.radius // 2), 2)

            # Calculate the points for the equilateral triangle
            half_base = 2.5  # Half the length of the base of the triangle
            height = half_base * (3 ** 0.5)  # Height of the triangle
            tip = (self.radius * 2, self.radius // 2)  # Tip of the triangle at the end of the missile
            left_base = (self.radius * 2 - half_base, self.radius // 2 - height // 2)
            right_base = (self.radius * 2 - half_base, self.radius // 2 + height // 2)

            # Draw the triangle
            pygame.draw.polygon(self.image, self.color, [tip, left_base, right_base])

            # Rotate the image
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(center=self.position)


        if not (0 <= self.position.x <= DISPLAY_WIDTH and 0 <= self.position.y <= DISPLAY_HEIGHT):
            self.kill()

def reload():
    global reloading, reload_start_time, pause_unpause
    if not is_paused and not pause_unpause:  # Check if the game is not paused or in pause_unpause
        reloading = True
        reload_start_time = pygame.time.get_ticks()

def handle_ammo():
    global reloading, reload_start_time

    if reloading:
        elapsed_time = (pygame.time.get_ticks() - reload_start_time) / 1000
        if elapsed_time >= player.reload_time:
            player.ammo = player.max_ammo
            reloading = False
            
    if player.ammo <= 0 and not reloading:
        reload()
        
class Bot(pygame.sprite.Sprite):
    def __init__(self, x, y, size, is_new=False):
        super().__init__()
        self.position = pygame.math.Vector2(x, y)
        self.size = size
        self.radius = size
        self.speed = max(0.5, 6 - size // 20)
        self.health = size
        self.max_health = self.health
        self.is_new = is_new
        self.exploded = False  # Add exploded flag
        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, WHITE, (size, size), size, 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.creation_time = pygame.time.get_ticks()

        if self.size < 10:
            self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.speed

    def update(self, player_x, player_y):
        if self.health <= 0:
            self.kill()
            return

        if self.size == 1 and pygame.time.get_ticks() - self.creation_time > 4000:
            self.kill()

        if self.size < 10:
            self.position += self.velocity
        else:
            direction = pygame.math.Vector2(player_x - self.position.x, player_y - self.position.y).normalize()
            self.position += direction * self.speed
        self.rect.center = self.position

    def explode(self, round_number):
        if self.exploded:  # Check if the bot has already exploded
            return []

        self.exploded = True  # Set the exploded flag to True
        new_bots = []
        if self.size > 99:  # Condition for the boss
            new_size_large = 9
            new_size_small = 1
            new_bots.extend(make_small_bots(self.position.x, self.position.y, self.radius, 50, new_size_large, 5))
            new_bots.extend(make_small_bots(self.position.x, self.position.y, self.radius, 100, new_size_small, 4))
        elif self.size > 10:  # Only explode if the bot is large enough
            new_size = self.size // 3
            new_bots.extend(make_small_bots(self.position.x, self.position.y, self.radius, 3, new_size, 5))
            new_bots.extend(make_small_bots(self.position.x, self.position.y, self.radius, 6, 1, 4))
        elif self.size <= 10:  # If the bot is smaller than 10, create small 1-pixel bots
            num_small_bots = max(1, self.size // 2)  # Ensure num_small_bots is at least 1
            new_bots.extend(make_small_bots(self.position.x, self.position.y, self.radius, num_small_bots, 1, 4))
        self.kill()  # Ensure the bot is removed when it explodes
        return new_bots

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.position.x), int(self.position.y)), self.size, 3)

def make_small_bots(x, y, radius, num_bots, size, speed):
    if num_bots <= 0:
        return []
    
    angle_increment = 2 * math.pi / num_bots
    small_bots = [
        Bot(
            x + radius * math.cos(i * angle_increment),
            y + radius * math.sin(i * angle_increment),
            size,
            is_new=True
        )
        for i in range(num_bots)
    ]
    for bot in small_bots:
        bot.speed = max(0.1, speed - size // 20)
        bot.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * bot.speed
    return small_bots


def hsv_to_rgb(h, s, v):
    return tuple(int(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def spawn_bot():
    side = random.choice(['top', 'bottom', 'left', 'right'])
    size = random.randint(36, 80)
    offset = size + 5
    positions = {
        'top': (random.randint(0, DISPLAY_WIDTH), -offset),
        'bottom': (random.randint(0, DISPLAY_WIDTH), DISPLAY_HEIGHT + offset),
        'left': (-offset, random.randint(0, DISPLAY_HEIGHT)),
        'right': (DISPLAY_WIDTH + offset, random.randint(0, DISPLAY_HEIGHT))
    }
    x, y = positions[side]
    return Bot(x, y, size)

def draw_text(surface, text, font, color, pos, align="center"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = pos
    elif align == "left":
        text_rect.midleft = pos
    surface.blit(text_surface, text_rect)

# Update the handle_screens function to include the weapon selection box
def handle_screens():
    global game_started, ammo, pause_unpause

    if is_paused and not game_started:
        display.fill(BLACK)
        draw_text(display, "Nano-Bots", font, WHITE, (DISPLAY_WIDTH // 2, 50))

        # Draw the WASDF keys
        key_size = 50
        keys = ['A', 'S', 'D', 'F']
        key_positions = [(100, 200), (160, 200), (220, 200), (280, 200)]
        for key, pos in zip(keys, key_positions):
            pygame.draw.rect(display, WHITE, (*pos, key_size, key_size), 2)
            draw_text(display, key, font, WHITE, (pos[0] + key_size // 2, pos[1] + key_size // 2))

        # Draw the W key
        w_key_position = (140, 140)
        pygame.draw.rect(display, WHITE, (*w_key_position, key_size, key_size), 2)
        draw_text(display, 'W', font, WHITE, (w_key_position[0] + key_size // 2, w_key_position[1] + key_size // 2))

        # Draw instructions
        instructions = [
            ("W, A, S, D  to move", 160),
            ("F to reload", 220),
            ("Use the mouse to aim", 340),
            ("Left click to fire", 400),
            ('Press "space" to begin', 660)
            
        ]
        for text, y in instructions:
            draw_text(display, text, font, WHITE, (375, y), align="left")

        draw_text(display, 'Press "escape" to exit', font, WHITE, (375, 700) , align="left")

        # Draw the mouse representation
        mouse_rect = pygame.Rect(150, 300, 100, 140)
        pygame.draw.rect(display, WHITE, mouse_rect, 2)

        # Draw the mouse buttons
        button_width, button_height, button_margin = 40, 50, 8
        button1_rect = pygame.Rect(mouse_rect.x + button_margin, mouse_rect.y + button_margin, button_width, button_height)
        button2_rect = pygame.Rect(mouse_rect.right - button_margin - button_width, mouse_rect.y + button_margin, button_width, button_height)
        pygame.draw.rect(display, WHITE, button1_rect, 2)
        pygame.draw.rect(display, WHITE, button2_rect, 2)
        
        # Draw the player representation
        draw_player_representation(display)

        # Draw the weapon selection box
        draw_weapon_selection(display)

        #Draw color selection
        draw_color_selection(display)


    elif is_paused and game_started and player_lives >= 0:
        display.fill(BLACK)
        if pause_unpause:
            draw_text(display, 'PAUSED', font_big, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 200))
        else: 
            draw_text(display, 'YOU DIED', font_big, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 200))
            player.ammo = player.max_ammo
            reloading = False
        draw_text(display, f'Score: {score}', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 100))
        draw_text(display, f'Lives: {player_lives}', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 50))
        draw_text(display, f'Round: {round_number}', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
        draw_text(display, 'Press "space" key to continue', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 50))
        draw_text(display, 'Press "escape" key to quit at anytime', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 100))
        
        
    
    elif is_paused and player_lives < 0:
        display.fill(BLACK)

    
        if player_lives < 0 and final_weapon:
            if final_weapon == 'chain gun':
                draw_text(display, f'High Score (Chain Gun): {chain_gun_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'grape shot':
                draw_text(display, f'High Score (Grape Shot): {grape_shot_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'laser':
                draw_text(display, f'High Score (Laser): {laser_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'blaster':
                draw_text(display, f'High Score (Blaster): {blaster_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'missile':
                draw_text(display, f'High Score (Missile): {missile_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'grenade':
                draw_text(display, f'High Score (Grenade): {grenade_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))
            elif final_weapon == 'cannon':
                draw_text(display, f'High Score (Cannon): {cannon_high_score}', font, WHITE, (DISPLAY_WIDTH // 2, 100))

        draw_text(display, f'Final Score: {score}', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 50))

        # Draw the weapon selection box on the end screen
        #draw_text(display, "weapon:", font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 - 90))
        draw_weapon_selection(display)

        #Draw player Rpresentation
        draw_player_representation(display)

        #draw color selection
        draw_color_selection(display)

        draw_text(display, 'Would you like to play again?', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
        draw_text(display, 'Press "space" to play again', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 50))
        draw_text(display, 'Press "escape" to exit', font, WHITE, (DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2 + 100))
        
        # Add the "made by" text in the bottom right corner
        #draw_text(display, 'made by', font, WHITE, (DISPLAY_WIDTH - 100, DISPLAY_HEIGHT - 70), align="right")
        draw_text(display, 'made by Brandon Williams', font_big, WHITE, (DISPLAY_WIDTH //2, DISPLAY_HEIGHT - 40),)

        pygame.mouse.set_visible(True)

def draw_weapon_selection(surface):
    global current_weapon_index

    # Box properties
    box_width, box_height = 250, 50  # Set width to 250
    box_x = DISPLAY_WIDTH - 325  # Adjusted x position
    box_y = 200  # Adjusted y position

    # Draw the text above the box
    draw_text(surface, "weapon:", font, WHITE, (box_x + box_width // 2, 160))

    # Draw the box
    pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height), 2)

    # Draw the weapon name
    weapon_name = WEAPONS[current_weapon_index]
    draw_text(surface, weapon_name, font, WHITE, (box_x + box_width // 2, box_y + box_height // 2))

    # Button properties
    button_width, button_height = 30, 50
    left_button_x = box_x - button_width - 10
    right_button_x = box_x + box_width + 10
    button_y = box_y

    # Draw the left button
    pygame.draw.rect(surface, WHITE, (left_button_x, button_y, button_width, button_height), 2)
    draw_text(surface, '<', font, WHITE, (left_button_x + button_width // 2, button_y + button_height // 2))

    # Draw the right button
    pygame.draw.rect(surface, WHITE, (right_button_x, button_y, button_width, button_height), 2)
    draw_text(surface, '>', font, WHITE, (right_button_x + button_width // 2, button_y + button_height // 2))

def handle_weapon_selection(mouse_pos, mouse_click):
    global current_weapon_index, weapon_changed, selected_weapon

    if is_paused:  # Only allow changes when the game is paused
        # Box properties
        box_width, box_height = 250, 50
        box_x = DISPLAY_WIDTH - 325
        box_y = 200

        # Button properties
        button_width, button_height = 30, 50
        left_button_x = box_x - button_width - 10
        right_button_x = box_x + box_width + 10
        button_y = box_y

        # Check if left button is clicked
        if left_button_x < mouse_pos[0] < left_button_x + button_width and button_y < mouse_pos[1] < button_y + button_height:
            if mouse_click[0] and not weapon_changed:
                current_weapon_index = (current_weapon_index - 1) % len(WEAPONS)
                weapon_changed = True
                selected_weapon = WEAPONS[current_weapon_index]
                player.switch_weapon(selected_weapon)

        # Check if right button is clicked
        if right_button_x < mouse_pos[0] < right_button_x + button_width and button_y < mouse_pos[1] < button_y + button_height:
            if mouse_click[0] and not weapon_changed:
                current_weapon_index = (current_weapon_index + 1) % len(WEAPONS)
                weapon_changed = True
                selected_weapon = WEAPONS[current_weapon_index]
                player.switch_weapon(selected_weapon)

        # Reset the flag when the mouse button is released
        if not mouse_click[0]:
            weapon_changed = False

def draw_color_selection(surface):
    global current_color_index_1, current_color_index_2

    # Box properties
    box_width, box_height = 250, 50
    box_x = DISPLAY_WIDTH - 325
    box_y_1 = (DISPLAY_HEIGHT // 2) + 120
    box_y_2 = (DISPLAY_HEIGHT // 2) + 200

    # Draw the boxes
    pygame.draw.rect(surface, WHITE, (box_x, box_y_1, box_width, box_height), 2)
    pygame.draw.rect(surface, WHITE, (box_x, box_y_2, box_width, box_height), 2)

    # Draw the color names
    color_name_1 = list(COLORS.keys())[current_color_index_1]
    color_name_2 = list(COLORS.keys())[current_color_index_2]
    draw_text(surface, color_name_1, font, WHITE, (box_x + box_width // 2, box_y_1 + box_height // 2))
    draw_text(surface, color_name_2, font, WHITE, (box_x + box_width // 2, box_y_2 + box_height // 2))

    # Button properties
    button_width, button_height = 30, 50
    left_button_x = box_x - button_width - 10
    right_button_x = box_x + box_width + 10

    # Draw the left and right buttons for the first box
    pygame.draw.rect(surface, WHITE, (left_button_x, box_y_1, button_width, button_height), 2)
    pygame.draw.rect(surface, WHITE, (right_button_x, box_y_1, button_width, button_height), 2)
    draw_text(surface, '<', font, WHITE, (left_button_x + button_width // 2, box_y_1 + button_height // 2))
    draw_text(surface, '>', font, WHITE, (right_button_x + button_width // 2, box_y_1 + button_height // 2))

    # Draw the left and right buttons for the second box
    pygame.draw.rect(surface, WHITE, (left_button_x, box_y_2, button_width, button_height), 2)
    pygame.draw.rect(surface, WHITE, (right_button_x, box_y_2, button_width, button_height), 2)
    draw_text(surface, '<', font, WHITE, (left_button_x + button_width // 2, box_y_2 + button_height // 2))
    draw_text(surface, '>', font, WHITE, (right_button_x + button_width // 2, box_y_2 + button_height // 2))

def handle_color_selection(mouse_pos, mouse_click):
    global current_color_index_1, current_color_index_2, color_changed_1, color_changed_2

    if is_paused:  # Only allow changes when the game is paused
        # Box properties
        box_width, box_height = 250, 50
        box_x = DISPLAY_WIDTH - 325
        box_y_1 = (DISPLAY_HEIGHT // 2) + 120
        box_y_2 = (DISPLAY_HEIGHT // 2) + 200

        # Button properties
        button_width, button_height = 30, 50
        left_button_x = box_x - button_width - 10
        right_button_x = box_x + box_width + 10

        # Check if left button is clicked for the first box
        if left_button_x < mouse_pos[0] < left_button_x + button_width and box_y_1 < mouse_pos[1] < box_y_1 + button_height:
            if mouse_click[0] and not color_changed_1:
                current_color_index_1 = (current_color_index_1 - 1) % len(COLORS)
                color_changed_1 = True
                player.circle_color = list(COLORS.values())[current_color_index_1]

        # Check if right button is clicked for the first box
        if right_button_x < mouse_pos[0] < right_button_x + button_width and box_y_1 < mouse_pos[1] < box_y_1 + button_height:
            if mouse_click[0] and not color_changed_1:
                current_color_index_1 = (current_color_index_1 + 1) % len(COLORS)
                color_changed_1 = True
                player.circle_color = list(COLORS.values())[current_color_index_1]

        # Check if left button is clicked for the second box
        if left_button_x < mouse_pos[0] < left_button_x + button_width and box_y_2 < mouse_pos[1] < box_y_2 + button_height:
            if mouse_click[0] and not color_changed_2:
                current_color_index_2 = (current_color_index_2 - 1) % len(COLORS)
                color_changed_2 = True
                player.line_color = list(COLORS.values())[current_color_index_2]

        # Check if right button is clicked for the second box
        if right_button_x < mouse_pos[0] < right_button_x + button_width and box_y_2 < mouse_pos[1] < box_y_2 + button_height:
            if mouse_click[0] and not color_changed_2:
                current_color_index_2 = (current_color_index_2 + 1) % len(COLORS)
                color_changed_2 = True
                player.line_color = list(COLORS.values())[current_color_index_2]

        # Reset the flag when the mouse button is released
        if not mouse_click[0]:
            color_changed_1 = False
            color_changed_2 = False

def rotate_point(cx, cy, angle, p):
    s = math.sin(angle)
    c = math.cos(angle)
    xnew = p[0] * c - p[1] * s
    ynew = p[0] * s + p[1] * c
    return (cx + xnew, cy + ynew)

def draw_weapon_shape_1(surface, end_pos, direction, weapon_type, diamond_size, width, length):
    if weapon_type == 'laser':
        # diamond_size = 28
        diamond_points = [
            (0, -diamond_size // 2),
            (diamond_size, 0),
            (0, diamond_size // 2),
            (-diamond_size, 0)
        ]

        angle = math.atan2(direction.y, direction.x)
        rotated_points = [rotate_point(end_pos.x, end_pos.y, angle, p) for p in diamond_points]
        pygame.draw.polygon(surface, player.line_color, rotated_points)
    else:
        rectangle_points = [
            (-width / 2, -length / 2),  # Top-left
            (width / 2, -length / 2),  # Top-right
            (width / 2, length / 2 ),  # Bottom-right
            (-width / 2, length / 2 )  # Bottom-left
        ]

        angle = math.atan2(direction.y, direction.x)
        rotated_rectangle_points = [rotate_point(end_pos.x, end_pos.y, angle, p) for p in rectangle_points]
        pygame.draw.polygon(surface, player.line_color, rotated_rectangle_points)

def draw_weapon_shape_2(surface, end_pos, direction, weapon_type, width, length, barrel_length_coeffecient):
    # Calculate midpoint
    midpoint = end_pos - (direction * (length * barrel_length_coeffecient))   # adjustable 

    rectangle_points = [
        (-width / 2, -length / 2),  # Top-left
        (width / 2, -length / 2),  # Top-right
        (width / 2, length / 2),  # Bottom-right
        (-width / 2, length / 2)  # Bottom-left
    ]

    angle = math.atan2(direction.y, direction.x)
    rotated_rectangle_points = [rotate_point(midpoint.x, midpoint.y, angle, p) for p in rectangle_points]
    pygame.draw.polygon(surface, player.line_color, rotated_rectangle_points)

def draw_weapon_shape_3(surface, end_pos, direction, weapon_type, taper_base_width, taper_end_width, length, barrel_length_coeffecient, grape_shot_offset):
    
    midpoint = end_pos - (direction * (length * barrel_length_coeffecient))

    rectangle_points = [
        (-taper_base_width / 2, -length / 2),  # Top-left
        (taper_base_width / 2, -length / 2),  # Top-right
        (taper_end_width / 2, length / 2 - grape_shot_offset),  # Bottom-right (wider end)
        (-taper_end_width / 2, length / 2 - grape_shot_offset)  # Bottom-left (wider end)
    ]

    length

    angle = math.atan2(direction.y, direction.x) - math.pi / 2  # Adjusted for -90 degrees rotation
    rotated_rectangle_points = [rotate_point(midpoint.x, midpoint.y, angle, p) for p in rectangle_points]
    pygame.draw.polygon(surface, player.line_color, rotated_rectangle_points)
                        
def draw_player_representation(surface):
    circle_pos = pygame.math.Vector2(DISPLAY_WIDTH - 200, (DISPLAY_HEIGHT // 2) + 20)
    circle_radius = 80
    circle_border = 24

    pygame.draw.circle(surface, player.circle_color, circle_pos, circle_radius, circle_border)

    mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
    direction = (mouse_pos - circle_pos).normalize()

    if player.current_weapon == 'chain gun':
        offset = direction.rotate(90) * 16
        end_pos1 = circle_pos + direction * 32
        end_pos2 = circle_pos + direction * 32

        end_pos3 = circle_pos + direction * 120 - direction * 16  
        end_pos4 = circle_pos + direction * 120 - direction * 16 

        pygame.draw.line(surface, player.line_color, circle_pos + offset, end_pos1 + offset, 24)
        pygame.draw.line(surface, player.line_color, circle_pos - offset, end_pos2 - offset, 24)

        pygame.draw.line(surface, player.line_color, circle_pos + offset - direction * 16, end_pos3 + offset, 16)
        pygame.draw.line(surface, player.line_color, circle_pos - offset - direction * 16, end_pos4 - offset, 16)
    
    else:
        end_pos = circle_pos + direction * 96
        pygame.draw.line(surface, player.line_color, circle_pos, end_pos, circle_border)

        if player.current_weapon in ['blaster', 'laser']:
            draw_weapon_shape_1(surface, end_pos, direction, 'laser', 32, 0, 0)
        elif player.current_weapon in ['missile', 'grenade']:
            draw_weapon_shape_1(surface, end_pos, direction, player.current_weapon, 24, 24, 32)
        elif player.current_weapon in ['cannon']:
            draw_weapon_shape_2(surface, end_pos, direction, player.current_weapon, 88, 32, 0.75)
        elif player.current_weapon == 'grape shot':
            draw_weapon_shape_3(surface, end_pos, direction, player.current_weapon, 16, 32, 80, 0.001, 16)

def handle_rounds():
    global round_display_pos, round_number, enemies_to_spawn, enemies_spawned, round_displayed, round_end_timer, player_lives
    #print("Handling rounds")  # Debugging print

    # Check if all initial enemies are defeated and start a new round
    if not bots and enemies_spawned == enemies_to_spawn:
        if round_end_timer == 0:
            round_end_timer = pygame.time.get_ticks()
            round_number += 1
            round_displayed = False
            round_display_pos = -50
            if round_number % 3 == 1 and round_number > 1:
                player_lives += 1
        elif pygame.time.get_ticks() - round_end_timer >= 2500:
            enemies_to_spawn = round_number + 4 if round_number % 3 != 0 else 1  # Reset enemies to spawn
            enemies_spawned = 0  # Reset number of enemies spawned
            round_end_timer = 0

    # Display round number once at the beginning of the round
    if not round_displayed and not is_paused:
        round_display_pos += 5
        draw_text(display, f'Round {round_number}', font, WHITE, (DISPLAY_WIDTH // 2, round_display_pos))
        if round_display_pos > DISPLAY_HEIGHT + 50:
            round_displayed = True
            round_display_pos = -50

    # Spawn the boss on every 3rd round
    if round_number % 3 == 0 and enemies_spawned == 0:
        bots.add(spawn_boss())
        enemies_spawned += 1
    
    # Check if the boss's health is zero and trigger explosion
    for bot in bots:
        if bot.size > 99 and bot.health <= 0:  # Ensure it's the boss
            new_bots = bot.explode(round_number)
            bots.add(new_bots)
            bots.remove(bot)

def restart_round():
    global player_lives, round_number, projectiles, bots, enemies_to_spawn, enemies_spawned, round_displayed, round_end_timer, is_paused, game_started, ammo, reloading
    # round_number = 1
    projectiles.empty()
    bots.empty()
    # enemies_to_spawn = 5
    enemies_spawned = 0
    round_displayed = False
    round_end_timer = 0
    is_paused = False
    player.ammo = player.max_ammo 
    player.laser_ammo = player.max_laser_ammo
    reloading = False

def reset_game():
    global player_lives, score, round_number, projectiles, bots, enemies_to_spawn, enemies_spawned, round_displayed, round_end_timer, is_paused, game_started, ammo, reloading 
    player_lives = 2
    score = 0
    round_number = 1
    projectiles.empty()
    bots.empty()
    enemies_to_spawn = 5
    enemies_spawned = 0
    round_displayed = False
    round_end_timer = 0
    is_paused = False
    player.ammo = player.max_ammo  
    player.laser_ammo = player.max_laser_ammo
    reloading = False
    game_ended = False  # Reset the game ended flag
    active = False  # Reset active flag
    final_weapon = None  # Reset the final weapon used

# Function to update small bots surface
def update_small_bots_surface():
    small_bots_surface.fill((0, 0, 0, 0))  # Clear the surface
    [pygame.draw.circle(small_bots_surface, WHITE, (int(bot.position.x), int(bot.position.y)), bot.size, 1) for bot in bots if bot.size == 1]

# Function to handle batch drawing
def batch_draw():
    projectiles.draw(display)
    bots.draw(display)
    display.blit(small_bots_surface, (0, 0))  # Draw the small bots surface

# Function to handle batch updates
def batch_update():
    projectiles.update()
    bots.update(player.position.x, player.position.y)
    update_small_bots_surface()  # Update the small bots surface

# Function to handle batch collision detection
def batch_collision_detection():
    global player_lives, is_paused, score, round_end_timer, round_number, round_displayed, round_display_pos

    # Group projectiles by type for efficient processing
    missile_projectiles = [p for p in projectiles if p.weapon_type == 'missile']
    cannon_projectiles = [p for p in projectiles if p.weapon_type == 'cannon']
    grenade_projectiles = [p for p in projectiles if p.weapon_type == 'grenade']
    other_projectiles = [p for p in projectiles if p.weapon_type not in ['missile', 'cannon', 'grenade']]


    # Check for collisions between projectiles and bots
    collisions = pygame.sprite.groupcollide(bots, projectiles, False, False, pygame.sprite.collide_circle)
    bots_to_remove = []

    if player.laser_active and player.current_weapon == 'laser':
        laser_start = player.position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.math.Vector2(mouse_x - player.position.x, mouse_y - player.position.y).normalize()
        laser_end = player.position + direction * player.laser_length
        closest_distance = player.laser_length
        collision_point = None  # Initialize collision point
        circle_color = (255, 0, 0)

        if player.laser_active and player.current_weapon == 'laser':
            laser_start = player.position
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - player.position.x, mouse_y - player.position.y).normalize()
            laser_end = player.position + direction * player.laser_length
            closest_distance = player.laser_length
            collision_point = None
            circle_color = (255, 0, 0)
            first_hit_bot = None

            for bot in bots:
                if line_intersects_circle(laser_start, laser_end, bot.position, bot.size):
                    distance = player.position.distance_to(bot.position) - bot.size
                    if distance < closest_distance:
                        closest_distance = distance
                        collision_point = player.position + direction * distance
                        first_hit_bot = bot  # Store the first hit bot

            if collision_point:
                draw_hollow_circle(display, collision_point, 7, circle_color)
                laser_end = player.position + direction * closest_distance
                if first_hit_bot:
                    first_hit_bot.health -= player.laser_damage * (clock.get_time() / 1000)
                    if first_hit_bot.health <= 0:
                        new_bots = first_hit_bot.explode(round_number)
                        bots.add(new_bots)
                        bots.remove(first_hit_bot)
                        if first_hit_bot.size > 10:
                            score += 1
            

    for bot, hit_projectiles in collisions.items():
        if bot.size > 1:  # Exclude small 1-pixel bots
            scored_for_bot = False  # Flag to ensure we only increment score once per bot
            for projectile in hit_projectiles:
                if projectile in missile_projectiles:
                    bot.health -= projectile.projectile_damage
                    if bot.health <= 0:
                        new_bots = bot.explode(round_number)
                        bots_to_remove.append(bot)
                        bots.add(new_bots)
                        if bot.size > 10:
                            score += 1  # Increment score only for larger bots
                        for fragment in generate_fragments(projectile):  # Generate visual-only fragments
                            projectiles.add(fragment)
                    create_explosion(projectile.position.x, projectile.position.y, explosions, weapon_type='grenade')
                    projectiles.remove(projectile)
                elif projectile in cannon_projectiles:
                    projectile.apply_damage(bot)
                    projectile.check_collision(bots)  # Ensure it handles the correct bots in path
                    if projectile.projectile_damage <= 0:
                        create_explosion(projectile.position.x, projectile.position.y, explosions)
                        projectiles.remove(projectile)
                elif projectile in grenade_projectiles:
                    bot.health -= projectile.projectile_damage
                    if bot.health <= 0:
                        new_bots = bot.explode(round_number)
                        bots_to_remove.append(bot)
                        bots.add(new_bots)
                        if bot.size > 10:
                            score += 1  # Increment score only for larger bots
                        for fragment in generate_fragments(projectile):  # Generate visual-only fragments
                            projectiles.add(fragment)
                    create_explosion(projectile.position.x, projectile.position.y, explosions, weapon_type='grenade')
                    projectiles.remove(projectile)
                else:  # Other projectiles
                    bot.health -= projectile.projectile_damage
                    if bot.health <= 0:
                        new_bots = bot.explode(round_number)
                        bots_to_remove.append(bot)
                        bots.add(new_bots)
                        if bot.size > 10 and not scored_for_bot:
                            score += 1  # Increment score only for larger bots
                            scored_for_bot = True
                    projectiles.remove(projectile)  # Remove other projectiles after collision

    # Remove bots in a batch
    for bot in bots_to_remove:
        bot.kill()

    # Check for collisions between player and bots
    player_pos = pygame.math.Vector2(player.position.x, player.position.y)
    for bot in bots:
        distance = pygame.math.Vector2(bot.position.x, bot.position.y).distance_to(player_pos)
        if distance < bot.size + player.radius:
            if bot.size == 1:  # If the bot is 1 pixel in size
                bot.velocity *= -1  # Reverse the direction of the bot
            else:
                player_lives -= 1
                is_paused = True
                player.reset_position()
                bots.empty()  # Clear all bots
                projectiles.empty()  # Clear all projectiles
                break

    # Remove bots that have moved off-screen, if their size is less than 10
    bots_to_remove = [bot for bot in bots if bot.size <= 10 and (bot.position.x < -bot.size or bot.position.x > DISPLAY_WIDTH + bot.size or bot.position.y < -bot.size or bot.position.y > DISPLAY_HEIGHT + bot.size)]
    bots.remove(*bots_to_remove)

def spawn_boss():
    side = random.choice(['left', 'right'])
    size = 175
    offset = size + 5
    positions = {
        'left': (-offset, random.randint(0, DISPLAY_HEIGHT)),
        'right': (DISPLAY_WIDTH + offset, random.randint(0, DISPLAY_HEIGHT))
    }
    x, y = positions[side]
    
    boss = Bot(x, y, size, is_new=True)
    boss.health = 500 + ((round_number // 3) - 1) * 75  # Increase health by 75 for every third round
    boss.max_health = boss.health  # Store the maximum health
    boss.speed = 4  # Increase the boss's speed slightly
    return boss

def draw_boss_health_bar(surface, boss):
    if boss.health > 0:
        bar_width = DISPLAY_WIDTH - 94  # 47 pixels from each edge
        bar_height = 10
        red_bar_height = 8
        bar_x = 47  # 47 pixels from the left edge
        bar_y = DISPLAY_HEIGHT - 50

        # Draw the white hollow rectangle
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 3)

        # Calculate the red line width based on the boss's health percentage
        health_percentage = boss.health / boss.max_health
        red_line_width = int(bar_width * health_percentage)

        # Calculate the starting position of the red line to center it
        red_line_start_x = bar_x + (bar_width - red_line_width) // 2

        # Draw the red line centered in the rectangle
        pygame.draw.rect(surface, (255, 0, 0), (red_line_start_x, bar_y + 1, red_line_width, red_bar_height))
        
def save_high_scores(weapon):
    lines = []
    with open('high_scores.txt', 'r') as file:
        lines = file.readlines()
    
    with open('high_scores.txt', 'w') as file:
        for line in lines:
            if line.startswith(f'{weapon}:'):
                if weapon == 'chain gun':
                    file.write(f'chain gun:{chain_gun_high_score}\n')
                elif weapon == 'grape shot':
                    file.write(f'grape shot:{grape_shot_high_score}\n')
                elif weapon == 'laser':
                    file.write(f'laser:{laser_high_score}\n')
                elif weapon == 'blaster':
                    file.write(f'blaster:{blaster_high_score}\n')
                elif weapon == 'missile':
                    file.write(f'missile:{missile_high_score}\n')
                elif weapon == 'grenade':
                    file.write(f'grenade:{grenade_high_score}\n')
                elif weapon == 'cannon':
                    file.write(f'cannon:{cannon_high_score}\n')
            else:
                file.write(line)
    
    # print("High scores saved.")  

def load_high_scores():
    global chain_gun_high_score, grape_shot_high_score, laser_high_score, blaster_high_score, missile_high_score, grenade_high_score, cannon_high_score
    try:
        with open('high_scores.txt', 'r') as file:
            for line in file:
                weapon, score = line.strip().split(':')
                if weapon == 'chain gun':
                    chain_gun_high_score = int(score)
                elif weapon == 'grape shot':
                    grape_shot_high_score = int(score)
                elif weapon == 'laser':
                    laser_high_score = int(score)
                elif weapon == 'blaster':
                    blaster_high_score = int(score)
                elif weapon == 'missile':
                    missile_high_score = int(score)
                elif weapon == 'grenade':
                    grenade_high_score = int(score)
                elif weapon == 'cannon':
                    cannon_high_score = int(score)
    except FileNotFoundError:
        save_high_scores()  # Create the file with initial scores if it doesn't exist
    # print("High scores loaded.")  # Debugging statement

def update_high_scores(weapon, score):
    global chain_gun_high_score, grape_shot_high_score, laser_high_score, blaster_high_score, missile_high_score, grenade_high_score, cannon_high_score

    updated = False

    if weapon == 'chain gun' and score > chain_gun_high_score:
        chain_gun_high_score = score
        updated = True
    elif weapon == 'grape shot' and score > grape_shot_high_score:
        grape_shot_high_score = score
        updated = True
    elif weapon == 'laser' and score > laser_high_score:
        laser_high_score = score
        updated = True
    elif weapon == 'blaster' and score > blaster_high_score:
        blaster_high_score = score
        updated = True
    elif weapon == 'missile' and score > missile_high_score:
        missile_high_score = score
        updated = True
    elif weapon == 'grenade' and score > grenade_high_score:
        grenade_high_score = score
        updated = True
    elif weapon == 'cannon' and score > cannon_high_score:
        cannon_high_score = score
        updated = True

    if updated:
        # print(f"New high score for {weapon} is {score}.")
        save_high_scores(weapon)  # Ensure to save immediately after updating
    # else:
    #     print(f"No new high score for {weapon}. Current high score: {score}.")

def update_color():
    global color_index
    color = rainbow_colors[color_index]
    color_index = (color_index + 1) % len(rainbow_colors)
    return color

# Player instance
player = Player(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2, 10, 5,)

# Group to store projectiles and bots
projectiles = pygame.sprite.Group()
bots = pygame.sprite.Group()

# Initialize small bots surface
small_bots_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)

# Game state variables
is_paused = True
game_started = False
pause_unpause = False
player_lives = 2
score = 0
round_number = 1
round_display_timer = 0
round_display_pos = -50
enemies_to_spawn = 5
enemies_spawned = 0
round_displayed = False
round_end_timer = 0
hue = 0
bot_spawn_timer = 0
WEAPONS = ['chain gun', 'missile', 'blaster', 'cannon', 'grape shot', 'laser', 'grenade']
current_weapon_index = 0
weapon_changed = False
current_color_index_1 = 0
current_color_index_2 = 0
color_changed_1 = False
color_changed_2 = False
ammo = player.max_ammo  
max_ammo = player.max_ammo  
reloading = False
reload_start_time = 0
last_shot_time_line1 = 0
last_shot_time_line2 = 0
last_shot_time = 0
next_line_to_fire = 1
explosions = []
num_colors = 100
rainbow_colors = [tuple(int(i * 255) for i in colorsys.hsv_to_rgb(j / num_colors, 1, 1)) for j in range(num_colors)]
initial_hue_blue = 0.6  
high_scores = load_high_scores()
# update_high_scores(weapon, score)
# save_high_scores()

chain_gun_high_score = 0
grape_shot_high_score = 0
laser_high_score = 0
blaster_high_score = 0
missile_high_score = 0
grenade_high_score = 0
cannon_high_score = 0
last_used_weapon = None  # Initialize without a default weapon to ensure correct tracking
final_weapon = None  # Store the final weapon used when the game ends
game_ended = False  # Flag to track game end
color_index = 63
color_change_delay = 500 
color_change_time = 0
pygame.mouse.set_visible(True)



# Main game loop
load_high_scores()
running = True
selected_weapon = 'chain gun'  # Default weapon
active = False
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if is_paused and game_started and player_lives >= 0 and not pause_unpause:
                    is_paused = False
                    pause_unpause = False
                    restart_round()
                elif pause_unpause:
                    is_paused = False
                    pause_unpause = False
                elif is_paused and player_lives < 0:
                    
                    reset_game()
                else:
                    if is_paused:
                        if player_lives < 0:
                            
                            reset_game()
                            
                        else:
                            is_paused = False
                        if not game_started:
                            game_started = True
                    else:
                        is_paused = True
                        pause_unpause = True
            elif event.key == pygame.K_f and player.ammo < player.max_ammo and not reloading:
                reload()

    # Get mouse position and click status
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # Handle weapon selection
    handle_weapon_selection(mouse_pos, mouse_click)

    # Handle color selection
    handle_color_selection(mouse_pos, mouse_click)

    # Handle screens
    handle_screens()

    # Handle ammo and reloading
    handle_ammo()

    

    if not is_paused:
        # Clear the screen
        display.fill(BLACK)

        if player_lives == 2:
            final_weapon = player.current_weapon
            

        # Handle rounds
        handle_rounds()

        # Move the player
        player.move()

        if pygame.mouse.get_pressed()[0] and player.current_weapon == 'laser' and player.laser_ammo > 0:
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = mouse_pos
            player.fire_laser(mouse_x, mouse_y)
        else:
            player.stop_laser()


        # Update and draw the player including the laser
        player.draw_laser(display)

        # Handle reloading
        if reloading and pygame.time.get_ticks() - reload_start_time >= player.reload_time * 1000:  # Use player.reload_time
            player.ammo = player.max_ammo
            reloading = False

        # Get mouse position and check for mouse button press
        current_time = pygame.time.get_ticks()
        if pygame.mouse.get_pressed()[0] and player.ammo > 0 and not reloading and current_time - player.last_shot_time >= player.shot_delay * 1000:  # Check shot_delay
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - player.position.x, mouse_y - player.position.y).normalize()
            
            if player.current_weapon == 'chain gun':
                player.fire_chain_gun(mouse_x, mouse_y, projectiles)
            elif player.current_weapon == 'grape shot':
                player.fire_grape_shot(mouse_x, mouse_y, projectiles)
            elif player.current_weapon == 'laser':
                player.fire_laser(mouse_x, mouse_y,)
            elif player.current_weapon == 'missile':
                player.fire_missile(mouse_x, mouse_y, projectiles)
            elif player.current_weapon == 'grenade':
                player.fire_grenade(mouse_x, mouse_y, projectiles)
            elif player.current_weapon == 'cannon':
                player.fire_cannon(mouse_x, mouse_y, projectiles)
            elif player.current_weapon == 'blaster':
                player.fire_blaster(mouse_x, mouse_y, projectiles)  
            elif player.current_weapon == 'firethrower':
                player.fire_firethrower(mouse_x, mouse_y, projectiles)      
            # else:
            #     projectile = Projectile(player.position.x, player.position.y, mouse_x, mouse_y, player.current_weapon)
            #     projectiles.add(projectile)
            #     player.ammo -= 1  # Decrement ammo by 1
            player.last_shot_time = current_time  # Update last_shot_time
            if player.ammo == 0:
                reload()

        # for projectile in projectiles:
        #     update_projectile()
        #     projectile.update_position()

        # Batch update
        batch_update()

        # Spawn bots every 1.5 seconds
        bot_spawn_timer += clock.get_time()
        if bot_spawn_timer >= 1500 and enemies_spawned < enemies_to_spawn:
            bots.add(spawn_bot())
            bot_spawn_timer = 0  # Reset the timer
            enemies_spawned += 1

        # Batch collision detection
        batch_collision_detection()

        # Draw the player
        player.draw(display)

        # Draw explosions
        for explosion, explosion_rect, update_explosion in explosions:
            display.blit(explosion, explosion_rect)
            update_explosion()

        # Batch draw
        batch_draw()

        # Draw the boss health bar if the boss is present
        for bot in bots:
            if bot.size > 99:  # Assuming size > 99 indicates the boss
                draw_boss_health_bar(display, bot)
                break

        # Draw the score, player lives, ammo count, and reloading status
        draw_text(display, f'Score: {score}', font, WHITE, (100, 50))
        draw_text(display, f'Enemies: {enemies_spawned}/{enemies_to_spawn}', font, WHITE, (140, 100))
        draw_text(display, f'Lives: {player_lives}', font, WHITE, (DISPLAY_WIDTH - 100, 50))
        if player.current_weapon == 'laser':
            draw_laser_ammo_bar(display, player)
        else:
            draw_text(display, f'Ammo: {player.ammo}', font, WHITE, (DISPLAY_WIDTH // 2, 50))

        # Ensure laser ammo updates are handled
        player.update_laser_ammo()

        if reloading:
            draw_text(display, 'Reloading...', font, WHITE, (DISPLAY_WIDTH // 2, 80))
        # Draw FPS counter
        # fps = clock.get_fps()
        # draw_text(display, f'FPS: {int(fps)}', font, WHITE, (DISPLAY_WIDTH - 100, DISPLAY_HEIGHT - 50))

        if not is_paused:
            pygame.mouse.set_visible(False)        

        if pygame.time.get_ticks() - color_change_time > color_change_delay:
            color = update_color()
            color_change_time = pygame.time.get_ticks()

        # pygame.draw.line(display, color, (mouse_pos[0] - 7, mouse_pos[1]), (mouse_pos[0] + 7, mouse_pos[1]), 1)
        # pygame.draw.line(display, color, (mouse_pos[0], mouse_pos[1]), (mouse_pos[0], mouse_pos[1] + 5), 3)
        pygame.draw.circle(display, color, mouse_pos, 4)

    if player_lives < 0 :
        if final_weapon == 'chain gun' and score > chain_gun_high_score:
            chain_gun_high_score = score
            save_high_scores('chain gun')
        elif final_weapon == 'grape shot' and score > grape_shot_high_score:
            grape_shot_high_score = score
            save_high_scores('grape shot')
        elif final_weapon == 'laser' and score > laser_high_score:
            laser_high_score = score
            save_high_scores('laser')
        elif final_weapon == 'blaster' and score > blaster_high_score:
            blaster_high_score = score
            save_high_scores('blaster')
        elif final_weapon == 'missile' and score > missile_high_score:
            missile_high_score = score
            save_high_scores('missile')
        elif final_weapon == 'grenade' and score > grenade_high_score:
            grenade_high_score = score
            save_high_scores('grenade')
        elif final_weapon == 'cannon' and score > cannon_high_score:
            cannon_high_score = score
            save_high_scores('cannon')

        if game_ended == False:
            final_weapon = player.current_weapon  # Store the final weapon used
            game_ended = True  # Set the game ended flag
            active = False


    # Update the display
    pygame.display.update()

    # Tick the clock
    clock.tick(FPS)

# Quit pygame
pygame.quit()

