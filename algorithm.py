from collections import deque
import heapq
import math

class PathfindingAlgorithms:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0

    def is_valid_move(self, pos, dynamic_obstacles=None):
        """Check if a position is valid (within bounds, not a wall, not a dynamic obstacle)"""
        row, col = pos
        if dynamic_obstacles and pos in dynamic_obstacles:
            return False  # It's a dynamic obstacle
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] != 1  # Not a wall
        return False

    def get_neighbors(self, pos, dynamic_obstacles=None):
        """Get all valid neighboring positions"""
        row, col = pos
        neighbors = []
        directions = [
            ('UP', (-1, 0)),
            ('DOWN', (1, 0)),
            ('LEFT', (0, -1)),
            ('RIGHT', (0, 1))
        ]

        for direction, (dr, dc) in directions:
            new_pos = (row + dr, col + dc)
            if self.is_valid_move(new_pos, dynamic_obstacles):
                neighbors.append((new_pos, direction))
        return neighbors

    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def bfs(self, start, target, dynamic_obstacles=None):
        """
        Breadth-First Search: Find shortest path from start to target
        Returns list of directions to reach target
        """
        queue = deque()
        queue.append((start, []))  # (position, path)
        visited = set()
        visited.add(start)

        while queue:
            current_pos, path = queue.popleft()

            if current_pos == target:
                return path

            for neighbor_pos, direction in self.get_neighbors(current_pos, dynamic_obstacles):
                if neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    queue.append((neighbor_pos, path + [direction]))
        return []

    def dijkstra(self, start, target, dynamic_obstacles=None):
        """
        Dijkstra's Algorithm: Find shortest path from start to target
        Returns list of directions to reach target
        """
        heap = [(0, start, [])]  # (distance, position, path)
        distances = {start: 0}
        processed_nodes = set()

        while heap:
            current_distance, current_pos, path = heapq.heappop(heap)

            if current_pos in processed_nodes:
                continue
            processed_nodes.add(current_pos)

            if current_pos == target:
                return path

            for neighbor_pos, direction in self.get_neighbors(current_pos, dynamic_obstacles):
                new_distance = current_distance + 1
                if neighbor_pos not in distances or new_distance < distances[neighbor_pos]:
                    distances[neighbor_pos] = new_distance
                    heapq.heappush(heap, (new_distance, neighbor_pos, path + [direction]))
        return []

    def a_star(self, start, target, dynamic_obstacles=None):
        """
        A* Search: Find optimal path from start to target using heuristic
        Returns list of directions to reach target
        """
        heap = [(0, 0, start, [])]  # (f_score, g_score, position, path)
        g_scores = {start: 0}
        closed_set = set()

        while heap:
            f_score_val, g_score, current_pos, path = heapq.heappop(heap)

            if current_pos in closed_set:
                continue
            closed_set.add(current_pos)

            if current_pos == target:
                return path

            for neighbor_pos, direction in self.get_neighbors(current_pos, dynamic_obstacles):
                tentative_g_score = g_score + 1
                if tentative_g_score < g_scores.get(neighbor_pos, float('inf')):
                    g_scores[neighbor_pos] = tentative_g_score
                    h_score = self.manhattan_distance(neighbor_pos, target)
                    new_f_score = tentative_g_score + h_score
                    heapq.heappush(heap, (new_f_score, tentative_g_score, neighbor_pos, path + [direction]))
        return []

    def find_closest_target(self, start, targets, algorithm='bfs', dynamic_obstacles=None):
        """
        Find the closest target from a set of targets using specified algorithm
        Returns (target_position, path_to_target)
        """
        if not targets:
            return None, []

        closest_target = None
        shortest_path = []
        min_distance = float('inf')

        pathfind_func = None
        if algorithm == 'bfs':
            pathfind_func = self.bfs
        elif algorithm == 'dijkstra':
            pathfind_func = self.dijkstra
        elif algorithm == 'astar':
            pathfind_func = self.a_star
        else:
            pathfind_func = self.bfs  # Default to BFS

        for target_pos in targets: # Changed target to target_pos for clarity
            path = pathfind_func(start, target_pos, dynamic_obstacles)
            if path and len(path) < min_distance:
                min_distance = len(path)
                closest_target = target_pos
                shortest_path = path
        return closest_target, shortest_path