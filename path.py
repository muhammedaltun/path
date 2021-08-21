x = 140
y = 40
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

import pygame, sys, math
from pygame.locals import *

WINDOWWIDTH = 720                          # size of window's width in pixels
WINDOWHEIGHT = 720                         # size of windows' height in pixels
CELLSIZE = 20                              # size of box height & width in pixels

BLACK    = (  0,   0,   0)
GRAY     = (100, 100, 100)
WHITE    = (255, 255, 255)
YELLOW   = (255, 255,   0)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)

points = [(73,86),(687,655)]

def main():
    global DISPLAYSURF
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    DISPLAYSURF.fill(GRAY)
    pygame.display.set_caption('PATH')

    drawGrid()
    for p in points:
        pygame.draw.circle(DISPLAYSURF, BLACK, p, 4, 0)
    
    
    painted = set()
    while True:                                # main loop
        for event in pygame.event.get():       # event handling loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if len(points) != 2: 
                    points.append(pos)
                    pygame.draw.circle(DISPLAYSURF, BLACK, pos, 4, 0)
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos     
            elif event.type == KEYDOWN:
                if event.key == K_RETURN: 
                    

                    DISPLAYSURF.fill(GRAY)                   
                    for p in painted:
                        paintCell(p[0],p[1],YELLOW) 
                    drawGrid() 
                    for p in points:
                        pygame.draw.circle(DISPLAYSURF, BLACK, p, 4, 0)
                    
                    m = minPath(points[0],points[1],painted)
                    if  m != []:
                        for i in range(len(m)-1):
                            pygame.draw.line(DISPLAYSURF, RED, m[i], m[i+1], 3)
                    
                    
                    
        if pygame.mouse.get_pressed()[0]: 
            (l,t) = cellCoordinates(mousex,mousey)
            if len(points) == 2:
                paintCell(l,t,YELLOW)
                drawGrid()
                painted.add((l,t))
        

        pygame.display.update()


def allCellVertices(cells):
    result = set()
    for cell in cells:
        vert = tuple(c*CELLSIZE for c in cell)
        vert1 = (vert[0]+CELLSIZE,vert[1])
        vert2 = (vert[0]+CELLSIZE,vert[1]+CELLSIZE)
        vert3 = (vert[0],vert[1]+CELLSIZE)
        result.add(vert)
        result.add(vert1)
        result.add(vert2)
        result.add(vert3)
    return result

def cellCoordinates(x,y):
    left = math.floor(x/CELLSIZE)
    top = math.floor(y/CELLSIZE)
    return (left,top)

def cellVertices(cell):
    vert = tuple(c*CELLSIZE for c in cell)
    vert1 = (vert[0],vert[1]+CELLSIZE)
    vert2 = (vert[0]+CELLSIZE,vert[1]+CELLSIZE)
    vert3 = (vert[0]+CELLSIZE,vert[1])
    return [vert,vert1,vert2,vert3]

def cellNeighbors(cell):
    a,b = cell[0],cell[1]
    return [(a+1,b+1),(a+1,b),(a+1,b-1),(a,b-1),(a-1,b-1),(a-1,b),(a-1,b+1),(a,b+1)]

def check(point1,point2,point3):     # checks if point3 is on the line passing through point1, point2
    lineVector = (point2[0]-point1[0],point2[1]-point1[1])
    vector = (point3[0]-point1[0],point3[1]-point1[1])
    determinant = lineVector[0]*vector[1] - lineVector[1]*vector[0]
    if determinant == 0: return 0     # 0 if they are linear
    if determinant > 0: return 1      # 1 if point3 is at one side of the line
    if determinant < 0: return -1     # -1 if point3 is on the other side of the line

def corners(cells):
    result = set()
    verts = allCellVertices(cells)
    for v in verts:
        if len(set(pointNeighbors(v[0],v[1])).intersection(cells)) == 1: result.add(v)
    return result

def distance(point1,point2):
    return math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, BLACK, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, BLACK, (0, y), (WINDOWWIDTH, y))   

def importantVertices(point,obstacle): 
    result = set()
    for v in corners(obstacle):
        if lineExists(point,v,obstacle): result.add(v)
    return result 

def imVertices(point,obstacle):
    result = set()
    for v in importantVertices(point,obstacle):
        if importantVertices(v,obstacle) - importantVertices(point,obstacle) != set(): result.add(v)
    return result

def linePassesCell(point1,point2,cell):
    vertices = cellVertices(cell)
    if check(point1,point2,vertices[0]) * check(point1,point2,vertices[2]) == -1 or check(point1,point2,vertices[1]) * check(point1,point2,vertices[3]) == -1:
        return True
    else: return False

def lineCells(point1,point2):
    lis = []
    if point1[0] % CELLSIZE == 0 and point1[0] ==point2[0]: return lis
    if point1[1] % CELLSIZE == 0 and point1[1] ==point2[1]: return lis

    dist = WINDOWWIDTH**2 + WINDOWHEIGHT**2
    for n in pointNeighbors(point2[0],point2[1]):
        if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point1[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point1[1])**2 < dist:
            last = n
            dist = (n[0]*CELLSIZE+CELLSIZE/2-point1[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point1[1])**2

    dist = WINDOWWIDTH**2 + WINDOWHEIGHT**2
    for n in pointNeighbors(point1[0],point1[1]):
        if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
            first = n
            dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
    
    lis.append(first)
    
    while True:
        verticeNeighbors = [cellNeighbors(first)[i] for i in range(8) if i % 2 == 0]
        edgeNeighbors = [cellNeighbors(first)[i] for i in range(8) if i % 2 == 1]
        for n in edgeNeighbors:
            if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
                first = n
                lis.append(first)
                dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
        if first == last: break
        for n in verticeNeighbors:
            if linePassesCell(point1,point2,n) and (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2 < dist:
                first = n
                lis.append(first)
                dist = (n[0]*CELLSIZE+CELLSIZE/2-point2[0])**2 + (n[1]*CELLSIZE+CELLSIZE/2-point2[1])**2
        if first == last: break

    return lis

def lineExists(point1,point2,obstacle):
    neigh1 = pointNeighbors(point1[0],point1[1])
    neigh2 = pointNeighbors(point2[0],point2[1])
    if point1 == point2: return True

    if point1[0] % CELLSIZE == 0 and point1[1] % CELLSIZE == 0 and point2[0] % CELLSIZE == 0 and point2[1] % CELLSIZE == 0:
        if neigh1[2] == neigh2[1] in obstacle and neigh1[3] == neigh2[0] in obstacle: return False
        if neigh1[1] == neigh2[2] in obstacle and neigh1[0] == neigh2[3] in obstacle: return False
        if neigh1[0] == neigh2[1] in obstacle and neigh1[3] == neigh2[2] in obstacle: return False
        if neigh1[1] == neigh2[0] in obstacle and neigh1[2] == neigh2[3] in obstacle: return False

    if set(lineCells(point1,point2)).intersection(obstacle) != set(): return False
    for v in allCellVertices(obstacle):
        neigh = pointNeighbors(v[0],v[1])
        if check(point1,point2,v) == 0:
            if point1[0] == point2[0] and (point1[1] < v[1] < point2[1] or point2[1] < v[1] < point1[1]):
                    if neigh[0] in obstacle and neigh[3] in obstacle: return False
                    if neigh[1] in obstacle and neigh[2] in obstacle: return False
            
            if point1[1] == point2[1] and (point1[0] < v[0] < point2[0] or point2[0] < v[0] < point1[0]):
                if neigh[0] in obstacle and neigh[1] in obstacle: return False
                if neigh[2] in obstacle and neigh[3] in obstacle: return False
            
            if point1[1] < v[1] < point2[1] or point2[1] < v[1] < point1[1]:
                if neigh[0] in obstacle and neigh[2] in obstacle: return False
                if neigh[1] in obstacle and neigh[3] in obstacle: return False

            if point1[0] < v[0] < point2[0] or point2[0] < v[0] < point1[0]:
                if neigh[0] in obstacle and neigh[2] in obstacle: return False
                if neigh[1] in obstacle and neigh[3] in obstacle: return False
    return True

def paintCell(x,y,colour):
    pygame.draw.rect(DISPLAYSURF, colour, (CELLSIZE*x, CELLSIZE*y, CELLSIZE, CELLSIZE))

def pointNeighbors(x,y):
    left = math.floor(x/CELLSIZE)
    top = math.floor(y/CELLSIZE)
    if x % CELLSIZE == 0 and y % CELLSIZE == 0: return [(left,top),(left,top-1),(left-1,top-1),(left-1,top)]
    if x % CELLSIZE != 0 and y % CELLSIZE != 0: return [(left,top)]
    if x % CELLSIZE != 0: return [(left,top),(left,top-1)]     
    if y % CELLSIZE != 0: return [(left,top),(left-1,top)]


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]

def subtract(a,b):
    return [a[0]-b[0],a[1]-b[1]]

def cosineSimilarity(a, b):
    return (dot(a,b))**2/(dot(a,a) * dot(b,b))



def minPath(p1,p2,obstacle):
    
    if lineExists(p1,p2,obstacle): return [p1,p2]
    
    inf = math.inf
    corn = {p1,p2}.union(corners(obstacle))
    corns = list(corn) 
    l = len(corns)
    distanceDict = {}
    for i in range(l):
        for j in range(l):
            if i < j: 
                if lineExists(corns[i],corns[j],obstacle):
                    dist = distance(corns[i],corns[j])  
                    distanceDict[(corns[i],corns[j])] = dist
                    distanceDict[(corns[j],corns[i])] = dist
                else:
                    distanceDict[(corns[i],corns[j])] = inf
                    distanceDict[(corns[j],corns[i])] = inf
    
    dic = {}
    for c in corns: 
        distanceDict[(c,c)] = 0
        dic[c] = [distanceDict[(c,p1)],p1]
    unvisited = corn - {p1}
    minAt = p1
    for u in unvisited:
        if minAt == p1: minAt = u
        elif dic[u][0] < dic[minAt][0]: minAt = u 
    
    while dic[minAt][0] < inf and unvisited != set():
        unvisited = unvisited - {minAt}
        for u in unvisited:
            dist = distanceDict[(minAt,u)] + dic[minAt][0]
            if dic[u][0] > dist: dic[u] = [dist,minAt]
        m = minAt
        for u in unvisited:
            if minAt == m: minAt = u
            elif dic[u][0] < dic[minAt][0]: minAt = u

    last = p2
    thePath = [p2]

    while last != p1:
        last = dic[last][1]
        thePath.append(last)
    
          
    return thePath






main()
