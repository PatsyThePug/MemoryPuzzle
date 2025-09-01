import pygame
import random
import time
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 4  # 4x4 grid
CARD_SIZE = 120
CARD_MARGIN = 10
FPS = 60

# Enhanced Color Palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 87, 87)
BLUE = (74, 144, 226)
YELLOW = (255, 206, 84)
GREEN = (129, 199, 132)
PURPLE = (149, 117, 205)
ORANGE = (255, 167, 38)
PINK = (240, 98, 146)
TEAL = (77, 182, 172)
GRAY = (158, 158, 158)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (97, 97, 97)
CARD_SHADOW = (0, 0, 0, 50)
HOVER_HIGHLIGHT = (255, 255, 255, 100)

# Enhanced Card Colors
CARD_COLORS = [
    RED, BLUE, YELLOW, GREEN,
    PURPLE, ORANGE, PINK, TEAL
]

class Card:
    def __init__(self, x, y, color, pair_id):
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        self.color = color
        self.pair_id = pair_id
        self.is_flipped = False
        self.is_matched = False
        self.is_hovered = False
        self.flip_animation = 0  # Animation progress (0-1)
        self.flip_speed = 0.15
        self.hover_scale = 1.0
        self.target_hover_scale = 1.0
        
    def flip(self):
        """Start the flip animation"""
        if not self.is_matched:
            self.is_flipped = not self.is_flipped
            self.flip_animation = 0
    
    def update(self):
        """Update animation and hover effects"""
        if self.flip_animation < 1:
            self.flip_animation = min(1, self.flip_animation + self.flip_speed)
        
        # Smooth hover scaling
        self.hover_scale += (self.target_hover_scale - self.hover_scale) * 0.2
        
        # Update hover target based on state
        if self.is_hovered and not self.is_flipped and not self.is_matched:
            self.target_hover_scale = 1.05
        else:
            self.target_hover_scale = 1.0
    
    def draw(self, screen, font):
        """Draw the card with enhanced visuals and animations"""
        # Calculate scaled size for hover effect
        scaled_size = int(CARD_SIZE * self.hover_scale)
        
        # Calculate card width based on flip animation
        if self.flip_animation < 0.5:
            # First half of flip - showing back
            width = scaled_size * (1 - self.flip_animation * 2)
            color = LIGHT_GRAY
            show_content = False
        else:
            # Second half of flip - showing front
            width = scaled_size * ((self.flip_animation - 0.5) * 2)
            color = self.color if (self.is_flipped or self.is_matched) else LIGHT_GRAY
            show_content = self.is_flipped or self.is_matched
        
        # Center the scaled card
        offset_x = (CARD_SIZE - scaled_size) // 2
        offset_y = (CARD_SIZE - scaled_size) // 2
        x = self.rect.x + offset_x + (scaled_size - width) // 2
        y = self.rect.y + offset_y
        card_rect = pygame.Rect(x, y, width, scaled_size)
        
        # Draw shadow for depth
        if not self.is_matched:
            shadow_rect = card_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height))
            shadow_surface.fill((0, 0, 0))
            shadow_surface.set_alpha(30)
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw card background with rounded corners effect
        if self.is_matched:
            # Matched cards have a subtle glow
            glow_rect = card_rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
            glow_surface.fill(color)
            glow_surface.set_alpha(50)
            screen.blit(glow_surface, glow_rect)
            
            pygame.draw.rect(screen, color, card_rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, card_rect, 3, border_radius=8)
        else:
            pygame.draw.rect(screen, color, card_rect, border_radius=8)
            
            # Hover highlight
            if self.is_hovered and not self.is_flipped:
                highlight_surface = pygame.Surface((card_rect.width, card_rect.height))
                highlight_surface.fill(WHITE)
                highlight_surface.set_alpha(40)
                screen.blit(highlight_surface, card_rect)
            
            # Border
            border_color = WHITE if self.is_hovered and not self.is_flipped else DARK_GRAY
            pygame.draw.rect(screen, border_color, card_rect, 2, border_radius=8)
        
        # Draw card content when flipped
        if show_content and self.flip_animation > 0.5:
            # Draw multiple shapes for better visual appeal
            center_x = card_rect.centerx
            center_y = card_rect.centery
            radius = min(width, scaled_size) // 5
            
            # Main circle
            pygame.draw.circle(screen, WHITE, (center_x, center_y), radius + 4)
            pygame.draw.circle(screen, DARK_GRAY, (center_x, center_y), radius)
            
            # Small decorative circles
            for angle in [0, 90, 180, 270]:
                import math
                offset_x = int(radius * 0.6 * math.cos(math.radians(angle)))
                offset_y = int(radius * 0.6 * math.sin(math.radians(angle)))
                small_radius = radius // 4
                pygame.draw.circle(screen, WHITE, 
                                 (center_x + offset_x, center_y + offset_y), small_radius)

class MemoryGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Memory Puzzle Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game state
        self.cards = []
        self.flipped_cards = []
        self.matches_found = 0
        self.total_pairs = (GRID_SIZE * GRID_SIZE) // 2
        self.score = 0
        self.attempts = 0
        self.start_time = time.time()
        self.game_won = False
        self.check_match_timer = 0
        self.mouse_pos = (0, 0)
        self.match_feedback_timer = 0
        self.last_match_was_success = False
        
        # Sound effects (basic tones using pygame)
        self.create_sounds()
        
        # Initialize game
        self.setup_game()
    
    def create_sounds(self):
        """Create simple sound effects"""
        try:
            # Create simple beep sounds
            self.flip_sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 1000)
            self.match_sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 2000)
            self.win_sound = pygame.mixer.Sound(buffer=b'\x00\x00' * 3000)
        except:
            # If sound creation fails, create dummy sounds
            self.flip_sound = None
            self.match_sound = None
            self.win_sound = None
    
    def setup_game(self):
        """Initialize the game board"""
        self.cards = []
        self.flipped_cards = []
        self.matches_found = 0
        self.score = 0
        self.attempts = 0
        self.start_time = time.time()
        self.game_won = False
        self.check_match_timer = 0
        
        # Create pairs of cards
        colors = CARD_COLORS[:self.total_pairs]
        card_data = colors * 2  # Create pairs
        random.shuffle(card_data)
        
        # Calculate grid position
        grid_width = GRID_SIZE * (CARD_SIZE + CARD_MARGIN) - CARD_MARGIN
        grid_height = GRID_SIZE * (CARD_SIZE + CARD_MARGIN) - CARD_MARGIN
        start_x = (WINDOW_WIDTH - grid_width) // 2
        start_y = (WINDOW_HEIGHT - grid_height) // 2 + 40
        
        # Create card objects
        for i, color in enumerate(card_data):
            row = i // GRID_SIZE
            col = i % GRID_SIZE
            x = start_x + col * (CARD_SIZE + CARD_MARGIN)
            y = start_y + row * (CARD_SIZE + CARD_MARGIN)
            
            # Find pair_id based on color
            pair_id = colors.index(color)
            card = Card(x, y, color, pair_id)
            self.cards.append(card)
    
    def handle_click(self, pos):
        """Handle mouse click on cards"""
        if self.game_won or self.check_match_timer > 0:
            return
        
        for card in self.cards:
            if card.rect.collidepoint(pos) and not card.is_flipped and not card.is_matched:
                if len(self.flipped_cards) < 2:
                    card.flip()
                    self.flipped_cards.append(card)
                    
                    # Play flip sound
                    if self.flip_sound:
                        try:
                            self.flip_sound.play()
                        except:
                            pass
                    
                    # Check for match when two cards are flipped
                    if len(self.flipped_cards) == 2:
                        self.attempts += 1
                        self.check_match_timer = 60  # Wait 1 second before checking
                break
    
    def check_match(self):
        """Check if the two flipped cards match"""
        if len(self.flipped_cards) == 2:
            card1, card2 = self.flipped_cards
            
            if card1.pair_id == card2.pair_id:
                # Match found
                card1.is_matched = True
                card2.is_matched = True
                self.matches_found += 1
                self.score += 10
                self.last_match_was_success = True
                self.match_feedback_timer = 30  # Show feedback for 0.5 seconds
                
                # Play match sound
                if self.match_sound:
                    try:
                        self.match_sound.play()
                    except:
                        pass
                
                # Check if game is won
                if self.matches_found == self.total_pairs:
                    self.game_won = True
                    # Bonus points for time and efficiency
                    elapsed_time = time.time() - self.start_time
                    time_bonus = max(0, 300 - int(elapsed_time))
                    efficiency_bonus = max(0, (self.total_pairs * 2 - self.attempts) * 5)
                    self.score += time_bonus + efficiency_bonus
                    
                    if self.win_sound:
                        try:
                            self.win_sound.play()
                        except:
                            pass
            else:
                # No match - flip cards back
                card1.flip()
                card2.flip()
                self.last_match_was_success = False
                self.match_feedback_timer = 30
            
            self.flipped_cards = []
    
    def update(self):
        """Update game state"""
        # Get mouse position
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Update hover states
        for card in self.cards:
            card.is_hovered = card.rect.collidepoint(self.mouse_pos) and not card.is_flipped and not card.is_matched
            card.update()
        
        # Handle match checking timer
        if self.check_match_timer > 0:
            self.check_match_timer -= 1
            if self.check_match_timer == 0:
                self.check_match()
        
        # Handle match feedback timer
        if self.match_feedback_timer > 0:
            self.match_feedback_timer -= 1
    
    def draw(self):
        """Draw the game"""
        self.screen.fill(WHITE)
        
        # Draw title
        title_text = self.title_font.render("Memory Puzzle", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title_text, title_rect)
        
        # Draw cards
        for card in self.cards:
            card.draw(self.screen, self.font)
        
        # Draw game stats
        self.draw_stats()
        
        # Draw game over message
        if self.game_won:
            self.draw_win_message()
        
        pygame.display.flip()
    
    def draw_stats(self):
        """Draw enhanced game statistics with progress bar"""
        # Calculate elapsed time
        if not self.game_won:
            elapsed_time = int(time.time() - self.start_time)
        else:
            elapsed_time = int(time.time() - self.start_time)
        
        # Background panel for stats
        stats_panel = pygame.Rect(20, 70, WINDOW_WIDTH - 40, 80)
        pygame.draw.rect(self.screen, LIGHT_GRAY, stats_panel, border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, stats_panel, 2, border_radius=10)
        
        # Left side - Score and Attempts with icons
        score_text = self.font.render(f"🏆 Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (35, 85))
        
        attempts_text = self.font.render(f"🎯 Attempts: {self.attempts}", True, BLACK)
        self.screen.blit(attempts_text, (35, 115))
        
        # Right side - Time and Matches
        time_text = self.font.render(f"⏱️ Time: {elapsed_time}s", True, BLACK)
        time_rect = time_text.get_rect()
        self.screen.blit(time_text, (WINDOW_WIDTH - time_rect.width - 35, 85))
        
        matches_text = self.font.render(f"🎴 Matches: {self.matches_found}/{self.total_pairs}", True, BLACK)
        matches_rect = matches_text.get_rect()
        self.screen.blit(matches_text, (WINDOW_WIDTH - matches_rect.width - 35, 115))
        
        # Progress bar
        progress = self.matches_found / self.total_pairs if self.total_pairs > 0 else 0
        progress_bar_rect = pygame.Rect(40, 160, WINDOW_WIDTH - 80, 20)
        
        # Progress bar background
        pygame.draw.rect(self.screen, GRAY, progress_bar_rect, border_radius=10)
        
        # Progress bar fill
        fill_width = int((WINDOW_WIDTH - 80) * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(40, 160, fill_width, 20)
            color = GREEN if progress == 1.0 else BLUE
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=10)
        
        # Progress bar border
        pygame.draw.rect(self.screen, DARK_GRAY, progress_bar_rect, 2, border_radius=10)
        
        # Progress percentage
        progress_text = self.font.render(f"{int(progress * 100)}%", True, BLACK)
        progress_text_rect = progress_text.get_rect(center=(WINDOW_WIDTH // 2, 190))
        self.screen.blit(progress_text, progress_text_rect)
        
        # Match feedback
        if self.match_feedback_timer > 0:
            feedback_alpha = int(255 * (self.match_feedback_timer / 30))
            if self.last_match_was_success:
                feedback_text = "✨ MATCH! ✨"
                feedback_color = GREEN
            else:
                feedback_text = "❌ Try Again"
                feedback_color = RED
            
            feedback_surface = self.font.render(feedback_text, True, feedback_color)
            feedback_surface.set_alpha(feedback_alpha)
            feedback_rect = feedback_surface.get_rect(center=(WINDOW_WIDTH // 2, 210))
            self.screen.blit(feedback_surface, feedback_rect)
        
        # Bottom center - Instructions with better styling
        if not self.game_won:
            instruction_text = self.font.render("💡 Click cards to flip them", True, DARK_GRAY)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(instruction_text, instruction_rect)
        
        restart_text = self.font.render("🔄 Press R to restart", True, DARK_GRAY)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 20))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_win_message(self):
        """Draw enhanced victory message"""
        # Semi-transparent overlay with gradient effect
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 20, 40))  # Dark blue tint
        self.screen.blit(overlay, (0, 0))
        
        # Victory panel
        panel_width = 400
        panel_height = 300
        panel_rect = pygame.Rect((WINDOW_WIDTH - panel_width) // 2, 
                                (WINDOW_HEIGHT - panel_height) // 2, 
                                panel_width, panel_height)
        
        # Panel background with glow
        glow_rect = panel_rect.inflate(20, 20)
        glow_surface = pygame.Surface((glow_rect.width, glow_rect.height))
        glow_surface.fill(YELLOW)
        glow_surface.set_alpha(100)
        self.screen.blit(glow_surface, glow_rect)
        
        pygame.draw.rect(self.screen, WHITE, panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, YELLOW, panel_rect, 4, border_radius=20)
        
        # Trophy emoji and title
        trophy_text = pygame.font.Font(None, 72).render("🏆", True, YELLOW)
        trophy_rect = trophy_text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.y + 60))
        self.screen.blit(trophy_text, trophy_rect)
        
        win_text = self.title_font.render("Congratulations!", True, DARK_GRAY)
        win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.y + 120))
        self.screen.blit(win_text, win_rect)
        
        # Game stats
        elapsed_time = int(time.time() - self.start_time)
        stats_lines = [
            f"🏆 Final Score: {self.score}",
            f"⏱️ Time: {elapsed_time}s", 
            f"🎯 Attempts: {self.attempts}",
            f"⭐ Efficiency: {int((self.total_pairs * 2 / max(self.attempts, 1)) * 100)}%"
        ]
        
        for i, line in enumerate(stats_lines):
            text = self.font.render(line, True, DARK_GRAY)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.y + 160 + i * 25))
            self.screen.blit(text, text_rect)
        
        # Play again instruction
        restart_text = self.font.render("🔄 Press R to play again", True, BLUE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, panel_rect.y + 270))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        self.setup_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update game
            self.update()
            
            # Draw game
            self.draw()
            
            # Control frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    try:
        # Initialize pygame mixer for sound
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    except:
        print("Warning: Could not initialize sound")
    
    # Create and run the game
    game = MemoryGame()
    game.run()

if __name__ == "__main__":
    main()
