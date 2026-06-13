import pygame
import json
import os
import glob
import math

# --- CONFIGS ---
LARGURA, ALTURA = 800, 600
FPS = 30
ZOOM = 250000 
FOLDER = "dispositivos"
CORES = [(255, 0, 85), (0, 255, 255), (255, 255, 0), (0, 255, 0), (200, 100, 255)]

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Multi-Device Radar")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Consolas", 14, bold=True)

c_lat, c_lon = None, None

def carregar_dispositivos():
    lista = []
    arquivos = glob.glob(os.path.join(FOLDER, "*.json"))
    for arq in arquivos:
        try:
            with open(arq, "r") as f:
                lista.append(json.load(f))
        except:
            pass
    return lista

rodando = True
while rodando:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: rodando = False
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE: c_lat = None # Recalibra centro

    tela.fill((15, 15, 15))
    
    # Desenha Grid
    for x in range(0, LARGURA, 50): pygame.draw.line(tela, (30, 30, 30), (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, 50): pygame.draw.line(tela, (30, 30, 30), (0, y), (LARGURA, y))

    dispositivos = carregar_dispositivos()
    
    if dispositivos:
        # Define centro pelo primeiro dispositivo
        if c_lat is None:
            c_lat = dispositivos[0].get("lat")
            c_lon = dispositivos[0].get("lon")

        for i, dev in enumerate(dispositivos):
            cor = CORES[i % len(CORES)]
            
            # Pega dados com segurança (evita KeyError)
            lat = dev.get("lat", 0)
            lon = dev.get("lon", 0)
            direcao = dev.get("dir", 0)
            dev_id = dev.get("id", "Desconhecido")
            dev_time = dev.get("time", "--:--:--")

            # Conversão
            x = (lon - c_lon) * ZOOM + (LARGURA // 2)
            y = (c_lat - lat) * ZOOM + (ALTURA // 2)

            # Offset visual para não sobrepor totalmente
            offset = i * 5
            fx, fy = x + offset, y + offset

            # Desenha Ponto
            pygame.draw.circle(tela, cor, (int(fx), int(fy)), 10)
            pygame.draw.circle(tela, (255, 255, 255), (int(fx), int(fy)), 10, 2)
            
            # Seta de direção
            ang = math.radians(direcao - 90)
            pygame.draw.line(tela, cor, (fx, fy), (fx + math.cos(ang)*20, fy + math.sin(ang)*20), 3)

            # Texto (Aqui estava o erro, agora protegido com .get)
            info = f"{dev_id} | {dev_time}"
            label = fonte.render(info, True, (255, 255, 255))
            tela.blit(label, (fx + 15, fy - 15))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()