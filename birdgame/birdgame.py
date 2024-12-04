import pygame
import random
import os

pygame.init()

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
PIPE_WIDTH = 52
PIPE_HEIGHT = 320
PIPE_GAP = 100  # 调整管道之间的左右间距
GAP = 130  # 调整上下管道之间的间隙
PIPE_VELOCITY = 3  # 管道移动速度
GROUND_HEIGHT = 112  # 地面高度
BIRD_WIDTH = 34  # 小鸟的宽度
BIRD_HEIGHT = 24  # 小鸟的高度
BIRD_X = 50  # 小鸟的初始X坐标
JUMP_VELOCITY = -9  # 小鸟跳跃的初速度
GRAVITY = 0.5  # 小鸟的重力加速度
ROTATION_SPEED = 5  # 旋转速度

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

script_dir = os.path.dirname(os.path.abspath(__file__))
background = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "background-day.png"))
ground = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "base.png"))
pipe_img = pygame.image.load(os.path.join(script_dir, "assets", "sprites", "pipe-green.png"))

pipe_top_img = pygame.transform.flip(pipe_img, False, True)  # 上管道是翻转的

# 加载小鸟的图片
bird_images = [
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-upflap.png")),
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-midflap.png")),
    pygame.image.load(os.path.join(script_dir, "assets", "sprites", "redbird-downflap.png"))
]
bird_index = 1  # 小鸟的初始图片（中间）

# 加载数字图片（0-9）
digit_images = [pygame.image.load(os.path.join(script_dir, "assets", "sprites", f"{i}.png")) for i in range(10)]

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, SCREEN_HEIGHT - GAP - GROUND_HEIGHT - 100)  # 调整范围，确保下管道不接地面
        self.top = self.height - PIPE_HEIGHT  # 上管道的顶部坐标
        self.bottom = self.height + GAP  # 下管道的底部坐标
        self.rect_top = pygame.Rect(self.x, self.top, PIPE_WIDTH, PIPE_HEIGHT)
        self.rect_bottom = pygame.Rect(self.x, self.bottom, PIPE_WIDTH, SCREEN_HEIGHT - self.bottom - GROUND_HEIGHT)  # 下管道不低于地面

    def move(self):
        self.x -= PIPE_VELOCITY
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x

    def draw(self, screen):
        screen.blit(pipe_top_img, self.rect_top)
        screen.blit(pipe_img, self.rect_bottom)

    def off_screen(self):
        return self.x < -PIPE_WIDTH

class Ground:
    def __init__(self):
        self.x = 0
        self.width = ground.get_width()
        self.y = SCREEN_HEIGHT - ground.get_height()

    def move(self):
        self.x -= 4

        if self.x <= -self.width:
            self.x = 0

    def draw(self, screen):
        screen.blit(ground, (self.x, self.y))
        screen.blit(ground, (self.x + self.width, self.y))

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = SCREEN_HEIGHT // 2
        self.vel_y = 0  # 小鸟的垂直速度
        self.angle = 0  # 当前角度
        self.target_angle = 0  # 目标角度
        self.image = bird_images[bird_index]
        self.image_index = 1
        self.frame_counter = 0  # 用于控制小鸟动画帧的切换

    def update(self):
        self.vel_y += GRAVITY  # 应用重力
        self.y += self.vel_y

        # 根据垂直速度确定目标角度
        if self.vel_y < 0:  # 向上跳跃
            self.target_angle = 30
        elif self.vel_y > 0:  # 向下下坠
            self.target_angle = -30

        # 逐渐过渡角度
        if self.angle < self.target_angle:
            self.angle = min(self.angle + ROTATION_SPEED, self.target_angle)
        elif self.angle > self.target_angle:
            self.angle = max(self.angle - ROTATION_SPEED, self.target_angle)

        # 根据小鸟的状态切换动画帧
        if self.vel_y < 0:  # 向上跳跃
            self.image_index = 0  # 使用上翅膀图片
        elif self.vel_y > 0:  # 向下下坠
            self.image_index = 2  # 使用下翅膀图片
        else:  # 处于平衡状态时
            self.image_index = 1  # 使用中间翅膀图片

        self.image = bird_images[self.image_index]

        # 限制小鸟下落不超过屏幕底部
        if self.y > SCREEN_HEIGHT - GROUND_HEIGHT - self.image.get_height():
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.image.get_height()
            self.vel_y = 0

        # 限制小鸟不超出顶部
        if self.y < 0:
            self.y = 0
            self.vel_y = 0

    def jump(self):
        self.vel_y = JUMP_VELOCITY  # 设置跳跃速度

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)  # 根据角度旋转小鸟
        screen.blit(rotated_image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

def draw_score(score, screen):
    """绘制得分，使用数字图片"""
    score_str = str(score)
    score_width = 0
    for digit in score_str:
        score_width += digit_images[int(digit)].get_width()

    x_offset = (SCREEN_WIDTH - score_width) // 2  # 使得分居中显示

    for digit in score_str:
        screen.blit(digit_images[int(digit)], (x_offset, 20))
        x_offset += digit_images[int(digit)].get_width()

def game_loop():
    clock = pygame.time.Clock()
    running = True
    pipes = [Pipe(SCREEN_WIDTH + 100)]  # 初始生成一个管道
    ground_obj = Ground()
    bird = Bird()  # 创建小鸟对象
    score = 0  # 初始得分

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                bird.jump()  # 鼠标点击或空格键控制小鸟跳跃

        for pipe in pipes:
            pipe.move()

        pipes = [pipe for pipe in pipes if not pipe.off_screen()]

        if pipes[-1].x < SCREEN_WIDTH - PIPE_GAP:
            pipes.append(Pipe(SCREEN_WIDTH + 100))

        bird.update()

        # 更新得分
        for pipe in pipes:
            if pipe.x + PIPE_WIDTH < bird.x and not hasattr(pipe, "passed"):
                score += 1  # 得分增加
                pipe.passed = True  # 标记管道已通过

        screen.blit(background, (0, 0))
        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)
        ground_obj.move()
        ground_obj.draw(screen)

        # 绘制得分
        draw_score(score, screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    game_loop()
