import pygame
from pygame.sprite import Sprite

class Alien(Sprite):
    """表示单个外星人的类"""

    def __init__(self, ai_game):
        """初始化外星人并设置其起始位置"""
        super().__init__()
        self.screen=ai_game.screen
        self.settings=ai_game.settings

        #加载外星人图像并设置rect属性
        self.image=pygame.image.load('python编程从入门到实践项目\\alien_invasion\images\\alien.bmp')
        self.rect=self.image.get_rect()

        #每个外星人最初都在屏幕左上角附近(不完全在左上角，这样更容易看清？)
        self.rect.x=self.rect.width
        self.rect.y=self.rect.height

        #存储外星人的精准水平位置
        self.x=float(self.rect.x)
        #这里是不是疑惑为什么不需要有self.y,外星人也在y轴上移动呀
        #我们一开始用这样是为了精确表示位置（不只是整数），在y轴上我们不需要做到那么精准？！

    def check_edges(self):
        """如果外星人位于屏幕边缘,就返回True"""
        screen_rect=self.screen.get_rect()
        if (self.rect.right >= screen_rect.right) or (self.rect.left <=0):
            return True

    def update(self):
        """向右或者向左移动外星人"""
        self.x+=(self.settings.alien_speed*
                 self.settings.fleet_direction)
        self.rect.x=self.x