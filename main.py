import pygame
import time
import math
from utils import scale_img, blit_rot_center, blit_text_center

pygame.init()

fact = 1
fact2 = 1

# Import Images
GRASS = scale_img(pygame.image.load('images/grass.jpg'), 2.5 * fact)
TRACK = scale_img(pygame.image.load('images/track.png'), 0.9 * fact)

TRACK_BORDER = scale_img(
    pygame.image.load('images/track-border.png'), 0.9 * fact)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = scale_img(pygame.image.load('images/finish.png'), fact)
FINISH_POS = (130*fact, 250*fact)
FINISH_MASK = pygame.mask.from_surface(FINISH)

RED_CAR = scale_img(pygame.image.load('images/red-car.png'), 0.5 * fact)
GREEN_CAR = scale_img(pygame.image.load('images/green-car.png'), 0.5 * fact)

# Defining Display
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont('comicsans', 44*fact)

# Universal Constants
FPS = 60
PATH = [
        (175, 119), (110, 70), (56, 133), (70, 481),
        (318, 731), (404, 680), (418, 521), (507, 475),
        (600, 551), (613, 715), (736, 713), (734, 399),
        (611, 357), (409, 343), (433, 257), (697, 258),
        (738, 123), (581, 71), (303, 78), (275, 377),
        (176, 388), (178, 260)
]

# PATH = [(int(x*fact), int(y*fact)) for x, y in PATH]


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

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
    def __init__(self, max_vel, rot_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rot_vel = rot_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.accel = 0.1 * fact2  # pixels/second^2

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rot_vel
        elif right:
            self.angle -= self.rot_vel

    def draw(self, win):
        blit_rot_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.accel, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.accel, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        ver = math.cos(radians) * self.vel
        hor = math.sin(radians) * self.vel

        self.y -= ver
        self.x -= hor

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x-x), int(self.y-y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180*fact, 200*fact)

    def red_speed(self):
        self.vel = max(self.vel - self.accel/2, 0)
        self.move()

    def bounce(self):
        self.vel = self.vel * (-0.5)
        self.move()


class CompCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150*fact, 200*fact)

    def __init__(self, max_vel, rot_vel, path=[]):
        super().__init__(max_vel, rot_vel)
        self.path = path
        self.curr_point = 0
        self.vel = max_vel

    # def draw_points(self, win):
    #     for point in self.path:
    #         pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.draw_points(win)

    def calc_angle(self):
        target_x, target_y = self.path[self.curr_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            des_angle = math.pi/2
        else:
            des_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            des_angle += math.pi

        diff_angles = self.angle - math.degrees(des_angle)
        if diff_angles >= 180:
            diff_angles -= 360

        if diff_angles > 0:
            self.angle -= min(self.rot_vel, abs(diff_angles))
        else:
            self.angle += min(self.rot_vel, abs(diff_angles))

    def update_path_point(self):
        target = self.path[self.curr_point]
        rect = pygame.Rect(
            int(self.x), int(self.y), self.img.get_width(),
            self.img.get_height())
        if rect.collidepoint(*target):
            self.curr_point += 1

    def move(self):
        if self.curr_point >= len(self.path):
            return

        self.calc_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.curr_point = 0


def draw(win, images, player_car, comp_car, game_info):
    for img, pos in images:
        x, y = pos
        win.blit(img, (int(x), int(y)))

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1,
                                  (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height()-70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1,
                                 (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height()-40))

    vel_text = MAIN_FONT.render(f"Vel: {player_car.vel}px/s", 1,
                                (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height()-10))

    player_car.draw(win)
    comp_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.red_speed()


def handle_coll(player_car, comp_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) is not None:
        player_car.bounce()

    comp_finish_poi_collide = comp_car.collide(FINISH_MASK, *FINISH_POS)
    if comp_finish_poi_collide is not None:
        blit_text_center(WIN, MAIN_FONT, "You Lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        comp_car.reset()

    finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POS)
    if finish_poi_collide is not None:
        if finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            comp_car.next_level(game_info.level)


def main():
    run = True
    clock = pygame.time.Clock()
    images = [
        (GRASS, (0, 0)),
        (TRACK, (0, 0)),
        (FINISH, FINISH_POS),
        (TRACK_BORDER, (0, 0))
        ]
    player_car = PlayerCar(4*fact2, 4*fact2)
    comp_car = CompCar(2*fact2, 2*fact2, PATH)
    game_info = GameInfo()

    while run:
        clock.tick(FPS)

        draw(WIN, images, player_car, comp_car, game_info)

        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT,
                             f"Press any key to start level{game_info.level}!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     pos = pygame.mouse.get_pos()
            #     comp_car.path.append(pos)

        move_player(player_car)
        comp_car.move()

        handle_coll(player_car, comp_car, game_info)
        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You Won the Game!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            comp_car.reset()

    pygame.quit()


if __name__ == '__main__':
    main()
