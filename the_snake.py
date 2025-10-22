"""
Модуль игры "Змейка".

Классы:
    GameObject - базовый класс игровых объектов
    Apple - класс яблока
    Snake - класс змейки

Функции:
    handle_keys() - обработка нажатий клавиш
    handle_apple_collision() - обработка столкновения с яблоком
    handle_self_collision() - обработка столкновения с собой
    main() - основная функция игры
"""
from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс содержит общие атрибуты."""

    def __init__(self) -> None:
        """Инициализирует игровой объект."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self, surface) -> None:
        """Отрисовывает объект на переданной поверхности."""
        raise NotImplementedError(
            "Метод draw должен быть реализован в дочернем классе"
        )


class Apple(GameObject):
    """Класс описание яблока."""

    def __init__(self, occupied_cells=None):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position(occupied_cells)

    def randomize_position(self, snake_positions=None):
        """Генерирует рандомное позицию яблока."""
        if snake_positions is None:
            snake_positions = []

        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        """Отрисовка яблока на переданной поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Описание действий змейки."""

    def __init__(self):
        """Инициализирует змейку в начальном состоянии."""
        super().__init__()
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки. Возвращает новую позицию головы."""
        snake_head_x, snake_head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_snake_head_x = snake_head_x + direction_x * GRID_SIZE
        new_snake_head_y = snake_head_y + direction_y * GRID_SIZE

        new_snake_head_x = new_snake_head_x % SCREEN_WIDTH
        new_snake_head_y = new_snake_head_y % SCREEN_HEIGHT

        new_position = (new_snake_head_x, new_snake_head_y)

        self.last = self.positions[-1]
        self.positions.insert(0, new_position)

        if len(self.positions) > self.length:
            self.positions.pop()
        else:
            self.last = None

        return new_position

    def draw(self, surface):
        """Отрисовка змейки на переданной поверхности."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_position = self.get_head_position()
        head_rect = pygame.Rect(head_position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def self_collided(self, new_position):
        """Проверяет, столкнулась ли змейка сама с собой."""
        return new_position in self.positions[1:]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, RIGHT, LEFT])
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def handle_apple_collision(snake, new_position, apple):
    """Обрабатывает столкновение змейки с яблоком."""
    if new_position == apple.position:
        snake.length += 1
        apple.randomize_position(snake.positions)
        return True
    return False


def handle_self_collision(snake, new_position, apple):
    """Обрабатывает столкновение змейки с самой собой."""
    if snake.self_collided(new_position):
        snake.reset()
        apple.randomize_position(snake.positions)
        return True
    return False


def main():
    """Основная функция игры."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    game_paused = False
    pause_end_time = 0

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        if game_paused:
            if pygame.time.get_ticks() >= pause_end_time:
                game_paused = False
            continue

        snake.update_direction()
        new_position = snake.move()

        handle_apple_collision(snake, new_position, apple)

        if handle_self_collision(snake, new_position, apple):
            game_paused = True
            pause_end_time = pygame.time.get_ticks() + 500
            screen.fill(BOARD_BACKGROUND_COLOR)
            pygame.display.update()
            continue

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw(screen)
        snake.draw(screen)
        pygame.display.update()


if __name__ == '__main__':
    main()
