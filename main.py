import time, pygame, math
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("images/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("images/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_image(pygame.image.load("images/finish.png"), 0.95)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("images/red-car.png"), 0.46)
GREAN_CAR = scale_image(pygame.image.load("images/green-car.png"), 0.46)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT - 10))
pygame.display.set_caption("CAR RACING!!")

MAIN_FONT = pygame.font.SysFont("georgia", 45)
MAIN_FONT1 = pygame.font.SysFont("arial", 25)

FPS = 60
path = [(179, 126), (122, 75), (56, 130), (66, 462), (308, 720), (357, 724), (400, 679), (432, 507), (502, 487), (587, 521),
        (592, 590), (598, 675), (636, 723), (708, 716), (739, 635), (739, 412), (694, 370), (451, 365), (398, 322), (432, 264),
        (691, 262), (742, 210), (714, 92), (324, 77), (282, 185), (280, 343), (180, 351), (184, 239)]

class GameInfo:
    LEVELS = 10

    def __init__(self,level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started =False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return time.time() - self.level_start_time

class AbstractCar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.x -= horizontal
        self.y -= vertical

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (150, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 0.2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel+2
        self.move()


class ComputerCar(AbstractCar):
    IMG = GREAN_CAR
    START_POS = (180, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -=360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(),self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self,level):
        self.reset()
        self.vel = self.max_vel + (level - 1)*0.2
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT1.render(f"Level {game_info.level}", 1, (0, 0, 0))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 80))

    time_text = MAIN_FONT1.render(f"Time - {round(game_info.get_level_time(), 1)}sec", 1, (0, 0, 0))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 60))

    car_vel = MAIN_FONT1.render(f"Velocity- {round(player_car.vel, 1)}px/sec", 1, (0, 0, 0))
    win.blit(car_vel, (10, HEIGHT - level_text.get_height() - 40))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def mov_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()


def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) is not None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide is not None:
        blit_text_center(WIN, MAIN_FONT, "You loss Bitch!!")
        pygame.display.update()
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()
        print("Computer won!")

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide is not None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)
            print("Finish")


run = True
Clock = pygame.time.Clock()
image = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4, 4)
computer_car = ComputerCar(3, 4, path)
game_info = GameInfo()

while run:
    Clock.tick(FPS)
    draw(WIN, image, player_car, computer_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    # pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    mov_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car, game_info )

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You Won Congo!!")
        pygame.time.wait(3000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

pygame.quit()
