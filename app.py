import cv2
import numpy as np
import onnxruntime as ort
import argparse
import os
import sys
from PIL import Image as PILImage

# ─── Chemin compatible PyInstaller (bundle) et dev ───────────────────────────

def resource_path(relative_path):
    """Retourne le chemin absolu, compatible avec PyInstaller --onefile."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

# ─── Constantes ──────────────────────────────────────────────────────────────

PATH_GIF         = resource_path("patHand.gif")
GIF_TARGET_SIZE  = (96, 100)
GIF_OFFSET       = (-50, -70)
IMAGE_TARGET_SIZE = (70, 70)
IMAGE_OFFSET      = (-90, GIF_OFFSET[1])

# ─── Fonctions utilitaires ───────────────────────────────────────────────────

def load_image(path, target_size):
    img_bgr = cv2.imread(path)
    if img_bgr is None:
        print(f"Error loading image: {path}")
        return None
    img_resized = cv2.resize(img_bgr, target_size)
    img_bgra = cv2.cvtColor(img_resized, cv2.COLOR_BGR2BGRA)
    img_bgra[:, :, 3] = 255

    h, w = img_bgra.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)
    radius = min(h, w) // 2
    cv2.circle(mask, center, radius, 255, -1)
    img_bgra[:, :, 3] = mask
    return img_bgra

def load_gif(path, target_size):
    try:
        gif = PILImage.open(path)
    except Exception as e:
        print(f"Erreur lors du chargement du GIF: {e}")
        return None

    frames = []
    try:
        while True:
            frame_rgba = PILImage.new("RGBA", gif.size, (0, 0, 0, 0))
            frame_rgba.paste(gif.convert("RGBA"), (0, 0))
            frame_rgba = frame_rgba.resize(target_size, PILImage.Resampling.LANCZOS)
            opencv_frame = cv2.cvtColor(np.array(frame_rgba), cv2.COLOR_RGBA2BGRA)
            frames.append(opencv_frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames

def rotate_frame(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), -angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))

def overlay_transparent(background, overlay, x, y):
    h_ov, w_ov = overlay.shape[:2]
    h_bg, w_bg = background.shape[:2]

    if x >= w_bg or y >= h_bg or x + w_ov <= 0 or y + h_ov <= 0:
        return background

    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w_ov, w_bg), min(y + h_ov, h_bg)

    overlay_x1, overlay_y1 = max(0, -x), max(0, -y)
    overlay_x2, overlay_y2 = overlay_x1 + (x2 - x1), overlay_y1 + (y2 - y1)

    overlay_region    = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2]
    background_region = background[y1:y2, x1:x2]

    b_ov, g_ov, r_ov, a_ov = cv2.split(overlay_region)
    alpha     = a_ov / 255.0
    inv_alpha = 1.0 - alpha

    background[y1:y2, x1:x2, 0] = (alpha * b_ov + inv_alpha * background_region[:, :, 0]).astype(np.uint8)
    background[y1:y2, x1:x2, 1] = (alpha * g_ov + inv_alpha * background_region[:, :, 1]).astype(np.uint8)
    background[y1:y2, x1:x2, 2] = (alpha * r_ov + inv_alpha * background_region[:, :, 2]).astype(np.uint8)
    return background

# ─── Fonction principale (importable + CLI) ───────────────────────────────────

def main(image_path=None):
    gif_frames = load_gif(PATH_GIF, GIF_TARGET_SIZE) or []
    gif_total_frames  = len(gif_frames)
    gif_frame_counter = 0

    cap = cv2.VideoCapture(0)

    opts = ort.SessionOptions()
    opts.intra_op_num_threads  = 4
    opts.log_severity_level    = 3

    facemark = cv2.face.createFacemarkLBF()
    facemark.loadModel(resource_path("lbfmodel.yaml"))

    session = ort.InferenceSession(
        resource_path("ultra_light_320.onnx"),
        sess_options=opts,
    )

    static_image = None
    if image_path:
        static_image = load_image(image_path, IMAGE_TARGET_SIZE)
        if static_image is None:
            print(f"Warning: Could not load static image '{image_path}'")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        target_w  = int(h * 4 / 3)
        x_start   = (w - target_w) // 2
        frame_cropped = frame[0:h, x_start:x_start + target_w]
        frame = cv2.resize(frame_cropped, (320, 240))

        image_rgb        = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_norm       = (image_rgb - 127.5) / 128.0
        image_transposed = np.transpose(image_norm, (2, 0, 1))
        input_tensor     = np.expand_dims(image_transposed, axis=0).astype(np.float32)

        input_name  = session.get_inputs()[0].name
        outputs     = session.run(None, {input_name: input_tensor})

        conf_scores     = outputs[0][0, :, 1]
        candidate_boxes = outputs[1][0, :, :]

        idxs         = np.where(conf_scores > 0.7)[0]
        final_boxes  = []
        final_scores = []

        for idx in idxs:
            x1, y1, x2, y2 = candidate_boxes[idx]
            left   = int(x1 * 320)
            top    = int(y1 * 240)
            right  = int(x2 * 320)
            bottom = int(y2 * 240)
            final_boxes.append([left, top, right - left, bottom - top])
            final_scores.append(float(conf_scores[idx]))

        indices = cv2.dnn.NMSBoxes(final_boxes, final_scores, 0.7, 0.3)

        if len(indices) > 0 and gif_total_frames > 0:
            rects = np.array([[final_boxes[i]] for i in indices.flatten()])
            ok, all_landmarks = facemark.fit(frame, rects)

            for idx, i in enumerate(indices.flatten()):
                x, y, w_box, h_box = final_boxes[i]
                gif_frame_counter = (gif_frame_counter + 1) % gif_total_frames
                current_gif_frame = gif_frames[gif_frame_counter]

                face_angle = 0.0
                if ok and idx < len(all_landmarks):
                    pts       = all_landmarks[idx][0]
                    left_eye  = pts[36:42].mean(axis=0)
                    right_eye = pts[42:48].mean(axis=0)
                    face_angle = np.degrees(np.arctan2(
                        right_eye[1] - left_eye[1],
                        right_eye[0] - left_eye[0]
                    ))

                rotated_gif = rotate_frame(current_gif_frame, face_angle)
                frame = overlay_transparent(frame, rotated_gif,
                                            x + GIF_OFFSET[0], y + GIF_OFFSET[1])

                if static_image is not None:
                    rotated_image = rotate_frame(static_image, face_angle)
                    frame = overlay_transparent(frame, rotated_image,
                                               x + IMAGE_OFFSET[0], y + IMAGE_OFFSET[1])

        cv2.imshow("Webcam", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Face detection with optional image overlay")
    parser.add_argument('--image', '-i', type=str, default=None,
                        help="Chemin vers l'image statique à superposer")
    args = parser.parse_args()
    main(image_path=args.image)
