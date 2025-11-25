import pygame
import random
import sys
import os

# --- Constants and Configurations ---
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20
FPS_BASE = 10

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (220, 220, 220)
RED = (210, 50, 50)

# --- New "Sleek" Color Scheme ---
BG_COLOR = (25, 25, 25)
GRID_COLOR = (40, 40, 40)
UI_BG = (50, 50, 50)
UI_BG_HOVER = (70, 160, 120)
UI_TEXT_HOVER = (255, 255, 0)

SNAKE_HEAD_COLOR = (20, 180, 90)

# --- New Food Colors ---
FOOD_RED = (210, 60, 60)
FOOD_YELLOW = (220, 180, 40)
FOOD_BLUE = (60, 140, 210)
FOOD_PURPLE = (160, 90, 200)

# --- Font Sizes ---
FONT_LARGE = 80
FONT_MEDIUM = 60
FONT_NORMAL = 40
FONT_SMALL = 30

# --- Initialization ---
pygame.init()

# --- Asset loading function ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- High Score Handling ---
HIGH_SCORE_FILE = "highscore.txt"
SETTINGS_FILE = "settings.txt"

class Snake:
    """Represents the snake."""
    def __init__(self):
        self.body = [[WIDTH // 2, HEIGHT // 2]]
        self.direction = (0, -BLOCK_SIZE) # (x_change, y_change)
        self.length = 1

    def move(self):
        """Moves the snake one block in its current direction."""
        head = self.body[-1]
        new_head = [head[0] + self.direction[0], head[1] + self.direction[1]]
        self.body.append(new_head)
        if len(self.body) > self.length:
            del self.body[0]

    def grow(self, amount=1):
        """Increases the length of the snake."""
        self.length += amount

    def change_direction(self, new_direction):
        """Changes the snake's direction, preventing 180-degree turns."""
        if (new_direction[0] != -self.direction[0] or \
            new_direction[1] != -self.direction[1]):
            self.direction = new_direction
            return True
        return False

    def check_collision(self):
        """Checks for collision with walls or self."""
        head = self.body[-1]
        if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
            return True # Wall collision
        if head in self.body[:-1]:
            return True # Self collision
        return False

    def draw(self, surface):
        """Draws the snake on the given surface with a 3D effect."""
        offset = 5 # Depth of the 3D effect

        # Draw body segments from tail to head so they overlap correctly
        for i, block_pos in enumerate(self.body):
            x, y = block_pos[0], block_pos[1]

            # Define colors
            if i == len(self.body) - 1:
                # Head colors
                top_color = SNAKE_HEAD_COLOR
                side_color_1 = (top_color[0], max(0, top_color[1] - 40), max(0, top_color[2] - 20))
                side_color_2 = (top_color[0], max(0, top_color[1] - 80), max(0, top_color[2] - 40))
            else:
                # Body colors with gradient
                progress = i / max(len(self.body) - 1, 1) if len(self.body) > 1 else 1
                g = 120 + int(60 * progress)
                top_color = (20, g, 90)
                side_color_1 = (top_color[0], max(0, top_color[1] - 30), max(0, top_color[2] - 20))
                side_color_2 = (top_color[0], max(0, top_color[1] - 60), max(0, top_color[2] - 40))

            # Points for the cube faces
            top_face_pts = [(x, y), (x + BLOCK_SIZE, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), (x, y + BLOCK_SIZE)]
            right_face_pts = [(x + BLOCK_SIZE, y), (x + BLOCK_SIZE + offset, y + offset), (x + BLOCK_SIZE + offset, y + BLOCK_SIZE + offset), (x + BLOCK_SIZE, y + BLOCK_SIZE)]
            bottom_face_pts = [(x, y + BLOCK_SIZE), (x + BLOCK_SIZE, y + BLOCK_SIZE), (x + BLOCK_SIZE + offset, y + BLOCK_SIZE + offset), (x + offset, y + BLOCK_SIZE + offset)]

            # Draw the side faces first
            pygame.draw.polygon(surface, side_color_2, bottom_face_pts)
            pygame.draw.polygon(surface, side_color_1, right_face_pts)
            
            # Draw the top face
            pygame.draw.polygon(surface, top_color, top_face_pts)
            
            # Draw a subtle highlight on the top-left edge
            highlight_color = tuple(min(255, c + 50) for c in top_color)
            pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + BLOCK_SIZE - 2, y + 2), 2)
            pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + 2, y + BLOCK_SIZE - 2), 2)


class Food:
    """Represents the food."""
    TYPES = {
        "normal": {"color": FOOD_RED, "power": 1},
        "speed": {"color": FOOD_YELLOW, "power": 1, "effect": "speed_up", "duration": 200, "boost": 7},
        "growth": {"color": FOOD_PURPLE, "power": 3},
        "slow": {"color": FOOD_BLUE, "power": 1, "effect": "slow_down", "duration": 300, "boost": -5},
    }

    def __init__(self):
        self.respawn()

    def respawn(self):
        """Respawns the food at a new random location and type."""
        self.type = random.choice(list(self.TYPES.keys()))
        self.position = (random.randrange(0, WIDTH, BLOCK_SIZE),
                         random.randrange(0, HEIGHT, BLOCK_SIZE))
        self.properties = self.TYPES[self.type]

    def draw(self, surface):
        """Draws the food on the given surface with a 3D effect."""
        offset = 5 # Depth of the 3D effect
        x, y = self.position[0], self.position[1]
        
        top_color = self.properties["color"]
        # Create darker and lighter versions for 3D effect
        side_color_1 = tuple(max(0, c - 30) for c in top_color)
        side_color_2 = tuple(max(0, c - 60) for c in top_color)
        highlight_color = tuple(min(255, c + 60) for c in top_color)

        # Points for the cube faces
        top_face_pts = [(x, y), (x + BLOCK_SIZE, y), (x + BLOCK_SIZE, y + BLOCK_SIZE), (x, y + BLOCK_SIZE)]
        right_face_pts = [(x + BLOCK_SIZE, y), (x + BLOCK_SIZE + offset, y + offset), (x + BLOCK_SIZE + offset, y + BLOCK_SIZE + offset), (x + BLOCK_SIZE, y + BLOCK_SIZE)]
        bottom_face_pts = [(x, y + BLOCK_SIZE), (x + BLOCK_SIZE, y + BLOCK_SIZE), (x + BLOCK_SIZE + offset, y + BLOCK_SIZE + offset), (x + offset, y + BLOCK_SIZE + offset)]

        # Draw the side faces first
        pygame.draw.polygon(surface, side_color_2, bottom_face_pts)
        pygame.draw.polygon(surface, side_color_1, right_face_pts)
        
        # Draw the top face
        pygame.draw.polygon(surface, top_color, top_face_pts)
        
        # Draw a subtle highlight on the top-left edge
        pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + BLOCK_SIZE - 2, y + 2), 2)
        pygame.draw.line(surface, highlight_color, (x + 2, y + 2), (x + 2, y + BLOCK_SIZE - 2), 2)


class Game:
    """Manages the main game loop and states."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        pygame.display.set_icon(self._create_icon())
        self.clock = pygame.time.Clock()
        self.game_state = "SPLASH" # SPLASH, PLAYING, PAUSED, GAME_OVER, SETTINGS
        self.previous_game_state = "SPLASH"
        self.score = 0
        self.high_score = self._load_high_score()
        self.speed_boost_timer = 0
        self.speed_boost_amount = 0
        self.settings = self._load_settings()
        self.selected_button_index = 0
        self._load_assets()
        self._apply_settings()

    def _load_assets(self):
        """Loads all game assets like sounds and fonts."""
        try:
            self.move_sound = pygame.mixer.Sound(resource_path(os.path.join("assets", "SFX", "snake-hissing-6092.mp3")))
            self.eat_sound = pygame.mixer.Sound(resource_path(os.path.join("assets", "SFX", "eat-323883.mp3")))
            self.gameover_sound = pygame.mixer.Sound(resource_path(os.path.join("assets", "SFX", "game-over-retro-video-game-music-soundroll-melody-4-4-00-03.mp3")))
        except pygame.error as e:
            print(f"Can't load sound: {e}")
            self.move_sound = self.eat_sound = self.gameover_sound = None

    def _load_settings(self):
        """Loads settings from a file."""
        defaults = {'volume': 1.0, 'grid': True}
        if not os.path.exists(SETTINGS_FILE):
            return defaults
        try:
            settings = defaults.copy()
            with open(SETTINGS_FILE, 'r') as f:
                for line in f:
                    key, value = line.strip().split('=')
                    if key == 'volume':
                        settings[key] = float(value)
                    elif key == 'grid':
                        settings[key] = (value == 'True')
            return settings
        except Exception:
            return defaults

    def _save_settings(self):
        """Saves the current settings to a file."""
        with open(SETTINGS_FILE, 'w') as f:
            for key, value in self.settings.items():
                f.write(f"{key}={value}\n")

    def _load_high_score(self):
        """Loads the high score from a file."""
        if not os.path.exists(HIGH_SCORE_FILE):
            return 0
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except (IOError, ValueError):
            return 0

    def _save_high_score(self):
        """Saves the high score to a file."""
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(self.high_score))

    def _create_icon(self):
        """Creates a 32x32 surface with a sleek, abstract 'S' for the window icon."""
        icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        icon_surface.fill(BG_COLOR)

        try:
            # Use a bold, blocky font for a modern look
            font = pygame.font.SysFont('Arial Black', 38, bold=True)
        except pygame.error:
            font = pygame.font.SysFont(None, 42, bold=True)

        # Render a stylized 'S'
        s_shadow = font.render("S", True, (0, 80, 40))
        s_main = font.render("S", True, SNAKE_HEAD_COLOR)

        icon_surface.blit(s_shadow, s_shadow.get_rect(center=(17, 18)))
        icon_surface.blit(s_main, s_main.get_rect(center=(16, 16)))
        
        return icon_surface

    def _apply_settings(self):
        """Applies the current settings, e.g., sound volume."""
        if self.move_sound: self.move_sound.set_volume(self.settings['volume'])
        if self.eat_sound: self.eat_sound.set_volume(self.settings['volume'])
        if self.gameover_sound: self.gameover_sound.set_volume(self.settings['volume'])

    def _draw_text(self, text, size, color, x, y, align="topleft"):
        """Helper function to draw text on the screen."""
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "topright":
            text_rect.topright = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def _draw_text_custom_font(self, font, text, color, x, y, align="topleft"):
        """Helper function to draw text with a specific font object."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "topright":
            text_rect.topright = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def _draw_button(self, text, index, total_buttons, y_offset, width=250, height=50):
        """Helper to draw a menu button and highlight if selected."""
        x = WIDTH // 2 - width // 2
        y = y_offset + index * (height + 15)
        
        is_selected = (self.selected_button_index == index)
        
        color = UI_TEXT_HOVER if is_selected else WHITE
        bg_color = UI_BG_HOVER if is_selected else UI_BG

        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, bg_color, button_rect, border_radius=8)
        
        self._draw_text(text, FONT_NORMAL, color, button_rect.centerx, button_rect.centery, align="center")
        return button_rect

    def _reset_game(self):
        """Resets the game to its initial state."""
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed_boost_timer = 0
        self.speed_boost_amount = 0
        self.game_state = "PLAYING"

    def run(self):
        """The main loop of the application."""
        running = True
        while running:
            if self.game_state == "SPLASH":
                self._splash_screen()
            elif self.game_state == "PLAYING":
                self._handle_events()
                self._update_game_state()
                self._draw_elements()
            elif self.game_state == "PAUSED":
                self._pause_menu()
            elif self.game_state == "GAME_OVER":
                self._game_over_screen()
            elif self.game_state == "SETTINGS":
                self._settings_screen()
            
            pygame.display.update()
            
            if self.game_state == "PLAYING":
                current_fps = FPS_BASE + (self.snake.length // 5) + self.speed_boost_amount
                self.clock.tick(current_fps)
            else:
                self.clock.tick(FPS_BASE) # Slower tick for menus

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """Handles events for the PLAYING state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                direction_changed = False
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "PAUSED"
                elif event.key == pygame.K_LEFT:
                    direction_changed = self.snake.change_direction((-BLOCK_SIZE, 0))
                elif event.key == pygame.K_RIGHT:
                    direction_changed = self.snake.change_direction((BLOCK_SIZE, 0))
                elif event.key == pygame.K_UP:
                    direction_changed = self.snake.change_direction((0, -BLOCK_SIZE))
                elif event.key == pygame.K_DOWN:
                    direction_changed = self.snake.change_direction((0, BLOCK_SIZE))
                
                if direction_changed and self.move_sound:
                    self.move_sound.play()

    def _update_game_state(self):
        """Updates the game logic for the PLAYING state."""
        # Update speed boost timer
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
        else:
            self.speed_boost_amount = 0 # Reset boost when timer runs out

        self.snake.move()

        if self.snake.check_collision():
            pygame.mixer.stop() # Stop all other sounds
            if self.gameover_sound: 
                self.gameover_sound.play()
            self.game_state = "GAME_OVER"
            return

        head = self.snake.body[-1]
        if head[0] == self.food.position[0] and head[1] == self.food.position[1]:
            power = self.food.properties["power"]
            self.snake.grow(power)
            self.score += power

            # Handle special food effects
            if self.food.type in ["speed", "slow"]:
                self.speed_boost_timer = self.food.properties.get("duration", 200)
                self.speed_boost_amount = self.food.properties.get("boost", 0)
            elif self.food.type == "normal":
                # Reset any active speed effects
                self.speed_boost_timer = 0
                self.speed_boost_amount = 0

            if self.eat_sound: self.eat_sound.play()
            
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            
            self.food.respawn()

    def _draw_elements(self):
        """Draws all elements for the PLAYING state."""
        self.screen.fill(BG_COLOR)
        # Draw grid
        if self.settings['grid']:
            for i in range(0, WIDTH, BLOCK_SIZE):
                pygame.draw.line(self.screen, GRID_COLOR, (i, 0), (i, HEIGHT))
            for j in range(0, HEIGHT, BLOCK_SIZE):
                pygame.draw.line(self.screen, GRID_COLOR, (0, j), (WIDTH, j))

        self.snake.draw(self.screen)
        self.food.draw(self.screen)

        self._draw_text(f"Score: {self.score}", FONT_SMALL, WHITE, 10, 10)
        self._draw_text(f"High Score: {self.high_score}", FONT_SMALL, UI_TEXT_HOVER, WIDTH - 10, 10, align="topright")

    def _splash_screen(self):
        """Displays the splash screen with menu options."""
        self.screen.fill(BG_COLOR)

        # --- New Title/Logo ---
        try:
            title_font = pygame.font.SysFont('Arial Black', FONT_LARGE)
        except pygame.error:
            title_font = pygame.font.SysFont(None, FONT_LARGE + 10, bold=True)

        title_text = "SNAKE"
        center_x, center_y = WIDTH // 2, HEIGHT * 0.2

        self._draw_text_custom_font(title_font, title_text, (10, 10, 10), center_x + 5, center_y + 5, "center") # Deep shadow
        self._draw_text_custom_font(title_font, title_text, SNAKE_HEAD_COLOR, center_x, center_y, "center") # Main color
        self._draw_text_custom_font(title_font, title_text, tuple(min(255, c+80) for c in SNAKE_HEAD_COLOR), center_x - 2, center_y - 2, "center") # Highlight
        
        buttons = ["Play", "Settings", "Quit"]
        button_rects = []
        for i, text in enumerate(buttons):
            button_rects.append(self._draw_button(text, i, len(buttons), HEIGHT * 0.4))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if self.selected_button_index == 0: # Play
                        self._reset_game()
                    elif self.selected_button_index == 1: # Settings
                        self.previous_game_state = "SPLASH"
                        self.game_state = "SETTINGS"
                        self.selected_button_index = 0
                    elif self.selected_button_index == 2: # Quit
                        pygame.quit()
                        sys.exit()

    def _pause_menu(self):
        """Displays the pause menu with options."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self._draw_text("Paused", FONT_MEDIUM + 10, UI_TEXT_HOVER, WIDTH // 2, HEIGHT * 0.2, align="center")

        buttons = ["Resume", "Settings", "Main Menu"]
        button_rects = []
        for i, text in enumerate(buttons):
            button_rects.append(self._draw_button(text, i, len(buttons), HEIGHT * 0.4))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "PLAYING"
                    return
                
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if self.selected_button_index == 0: # Resume
                        self.game_state = "PLAYING"
                    elif self.selected_button_index == 1: # Settings
                        self.previous_game_state = "PAUSED"
                        self.game_state = "SETTINGS"
                        self.selected_button_index = 0
                    elif self.selected_button_index == 2: # Main Menu
                        self.game_state = "SPLASH"
                        self.selected_button_index = 0

    def _settings_screen(self):
        """Displays the settings menu."""
        self.screen.fill(BG_COLOR)
        self._draw_text("Settings", FONT_MEDIUM, UI_TEXT_HOVER, WIDTH // 2, HEIGHT * 0.15, align="center")

        volume_text = f"Volume: < {int(self.settings['volume'] * 100)}% >"
        grid_text = f"Show Grid: {'On' if self.settings['grid'] else 'Off'}"
        
        buttons = [volume_text, grid_text, "Back"]
        button_rects = []
        for i, text in enumerate(buttons):
            button_rects.append(self._draw_button(text, i, len(buttons), HEIGHT * 0.35, width=350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_LEFT and self.selected_button_index == 0:
                    self.settings['volume'] = round(max(0.0, self.settings['volume'] - 0.1), 1)
                    self._apply_settings()
                    self._save_settings()
                elif event.key == pygame.K_RIGHT and self.selected_button_index == 0:
                    self.settings['volume'] = round(min(1.0, self.settings['volume'] + 0.1), 1)
                    self._apply_settings()
                    self._save_settings()
                elif event.key == pygame.K_RETURN:
                    if self.selected_button_index == 1: # Grid
                        self.settings['grid'] = not self.settings['grid']
                        self._save_settings()
                    elif self.selected_button_index == 2: # Back
                        self.game_state = self.previous_game_state
                        self.selected_button_index = 0

    def _game_over_screen(self):
        """Displays the game over screen with menu options over the final game state."""
        # Create a semi-transparent overlay to darken the background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self._draw_text("Game Over", FONT_LARGE, RED, WIDTH // 2, HEIGHT * 0.2, align="center")
        self._draw_text(f"Your Score: {self.score}", FONT_NORMAL, WHITE, WIDTH // 2, HEIGHT * 0.35, align="center")
        
        buttons = ["Restart", "Main Menu"]
        button_rects = []
        for i, text in enumerate(buttons):
            button_rects.append(self._draw_button(text, i, len(buttons), HEIGHT * 0.55))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

            if event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_button_index = i

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_button_index = (self.selected_button_index - 1) % len(buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button_index = (self.selected_button_index + 1) % len(buttons)
                elif event.key == pygame.K_RETURN:
                    if self.selected_button_index == 0: # Restart
                        self._reset_game()
                    elif self.selected_button_index == 1: # Main Menu
                        self.game_state = "SPLASH"
                        self.selected_button_index = 0

if __name__ == '__main__':
    game_instance = Game()
    game_instance.run()
