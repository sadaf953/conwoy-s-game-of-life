import pygame
import numpy as np
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 900  # Doubled the window size
CELL_SIZE = 10  # Increased cell size for better visibility
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)  # Darker gray for less intrusive grid
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Conway's Game of Life - Large Grid")

# Create a grid
grid = np.zeros((ROWS, COLS))

# Drawing modes
DRAW_MODE = 1  # 1 for single cells, 2 for glider, 3 for blinker, 4 for block
drawing = False

def create_glider(x, y):
    """Create a glider pattern at the specified position."""
    positions = [(x-1, y), (x, y+1), (x+1, y-1), (x+1, y), (x+1, y+1)]
    for pos in positions:
        if 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS:
            grid[pos[0], pos[1]] = 1

def create_blinker(x, y):
    """Create a blinker pattern at the specified position."""
    positions = [(x-1, y), (x, y), (x+1, y)]
    for pos in positions:
        if 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS:
            grid[pos[0], pos[1]] = 1

def create_block(x, y):
    """Create a block pattern at the specified position."""
    positions = [(x, y), (x, y+1), (x+1, y), (x+1, y+1)]
    for pos in positions:
        if 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS:
            grid[pos[0], pos[1]] = 1

def create_glider_gun(x, y):
    """Create a Gosper Glider Gun pattern at the specified position."""
    gun = [
        (0, 4), (0, 5), (1, 4), (1, 5),  # Block
        (10, 4), (10, 5), (10, 6), (11, 3), (11, 7), (12, 2), (12, 8),
        (13, 2), (13, 8), (14, 5), (15, 3), (15, 7), (16, 4), (16, 5),
        (16, 6), (17, 5),  # Left gun
        (20, 2), (20, 3), (20, 4), (21, 2), (21, 3), (21, 4), (22, 1),
        (22, 5), (24, 0), (24, 1), (24, 5), (24, 6),  # Right gun
        (34, 2), (34, 3), (35, 2), (35, 3)  # Block
    ]
    for dx, dy in gun:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < ROWS and 0 <= new_y < COLS:
            grid[new_x, new_y] = 1

def count_neighbors(grid, x, y):
    """Count the number of live neighbors for a cell."""
    total = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            row = (x + i + ROWS) % ROWS
            col = (y + j + COLS) % COLS
            total += grid[row, col]
    return total

def update_grid():
    """Update the grid according to Conway's Game of Life rules."""
    new_grid = grid.copy()
    for i in range(ROWS):
        for j in range(COLS):
            neighbors = count_neighbors(grid, i, j)
            if grid[i, j] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[i, j] = 0
            else:
                if neighbors == 3:
                    new_grid[i, j] = 1
    return new_grid

def draw_grid():
    """Draw the current state of the grid."""
    screen.fill(BLACK)
    
    # Draw cells
    for i in range(ROWS):
        for j in range(COLS):
            if grid[i, j] == 1:
                pygame.draw.rect(screen, WHITE, 
                               (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1))

    # Draw grid lines (only if close enough to see them)
    for i in range(ROWS + 1):
        pygame.draw.line(screen, GRAY, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
    for j in range(COLS + 1):
        pygame.draw.line(screen, GRAY, (j * CELL_SIZE, 0), (j * CELL_SIZE, HEIGHT))

    # Draw current mode indicator
    mode_text = {
        1: "Mode: Single Cell",
        2: "Mode: Glider",
        3: "Mode: Blinker",
        4: "Mode: Block",
        5: "Mode: Glider Gun"
    }
    font = pygame.font.Font(None, 48)  # Increased font size
    text = font.render(mode_text[DRAW_MODE], True, GREEN)
    screen.blit(text, (20, 20))
    
    # Draw instructions
    instructions = [
        "Space: Play/Pause",
        "C: Clear Grid",
        "R: Random Grid",
        "1-5: Change Pattern",
        "Left Click: Draw",
        "Right Click: Erase",
        "S: Save Pattern",
        "L: Load Pattern"
    ]
    for i, instruction in enumerate(instructions):
        text = font.render(instruction, True, RED)
        screen.blit(text, (10, 80 + i * 40))

# Main game loop
running = True
paused = True  # Start paused for easier pattern creation
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                grid = np.random.choice([0, 1], size=(ROWS, COLS), p=[0.85, 0.15])
            elif event.key == pygame.K_c:
                grid = np.zeros((ROWS, COLS))
            elif event.key == pygame.K_s:
                np.save('game_of_life_pattern.npy', grid)
            elif event.key == pygame.K_l:
                try:
                    grid = np.load('game_of_life_pattern.npy')
                except:
                    print("No saved pattern found")
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                DRAW_MODE = int(event.unicode)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        
        # Handle drawing while mouse button is held down
        if drawing and paused:
            pos = pygame.mouse.get_pos()
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            
            # Left click to draw, right click to erase
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left click
                    if DRAW_MODE == 1:
                        grid[row, col] = 1
                    elif DRAW_MODE == 2:
                        create_glider(row, col)
                    elif DRAW_MODE == 3:
                        create_blinker(row, col)
                    elif DRAW_MODE == 4:
                        create_block(row, col)
                    elif DRAW_MODE == 5:
                        create_glider_gun(row, col)
                elif pygame.mouse.get_pressed()[2]:  # Right click
                    grid[row, col] = 0

    if not paused:
        grid = update_grid()
    
    draw_grid()
    pygame.display.flip()
    clock.tick(15)  # Slightly increased simulation speed

pygame.quit()