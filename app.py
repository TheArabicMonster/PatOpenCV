import cv2
import numpy as np
import onnxruntime as ort 

cap = cv2.VideoCapture(0) #capture de la webcam

opts = ort.SessionOptions() #objet de config de la bibliotheque onnxruntime
opts.intra_op_num_threads = 4 #nombre max de tthreads

session = ort.InferenceSession(
    "ultra_light_320.onnx", #chemin versle model
    sess_options=opts, #config de la session (nombre de threads)
    providers=['CPUExecutionProvider'] #qui vas executer le model (CPU) (peut aussi mettre CUDA, GPU etc)
)

while True:
    ret, frame = cap.read() #capture de la webcam
    if not ret: #si pas de frame -> break
        break

    #croper le centre l'image
    h, w = frame.shape[:2]
    target_w = int(h * 4 / 3) #calcul de la largeur cible pour un ratio 4:3
    x_start = (w - target_w) // 2 #calcul de la position de départ du crop
    x_end = x_start + target_w #calcul de la position de fin du crop
    frame_cropped = frame[0:h, x_start:x_end] #crop de l'image
    
    frame = cv2.resize(frame_cropped, (320, 240))#redimensionner l'image de la cam
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #conversion de l'image en RGB
    image_norm = (image_rgb - 127.5) / 128.0 #normalisation de l'image (valeurs des couleurs entre -1 et 1)
    image_transposed = np.transpose(image_norm, (2, 0, 1)) 
    input_tensor = np.expand_dims(image_transposed, axis=0).astype(np.float32)


    cv2.imshow("Webcam", frame) #affichage de la webcam

    if cv2.waitKey(1) & 0xFF == 27: #si on appuie sur la touche "echap"
        break

cap.release() #libération de la webcam
cv2.destroyAllWindows() #fermeture de toutes les fenêtres