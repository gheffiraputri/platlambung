import os
import random
import shutil

def split_dataset(split_ratio=0.15):
    base_dir = "D:/scanplatlambung/dataset"
    train_img_dir = os.path.join(base_dir, "train/images")
    train_lbl_dir = os.path.join(base_dir, "train/labels")
    
    val_img_dir = os.path.join(base_dir, "val/images")
    val_lbl_dir = os.path.join(base_dir, "val/labels")

    # Buat foldernya kalau belum ada
    os.makedirs(val_img_dir, exist_ok=True)
    os.makedirs(val_lbl_dir, exist_ok=True)

    # Ambil semua daftar file gambar di folder train
    images = [f for f in os.listdir(train_img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Hitung berapa banyak file yang mau dipindahkan ke val
    num_val = int(len(images) * split_ratio)
    print(f"Total semua data train: {len(images)} gambar.")
    print(f"Mengambil {num_val} data secara acak untuk dipindahkan ke folder val...")

    # Acak urutan gambar
    val_images = random.sample(images, num_val)

    # Proses pemindahan file
    moved_count = 0
    for img_name in val_images:
        name_without_ext = os.path.splitext(img_name)[0]
        lbl_name = name_without_ext + ".txt"

        src_img = os.path.join(train_img_dir, img_name)
        src_lbl = os.path.join(train_lbl_dir, lbl_name)
        
        dst_img = os.path.join(val_img_dir, img_name)
        dst_lbl = os.path.join(val_lbl_dir, lbl_name)

        # Pastikan pasangan teks .txt nya ada baru kita pindahkan
        if os.path.exists(src_lbl):
            shutil.move(src_img, dst_img)
            shutil.move(src_lbl, dst_lbl)
            moved_count += 1
        else:
            print(f"Peringatan: Label untuk {img_name} tidak ditemukan, skip.")

    print(f"Selesai! Berhasil memindahkan {moved_count} pasang data ke folder val.")

if __name__ == "__main__":
    split_dataset()