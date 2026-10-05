from ultralytics import YOLO

def main():
    # 1. Load model YOLOv11 versi nano (sangat ringan buat laptop)
    model = YOLO("yolov11n.pt") 

    # 2. Mulai proses training
    results = model.train(
        data="D:/scanplatlambung/data.yaml", # Mengarah ke file data.yaml kamu
        epochs=50,                           # Kita coba 50 putaran dulu
        imgsz=640,                           # Ukuran gambar standar
        batch=8,                             # Kita set ke 8 dulu biar laptop gak ngos-ngosan
        device="cpu"                         # Pakai prosesor laptop
    )

if __name__ == "__main__":
    main()