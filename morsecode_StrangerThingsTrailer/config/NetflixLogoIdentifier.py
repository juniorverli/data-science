from copyreg import pickle
import cv2
import pickle

#Tamanho necessário para criação do retangulo na imagem
width, height = 150, 60

#Lista responsável por conter todas as posições dos retangulos na imagem
posList = []

try:
    with open('NetflixLogoPos', 'wb') as f:
        posList = pickle.load(f)

except:

    posList = []

def mouseClick(events,x,y,flags,params):
    #Cria o posicionamento da area do retangulo em que ficará o logo
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x,y))
    #Remove o posicionamento criado acima clickando em cima do quadrado
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)
    
    #salva no arquivo de configuração de posicionamento do retangulo
    with open('NetflixLogoPos', 'wb') as f:
        pickle.dump(posList, f)
    
while True:
    #lendo o frame printado do vídeo utilizada para treino
    img = cv2.imread('assets/StrangerThings_Moment.jpg')

    #retorna todos os retangulos na imagem, posição, tamanho e cor
    for pos in posList:
        cv2.rectangle(img,pos,(pos[0]+width, pos[1]+height), (255,0,255),2)

    #mostrando a imagem
    cv2.imshow("Image", img)
    #função executada pelo mouse na imagem mostrada
    cv2.setMouseCallback("Image", mouseClick)
    #tempo de espera do método waitKey
    cv2.waitKey(1)
