import pygame
import sys
import time
import random # Added for ghost's random move if stuck
from algorithm import PathfindingAlgorithms

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 700
GRID_SIZE = 30
ROWS, COLS = 20, 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 182, 193)  # Ghost color
GHOST_PENALTY_TIME = 5  # Seconds added to timer if caught

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Algorithm Comparison with Ghost") # Updated Caption
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20)
big_font = pygame.font.SysFont('Arial', 32)

class GameState:
    MENU = "menu"
    PLAYING = "playing"
    FINISHED = "finished" # This state might be implicitly handled by game_completed flag
    RESULTS = "results"

class PacmanGame:
    def __init__(self):
        self.grid = []
        self.pacman_pos = None
        self.food_positions = set()
        self.original_food_positions = set()
        self.score = 0
        self.start_time = None
        self.end_time = None
        self.game_completed = False
        self.pathfinder = None
        self.current_algorithm = None
        self.state = GameState.MENU
        self.results = {}  # Store results for each algorithm
        self.tested_algorithms = set()

        # Ghost attributes
        self.ghost_pos = None
        self.initial_ghost_pos = (ROWS - 2, COLS - 2) 
        self.ghost_move_interval = 0.3  # Seconds, ghost moves
        self.ghost_last_move_time = 0
        self.pacman_caught_count = 0
        self.time_penalty = 0 # Total time penalty from being caught in current run

        self.current_path_to_food = [] # Pacman's current path

        self.create_grid()
        self.pathfinder = PathfindingAlgorithms(self.grid)

    def create_grid(self):
        """Create the maze layout"""
        maze = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1], # Pacman at (1,1)
            [1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1],
            [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1], # Ghost near (18,18) -> (ROWS-2, COLS-2)
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        self.grid = maze
        self.food_positions.clear()
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == 0:
                    self.food_positions.add((r, c))
        
        self.original_food_positions = self.food_positions.copy()
        self.pacman_pos = (1, 1)
        self.food_positions.discard(self.pacman_pos)
        self.original_food_positions.discard(self.pacman_pos)

        # Initialize ghost position safely
        self.ghost_pos = self.initial_ghost_pos
        if self.grid[self.ghost_pos[0]][self.ghost_pos[1]] == 1 or self.ghost_pos == self.pacman_pos:
            found_valid_ghost_start = False
            for r_idx in range(ROWS - 2, 0, -1):
                for c_idx in range(COLS - 2, 0, -1):
                    if self.grid[r_idx][c_idx] == 0 and (r_idx, c_idx) != self.pacman_pos:
                        self.ghost_pos = (r_idx, c_idx)
                        found_valid_ghost_start = True
                        break
                if found_valid_ghost_start:
                    break
            if not found_valid_ghost_start: # Fallback if no good spot found (should not happen in this map)
                 self.ghost_pos = (ROWS - 2, 1) if self.grid[ROWS-2][1] == 0 else (1, COLS-2)


        self.food_positions.discard(self.ghost_pos) # Ghost doesn't sit on food
        self.original_food_positions.discard(self.ghost_pos)

    def reset_game(self):
        self.food_positions = self.original_food_positions.copy()
        self.pacman_pos = (1, 1)
        
        # Reset ghost position safely
        self.ghost_pos = self.initial_ghost_pos
        if self.grid[self.ghost_pos[0]][self.ghost_pos[1]] == 1 or self.ghost_pos == self.pacman_pos:
            found_valid_ghost_start = False
            for r_idx in range(ROWS - 2, 0, -1):
                for c_idx in range(COLS - 2, 0, -1):
                    if self.grid[r_idx][c_idx] == 0 and (r_idx, c_idx) != self.pacman_pos:
                        self.ghost_pos = (r_idx, c_idx)
                        found_valid_ghost_start = True
                        break
                if found_valid_ghost_start:
                    break
            if not found_valid_ghost_start:
                 self.ghost_pos = (ROWS - 2, 1) if self.grid[ROWS-2][1] == 0 and (ROWS-2,1) != self.pacman_pos else (1, COLS-2)


        self.score = 0
        self.start_time = None
        self.end_time = None
        self.game_completed = False
        self.pacman_caught_count = 0
        self.time_penalty = 0
        self.current_path_to_food = []
        self.ghost_last_move_time = 0

    def draw_menu(self):
        screen.fill(BLACK)
        title = big_font.render("Choose Pathfinding Algorithm", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        algorithms = [
            ("1. BFS (Breadth-First Search)", BLUE),
            ("2. Dijkstra's Algorithm", RED),
            ("3. A* (A-Star Search)", GREEN)
        ]
        for i, (text, color) in enumerate(algorithms):
            algo_key = ['bfs', 'dijkstra', 'astar'][i]
            if algo_key in self.tested_algorithms:
                text += " - COMPLETED"
                # Try to show time if available
                if algo_key in self.results:
                     text += f" ({self.results[algo_key]:.2f}s)"
                color = (128, 128, 128)
            
            algo_text = font.render(text, True, color)
            screen.blit(algo_text, (WIDTH // 2 - 200, 200 + i * 50)) # Adjusted x for longer text
        
        instruction_text = "Press number to test. Ghost is active!" if len(self.tested_algorithms) == 0 else f"Test remaining algorithms ({3-len(self.tested_algorithms)} left). Ghost active!"
        instruction = font.render(instruction_text, True, WHITE)
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, 400))
        screen.blit(instruction, instruction_rect)
        
        if self.tested_algorithms:
            tested_text = font.render(f"Algorithms tested: {len(self.tested_algorithms)}/3", True, YELLOW)
            tested_rect = tested_text.get_rect(center=(WIDTH // 2, 450))
            screen.blit(tested_text, tested_rect)
        pygame.display.flip()

    def draw_game(self):
        screen.fill(BLACK)
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == 1:
                    pygame.draw.rect(screen, BLUE, (c * GRID_SIZE, r * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        for food in self.food_positions:
            pygame.draw.circle(screen, WHITE, (food[1] * GRID_SIZE + GRID_SIZE // 2, food[0] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 8)
        
        pygame.draw.circle(screen, YELLOW, (self.pacman_pos[1] * GRID_SIZE + GRID_SIZE // 2, self.pacman_pos[0] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2)
        
        # Draw Ghost
        if self.ghost_pos:
            pygame.draw.circle(screen, PINK, (self.ghost_pos[1] * GRID_SIZE + GRID_SIZE // 2, self.ghost_pos[0] * GRID_SIZE + GRID_SIZE // 2), GRID_SIZE // 2 - 1)
            # Simple eyes for ghost
            eye_r = GRID_SIZE // 8
            eye_offset_x = GRID_SIZE // 5
            pupil_r = GRID_SIZE // 12
            pygame.draw.circle(screen, WHITE, (self.ghost_pos[1] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x, self.ghost_pos[0] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x//2), eye_r)
            pygame.draw.circle(screen, WHITE, (self.ghost_pos[1] * GRID_SIZE + GRID_SIZE // 2 + eye_offset_x, self.ghost_pos[0] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x//2), eye_r)
            pygame.draw.circle(screen, BLACK, (self.ghost_pos[1] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x, self.ghost_pos[0] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x//2), pupil_r)
            pygame.draw.circle(screen, BLACK, (self.ghost_pos[1] * GRID_SIZE + GRID_SIZE // 2 + eye_offset_x, self.ghost_pos[0] * GRID_SIZE + GRID_SIZE // 2 - eye_offset_x//2), pupil_r)


        algo_name_disp = self.current_algorithm.upper() if self.current_algorithm else "N/A"
        if algo_name_disp == 'DIJKSTRA': algo_name_disp = "DIJKSTRA'S"
        algo_text = font.render(f'Algorithm: {algo_name_disp}', True, WHITE)
        screen.blit(algo_text, (10, HEIGHT - 160)) # Adjusted Y position

        score_text = font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, HEIGHT - 140))

        food_text = font.render(f'Food Left: {len(self.food_positions)}', True, WHITE)
        screen.blit(food_text, (10, HEIGHT - 120))
        
        caught_info_text = f'Caught: {self.pacman_caught_count} | Penalty: {self.time_penalty:.2f}s'
        caught_text = font.render(caught_info_text, True, RED)
        screen.blit(caught_text, (10, HEIGHT - 100))

        if self.start_time:
            current_total_time = (time.time() - self.start_time) + self.time_penalty
            if self.game_completed and self.end_time:
                current_total_time = (self.end_time - self.start_time) + self.time_penalty
                time_disp_text = f'Final Time: {current_total_time:.2f}s'
                time_color = GREEN
            else:
                time_disp_text = f'Time: {current_total_time:.2f}s'
                time_color = WHITE
            time_text_surf = font.render(time_disp_text, True, time_color)
            screen.blit(time_text_surf, (10, HEIGHT - 80))
        
        if self.game_completed:
            completion_text = font.render('Algorithm Run Complete!', True, GREEN) # Changed text
            text_rect = completion_text.get_rect(center=(WIDTH // 2, HEIGHT - 40))
            screen.blit(completion_text, text_rect)
            continue_text = font.render('Press SPACE for Menu / Results', True, WHITE) # Changed text
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT - 20))
            screen.blit(continue_text, continue_rect)
        pygame.display.flip()

    def draw_results(self):
        screen.fill(BLACK)
        title = big_font.render("Algorithm Performance Results", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)
        
        sorted_results_list = sorted(self.results.items(), key=lambda x: x[1])
        rank_colors = [GREEN, YELLOW, ORANGE] 
        
        y_pos = 150
        for i, (algo, time_val) in enumerate(sorted_results_list):
            rank = i + 1
            color = rank_colors[i] if i < len(rank_colors) else WHITE
            display_name = algo.upper()
            if display_name == 'DIJKSTRA': display_name = "DIJKSTRA'S"
            
            # Assuming results store time directly; if storing dicts, adjust access
            rank_text_content = f"{rank}. {display_name}: {time_val:.2f} seconds"
            # To show catches per algorithm, you'd need to store it in self.results
            # e.g. self.results[algo] = {'time': time_val, 'catches': num_catches}
            # Then rank_text_content += f" (Caught: {self.results[algo]['catches']} times)"
            
            result_surface = font.render(rank_text_content, True, color)
            screen.blit(result_surface, (WIDTH // 2 - 200, y_pos)) # Adjusted x
            
            desc = ""
            if rank == 1: desc = "🏆 FASTEST"
            elif rank == 2: desc = "🥈 SECOND"
            elif rank == 3: desc = "🥉 THIRD"
            if desc:
                desc_surface = font.render(desc, True, color)
                screen.blit(desc_surface, (WIDTH // 2 + 150, y_pos)) # Adjusted x
            y_pos += 40
        
        analysis_y = y_pos + 30
        if sorted_results_list:
            fastest_algo_name, fastest_time_val = sorted_results_list[0]
            slowest_algo_name, slowest_time_val = sorted_results_list[-1]

            fastest_display_name = fastest_algo_name.upper()
            if fastest_display_name == 'DIJKSTRA': fastest_display_name = "DIJKSTRA'S"
            slowest_display_name = slowest_algo_name.upper()
            if slowest_display_name == 'DIJKSTRA': slowest_display_name = "DIJKSTRA'S"

            analysis_lines = [
                f"Fastest: {fastest_display_name} ({fastest_time_val:.2f}s)",
                f"Slowest: {slowest_display_name} ({slowest_time_val:.2f}s)",
                f"Time Difference: {slowest_time_val - fastest_time_val:.2f}s"
            ]
            for line in analysis_lines:
                analysis_surface = font.render(line, True, WHITE)
                text_rect = analysis_surface.get_rect(center=(WIDTH // 2, analysis_y))
                screen.blit(analysis_surface, text_rect)
                analysis_y += 30
        
        instruction = font.render("Press R to restart all tests or Q to quit", True, WHITE) # Changed text
        instruction_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(instruction, instruction_rect)
        pygame.display.flip()

    def move_pacman(self, direction):
        row, col = self.pacman_pos
        new_pos = None
        if direction == 'UP': new_pos = (row - 1, col)
        elif direction == 'DOWN': new_pos = (row + 1, col)
        elif direction == 'LEFT': new_pos = (row, col - 1)
        elif direction == 'RIGHT': new_pos = (row, col + 1)
        
        # Pathfinding should ensure this move is valid regarding walls/ghost at planning time
        # This basic check is for walls only when executing the move.
        if new_pos and self.pathfinder.is_valid_move(new_pos, dynamic_obstacles=None): # Pacman doesn't self-sabotage with dynamic obstacles for its own move execution
            self.pacman_pos = new_pos
            if self.pacman_pos in self.food_positions:
                self.food_positions.remove(self.pacman_pos)
                self.score += 10
            return True
        return False

    def move_ghost(self):
        if not self.ghost_pos or self.game_completed:
            return

        now = time.time()
        if now - self.ghost_last_move_time > self.ghost_move_interval:
            self.ghost_last_move_time = now
            # Ghost targets Pacman, does not consider itself an obstacle for its own path.
            path_to_pacman = self.pathfinder.bfs(self.ghost_pos, self.pacman_pos, dynamic_obstacles=None)
            
            if path_to_pacman:
                direction = path_to_pacman[0]
                r, c = self.ghost_pos
                next_ghost_pos = None
                if direction == 'UP': next_ghost_pos = (r - 1, c)
                elif direction == 'DOWN': next_ghost_pos = (r + 1, c)
                elif direction == 'LEFT': next_ghost_pos = (r, c - 1)
                elif direction == 'RIGHT': next_ghost_pos = (r, c + 1)

                if next_ghost_pos and self.pathfinder.is_valid_move(next_ghost_pos): # Ghost can move if valid (not wall)
                    self.ghost_pos = next_ghost_pos
            else: # Ghost is stuck or Pacman is somehow unreachable by BFS (e.g. map error)
                  # Try a random valid move to unstick itself
                neighbors = self.pathfinder.get_neighbors(self.ghost_pos, dynamic_obstacles=None)
                if neighbors:
                    chosen_move_pos, _ = random.choice(neighbors)
                    self.ghost_pos = chosen_move_pos
    
    def handle_pacman_caught(self):
        print(f"Pacman caught by ghost! Penalty +{GHOST_PENALTY_TIME}s.")
        self.pacman_caught_count += 1
        self.time_penalty += GHOST_PENALTY_TIME
        self.pacman_pos = (1, 1) # Reset Pacman
        
        # Optionally reset ghost or move it away to give Pacman a fresh start
        # self.ghost_pos = self.initial_ghost_pos 
        # Ensure ghost is not on Pacman's reset spot
        if self.ghost_pos == self.pacman_pos:
            self.ghost_pos = self.initial_ghost_pos if self.initial_ghost_pos != self.pacman_pos else (ROWS -2, COLS -2)
            # Further ensure new ghost_pos is valid
            if self.grid[self.ghost_pos[0]][self.ghost_pos[1]] == 1 or self.ghost_pos == self.pacman_pos:
                 self.ghost_pos = (1, COLS-2) # A fallback

        self.current_path_to_food = [] # Force path recalculation
        self.draw_game() # Show updated state
        pygame.time.delay(500) # Brief pause to signify being caught

    def auto_play_step(self):
        if not self.start_time:
            self.start_time = time.time()
            self.ghost_last_move_time = self.start_time # Sync ghost's first potential move

        if self.game_completed:
            return

        # 1. Ghost moves
        self.move_ghost()

        # 2. Check collision: Ghost moved onto Pacman
        if self.pacman_pos == self.ghost_pos:
            self.handle_pacman_caught()
            return # End this step early as Pacman is reset

        # 3. Pacman acts (if not caught above)
        if self.food_positions:
            recalculate_pacman_path = not self.current_path_to_food
            if self.current_path_to_food: # Check if current path is still valid (e.g. ghost moved into it)
                next_step_dir = self.current_path_to_food[0]
                r, c = self.pacman_pos
                potential_next_pac_pos = None
                if next_step_dir == 'UP': potential_next_pac_pos = (r - 1, c)
                elif next_step_dir == 'DOWN': potential_next_pac_pos = (r + 1, c)
                elif next_step_dir == 'LEFT': potential_next_pac_pos = (r, c - 1)
                elif next_step_dir == 'RIGHT': potential_next_pac_pos = (r, c + 1)
                
                if potential_next_pac_pos == self.ghost_pos: # Pacman's next step is where ghost is NOW
                    recalculate_pacman_path = True

            if recalculate_pacman_path:
                # Pacman plans path to food, avoiding current ghost position
                closest_food_pos, path_to_food = self.pathfinder.find_closest_target(
                    self.pacman_pos, list(self.food_positions), self.current_algorithm,
                    dynamic_obstacles={self.ghost_pos} # Pacman avoids the ghost
                )
                self.current_path_to_food = path_to_food
            
            if self.current_path_to_food:
                direction_to_move = self.current_path_to_food.pop(0)
                self.move_pacman(direction_to_move)

                # 4. Check collision: Pacman moved onto Ghost
                if self.pacman_pos == self.ghost_pos:
                    self.handle_pacman_caught()
                    return # End this step early
        
        # 5. Check game completion (all food eaten)
        if not self.food_positions and not self.game_completed:
            self.game_completed = True
            self.end_time = time.time()
            final_run_time = (self.end_time - self.start_time) + self.time_penalty
            self.results[self.current_algorithm] = final_run_time # Store total time including penalties
            self.tested_algorithms.add(self.current_algorithm)
            
            algo_disp_name = self.current_algorithm.upper()
            if algo_disp_name == 'DIJKSTRA': algo_disp_name = "DIJKSTRA'S"
            
            print(f"{algo_disp_name} completed in {final_run_time:.2f}s (Score: {self.score}, Caught: {self.pacman_caught_count}, Penalty: {self.time_penalty:.2f}s).")

    def select_algorithm(self, choice):
        algorithms_map = {1: 'bfs', 2: 'dijkstra', 3: 'astar'}
        if choice in algorithms_map:
            selected_algo_key = algorithms_map[choice]
            if selected_algo_key not in self.tested_algorithms:
                self.current_algorithm = selected_algo_key
                self.reset_game() # Reset for the new algorithm test
                self.state = GameState.PLAYING
                return True
        return False

def main():
    game = PacmanGame()
    running = True
    print("Pacman Algorithm Comparison")
    print("Test BFS, Dijkstra's, and A* algorithms. Pacman will try to dodge the ghost.")
    print("Collisions with the ghost incur a time penalty.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game.state == GameState.MENU:
                    if event.key == pygame.K_1: game.select_algorithm(1)
                    elif event.key == pygame.K_2: game.select_algorithm(2)
                    elif event.key == pygame.K_3: game.select_algorithm(3)
                elif game.state == GameState.PLAYING and game.game_completed:
                    if event.key == pygame.K_SPACE:
                        if len(game.tested_algorithms) == 3: # All algorithms tested
                            game.state = GameState.RESULTS
                        else:
                            game.state = GameState.MENU # Go back to menu for next selection
                elif game.state == GameState.RESULTS:
                    if event.key == pygame.K_r: # Restart all tests
                        game = PacmanGame() # Re-initialize the game object fully
                        game.state = GameState.MENU # Start from menu
                    elif event.key == pygame.K_q:
                        running = False
        
        if game.state == GameState.MENU:
            game.draw_menu()
        elif game.state == GameState.PLAYING:
            if not game.game_completed:
                game.auto_play_step()
            game.draw_game() # Draw regardless of completion to show final state / "Press SPACE"
        elif game.state == GameState.RESULTS:
            game.draw_results()
        
        clock.tick(10) # 10 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()