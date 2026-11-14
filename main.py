import json
import random
from pathlib import Path

import pygame


WIDTH = 960
HEIGHT = 700
CELL_SIZE = 24
BOARD_COLUMNS = 30
BOARD_ROWS = 20
BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
BOARD_LEFT = (WIDTH - BOARD_WIDTH) // 2
BOARD_TOP = 150
MOVE_INTERVAL = 125

BACKGROUND = (13, 22, 27)
PANEL = (22, 35, 40)
BOARD = (17, 29, 34)
GRID = (28, 45, 49)
TEXT = (235, 244, 232)
MUTED = (140, 162, 157)
GREEN = (137, 220, 118)
CORAL = (255, 119, 105)

BEST_SCORE_PATH = Path(__file__).with_name("snake_high_score.json")


def load_best_score():
    try:
        return int(json.loads(BEST_SCORE_PATH.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_best_score(score):
    BEST_SCORE_PATH.write_text(json.dumps(score), encoding="utf-8")


def make_food(snake):
    open_cells = [
        (column, row)
        for column in range(BOARD_COLUMNS)
        for row in range(BOARD_ROWS)
        if (column, row) not in snake
    ]
    return random.choice(open_cells) if open_cells else None


def draw_text(surface, font, text, color, center):
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def draw_game(screen, fonts, snake, food, score, best_score, state):
    screen.fill(BACKGROUND)

    title = fonts["title"].render("SNAKE", True, TEXT)
    screen.blit(title, (BOARD_LEFT, 35))
    draw_text(screen, fonts["small"], "ARROW KEYS / WASD", MUTED, (WIDTH // 2, 58))

    score_box = pygame.Rect(WIDTH - BOARD_LEFT - 190, 34, 190, 62)
    pygame.draw.rect(screen, PANEL, score_box, border_radius=8)
    draw_text(screen, fonts["label"], "SCORE", MUTED, (score_box.x + 52, score_box.y + 20))
    draw_text(screen, fonts["score"], str(score), TEXT, (score_box.x + 146, score_box.y + 34))

    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, BOARD, board_rect, border_radius=8)
    for column in range(1, BOARD_COLUMNS):
        x = BOARD_LEFT + column * CELL_SIZE
        pygame.draw.line(screen, GRID, (x, BOARD_TOP), (x, BOARD_TOP + BOARD_HEIGHT))
    for row in range(1, BOARD_ROWS):
        y = BOARD_TOP + row * CELL_SIZE
        pygame.draw.line(screen, GRID, (BOARD_LEFT, y), (BOARD_LEFT + BOARD_WIDTH, y))

    if food is not None:
        food_rect = pygame.Rect(
            BOARD_LEFT + food[0] * CELL_SIZE + 5,
            BOARD_TOP + food[1] * CELL_SIZE + 5,
            CELL_SIZE - 10,
            CELL_SIZE - 10,
        )
        pygame.draw.ellipse(screen, CORAL, food_rect)

    for index, (column, row) in enumerate(snake):
        inset = 2 if index else 1
        segment = pygame.Rect(
            BOARD_LEFT + column * CELL_SIZE + inset,
            BOARD_TOP + row * CELL_SIZE + inset,
            CELL_SIZE - inset * 2,
            CELL_SIZE - inset * 2,
        )
        pygame.draw.rect(screen, GREEN if index else (185, 241, 145), segment, border_radius=6)

    footer_y = BOARD_TOP + BOARD_HEIGHT + 35
    draw_text(screen, fonts["small"], f"BEST  {best_score}", MUTED, (BOARD_LEFT + 75, footer_y))
    draw_text(screen, fonts["small"], "P  PAUSE     R  RESTART     ESC  QUIT", MUTED, (WIDTH // 2 + 120, footer_y))

    if state != "playing":
        shade = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        shade.fill((5, 12, 15, 190))
        screen.blit(shade, board_rect.topleft)
        if state == "ready":
            heading, prompt = "READY?", "PRESS SPACE TO PLAY"
        elif state == "paused":
            heading, prompt = "PAUSED", "PRESS P TO RESUME"
        else:
            heading, prompt = "GAME OVER", "SPACE TO PLAY AGAIN     R TO RESTART"
        draw_text(screen, fonts["overlay"], heading, TEXT, board_rect.center)
        draw_text(screen, fonts["small"], prompt, GREEN, (WIDTH // 2, board_rect.centery + 42))

    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption("Snake | Classic Arcade")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fonts = {
        "title": pygame.font.SysFont("segoeui", 34, bold=True),
        "small": pygame.font.SysFont("segoeui", 15, bold=True),
        "label": pygame.font.SysFont("segoeui", 12, bold=True),
        "score": pygame.font.SysFont("segoeui", 26, bold=True),
        "overlay": pygame.font.SysFont("segoeui", 40, bold=True),
    }

    best_score = load_best_score()
    snake = [(BOARD_COLUMNS // 2, BOARD_ROWS // 2)]
    direction = (1, 0)
    next_direction = direction
    food = make_food(snake)
    score = 0
    state = "ready"
    elapsed = 0
    running = True

    while running:
        elapsed += clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if state in ("ready", "game_over"):
                        snake = [(BOARD_COLUMNS // 2, BOARD_ROWS // 2)]
                        direction = (1, 0)
                        next_direction = direction
                        food = make_food(snake)
                        score = 0
                        state = "playing"
                        elapsed = 0
                    elif state == "paused":
                        state = "playing"
                elif event.key == pygame.K_r:
                    snake = [(BOARD_COLUMNS // 2, BOARD_ROWS // 2)]
                    direction = (1, 0)
                    next_direction = direction
                    food = make_food(snake)
                    score = 0
                    state = "playing"
                    elapsed = 0
                elif event.key == pygame.K_p:
                    if state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"
                elif state == "playing":
                    key_directions = {
                        pygame.K_UP: (0, -1),
                        pygame.K_w: (0, -1),
                        pygame.K_DOWN: (0, 1),
                        pygame.K_s: (0, 1),
                        pygame.K_LEFT: (-1, 0),
                        pygame.K_a: (-1, 0),
                        pygame.K_RIGHT: (1, 0),
                        pygame.K_d: (1, 0),
                    }
                    candidate = key_directions.get(event.key)
                    if candidate and candidate != (-direction[0], -direction[1]):
                        next_direction = candidate

        if state == "playing":
            while elapsed >= MOVE_INTERVAL:
                elapsed -= MOVE_INTERVAL
                direction = next_direction
                head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                eating = head == food
                body = snake if eating else snake[:-1]
                if (
                    head[0] < 0
                    or head[0] >= BOARD_COLUMNS
                    or head[1] < 0
                    or head[1] >= BOARD_ROWS
                    or head in body
                ):
                    state = "game_over"
                    if score > best_score:
                        best_score = score
                        save_best_score(best_score)
                    break

                snake.insert(0, head)
                if eating:
                    score += 1
                    food = make_food(snake)
                    if food is None:
                        state = "game_over"
                        break
                else:
                    snake.pop()

        draw_game(screen, fonts, snake, food, score, best_score, state)

    pygame.quit()


if __name__ == "__main__":
    main()