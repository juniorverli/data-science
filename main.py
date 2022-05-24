import cv2
import pickle
import cvzone
import numpy as np
import morse_code

#Lê a posição fixa do logo da Netflix
with open('config/NetflixLogoPos', 'rb') as f:
        posList = pickle.load(f)

#Retorna o tamanho da dimensão necessária para o quadrado 
width, height = 150, 60

def checkNetflixLogo(imgPro):
    #verifica todas as posições contidas no arquivo NetflixLogoPos
    for pos in posList:
        #retorna as posições x,y e realiza o corte da área do logo
        x, y = pos
        imgCrop = imgPro[y:y+height, x:x+width]
        cv2.imshow(str(x*y),imgCrop)
        count = cv2.countNonZero(imgCrop)
        cvzone.putTextRect(img, str(count), (x,y+height-10), scale = 1, thickness=1, offset=0)

        #se for maior que 3000 tem logo se for menor não tem
        if count > 3000:
            color = (0,255,0)
            tickness = 1
        else:
            color = (0,0,255)
            tickness = 1
        #retorna todos os retangulos na imagem, posição, tamanho e cor
        cv2.rectangle(img,pos,(pos[0]+width, pos[1]+height), (color),tickness)

    return count

### Variaveis utilizadas
COUNTER = 0
BREAK_COUNTER = 0
APPEAR_COUNTER = 0
CLOSED = False
WORD_PAUSE = False
PAUSED = False
CONSEC_FRAMES = 2
CONSEC_FRAMES_CLOSED = 5
PAUSE_CONSEC_FRAMES = 9
WORD_PAUSE_CONSEC_FRAMES = 9
BREAK_LOOP_FRAMES = 120
#retorna o código total
total_morse = ""
#retorna a palavra
morse_word = ""
#retorna o caractere
morse_char = ""


#cria o método de captura em tela através do vídeo
cap = cv2.VideoCapture('assets/StrangerThings4.mp4')
#time.sleep(1.0)

while True:
    #contador e posicionador dos frames dos vídeos
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    #tempo de espera antes de executar o próximo passo
    cv2.waitKey(10)
    #lendo o vídeo utilizado para decodificação do código morse
    success, img = cap.read()
    #sequencia de imagens criadas para chegar na imagem dilatada
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25,15)
    imgMedian = cv2.medianBlur(imgThreshold,5)
    kernel = np.ones((3,3),np.uint8)
    #imagem responsável por identificar se há o logo ou não
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    

    if checkNetflixLogo(imgDilate) < 3000:
        COUNTER += 1
        BREAK_COUNTER += 1
        if COUNTER >= CONSEC_FRAMES:
            CLOSED = True
        #limpa o código morse quando houver o caractere "/"
        if not PAUSED:
            morse_char = ""
        #assim que é finalizado a decodificação do código morse, 
        #aqui é realizado o tempo de espera antes de fechar o vídeo
        if (BREAK_COUNTER >= BREAK_LOOP_FRAMES):
            break
    else:
        #enquanto o logo aparece por pouco tempo  
        if (BREAK_COUNTER < BREAK_LOOP_FRAMES):
            BREAK_COUNTER = 0
            APPEAR_COUNTER += 1
        #detectado que o logo sumiu por muito tempo
        #registra caractere "-"
        if COUNTER >= CONSEC_FRAMES_CLOSED:
            morse_word += "-"
            total_morse += "-"
            morse_char += "-"
        #reseta o contador de frames
            COUNTER = 0
            CLOSED = False
            PAUSED = True
            APPEAR_COUNTER = 0
        #detectado que o logo sumiu por pouco tempo
        #registra caractere "."
        elif CLOSED:
            morse_word += "."
            total_morse += "."
            morse_char += "."
            COUNTER = 1
            CLOSED = False
            PAUSED = True
            APPEAR_COUNTER = 0
        #responsavel por adicionar espaço entre as letras
        #somente se o logo que aparece for maior que PAUSE_CONSEC_FRAMES
        elif PAUSED and (APPEAR_COUNTER >= 
            PAUSE_CONSEC_FRAMES):
            morse_word += "/"
            total_morse += "/"
            morse_char = "/"
            PAUSED = False
            WORD_PAUSE = True
            CLOSED = False
            APPEAR_COUNTER = 0
            morse_word = ""
            #responsavel por adicionar espaço entre as palavras
            #somente se o logo que aparece for maior que WORD_PAUSE_CONSEC_FRAMES
        elif (WORD_PAUSE and APPEAR_COUNTER >= WORD_PAUSE_CONSEC_FRAMES):
        #converte o caractere "¦" para espaço entre as palavras
            total_morse += "¦/"
            morse_char = ""
            WORD_PAUSE = False
            CLOSED = False
            APPEAR_COUNTER = 0

        #retorna na imagem o código morse, o retangulo da área do logo
        #e a mensagem decodificada
        cv2.putText(img, "Codigo Morse: {}".format(morse_char), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, "NetflixLogo: {:.2f}".format(checkNetflixLogo(imgDilate)), (600, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, "Mensagem: {}".format(morse_code.from_morse(total_morse)), (10,100), 
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
    #mostrando a imagem
    cv2.imshow('Image', img)
    #cv2.imshow('Image2', imgThreshold)
    #cv2.imshow('Image3', imgMedian)
    #tempo de espera do método waitKey
    cv2.waitKey(1)

#após a execução do vídeo é destruido todas as telas geradas pelo código
cv2.destroyAllWindows()
#print final do código morse decodificado
print("Codigo Morse: {}".format(morse_code.from_morse(total_morse)))