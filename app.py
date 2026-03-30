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

    input_name = session.get_inputs()[0].name #nom de l'input du model
    outputs = session.run(None, {input_name: input_tensor}) #exécution du model

    conf_scores = outputs[0][0, :, 1] 
    candidate_boxes = outputs[1][0, :, :]

    idxs = np.where(conf_scores > 0.7)[0] #seuillage des scores de confiance

    final_boxes = []
    final_scores = []

    for idx in idxs:
        x1, y1, x2, y2 = candidate_boxes[idx] #coordonnées de la box

        #coordonnées de la box en pixels 
        left = int(x1 * 320)
        top = int(y1 * 240)
        right = int(x2 * 320)
        bottom = int(y2 * 240)

        final_boxes.append([left, top, right - left, bottom - top]) # Format [x, y, w, h]
        final_scores.append(float(conf_scores[idx]))

    indices = cv2.dnn.NMSBoxes(final_boxes, final_scores, 0.7, 0.3) 
    
    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = final_boxes[i]
            # Dessiner le rectangle sur l'image 'frame' (320x240)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # Ajouter le score au dessus du carré
            text = f"{final_scores[i]:.2f}"
            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imshow("Webcam", frame) #affichage de la webcam

    if cv2.waitKey(1) & 0xFF == 27: #si on appuie sur la touche "echap"
        break

cap.release() #libération de la webcam
cv2.destroyAllWindows() #fermeture de toutes les fenêtres