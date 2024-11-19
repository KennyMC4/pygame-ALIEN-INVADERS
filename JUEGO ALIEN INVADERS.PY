import pygame
import random
import os

pygame.init()
pygame.mixer.init()


fondo = pygame.image.load("imagenes/fondo.png")
laser_sonido = pygame.mixer.Sound("imagenes/laser.wav")
explosion_sonido = pygame.mixer.Sound("imagenes/explosion.wav")
golpe_sonido = pygame.mixer.Sound("imagenes/golpe.wav")


width, height = fondo.get_width(), fondo.get_height()
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Juego Alien Invaders")
fps = 60
clock = pygame.time.Clock()
blanco, negro = (255, 255, 255), (0, 0, 0)


score = 0
vida = 100
nivel = 1
enemigos_minimos = 5  
pausa = False
velocidad_fondo = 2
fondo_y = 0


tiempo_enemigos = pygame.USEREVENT + 1
pygame.time.set_timer(tiempo_enemigos, 2000)


explosion_list = []
for i in range(1, 8):  
    explosion = pygame.image.load(f"explosion/{i}.png").convert_alpha()
    explosion_list.append(explosion)


def texto_puntuacion(frame, text, size, x, y):
    font = pygame.font.SysFont("small fonts", size, bold=True)
    text_frame = font.render(text, True, blanco, negro)
    text_rect = text_frame.get_rect()
    text_rect.midtop = (x, y)
    frame.blit(text_frame, text_rect)

def barra_vida(frame, x, y, nivel):
    longitud, alto = 100, 20
    fill = int((nivel / 100) * longitud)
    border = pygame.Rect(x, y, longitud, alto)
    fill_rect = pygame.Rect(x, y, fill, alto)
    pygame.draw.rect(frame, (255, 0, 55), fill_rect)
    pygame.draw.rect(frame, negro, border, 4)

def mostrar_menu_principal():
    menu_activo = True
    while menu_activo:
        window.fill(negro)
        texto_puntuacion(window, "ALIEN INVADERS", 50, width // 2, height // 4)
        texto_puntuacion(window, "Presiona ENTER para jugar", 30, width // 2, height // 2)
        texto_puntuacion(window, "Presiona ESC para salir", 20, width // 2, height // 1.5)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  
                    menu_activo = False
                elif event.key == pygame.K_ESCAPE:  
                    pygame.quit()
                    exit()

def mostrar_game_over():
    window.fill(negro)
    texto_puntuacion(window, "GAME OVER", 50, width // 2, height // 4)
    texto_puntuacion(window, f"PUNTUACIÓN: {score}", 30, width // 2, height // 2)
    texto_puntuacion(window, "Presiona R para reiniciar o ESC para salir", 20, width // 2, height // 1.5)
    pygame.display.flip()

    esperando = True
    while esperando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  
                    reiniciar_juego()
                    return
                elif event.key == pygame.K_ESCAPE:  
                    pygame.quit()
                    exit()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosion_list[0]
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_list):
                self.kill()  
            else:
                self.image = explosion_list[self.frame]
                self.rect = self.image.get_rect(center=self.rect.center)


class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("imagenes/A1.png")
        self.rect = self.image.get_rect(center=(width // 2, height - 50))
        self.velocidad_x = 0
        self.vida = 100

    def update(self):
        self.velocidad_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.velocidad_x = -5
        elif keystate[pygame.K_RIGHT]:
            self.velocidad_x = 5

        self.rect.x += self.velocidad_x
        if self.rect.right > width:
            self.rect.right = width
        elif self.rect.left < 0:
            self.rect.left = 0

    def disparar(self):
        bala = Balas(self.rect.centerx, self.rect.top)
        grupo_balas_jugador.add(bala)
        laser_sonido.play()


class Enemigos(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("imagenes/E1.png").convert_alpha()
        self.rect = self.image.get_rect(x=random.randint(0, width - 50), y=random.randint(-100, -40))
        self.velocidad_y = random.randint(2, 6)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > height:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, width - 50)

        
        now = pygame.time.get_ticks()
        if now - self.last_shot > random.randint(1000, 3000):
            self.disparar()
            self.last_shot = now

    def disparar(self):
        bala = Balas_enemigos(self.rect.centerx, self.rect.bottom)
        grupo_balas_enemigos.add(bala)
        laser_sonido.play()


class Balas(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("imagenes/B2.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = -10

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0:
            self.kill()


class Balas_enemigos(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("imagenes/B1.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 5

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > height:
            self.kill()


grupo_jugador = pygame.sprite.GroupSingle()
grupo_enemigos = pygame.sprite.Group()
grupo_balas_jugador = pygame.sprite.Group()
grupo_balas_enemigos = pygame.sprite.Group()
grupo_explosiones = pygame.sprite.Group()

player = Jugador()
grupo_jugador.add(player)


def reiniciar_juego():
    global score, vida, fondo_y, pausa
    score = 0
    vida = 100
    fondo_y = 0
    pausa = False
    grupo_enemigos.empty()
    grupo_balas_jugador.empty()
    grupo_balas_enemigos.empty()
    grupo_explosiones.empty()

reiniciar_juego()


mostrar_menu_principal()

run = True
while run:
    clock.tick(fps)

    
    fondo_y += velocidad_fondo
    if fondo_y >= height:
        fondo_y = 0
    window.blit(fondo, (0, fondo_y))
    window.blit(fondo, (0, fondo_y - height))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.disparar()
            if event.key == pygame.K_p:
                pausa = not pausa
        elif event.type == tiempo_enemigos:  
            enemigo = Enemigos()
            grupo_enemigos.add(enemigo)

    if not pausa:
        
        if len(grupo_enemigos) < enemigos_minimos:
            for _ in range(enemigos_minimos - len(grupo_enemigos)):
                enemigo = Enemigos()
                grupo_enemigos.add(enemigo)

        
        grupo_jugador.update()
        grupo_enemigos.update()
        grupo_balas_jugador.update()
        grupo_balas_enemigos.update()
        grupo_explosiones.update()

        
        colisiones_balas = pygame.sprite.groupcollide(grupo_balas_jugador, grupo_balas_enemigos, True, True)

        
        colisiones_balas_jugador = pygame.sprite.spritecollide(player, grupo_balas_enemigos, True)
        for bala in colisiones_balas_jugador:
            vida -= 10  
            golpe_sonido.play()  
            if vida <= 0:
                mostrar_game_over()

        
        colisiones = pygame.sprite.groupcollide(grupo_enemigos, grupo_balas_jugador, True, True)
        for enemigo in colisiones:
            score += 10
            explosion = Explosion(enemigo.rect.center)
            grupo_explosiones.add(explosion)
            explosion_sonido.set_volume(0.3)  
            explosion_sonido.play()

        
        grupo_jugador.draw(window)
        grupo_enemigos.draw(window)
        grupo_balas_jugador.draw(window)
        grupo_balas_enemigos.draw(window)
        grupo_explosiones.draw(window)

        
        texto_puntuacion(window, f"SCORE: {score}", 30, width - 100, 10)
        barra_vida(window, 10, 10, vida)
    else:
        texto_puntuacion(window, "PAUSA", 50, width // 2, height // 2)
        pygame.display.flip()

    pygame.display.flip()

pygame.quit()




