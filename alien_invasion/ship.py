import pygame
from pygame.sprite import Sprite

#rect是指rectangle，pygame让你能像处理矩形一样处理所有的游戏元素

class Ship(Sprite):
    """管理飞船的类"""

    def __init__(self,ai_game):
        """初始化飞船并设置其初始位置"""
        super().__init__()
        self.screen=ai_game.screen
        self.screen_rect=ai_game.screen.get_rect()
        self.settings=ai_game.settings
        #这里挺有意思：直接使用ai_game的settings,我的第一想法还是import settings然后让它成为ship的属性

        #加载飞船图像并获取其外接矩形
        self.image=pygame.image.load('python编程从入门到实践项目\\alien_invasion\images\ship.bmp') 
        #这里\\用到了转义操作，这个目录是因为当前在python文件夹
        self.rect=self.image.get_rect()

        #对于每艘新飞船，都将其放在屏幕底部的中央
        self.rect.midbottom=self.screen_rect.midbottom

        #在飞船的属性x中存储小数值
        self.x=float(self.rect.x)
        #这是因为rect的x等属性只能存储整数值,先让self.x用浮点数形式记录初始位置

        #移动标志
        self.moving_right=False
        self.moving_left=False
    
    def update(self):
        """根据移动标志调整飞船的位置"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x+=self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x-=self.settings.ship_speed
        #这样的条件设置应该是因为pygame默认左上角的坐标为0,0

        #根据self.x更新rect对象
        self.rect.x=self.x

    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image, self.rect)

    def center_ship(self):
        """让飞船在屏幕底端居中"""
        self.rect.midbottom=self.screen_rect.midbottom
        self.x=float(self.rect.x)
    #注意一个比较反直觉的点：在整个游戏运行期间其实只有一个飞船实例，撞倒后只是将其重新居中