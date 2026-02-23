import pygame
import json
import time
import sys
import os

# --- Configuration ---
FREQS = {'A': 8.0, 'B': 10.0, 'C': 12.0} # Frequencies used in almost every scene
FPS = 60
WIDTH, HEIGHT = 1000, 700
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
HIGHLIGHT = (0, 255, 255)
YELLOW = (255, 255, 0)

STATE_FILE = "state.json"

# Hierarchy Mapping
HIERARCHY = {
    "ROOT": ["A-M", "N-Z", "UTILS"],
    "A-M": ["A-D", "E-I", "J-M"],
    "N-Z": ["N-S", "T-W", "X-Z"],
    "UTILS": ["SPACE", "DELETE", "ROOT"],
    "A-D": ["A", "B", "C-D"],
    "E-I": ["E-G", "H", "I"],
    "J-M": ["J", "K", "L-M"],
    "N-S": ["N-P", "Q", "R-S"],
    "T-W": ["T", "U", "V-W"],
    "X-Z": ["X", "Y", "Z"],
}

def get_labels_for_scene(scene):
    if scene in HIERARCHY:
        return HIERARCHY[scene]
    
    # Sub-sub groups
    if scene == "C-D": return ["C", "D", "BACK"]
    if scene == "E-G": return ["E", "F", "G"]
    if scene == "L-M": return ["L", "M", "BACK"]
    if scene == "N-P": return ["N", "O", "P"]
    if scene == "R-S": return ["R", "S", "BACK"]
    if scene == "V-W": return ["V", "W", "BACK"]
    
    return []

BLUE = (0, 100, 255)

STATE_FILE = "state.json"

def read_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"scene": "ROOT", "highlight_idx": 1}

class Box:
    def __init__(self, label, pos):
        self.label = label
        self.pos = pos

    def draw(self, surface, font, is_focused=False, is_selected=False):
        # Base color
        rect_color = GRAY
        if is_selected:
            rect_color = YELLOW
        
        # Border for focus
        rect = pygame.Rect(self.pos[0] - 100, self.pos[1] - 90, 200, 180)
        pygame.draw.rect(surface, rect_color, rect)
        
        if is_focused:
            pygame.draw.rect(surface, BLUE, rect, 8) # Thick blue border
            
        text_surf = font.render(self.label, True, WHITE)
        text_rect = text_surf.get_rect(center=self.pos)
        surface.blit(text_surf, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mental Motion Speller")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 48, bold=True)
    header_font = pygame.font.SysFont("Arial", 24)

    current_scene_name = ""
    boxes = []

    running = True
    while running:
        # Check for state changes
        state = read_state()
        new_scene = state.get("scene", "ROOT")
        highlight_idx = state.get("highlight_idx", 1)
        selection_idx = state.get("selection_idx", -1)
        h_time = state.get("highlight_time", 0)
        
        # Keep highlight for 0.5 seconds
        show_yellow = (time.time() - h_time < 0.5)

        if new_scene != current_scene_name:
            current_scene_name = new_scene
            # Get labels for the new scene
            labels = get_labels_for_scene(current_scene_name)
            
            # Re-initialize stimuli
            boxes = []
            positions = [(WIDTH // 4, HEIGHT // 2), (WIDTH // 2, HEIGHT // 2), (3 * WIDTH // 4, HEIGHT // 2)]
            
            for i, label in enumerate(labels):
                if i < 3:
                    boxes.append(Box(label, positions[i]))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        
        # Header
        header = header_font.render(f"Current Level: {current_scene_name} | Tilt head to navigate, Blink to select", True, HIGHLIGHT)
        screen.blit(header, (20, 20))

        # Mental Intensity Bar
        focus_score = state.get("focus_score", 0.0)
        bar_width = 300
        bar_height = 20
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - bar_width//2, 60, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 100), (WIDTH//2 - bar_width//2, 60, int(bar_width * focus_score), bar_height))
        intensity_label = header_font.render(f"Focus Intensity: {int(focus_score * 100)}%", True, WHITE)
        screen.blit(intensity_label, (WIDTH//2 - bar_width//2, 85))

        # Draw boxes
        for i, box in enumerate(boxes):
            is_f = (i == highlight_idx)
            is_s = show_yellow and (i == selection_idx)
            box.draw(screen, font, is_focused=is_f, is_selected=is_s)

        pygame.display.flip()
        clock.tick(30) # No need for high FPS anymore

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
