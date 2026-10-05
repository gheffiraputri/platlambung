import os

root_dir = "D:/SCANPLATLAMBUNG"  # Sesuaikan dengan path project kamu
dir_images = os.path.join(root_dir, "dataset", "train", "images")
dir_labels = os.path.join(root_dir, "dataset", "train", "labels")

# 1. Ambil nama file tanpa ekstensi (.jpg/.png/.txt)
set_images = {os.path.splitext(f)[0] for f in os.listdir(dir_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))}
set_labels = {os.path.splitext(f)[0] for f in os.listdir(dir_labels) if f.endswith('.txt') and f != 'classes.txt'}

# 2. Cari mana file teks yang GAK PUNYA gambar pasangannya
labels_tanpa_gambar = set_labels - set_images
for label_name in labels_tanpa_gambar:
    file_target = os.path.join(dir_labels, label_name + ".txt")
    if os.path.exists(file_target):
        os.remove(file_target)

# 3. Cari mana gambar yang GAK PUNYA file teks pasangannya
gambar_tanpa_label = set_images - set_labels
for img_name in os.listdir(dir_images):
    name_without_ext = os.path.splitext(img_name)[0]
    if name_without_ext in gambar_tanpa_label:
        file_target = os.path.join(dir_images, img_name)
        if os.path.exists(file_target):
            os.remove(file_target)

# 4. Hitung ulang hasil akhir yang sudah bersih
total_img = len(os.listdir(dir_images))
total_lbl = len([f for f in os.listdir(dir_labels) if f.endswith('.txt') and f != 'classes.txt'])

print(f"Selesai! Sekarang data kamu balance 100%, Fir.")
print(f"Total Gambar di folder images: {total_img}")
print(f"Total File Teks di folder labels: {total_lbl}")