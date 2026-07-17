import pygame
import os
import sys
import random

# --- Constants & Configuration ---
WIDTH = 800
HEIGHT = 600
FPS = 60

# Zelda-inspired Retro Palette
DARK_FOREST_SLATE = (24, 28, 20)
RETRO_MOSS_GREEN = (40, 54, 38)
TRIFORCE_GREEN = (144, 238, 144)
WHITE = (255, 255, 255)
RUPEE_GREEN = (80, 200, 120)
SETTINGS_BG = (30, 40, 30)

class AudioDashboardApp:
    def __init__(self):
        try:
            pygame.init()
            pygame.mixer.init()
        except Exception as e:
            print(f"Error initializing Pygame modules: {e}")
            sys.exit(1)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retro Audio Dashboard & Interactive Game")
        self.clock = pygame.time.Clock()

        self._init_fonts()
        
        self.sprite_image = None
        self.sprite_rect = None
        
        self.player_speed = 6
        self.score = 0
        
        self._load_character_sprite()
        
        self.collectible_rect = pygame.Rect(0, 0, 20, 30)
        self._spawn_collectible()
        
        # Audio properties
        self.music_loaded = False
        self.is_playing = False
        self.music_started = False
        self.volume = 0.5
        self.is_muted = False
        
        # UI Properties
        self.show_settings = False
        self.settings_btn_rect = pygame.Rect(WIDTH - 60, 15, 40, 50)
        
        # Pop-up Menu Rects
        self.popup_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 120, 300, 240)
        self.btn_vol_down = pygame.Rect(self.popup_rect.centerx - 100, self.popup_rect.y + 90, 80, 30)
        self.btn_vol_up = pygame.Rect(self.popup_rect.centerx + 20, self.popup_rect.y + 90, 80, 30)
        self.btn_mute = pygame.Rect(self.popup_rect.centerx - 60, self.popup_rect.y + 140, 120, 30)
        self.btn_close = pygame.Rect(self.popup_rect.centerx - 60, self.popup_rect.y + 190, 120, 30)
        
        self._load_audio()

    def _init_fonts(self):
        try:
            self.title_font = pygame.font.SysFont("Courier New", 20, bold=True)
            self.info_font = pygame.font.SysFont("Courier New", 18, bold=True)
            self.guideline_font = pygame.font.SysFont("Courier New", 16)
        except Exception as e:
            print(f"Warning: Preferred fonts could not be loaded ({e}). Using fallbacks.")
            self.title_font = pygame.font.Font(None, 32)
            self.info_font = pygame.font.Font(None, 24)
            self.guideline_font = pygame.font.Font(None, 20)

    def _load_character_sprite(self):
        try:
            image_path = os.path.join(os.path.dirname(__file__), "character.png")
            if not os.path.exists(image_path):
                image_path = "character.png"

            raw_image = pygame.image.load(image_path).convert_alpha()
            self.sprite_image = pygame.transform.scale(raw_image, (100, 100))
            self.sprite_rect = self.sprite_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: 'character.png' not found ({e}). Using fallback rectangle.")
            self.sprite_image = None
            self.sprite_rect = pygame.Rect(0, 0, 100, 100)
            self.sprite_rect.center = (WIDTH // 2, HEIGHT // 2 + 50)

    def _apply_volume(self):
        if self.music_loaded:
            if self.is_muted:
                pygame.mixer.music.set_volume(0.0)
            else:
                pygame.mixer.music.set_volume(self.volume)

    def _load_audio(self):
        try:
            music_path = os.path.join(os.path.dirname(__file__), "bg_music.mp3")
            if not os.path.exists(music_path):
                music_path = "bg_music.mp3"

            pygame.mixer.music.load(music_path)
            self.music_loaded = True
            self._apply_volume()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: 'bg_music.mp3' not found ({e}). Audio features disabled.")
            self.music_loaded = False

    def _spawn_collectible(self):
        margin_x = 50
        min_y = 90  
        max_y = HEIGHT - 120  
        
        self.collectible_rect.x = random.randint(margin_x, WIDTH - margin_x - self.collectible_rect.width)
        self.collectible_rect.y = random.randint(min_y, max_y - self.collectible_rect.height)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouseclick(event.pos)
        
        # Only allow game loop mechanics if settings menu is closed
        if not self.show_settings:
            keys = pygame.key.get_pressed()
            self._handle_movement(keys)
            
            if self.sprite_rect.colliderect(self.collectible_rect):
                self.score += 10
                self._spawn_collectible()
            
        return True

    def _handle_mouseclick(self, pos):
        # Toggle settings menu
        if self.settings_btn_rect.collidepoint(pos):
            self.show_settings = not self.show_settings
            return
            
        # Process settings buttons if menu is open
        if self.show_settings:
            if self.btn_vol_up.collidepoint(pos):
                self.volume = min(1.0, self.volume + 0.1)
                self._apply_volume()
            elif self.btn_vol_down.collidepoint(pos):
                self.volume = max(0.0, self.volume - 0.1)
                if self.volume < 0.01:
                    self.volume = 0.0
                self._apply_volume()
            elif self.btn_mute.collidepoint(pos):
                self.is_muted = not self.is_muted
                self._apply_volume()
            elif self.btn_close.collidepoint(pos):
                self.show_settings = False

    def _handle_movement(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.sprite_rect.x -= self.player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.sprite_rect.x += self.player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.sprite_rect.y -= self.player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.sprite_rect.y += self.player_speed
            
        if self.sprite_rect.left < 0:
            self.sprite_rect.left = 0
        if self.sprite_rect.right > WIDTH:
            self.sprite_rect.right = WIDTH
            
        if self.sprite_rect.top < 90:
            self.sprite_rect.top = 90
        if self.sprite_rect.bottom > HEIGHT - 50:
            self.sprite_rect.bottom = HEIGHT - 50

    def _handle_keydown(self, event):
        # Pressing Escape toggles settings
        if event.key == pygame.K_ESCAPE:
            self.show_settings = not self.show_settings
            
        # Block other key commands if settings are open
        if self.show_settings:
            return

        if event.key == pygame.K_SPACE:
            if self.music_loaded:
                if self.is_playing:
                    pygame.mixer.music.pause()
                    self.is_playing = False
                else:
                    if not self.music_started:
                        try:
                            pygame.mixer.music.play(-1)
                            self.music_started = True
                        except Exception as e:
                            print(f"Failed to play music: {e}")
                    else:
                        pygame.mixer.music.unpause()
                    self.is_playing = True
        
        elif event.key == pygame.K_r:
            if self.music_loaded:
                try:
                    pygame.mixer.music.play(-1)
                    self.is_playing = True
                    self.music_started = True
                except Exception as e:
                    print(f"Failed to restart music: {e}")
        
        elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
            self.volume = min(1.0, self.volume + 0.1)
            self._apply_volume()
        
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            self.volume = max(0.0, self.volume - 0.1)
            if self.volume < 0.01:
                self.volume = 0.0
            self._apply_volume()

    def draw_dashboard(self):
        # Unified Main Dashboard Panel
        panel_rect = pygame.Rect(20, 15, WIDTH - 40, 50)
        pygame.draw.rect(self.screen, RETRO_MOSS_GREEN, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, TRIFORCE_GREEN, panel_rect, width=2, border_radius=10)

        title_surf = self.title_font.render("ZELDA AUDIO & ADVENTURE", True, TRIFORCE_GREEN)
        
        if not self.music_loaded:
            status_text = "NO TRACK"
        else:
            status_text = "PLAYING" if self.is_playing else "PAUSED"
            
        status_surf = self.info_font.render(f"[{status_text}]", True, WHITE)
        score_surf = self.info_font.render(f"SCORE: {self.score}", True, TRIFORCE_GREEN)

        center_y = panel_rect.centery
        self.screen.blit(title_surf, (40, center_y - title_surf.get_height() // 2))
        
        # Hamburger Menu Area (Right side inside the unified panel)
        divider_x = panel_rect.right - 60
        # Draw a vertical separator line for the settings button
        pygame.draw.line(self.screen, TRIFORCE_GREEN, (divider_x, panel_rect.top), (divider_x, panel_rect.bottom - 1), 2)
        
        # Update settings_btn_rect dynamically to match the integrated section
        self.settings_btn_rect.update(divider_x, panel_rect.top, 60, 50)
        
        # Hamburger lines inside settings_btn_rect
        cx = self.settings_btn_rect.centerx
        cy = self.settings_btn_rect.centery
        w = 18
        pygame.draw.line(self.screen, TRIFORCE_GREEN, (cx - w//2, cy - 6), (cx + w//2, cy - 6), 2)
        pygame.draw.line(self.screen, TRIFORCE_GREEN, (cx - w//2, cy), (cx + w//2, cy), 2)
        pygame.draw.line(self.screen, TRIFORCE_GREEN, (cx - w//2, cy + 6), (cx + w//2, cy + 6), 2)

        # Place score and status to the left of the divider
        score_x = divider_x - score_surf.get_width() - 20
        self.screen.blit(score_surf, (score_x, center_y - score_surf.get_height() // 2))
        
        status_x = score_x - status_surf.get_width() - 30
        self.screen.blit(status_surf, (status_x, center_y - status_surf.get_height() // 2))

    def draw_settings_menu(self):
        if not self.show_settings:
            return
            
        # Draw dark semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Popup box
        pygame.draw.rect(self.screen, SETTINGS_BG, self.popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, TRIFORCE_GREEN, self.popup_rect, width=3, border_radius=15)
        
        title_surf = self.title_font.render("SETTINGS", True, TRIFORCE_GREEN)
        self.screen.blit(title_surf, (self.popup_rect.centerx - title_surf.get_width()//2, self.popup_rect.y + 20))
        
        # Volume info
        vol_pct = int(round(self.volume * 100))
        vol_text = f"Volume: {vol_pct}%" if not self.is_muted else "Volume: MUTED"
        vol_surf = self.info_font.render(vol_text, True, WHITE)
        self.screen.blit(vol_surf, (self.popup_rect.centerx - vol_surf.get_width()//2, self.popup_rect.y + 55))
        
        # Interactive Buttons
        self._draw_button(self.btn_vol_down, "Vol -")
        self._draw_button(self.btn_vol_up, "Vol +")
        
        mute_text = "Unmute" if self.is_muted else "Mute"
        self._draw_button(self.btn_mute, mute_text)
        
        self._draw_button(self.btn_close, "Close")

    def _draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        
        color = TRIFORCE_GREEN if is_hovered else RETRO_MOSS_GREEN
        text_color = DARK_FOREST_SLATE if is_hovered else TRIFORCE_GREEN
        
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        if not is_hovered:
            pygame.draw.rect(self.screen, TRIFORCE_GREEN, rect, width=2, border_radius=8)
            
        text_surf = self.guideline_font.render(text, True, text_color)
        self.screen.blit(text_surf, (rect.centerx - text_surf.get_width()//2, rect.centery - text_surf.get_height()//2))

    def draw_character(self):
        if self.sprite_image:
            self.screen.blit(self.sprite_image, self.sprite_rect)
        else:
            pygame.draw.rect(self.screen, RETRO_MOSS_GREEN, self.sprite_rect, border_radius=10)
            pygame.draw.rect(self.screen, TRIFORCE_GREEN, self.sprite_rect, width=2, border_radius=10)
            
            fallback_text = self.guideline_font.render("Link", True, TRIFORCE_GREEN)
            text_rect = fallback_text.get_rect(center=self.sprite_rect.center)
            self.screen.blit(fallback_text, text_rect)

    def draw_collectible(self):
        points = [
            (self.collectible_rect.centerx, self.collectible_rect.top),
            (self.collectible_rect.right, self.collectible_rect.centery),
            (self.collectible_rect.centerx, self.collectible_rect.bottom),
            (self.collectible_rect.left, self.collectible_rect.centery)
        ]
        pygame.draw.polygon(self.screen, RUPEE_GREEN, points)
        pygame.draw.polygon(self.screen, WHITE, points, width=2)

    def draw_footer(self):
        footer_y = HEIGHT - 80
        guidelines = [
            "[W/A/S/D] or [ARROWS] Move  |  [ESC] or Icon Toggle Settings",
            "[SPACE] Play / Pause Audio | [R] Restart"
        ]
        
        for i, text in enumerate(guidelines):
            guide_surf = self.guideline_font.render(text, True, TRIFORCE_GREEN)
            guide_rect = guide_surf.get_rect(center=(WIDTH // 2, footer_y + i * 25))
            self.screen.blit(guide_surf, guide_rect)

    def render(self):
        self.screen.fill(DARK_FOREST_SLATE)
        
        self.draw_dashboard()
        self.draw_collectible()
        self.draw_character()
        self.draw_footer()
        
        # Render settings menu ON TOP of everything
        self.draw_settings_menu()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.render()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = AudioDashboardApp()
    app.run()
