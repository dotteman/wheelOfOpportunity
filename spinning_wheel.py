import pygame
import sys
import math
import random
import logging
import pyperclip  # Import the clipboard library

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1200
HEIGHT = 1000  # Increased height to fit more items
# Adjust CENTER_X to be in the middle of the space left of the CR UI
WHEEL_AREA_WIDTH = WIDTH - 300 - 10
CENTER_X = WHEEL_AREA_WIDTH // 2
CENTER_Y = HEIGHT // 2  # Recalculate vertical center
CENTER = (CENTER_X, CENTER_Y)  # Adjusted center for the wheel
WHEEL_RADIUS = 200
FONT_SIZE = 36  # Slightly larger font size
CR_UI_WIDTH = 300
CR_UI_X = WIDTH - CR_UI_WIDTH - 10  # positions CR UI 10 px from right edge
# Adjust heights for CR List and Assignments boxes based on new HEIGHT
INPUT_AREA_HEIGHT = 100  # Approximate height for input boxes + labels
AVAILABLE_UI_HEIGHT = HEIGHT - INPUT_AREA_HEIGHT - 20  # Total height minus input area and top/bottom padding
BOX_PADDING = 10
CR_LIST_HEIGHT = (AVAILABLE_UI_HEIGHT - BOX_PADDING) // 2
ASSIGNMENTS_HEIGHT = (AVAILABLE_UI_HEIGHT - BOX_PADDING) // 2
ASSIGNMENTS_Y_START = 10 + CR_LIST_HEIGHT + BOX_PADDING  # Position below CR list with padding
MAX_CR_ENTRIES = 8  # Define max number of CRs to keep

# TRON-inspired Colors
TRON_BG = (10, 20, 30)           # Deep blue-black background
TRON_CYAN = (0, 255, 255)        # Neon cyan
TRON_BLUE = (0, 180, 255)        # Neon blue
TRON_ORANGE = (255, 120, 0)      # Neon orange
TRON_YELLOW = (255, 255, 80)     # Neon yellow
TRON_WHITE = (220, 255, 255)     # Pale white/blue
TRON_DARK = (20, 40, 60)         # Slightly lighter than bg
TRON_GRAY = (60, 80, 100)        # For borders/shadows
TRON_BLACK = (0, 0, 0)
TRON_RED = (255, 60, 60)

# Update main color lists for wheel slices and fireworks
COLORS = [
    TRON_CYAN, TRON_BLUE, TRON_ORANGE, TRON_YELLOW, TRON_WHITE, TRON_DARK,
    (0, 200, 255), (0, 255, 200), (255, 200, 0)
]
FIREWORK_COLORS = [
    TRON_CYAN, TRON_BLUE, TRON_ORANGE, TRON_YELLOW, TRON_WHITE, TRON_RED,
    (0, 255, 180), (180, 255, 255)
]

class Particle:
    def __init__(self, x: float, y: float, color: tuple):
        """Initializes a particle at (x, y) with the given color."""
        self.x = x
        self.y = y
        self.color = color
        self.velocity = [random.uniform(-3, 3), random.uniform(-8, -4)]
        self.gravity = 0.1
        self.lifetime = random.randint(40, 80)
        self.size = random.randint(2, 4)
        self.alpha = 255
        self.fade_rate = 255 / self.lifetime
        
    def update(self) -> bool:
        self.velocity[1] += self.gravity
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.alpha = max(0, self.alpha - self.fade_rate)
        return self.lifetime > 0
        
    def draw(self, surface) -> None:
        if self.alpha > 0:
            color_with_alpha = (self.color[0], self.color[1], self.color[2], int(self.alpha))
            temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color_with_alpha, (self.size, self.size), self.size)
            surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class Firework:
    def __init__(self, x: int, y: int):
        """Initializes a firework at position (x, y)."""
        self.x = x
        self.y = y
        self.particles = []
        self.exploded = False
        self.explosion_color = random.choice(FIREWORK_COLORS)
        self.timer = random.randint(5, 15)  # Delay before explosion
        
    def update(self) -> bool:
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0:
                self.explode()
        else:
            self.particles = [p for p in self.particles if p.update()]
        return len(self.particles) > 0 or not self.exploded
        
    def explode(self) -> None:
        self.exploded = True
        num_particles = random.randint(40, 80)
        for _ in range(num_particles):
            self.particles.append(Particle(self.x, self.y, self.explosion_color))
            
    def draw(self, surface) -> None:
        if not self.exploded:
            # Draw the rocket going up
            pygame.draw.rect(surface, self.explosion_color, (self.x - 1, self.y - 4, 2, 4))
        else:
            # Draw all explosion particles
            for particle in self.particles:
                particle.draw(surface)

class SpinningWheel:
    def __init__(self) -> None:
        """Initializes the spinning wheel and its properties."""
        # Use the globally calculated CENTER for this instance
        self.center = CENTER  # Ensure this uses the updated CENTER_Y
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # Update the window title
        pygame.display.set_caption("Wheel of Opportunity")
        self.clock = pygame.time.Clock()
        # Try finding a blocky system font, or suggest loading a pixel font TTF
        try:
            # Attempt to find a monospaced/blocky font
            font_name = pygame.font.match_font('consolas, courier new, monospace')
            self.font = pygame.font.Font(font_name, FONT_SIZE)
        except:
             # Fallback to default font
            self.font = pygame.font.Font(None, FONT_SIZE)
            print("Blocky font not found, using default.")
        # Create a smaller font for CR and assignments at 75% of the current size
        if 'font_name' in locals() and font_name:
            self.small_font = pygame.font.Font(font_name, int(FONT_SIZE * 0.75))
            self.tiny_font = pygame.font.Font(font_name, int(FONT_SIZE * 0.55))
        else:
            self.small_font = pygame.font.Font(None, int(FONT_SIZE * 0.75))
            self.tiny_font = pygame.font.Font(None, int(FONT_SIZE * 0.55))  # Fixed: added closing parenthesis
        
        # Start with an empty list of names
        self.names: list[str] = []
        self.angle: float = 0  # Angle in radians
        self.spinning: bool = False
        self.spin_speed: float = 0
        self.selected_name: str | None = None
        
        # Text input properties
        self.input_text: str = ""
        self.input_active: bool = True  # Start with input active
        self.cursor_visible: bool = True
        self.cursor_time: int = pygame.time.get_ticks()
        
        # Fireworks
        self.fireworks: list[Firework] = []
        self.celebration_active: bool = False
        self.celebration_start_time: int = 0
        self.celebration_duration: int = 5000  # 5 seconds of fireworks

        # New CR input properties
        self.cr_input_text: str = ""
        self.cr_input_active: bool = False
        self.cr_list: list[str] = []
        self.cr_selected: str | None = None
        # Change cr_associations to store one name per CR
        self.cr_associations: dict[str, str | None] = {}

        # Copy Assignments button properties
        self.copy_assignments_button_rect = None  # Store button rect for click detection
        self.copy_feedback_time = 0  # For showing "Copied!" feedback

        # Spin button properties
        self.spin_button_rect = None  # Store spin button rect for click detection

        # Delete icon properties
        self.cr_delete_icon_rects = {}  # Map CR to its delete icon rect
        
    def add_name(self, name: str) -> None:
        """Adds a new name if valid."""
        if name.strip():
            self.names.append(name.strip())
            logging.info(f"Added name: {name}")

    # Updated method: add a CR, limiting the list size and updating associations
    def add_cr(self, cr: str) -> None:
        """Add a new CR if valid, keeping only the latest MAX_CR_ENTRIES."""
        cr_stripped = cr.strip()
        if cr_stripped:
            # Remove oldest if list is full and delete its association too
            if len(self.cr_list) >= MAX_CR_ENTRIES:
                old_cr = self.cr_list.pop(0)  # Remove the first (oldest) item
                if old_cr in self.cr_associations:
                    del self.cr_associations[old_cr]
            self.cr_list.append(cr_stripped)
            # Initialize association for new CR
            self.cr_associations[cr_stripped] = None
            logging.info(f"Added CR: {cr_stripped}. List size: {len(self.cr_list)}")
    
    def draw_wheel(self) -> None:
        # Use TRON background
        self.screen.fill(TRON_BG)
        
        # Draw active fireworks in the background
        for firework in self.fireworks:
            firework.draw(self.screen)
        
        # ALWAYS draw the input instructions and box, even if there are no names
        # Input box label - Use TRON_WHITE
        label = self.font.render("TYPE NAMES HERE:", True, TRON_WHITE)
        self.screen.blit(label, (10, HEIGHT - 80))
        
        # Input box: neon cyan border, dark bg
        input_box = pygame.Rect(10, HEIGHT - 50, 300, 40)
        pygame.draw.rect(self.screen, TRON_DARK, input_box)
        border_color = TRON_CYAN if self.input_active else TRON_GRAY
        pygame.draw.rect(self.screen, border_color, input_box, 4)
        
        # Draw text in input box - TRON_WHITE text
        text_surface = self.font.render(self.input_text, True, TRON_WHITE)
        self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        
        # Draw cursor - Neon cyan
        if self.input_active and self.cursor_visible:
            cursor_pos = (input_box.x + 10 + text_surface.get_width(), input_box.y + 10)
            pygame.draw.line(self.screen, TRON_CYAN,
                           cursor_pos,
                           (cursor_pos[0], cursor_pos[1] + text_surface.get_height()),
                           3)
        
        # Draw "Spin the Wheel" button at the bottom right of the input area, right of the input box
        spin_btn_width = 220
        spin_btn_height = 40  # Match input box height (input box is 40)
        spin_btn_x = 10 + 300 + 20  # 10 (left margin) + 300 (input box width) + 20 (gap)
        spin_btn_y = HEIGHT - 50  # Align with input box (input box y)
        self.spin_button_rect = pygame.Rect(spin_btn_x, spin_btn_y, spin_btn_width, spin_btn_height)
        pygame.draw.rect(self.screen, TRON_BLUE, self.spin_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, TRON_CYAN, self.spin_button_rect, 2, border_radius=8)
        spin_btn_text = self.small_font.render("Spin the Wheel", True, TRON_WHITE)
        self.screen.blit(
            spin_btn_text,
            (self.spin_button_rect.centerx - spin_btn_text.get_width() // 2, self.spin_button_rect.centery - spin_btn_text.get_height() // 2)
        )
        
        if not self.names:
            # Instructions text - Use TRON_WHITE
            text1 = self.font.render("Enter names in the box below", True, TRON_WHITE)
            text2 = self.font.render("Press ENTER after each name", True, TRON_WHITE)
            text_rect1 = text1.get_rect(center=(self.center[0], self.center[1] - 50))
            text_rect2 = text2.get_rect(center=(self.center[0], self.center[1]))
            self.screen.blit(text1, text_rect1)
            self.screen.blit(text2, text_rect2)
            
            # Draw an empty wheel outline to indicate where the wheel will appear
            pygame.draw.circle(self.screen, TRON_CYAN, self.center, WHEEL_RADIUS, 2)
            return
        
        # Calculate slice angle in radians
        slice_angle = 2 * math.pi / len(self.names)
        
        # Draw each slice using TRON colors
        for i, name in enumerate(self.names):
            start_angle = i * slice_angle + self.angle
            end_angle = (i + 1) * slice_angle + self.angle
            
            # Draw the slice as a polygon
            points = [self.center]
            for j in range(21):  # Use 20 segments for smooth arc
                a = start_angle + (end_angle - start_angle) * j / 20
                x = self.center[0] + WHEEL_RADIUS * math.cos(a)
                y = self.center[1] + WHEEL_RADIUS * math.sin(a)
                points.append((x, y))
            
            # Draw slice with TRON color and neon cyan border
            pygame.draw.polygon(self.screen, COLORS[i % len(COLORS)], points)
            pygame.draw.polygon(self.screen, TRON_CYAN, points, 2)
            
            # Draw the name - Black, bold text
            mid_angle = (start_angle + end_angle) / 2
            # Use bold font for names on the wheel
            try:
                bold_font = pygame.font.Font(self.font.get_name(), self.font.get_height())
                bold_font.set_bold(True)
            except Exception:
                bold_font = self.font
            text = bold_font.render(name, True, TRON_BLACK)
            text_x = self.center[0] + (WHEEL_RADIUS * 0.7) * math.cos(mid_angle) - text.get_width() / 2
            text_y = self.center[1] + (WHEEL_RADIUS * 0.7) * math.sin(mid_angle) - text.get_height() / 2
            self.screen.blit(text, (text_x, text_y))
        
        # Draw pointer - Neon orange triangle
        pointer_points = [
            (self.center[0], self.center[1] - WHEEL_RADIUS - 20),
            (self.center[0] - 10, self.center[1] - WHEEL_RADIUS),
            (self.center[0] + 10, self.center[1] - WHEEL_RADIUS)
        ]
        pygame.draw.polygon(self.screen, TRON_ORANGE, pointer_points)
        pygame.draw.circle(self.screen, TRON_BG, (self.center[0], self.center[1] - WHEEL_RADIUS), 5)
        
        # Draw a line from center to selection - Neon orange
        if not self.spinning and self.selected_name:
            pygame.draw.line(self.screen, TRON_ORANGE, self.center, (self.center[0], self.center[1] - WHEEL_RADIUS), 2)
        
        # Draw instructions - Neon white, highlight selected name with neon red bg
        instructions_prefix = [
            "Enter names in the box below, press Enter",
            "Selected: "  # Prefix for the selected name line
        ]
        y_offset = 10
        prefix_x = 10
        for i, prefix_str in enumerate(instructions_prefix):
            # Render and draw the prefix text
            prefix_text_surface = self.font.render(prefix_str, True, TRON_WHITE)
            self.screen.blit(prefix_text_surface, (prefix_x, y_offset))
            current_x = prefix_x + prefix_text_surface.get_width()  # Keep track of horizontal position

            # Special handling for the "Selected:" line
            if i == 1 and self.selected_name:
                # Render name in neon white
                name_text_surface = self.font.render(self.selected_name, True, TRON_WHITE)
                name_rect = name_text_surface.get_rect(topleft=(current_x, y_offset))

                # Draw neon red background rectangle behind the name
                pygame.draw.rect(self.screen, TRON_RED, name_rect)

                # Draw the neon white name text on top of the neon red background
                self.screen.blit(name_text_surface, name_rect.topleft)

            # Update y_offset for the next line, using the height of the prefix
            y_offset += prefix_text_surface.get_height() + 5  # Use consistent spacing

        # After drawing instructions, add CR UI on the right:
        self.draw_cr_input_box()
        self.draw_cr_list()
        self.draw_cr_associations()
    
    def draw_cr_input_box(self) -> None:
        """Draw the CR input box - TRON Style."""
        cr_label = self.tiny_font.render("ENTER CR:", True, TRON_WHITE)  # Use tiny font
        self.screen.blit(cr_label, (CR_UI_X, HEIGHT - 80))
        cr_box = pygame.Rect(CR_UI_X, HEIGHT - 50, CR_UI_WIDTH, 40)
        pygame.draw.rect(self.screen, TRON_DARK, cr_box)  # Dark background
        border_color = TRON_CYAN if self.cr_input_active else TRON_GRAY  # Neon cyan border when active
        pygame.draw.rect(self.screen, border_color, cr_box, 4)  # No border_radius
        cr_text_surf = self.tiny_font.render(self.cr_input_text, True, TRON_WHITE)  # Neon white text
        self.screen.blit(cr_text_surf, (cr_box.x + 10, cr_box.y + 10))
        # Draw cursor if CR input is active
        if self.cr_input_active and self.cursor_visible:
             cursor_pos = (cr_box.x + 10 + cr_text_surf.get_width(), cr_box.y + 10)
             pygame.draw.line(self.screen, TRON_CYAN,
                            cursor_pos,
                            (cursor_pos[0], cursor_pos[1] + cr_text_surf.get_height()),
                            3)
    
    def draw_cr_list(self) -> None:
        """Draw the list of CR entries - TRON Style, with delete icon."""
        list_box = pygame.Rect(CR_UI_X, 10, CR_UI_WIDTH, CR_LIST_HEIGHT)
        pygame.draw.rect(self.screen, TRON_DARK, list_box)
        pygame.draw.rect(self.screen, TRON_CYAN, list_box, 2)
        y_offset = list_box.y + 10
        title = self.tiny_font.render("CRs:", True, TRON_WHITE)
        self.screen.blit(title, (list_box.x + 10, y_offset))
        y_offset += title.get_height() + 5

        self.cr_delete_icon_rects = {}  # Reset mapping each frame

        for cr in self.cr_list:
            available_width = list_box.width - 20 - 28  # Reserve space for delete icon (24px + gap)
            cr_display_text = cr
            cr_text_surface = self.tiny_font.render(cr_display_text, True, TRON_WHITE)
            while cr_text_surface.get_width() > available_width and len(cr_display_text) > 0:
                cr_display_text = cr_display_text[:-1]
                cr_text_surface = self.tiny_font.render(cr_display_text + "...", True, TRON_WHITE)

            entry_rect = pygame.Rect(list_box.x + 10, y_offset, list_box.width - 20, cr_text_surface.get_height())
            text_color = TRON_WHITE
            if self.cr_selected == cr:
                pygame.draw.rect(self.screen, TRON_ORANGE, entry_rect)
                text_color = TRON_BLACK

            final_text_surface = self.tiny_font.render(cr_display_text + ("..." if cr_display_text != cr else ""), True, text_color)
            self.screen.blit(final_text_surface, (entry_rect.x, entry_rect.y))

            # Draw delete icon (simple X) at right side of entry_rect
            icon_size = 18
            icon_margin = 6
            icon_x = entry_rect.right - icon_size - icon_margin
            icon_y = entry_rect.y + (entry_rect.height - icon_size) // 2
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
            self.cr_delete_icon_rects[cr] = icon_rect
            # Draw a neon cyan border for the icon
            pygame.draw.rect(self.screen, TRON_CYAN, icon_rect, border_radius=4)
            # Draw X in the icon
            pygame.draw.line(self.screen, TRON_RED, (icon_rect.left+4, icon_rect.top+4), (icon_rect.right-4, icon_rect.bottom-4), 2)
            pygame.draw.line(self.screen, TRON_RED, (icon_rect.left+4, icon_rect.bottom-4), (icon_rect.right-4, icon_rect.top+4), 2)

            y_offset += final_text_surface.get_height() + 5
            if y_offset + final_text_surface.get_height() > list_box.bottom - 10:
                break
    
    def draw_cr_associations(self) -> None:
        """Draw the CR assignments - TRON Style, with Copy button at the bottom inside the box."""
        assoc_box = pygame.Rect(CR_UI_X, ASSIGNMENTS_Y_START, CR_UI_WIDTH, ASSIGNMENTS_HEIGHT)
        pygame.draw.rect(self.screen, TRON_DARK, assoc_box)
        pygame.draw.rect(self.screen, TRON_CYAN, assoc_box, 2)
        y_offset = assoc_box.y + 10

        # Draw "Assignments:" title
        title = self.tiny_font.render("Assignments:", True, TRON_WHITE)  # Neon white text
        self.screen.blit(title, (assoc_box.x + 10, y_offset))
        y_offset += title.get_height() + 5

        # Reserve space for the button at the bottom
        button_height = 48  # Increased height
        button_width = 260  # Increased width
        button_x = assoc_box.x + (assoc_box.width - button_width) // 2
        button_y = assoc_box.bottom - button_height - 10
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        self.copy_assignments_button_rect = button_rect

        # Draw assignments list (stop if would overlap button)
        max_y = button_y - 8
        for cr, name in self.cr_associations.items():
            if name is not None:
                line = f"{cr}: {name}"
                available_width = assoc_box.width - 20
                display_line = line
                line_text_surface = self.tiny_font.render(display_line, True, TRON_WHITE)  # Neon white text
                while line_text_surface.get_width() > available_width and len(display_line) > 0:
                    display_line = display_line[:-1]
                    line_text_surface = self.tiny_font.render(display_line + "...", True, TRON_WHITE)
                final_line_text = self.tiny_font.render(display_line + ("..." if display_line != line else ""), True, TRON_WHITE)  # Neon white text
                if y_offset + final_line_text.get_height() > max_y:
                    pygame.draw.rect(self.screen, TRON_BG, (assoc_box.x + 5, max_y, assoc_box.width - 10, 10))
                    more_text = self.tiny_font.render("...", True, TRON_WHITE)  # Neon white text
                    self.screen.blit(more_text, (assoc_box.centerx - more_text.get_width() // 2, max_y))
                    break
                self.screen.blit(final_line_text, (assoc_box.x + 10, y_offset))
                y_offset += final_line_text.get_height() + 2

        # Draw "Copy Assignments" button at the bottom inside the box
        pygame.draw.rect(self.screen, TRON_BLUE, button_rect, border_radius=8)
        pygame.draw.rect(self.screen, TRON_CYAN, button_rect, 2, border_radius=8)
        btn_text = self.tiny_font.render("Copy Assignments", True, TRON_WHITE)  # Neon white text
        self.screen.blit(
            btn_text,
            (button_rect.centerx - btn_text.get_width() // 2, button_rect.centery - btn_text.get_height() // 2)
        )

        # Show "Copied!" feedback for 1.2 seconds after copying
        if self.copy_feedback_time and pygame.time.get_ticks() - self.copy_feedback_time < 1200:
            copied_text = self.tiny_font.render("Copied!", True, TRON_CYAN)  # Neon cyan text
            self.screen.blit(
                copied_text,
                (button_rect.centerx - copied_text.get_width() // 2, button_rect.top - copied_text.get_height() - 2)
            )

    def copy_assignments_to_clipboard(self):
        """Copy all assignments to clipboard as plain text."""
        lines = []
        for cr, name in self.cr_associations.items():
            if name is not None:
                lines.append(f"{cr}: {name}")
        if lines:
            pyperclip.copy('\n'.join(lines))
            self.copy_feedback_time = pygame.time.get_ticks()
        else:
            self.copy_feedback_time = 0
    
    def start_celebration(self):
        self.celebration_active = True
        self.celebration_start_time = pygame.time.get_ticks()
        
    def update_fireworks(self):
        # Create new fireworks during celebration
        if self.celebration_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.celebration_start_time > self.celebration_duration:
                self.celebration_active = False
            
            # Add new fireworks randomly during celebration
            if random.random() < 0.1:  # 10% chance each frame
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 200)  # Keep above the bottom area
                self.fireworks.append(Firework(x, y))
        
        # Update existing fireworks
        self.fireworks = [fw for fw in self.fireworks if fw.update()]
    
    def spin(self):
        if not self.spinning and self.names:
            self.spinning = True
            self.spin_speed = random.uniform(0.05, 0.2)  # In radians
            self.selected_name = None
            
    def update(self):
        # Update cursor blinking - only blink if one of the inputs is active
        if self.input_active or self.cr_input_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.cursor_time > 500:  # Blink every 500ms
                self.cursor_visible = not self.cursor_visible
                self.cursor_time = current_time
        else:
             self.cursor_visible = False  # Hide cursor if no input is active
        
        # Update fireworks
        self.update_fireworks()
        
        # Update wheel spinning
        if self.spinning:
            self.angle += self.spin_speed
            self.spin_speed *= 0.99  # Apply friction
            
            # Keep angle within 0-2π
            self.angle %= (2 * math.pi)
            
            if self.spin_speed < 0.01:
                self.spinning = False
                self.spin_speed = 0
                
                # Find which slice is at the top (270 degrees or 3π/2)
                top_angle = 3 * math.pi / 2  # This is our pointer position
                
                # Calculate the relative angle
                relative_angle = (top_angle - self.angle) % (2 * math.pi)
                slice_angle = 2 * math.pi / len(self.names)
                selected_index = int(relative_angle / slice_angle) % len(self.names)
                self.selected_name = self.names[selected_index]
                
                print(f"Selected: {self.selected_name}")
                
                # Start fireworks celebration when wheel stops
                self.start_celebration()

                # If no CR is currently selected, auto select the first one if present
                if not self.cr_selected and self.cr_list:
                    self.cr_selected = self.cr_list[0]
                
                # Assign the selected name to the chosen CR
                if self.cr_selected:
                    self.cr_associations[self.cr_selected] = self.selected_name
                    logging.info(f"Assigned {self.selected_name} to CR {self.cr_selected}")
        
    def run(self):
        running = True
        
        # Print console message to help debug
        print("Spinning wheel started. You should see a yellow input box at the bottom of the screen.")
        print("Click in the yellow box and type names, then press Enter after each name.")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Get pressed keys and modifier state
                    mods = pygame.key.get_mods()
                    is_ctrl_pressed = mods & pygame.KMOD_CTRL

                    # Handle Paste (Ctrl+V)
                    if is_ctrl_pressed and event.key == pygame.K_v:
                        try:
                            pasted_text = pyperclip.paste()
                            if pasted_text:  # Check if clipboard has text
                                if self.input_active:
                                    self.input_text += pasted_text
                                elif self.cr_input_active:
                                    self.cr_input_text += pasted_text
                                # Reset cursor blink on paste
                                self.cursor_visible = True
                                self.cursor_time = pygame.time.get_ticks()
                        except pyperclip.PyperclipException as e:
                            logging.error(f"Clipboard error: {e}")
                        # Skip further processing for Ctrl+V
                        continue

                    if self.input_active:
                        if event.key == pygame.K_RETURN:
                            self.add_name(self.input_text)
                            self.input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif not is_ctrl_pressed:
                            self.input_text += event.unicode
                        self.cursor_visible = True
                        self.cursor_time = pygame.time.get_ticks()
                    elif self.cr_input_active:
                        if event.key == pygame.K_RETURN:
                            self.add_cr(self.cr_input_text)
                            self.cr_input_text = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.cr_input_text = self.cr_input_text[:-1]
                        elif not is_ctrl_pressed:
                            self.cr_input_text += event.unicode
                        self.cursor_visible = True
                        self.cursor_time = pygame.time.get_ticks()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    cr_box = pygame.Rect(CR_UI_X, HEIGHT - 50, CR_UI_WIDTH, 40)
                    name_box = pygame.Rect(10, HEIGHT - 50, 300, 40)
                    cr_list_box = pygame.Rect(CR_UI_X, 10, CR_UI_WIDTH, CR_LIST_HEIGHT)

                    # --- Spin the Wheel button click detection ---
                    if self.spin_button_rect and self.spin_button_rect.collidepoint(mouse_pos):
                        self.spin()
                        continue

                    # --- Copy Assignments button click detection ---
                    if self.copy_assignments_button_rect and self.copy_assignments_button_rect.collidepoint(mouse_pos):
                        self.copy_assignments_to_clipboard()
                        continue

                    # --- Delete CR icon click detection ---
                    for cr, icon_rect in list(self.cr_delete_icon_rects.items()):
                        if icon_rect.collidepoint(mouse_pos):
                            # Remove CR and its assignment
                            if cr in self.cr_list:
                                self.cr_list.remove(cr)
                            if cr in self.cr_associations:
                                del self.cr_associations[cr]
                            if self.cr_selected == cr:
                                self.cr_selected = None
                            continue  # Don't process further for this click

                    # --- Assign user to CR: Click a CR, then click a name on the wheel ---
                    # Detect click in CR list
                    if cr_list_box.collidepoint(mouse_pos):
                        self.input_active = False
                        self.cr_input_active = False
                        title_height = self.tiny_font.render("CRs:", True, TRON_WHITE).get_height()
                        y_offset = cr_list_box.y + 10 + title_height + 5
                        for cr in self.cr_list:
                            available_width = cr_list_box.width - 20
                            cr_display_text = cr
                            temp_text_surface = self.tiny_font.render(cr_display_text, True, TRON_WHITE)
                            while temp_text_surface.get_width() > available_width and len(cr_display_text) > 0:
                                cr_display_text = cr_display_text[:-1]
                                temp_text_surface = self.tiny_font.render(cr_display_text + "...", True, TRON_WHITE)
                            final_text_surface = self.tiny_font.render(cr_display_text + ("..." if cr_display_text != cr else ""), True, TRON_WHITE)
                            text_height = final_text_surface.get_height()
                            entry_rect = pygame.Rect(cr_list_box.x + 10, y_offset, cr_list_box.width - 20, text_height)
                            if entry_rect.collidepoint(mouse_pos):
                                self.cr_selected = cr
                                self.awaiting_user_assignment = True  # New flag: waiting for user click
                                break
                            y_offset += text_height + 5
                            if y_offset > cr_list_box.bottom - 10:
                                break
                        continue  # Don't deactivate input if clicking CR list

                    # If awaiting user assignment, check if a name on the wheel was clicked
                    if hasattr(self, "awaiting_user_assignment") and self.awaiting_user_assignment and self.cr_selected and self.names:
                        # Detect click on a name on the wheel
                        slice_angle = 2 * math.pi / len(self.names)
                        for i, name in enumerate(self.names):
                            mid_angle = (i + 0.5) * slice_angle + self.angle
                            name_x = self.center[0] + (WHEEL_RADIUS * 0.7) * math.cos(mid_angle)
                            name_y = self.center[1] + (WHEEL_RADIUS * 0.7) * math.sin(mid_angle)
                            # Use bold font for hit detection as well
                            try:
                                bold_font = pygame.font.Font(self.font.get_name(), self.font.get_height())
                                bold_font.set_bold(True)
                            except Exception:
                                bold_font = self.font
                            text_surface = bold_font.render(name, True, TRON_BLACK)
                            text_rect = text_surface.get_rect(center=(name_x, name_y))
                            if text_rect.collidepoint(mouse_pos):
                                # Assign this user to the selected CR
                                self.cr_associations[self.cr_selected] = name
                                self.awaiting_user_assignment = False
                                break

                    if cr_box.collidepoint(mouse_pos):
                        self.cr_input_active = True
                        self.input_active = False
                        self.cursor_visible = True
                        self.cursor_time = pygame.time.get_ticks()
                    elif name_box.collidepoint(mouse_pos):
                        self.input_active = True
                        self.cr_input_active = False
                        self.cursor_visible = True
                        self.cursor_time = pygame.time.get_ticks()
                    else:
                        self.input_active = False
                        self.cr_input_active = False

                    if self.input_active or self.cr_input_active:
                        self.cursor_visible = True
                        self.cursor_time = pygame.time.get_ticks()
            
            self.update()
            self.draw_wheel()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    wheel = SpinningWheel()
    wheel.run()
