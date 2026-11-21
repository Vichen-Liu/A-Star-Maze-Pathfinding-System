import sys
import pygame
import random

CELL_SIZE=30
MAZE_WIDTH=21
MAZE_HEIGHT=21

SCREEN_WIDTH=CELL_SIZE*MAZE_WIDTH
SCREEN_HEIGHT=CELL_SIZE*MAZE_HEIGHT+60

WHITE=(255,255,255)
BLACK=(0,0,0)
GRAY=(180,180,180)
BLUE=(0,100,255)
RED=(200,50,50)
GREEN=(50,200,50)

class Maze:
    def __init__(self):
        pygame.init()
        self.clock=pygame.time.Clock()
        self.screen=pygame.display.set_mode((int(SCREEN_WIDTH),int(SCREEN_HEIGHT)))
        pygame.display.set_caption("迷宫寻路")
        self.bg_color=WHITE
        self.start_button=pygame.Rect(10,10,100,40)
        self.answer_button=pygame.Rect(SCREEN_WIDTH-110,10,100,40)
        self.maze=None
        self.path=None
        self.player_position=(0,0)
        self.game_state="idle"
        self.wait_for_key=False
        self.player_steps=0
        self.best_steps=None
        self.show_path=False
        self.player_path=[]

    def create_maze(self):
        self.player_steps = 0
        self.best_steps = None
        self.maze=[]
        for y in range(MAZE_HEIGHT):
            row=[]
            for x in range(MAZE_WIDTH):
                row.append(1)
            self.maze.append(row)
        start_x,start_y=0,0
        self.maze[start_y][start_x]=0

        stack=[(start_x,start_y)]

        directions=[(2,0),(-2,0),(0,2),(0,-2)]

        while stack:
            x,y=stack[-1]
            random.shuffle(directions)
            carved=False

            for dx,dy in directions:
                nx,ny=x+dx,y+dy
                if(0<=nx<MAZE_WIDTH and 0<=ny<MAZE_HEIGHT and self.maze[ny][nx]==1):
                    self.maze[y+dy//2][x+dx//2]=0
                    self.maze[ny][nx]=0
                    stack.append((nx,ny))
                    carved=True
                    break
            if not carved:
                    stack.pop()
        self.player_position=(0,0)
        self.game_state="playing"
        self.path=None
        self.player_path=[(0,0)]
        self.show_path=False

    def way_search(self):
        start=(0,0)
        goal=(MAZE_WIDTH-1,MAZE_HEIGHT-1)

        g_cost={}
        g_cost[start]=0

        came_from={}
        open_list=[start]

        while open_list:
            best=None
            best_f=float('inf')
            for node in open_list:
                g=g_cost[node]
                h=abs(node[0]-goal[0])+abs(node[1]-goal[1])
                f=g+h
                if f<best_f:
                    best_f=f
                    best=node
            current=best
            open_list.remove(current)

            if current==goal:
                path=[current]
                while current in came_from:
                    current=came_from[current]
                    path.append(current)
                self.path=path[::-1]
                self.best_steps=len(path)-1
                return

            x,y=current

            for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)]:
                nx,ny=x+dx,y+dy
                if(0<=nx<MAZE_WIDTH and 0<=ny<MAZE_HEIGHT and self.maze[ny][nx]==0):
                    new_g=g_cost[current]+1
                    if(nx,ny)not in g_cost or new_g<g_cost[(nx,ny)]:
                        g_cost[(nx,ny)]=new_g
                        came_from[(nx,ny)]=current
                        if (nx,ny)not in open_list:
                            open_list.append((nx,ny))

    def draw_start_button(self):
        pygame.draw.rect(self.screen,GRAY,self.start_button)
        font=pygame.font.Font(None,28)
        text=font.render("start",True,BLACK)
        text_rect=text.get_rect(center=self.start_button.center)
        self.screen.blit(text,text_rect)

    def draw_answer_button(self):
        pygame.draw.rect(self.screen,GRAY,self.answer_button)
        font=pygame.font.Font(None,28)
        text=font.render("answer",True,BLACK)
        text_rect=text.get_rect(center=self.answer_button.center)
        self.screen.blit(text,text_rect)

    def draw_maze(self):
        if self.maze is None:
            return
        offset_y=60
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if self.maze[y][x]==1:
                    color=BLACK
                elif(x,y)==(0,0):
                    color=RED
                elif(x,y)==(MAZE_WIDTH-1,MAZE_HEIGHT-1):
                    color=RED
                else:
                    color=WHITE

                rect=pygame.Rect(
                    x*CELL_SIZE,
                    y*CELL_SIZE+offset_y,
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(self.screen,color,rect)
                pygame.draw.rect(self.screen,GRAY,rect,1)
        for (x,y) in self.player_path:
            if(x,y)==(0,0)or(x,y)==(MAZE_WIDTH-1,MAZE_HEIGHT-1):
                continue
            rect=pygame.Rect(x*CELL_SIZE+CELL_SIZE//3,y*CELL_SIZE+offset_y+CELL_SIZE//3,CELL_SIZE//3,CELL_SIZE//3)
            pygame.draw.rect(self.screen,GREEN,rect)

        if self.show_path and self.path:
            for (x,y) in self.path:
                if (x,y)==(0,0) or (x,y)==(MAZE_WIDTH-1,MAZE_HEIGHT-1):
                    continue
                rect=pygame.Rect(
                    x*CELL_SIZE+CELL_SIZE//4,
                    y*CELL_SIZE+offset_y+CELL_SIZE//4,
                    CELL_SIZE//2,
                    CELL_SIZE//2
                )
                pygame.draw.rect(self.screen,BLUE,rect)

        px,py=self.player_position
        offset_y=60
        player_rect=pygame.Rect(px*CELL_SIZE,py*CELL_SIZE+offset_y,CELL_SIZE,CELL_SIZE)
        pygame.draw.rect(self.screen,GREEN,player_rect)

        if self.game_state=="solved":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            font1=pygame.font.Font(None,128)
            text_win=font1.render("Win!",True,(255,215,0))
            rect_win=text_win.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2))
            self.screen.blit(text_win,rect_win)

            font2=pygame.font.Font(None,36)
            player_text=f"Your steps:{self.player_steps}"
            best_text=f"Best steps:{self.best_steps}"
            text_player = font2.render(player_text, True, WHITE)
            text_best = font2.render(best_text, True, WHITE)
            self.screen.blit(text_player, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(text_best, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70))

    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    sys.exit()
                elif event.type==pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        self.create_maze()
                    elif self.answer_button.collidepoint(event.pos):
                        if self.maze:
                            self.way_search()
                            self.show_path=True
                elif event.type==pygame.KEYDOWN and self.game_state=="playing":
                    x,y=self.player_position
                    nx,ny=x,y
                    if event.key==pygame.K_UP:
                        ny-=1
                    elif event.key==pygame.K_DOWN:
                        ny+=1
                    elif event.key==pygame.K_LEFT:
                        nx-=1
                    elif event.key==pygame.K_RIGHT:
                        nx+=1

                    if 0<=nx<MAZE_WIDTH and 0<=ny<MAZE_HEIGHT:
                        if self.maze[ny][nx]==0:
                            self.player_position=(nx,ny)
                            self.player_steps+=1
                            self.player_path.append((nx,ny))
                    if self.player_position==(MAZE_WIDTH-1,MAZE_HEIGHT-1):
                        self.game_state="solved"
                        if self.maze and self.best_steps is None:
                            self.way_search()
                            self.show_path=False
                elif event.type==pygame.KEYDOWN and self.game_state=="solved":
                    self.game_state="playing"

            self.screen.fill(self.bg_color)
            self.draw_start_button()
            self.draw_answer_button()
            self.draw_maze()

            pygame.display.flip()
            self.clock.tick(60)

if __name__=='__main__':
    maze=Maze()
    maze.run_game()


