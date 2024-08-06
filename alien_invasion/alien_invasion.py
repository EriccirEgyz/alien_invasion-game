import sys
from time import sleep

import pygame

from settings import Settings #不导入整个模块，直接把Settings类导入到当前的命名空间？
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings=Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        #创建一个用于存储游戏统计信息的实例
        #并创建记分牌
        self.stats=GameStats(self)
        self.sb=Scoreboard(self)

        self.ship=Ship(self) #这里的参数很巧妙，Ship(self)的self是AlienInvasion实例，是Ship类的第二个参数
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()

        self._create_fleet()

        #创建play按钮
        self.play_button = Button(self, "Play")

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
            #这里要注意：即使游戏处于非运行状态时，上下的_check_events和_update_screen还是要继续的，所以不要放在if内
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                #放在_update_bullets之后，因为稍后要检查是否有子弹击中了外星人

            self._update_screen()
            

    #将一开始的run_game拆成两个辅助方法：以_开头的
    #开发游戏项目时经常会这样：先编写可行的代码，等代码越来越复杂时再进行重构

    def _check_events(self):
        """相应案件和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit() #用来退出游戏

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            #无论玩家用鼠标点击什么地方，都会触发此事件，但我们只想让玩家再点击play按钮时做出下那英
            #为此，get_pos()返回一个元组，包含x和y坐标

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event) #这里传参也要注意

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        """在玩家单击play按钮时开始游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos) #这个也有集成的方法可以用
        if button_clicked and not self.stats.game_active:
        #game_active为False时才能点击play按钮重开游戏,防止玩家用鼠标误触到了那片区域
            #重置游戏动态设置（这个真没想到
            self.settings.initialize_dynamic_settings()

            #重置游戏统计信息
            self.stats.reset_stats()
            self.stats.game_active=True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            #清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()

            #创建一群新的外星人并让飞船居中
            self._create_fleet()
            self.ship.center_ship()

            #在游戏处于活动状态时让光标不可见，这个很细节了
            pygame.mouse.set_visible(False)

    #这里预测到辅助方法_check_events会越来越长,因此又拆成了两个辅助方法_check_keydown_events和_check_keyup_events
    def _check_keydown_events(self,event):
        """响应案件"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right=True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left=True
        elif event.key == pygame.K_q: #这里添加了推出游戏的快捷键 按q,但为什么似乎没用？
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right=False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left=False

    def _fire_bullet(self): #拆分成的辅助方法_check_keydown_events又被进一步分解了
        """创建一颗子弹,并将其加入编组bullets中"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并删除消失的子弹"""
        #更新子弹的位置
        self.bullets.update() #这个是不是看上去很奇怪啊
        #其实是这样的：当对编组调用update()时，编组自动对其中的每个调用update()

        #删除消失的子弹
        for bullet in self.bullets.copy():

        #看到这里的copy有没有觉得很奇怪。这是因为使用for循环遍历列表（编组）时,
        # python要求列表的长度在整个循环中保持不变，所以必须遍历编组的副本!

            if bullet.rect.bottom <=0:
                self.bullets.remove(bullet) #这些子弹已经飞过了屏幕顶端，要删除

        #print(len(self.bullets)) 用于检测上面的子弹是否删除了

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        #检查是否有子弹击中了外星人。
        #如果是，就删除对应的子弹和外星人
        collisions=pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True
        )

        #这里groupcollide是将编组中每个元素的rect同另一个编组中每个元素的rect进行比较。
        #返回的是一个字典，每个键都是一颗子弹，而关联的值则是被子弹击中的外星人
        #有个问题呀，万一在其它问题场景下，一个元素可以击中多个另一种元素，这时用字典还怎么表示呢？
        #是这样的，每个值都是一个列表，包含被同一颗子弹击中的所有外星人

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        #外星人都是在这里被消灭的，所以在这里检测
        if not self.aliens: #这里挺有意思：空编组相当于FALSE
            #删除现有的子弹并新建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #提高等级
            self.stats.level += 1
            self.sb.prep_level()
    
    def _update_aliens(self):
        """
        检查是否有外星人位于屏幕边缘
        更新外星人群中所有外星人的位置
        """
        self._check_fleet_edges()
        self.aliens.update()

        #在更新每个外星人位置后，立即检测外星人和飞船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect=self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #像飞船被撞到一样处理
                self._ship_hit()
                break

    def _create_fleet(self):
        """创建外星人群"""
        #创建一个外星人并计算一行可以容纳多少个外星人
        #外星人的间距为外星人宽度
        alien=Alien(self)
        alien_width, alien_height=alien.rect.size
        available_space_x = self.settings.screen_width-(2*alien_width) #外星人离边框一定宽度比较美观
        number_aliens_x=available_space_x // (2*alien_width) #整除
        #注意，这里做的计算可以直接用程序进行，这样便于之后浏览，还方便修改扩展

        #计算屏幕可以容纳多少行外星人
        ship_height=self.ship.rect.height
        available_space_y=(self.settings.screen_height-
                           (3*alien_height)-ship_height)
        #这里书中建议将计算公式分成两行，以遵循每行不超过79个字符的建议
        number_rows=available_space_y // (2*alien_height)

        #创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
            
    def _create_alien(self,alien_number,row_number):
        """创建一个外星人并将其放在当前行"""
        alien=Alien(self)
        alien_width, alien_height=alien.rect.size
        alien.x=alien_width+2*alien_width*alien_number
        #这个巧妙，第一个alien_number是0，与左边的距离正好就是alien_width
        alien.rect.x=alien.x
        alien.rect.y=alien.rect.height+2*alien.rect.height*row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整群外星人下移,并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction = self.settings.fleet_direction*(-1)
        #之前将右左分别设置成1，-1就非常方便，直接取个负就可以

    def _ship_hit(self):
        """响应飞船被外星人撞到"""
        if self.stats.ships_left >0:
            #将ships_left-1
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #清空余下的外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            #这里是利用了清空pygame编组的方法

            #创建一群新的外星人，并将飞船放到屏幕底端的中央
            self._create_fleet()
            self.ship.center_ship()

            #暂停
            sleep(1)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
            #当游戏进入非活动状态后立即让光标可见
            #要让玩家专注于玩游戏而不是费力理解用户界面（这样做好难呀
            self.save_number_to_file(self.stats.high_score) #将历史最高分写入文件
 
    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""

        #重绘屏幕
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        #draw()方法将编组的每个元素绘制到属性rect制定的位置，draw的参数制定了编组中的元素绘制到哪个surface上

        #显示得分
        self.sb.show_score()

        #如果游戏处于非活动状态，就绘制Play按钮
        if not self.stats.game_active:
            self.play_button.draw_button()

        #让最近绘制的屏幕可见
        pygame.display.flip()

    def save_number_to_file(self, number, filename='D:\code\python\python编程从入门到实践项目\\alien_invasion\\number.txt'):
        """在number.txt中保存历史最高分"""
        with open(filename, 'r') as file:
            current_number = int(file.read())

        if number > current_number:
            with open(filename, 'w') as file:
                file.write(str(number))


        
if __name__ == '__main__': #这段有什么作用呢
    #创建游戏实例并运行游戏
    ai=AlienInvasion()
    ai.run_game()