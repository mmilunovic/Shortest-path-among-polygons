import pyvisgraph as vg
#from visgraph.vis_graph import VisGraph as vg
import pygame

pygame.init()

display_width = 1280
display_height = 720

black = (0, 0, 0)
white = (255, 255, 255)
red = (237, 41, 57)
gray = (169, 169, 169)
green = (0, 128, 0)

LEFT = 1
RIGHT = 3

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('2.6 Milos Milunovic RN 17-2016')
clock = pygame.time.Clock()

def draw_polygon(polygon, color, size, complete=True):
    if complete:
        polygon.append(polygon[0])
    p1 = polygon[0]
    for p2 in polygon[1:]:
        pygame.draw.line(gameDisplay, color, (p1.x, p1.y), (p2.x, p2.y), size)
        p1 = p2

def draw_visible_vertices(edges, color, size):
    for edge in edges:
        pygame.draw.line(gameDisplay, color, (edge.p1.x, edge.p1.y), (edge.p2.x, edge.p2.y), size)

def draw_text(mode_txt, color, size, x, y):
    font = pygame.font.SysFont(None, size)
    text = font.render(mode_txt, True, color)
    gameDisplay.blit(text, (x, y))

def help_screen():
    rectw = 550
    recth = 500
    rectwi = rectw-10
    recthi = recth-10
    startx = display_width*0.5-rectw/2
    starty = display_height*0.5-recth/2
    startxi = display_width*0.5-rectwi/2
    startyi = display_height*0.5-recthi/2

    helping = True
    while helping:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_h:
                    helping = False

        pygame.draw.rect(gameDisplay, black, (startx, starty, rectw, recth))
        pygame.draw.rect(gameDisplay, white, (startxi, startyi, rectwi, recthi))

        draw_text("-- 2.6 Shortest path among polygons --", black, 30, startxi+90, startyi+10)
        draw_text("Q - QUIT", black, 25, startxi+10, startyi+100)
        draw_text("H - Toggle Help", black, 25, startxi+10, startyi+150)
        draw_text("D - Draw polygons", black, 25, startxi+10, startyi+200)
        draw_text("C - Clear polygons", black, 25, startxi+10, startyi+250)
        draw_text("S - Mark start and finish", black, 25, startxi+10, startyi+300)
        pygame.display.update()
        clock.tick(10)

class Simulator():

    def __init__(self):
        self.polygons = []
        self.work_polygon = []
        self.mouse_point = None
        self.start_point = None
        self.end_point = None
        self.shortest_path = []

        self.g = vg.VisGraph()
        self.built = False
        self.mode_draw = True
        self.mode_path = False

    def toggle_draw_mode(self):
        self.mode_draw = not self.mode_draw
        self._clear_shortest_path()
        self.mode_path = False

    def close_polygon(self):
        if len(self.work_polygon) > 1:
            self.polygons.append(self.work_polygon)
            self.work_polygon = []
            self.g.build(self.polygons, status=False)
            self.built = True

    def toggle_shortest_path_mode(self):
        if self.mode_path:
            self._clear_shortest_path()
        self.mode_path = not self.mode_path
        self.mode_draw = False

    def clear_all(self):
        self.__init__()

    def _clear_shortest_path(self):
        self.shortest_path = []
        self.start_point = []
        self.end_point = [] 

def game_loop():
    sim = Simulator()
    gameExit = False

    while not gameExit:

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_h:
                    help_screen()
                elif event.key == pygame.K_d:
                    sim.toggle_draw_mode()
                elif event.key == pygame.K_s:
                    sim.toggle_shortest_path_mode()

            if sim.mode_draw:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_c:
                        sim.clear_all()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == LEFT:
                        sim.work_polygon.append(vg.Point(pos[0], pos[1]))
                    elif event.button == RIGHT:
                        sim.close_polygon()

            if sim.mode_path and sim.built:
                if event.type == pygame.MOUSEBUTTONUP or any(pygame.mouse.get_pressed()):
                    if pygame.mouse.get_pressed()[LEFT-1] or event.button == LEFT:
                        sim.start_point = vg.Point(pos[0], pos[1])
                    elif pygame.mouse.get_pressed()[RIGHT-1] or event.button == RIGHT:
                        sim.end_point = vg.Point(pos[0], pos[1])
                    if sim.start_point and sim.end_point:
                        sim.shortest_path = sim.g.shortest_path(sim.start_point, sim.end_point)
           
        gameDisplay.fill(white)

        if len(sim.work_polygon) > 1:
            draw_polygon(sim.work_polygon, black, 3, complete=False)

        if len(sim.polygons) > 0:
            for polygon in sim.polygons:
                draw_polygon(polygon, black, 3)
        if len(sim.shortest_path) > 1:
            draw_polygon(sim.shortest_path, red, 3, complete=False)

        if sim.mode_draw:
            draw_text("-- Drawing --", black, 25, 5, 5)
        elif sim.mode_path:
            draw_text("-- Path --", black, 25, 5, 5)
        else:
            draw_text("-- Help --", black, 25, 5, 5)

        pygame.display.update()
        clock.tick(20)

if __name__ == "__main__":
    gameDisplay.fill(white)
    help_screen()
    game_loop()
    pygame.quit()
    quit()
