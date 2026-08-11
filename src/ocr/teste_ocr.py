import cv2
import pytesseract

# Configurações do Tesseract
custom_config = r'--oem 3 --psm 6'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

imagem_cinza = cv2.imread('dados/entrada/bula_teste.jpeg', cv2.IMREAD_GRAYSCALE)
fx = 1  # Fator de escala para redimensionamento
fy = 1  # Fator de escala para redimensionamento

redimensionada = cv2.resize(
        imagem_cinza, None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR
    )

texto_extraido = pytesseract.image_to_string(redimensionada, config=custom_config)

cv2.imshow('Imagem Redimensionada', redimensionada)
cv2.waitKey(0)
cv2.destroyAllWindows()
