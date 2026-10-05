"""
ANPR Inference - deteksi & baca plat nomor truk tambang.
Versi upgrade: preprocessing adaptif, OCR config lebih baik,
confidence filter, format validation, error handling.

Dibungkus jadi fungsi read_plate() biar gampang dipanggil dari FastAPI.
"""

from ultralytics import YOLO
import easyocr
import cv2
import re
import os

# ============================================================
# SETUP (load sekali aja, jangan di dalam loop -> berat)
# ============================================================
model = YOLO("best.pt")
reader = easyocr.Reader(["en"], gpu=True)  # 'id' nggak ngaruh buat plat (cuma A-Z 0-9)

# Karakter yang valid di plat. Lebih efektif dari blocklist.
# Sesuaikan kalau format plat tambangmu beda.
ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Format plat yang diharapkan, contoh: HT544 = 2 huruf + 3 angka.
# Ubah regex ini sesuai format asli platmu.
PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{3}$")


# ============================================================
# PREPROCESSING ADAPTIF
# ============================================================
def preprocess(crop):
    """Bikin crop plat lebih kebaca OCR. Adaptif, nggak maksa 3x."""
    h, w = crop.shape[:2]

    # 1. Resize adaptif: cuma perbesar kalau platnya kekecilan.
    #    Target lebar ~320px. Upscale gede-gedean malah bikin blur.
    if w < 320:
        scale = min(320 / w, 3.0)
        crop = cv2.resize(crop, None, fx=scale, fy=scale,
                          interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # 3. Denoise dulu (penting buat debu tambang) sebelum naikin kontras
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # 4. CLAHE moderate -> ratain pencahayaan tanpa over-contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return enhanced


# ============================================================
# POST-PROCESSING
# ============================================================
def clean_and_join(ocr_result, conf_threshold=0.3):
    """Filter confidence rendah, gabung fragmen jadi satu string plat."""
    parts = []
    confs = []
    for (_, text, conf) in ocr_result:
        if conf >= conf_threshold:
            cleaned = re.sub(r"[^A-Z0-9]", "", text.upper())
            if cleaned:
                parts.append(cleaned)
                confs.append(conf)

    plate = "".join(parts)
    avg_conf = sum(confs) / len(confs) if confs else 0.0
    return plate, avg_conf


# ============================================================
# FUNGSI UTAMA
# ============================================================
def read_plate(image_path, det_conf=0.25, save_debug=False):
    """
    Return list of dict: [{plate, confidence, valid, box}, ...]
    Bisa lebih dari satu kalau ada >1 truk di frame.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Gambar nggak ketemu: {image_path}")

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Gagal baca gambar (format rusak?): {image_path}")

    results = model.predict(source=img, conf=det_conf, verbose=False)
    boxes = results[0].boxes

    if len(boxes) == 0:
        return []  # plat nggak kedeteksi

    detections = []
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        crop = img[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        enhanced = preprocess(crop)

        if save_debug:
            cv2.imwrite(f"debug_crop_{i}.jpg", enhanced)

        ocr_result = reader.readtext(
            enhanced,
            decoder="beamsearch",   # lebih akurat dari greedy
            beamWidth=15,           # search space lebih lebar
            allowlist=ALLOWLIST,    # paksa cuma A-Z 0-9
        )

        plate, conf = clean_and_join(ocr_result)
        detections.append({
            "plate": plate,
            "confidence": round(conf, 3),
            "valid": bool(PLATE_PATTERN.match(plate)),
            "box": [x1, y1, x2, y2],
        })

    return detections


# ============================================================
# CONTOH PEMAKAIAN
# ============================================================
if __name__ == "__main__":
    image_path = "0a2df214-20260425_150843_HT544.PNG"

    try:
        plates = read_plate(image_path, save_debug=True)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        plates = []

    if not plates:
        print("Plat nggak terdeteksi. Cek model deteksi / threshold.")
    else:
        for p in plates:
            status = "VALID" if p["valid"] else "CEK MANUAL"
            print("=" * 40)
            print(f"Plat       : {p['plate']}")
            print(f"Confidence : {p['confidence']}")
            print(f"Status     : {status}")
            print("=" * 40)