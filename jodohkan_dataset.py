import os
import shutil

# Sesuaikan dengan lokasi folder di laptopmu
root_dir = "D:/SCANPLATLAMBUNG"  # Ubah jika path project kamu berbeda
dir_labels = os.path.join(root_dir, "dataset", "train", "labels")
dir_mentah = os.path.join(root_dir, "images_mentah")
dir_target_images = os.path.join(root_dir, "dataset", "train", "images")

os.makedirs(dir_target_images, exist_ok=True)

# Ambil semua file teks koordinat dari Label Studio
all_txt_files = [f for f in os.listdir(dir_labels) if f.endswith('.txt')]
all_raw_images = os.listdir(dir_mentah)

terjodohkan = 0

for txt_file in all_txt_files:
    # Mengambil nama asli file sebelum tanda "-" dari Label Studio
    # Contoh: "0a2df214-20260425_150843_HT544.txt" diambil bagian "20260425_150843_HT544"
    if "-" in txt_file:
        nama_asli_tanpa_id = txt_file.split("-", 1)[1].rsplit(".", 1)[0]
    else:
        nama_asli_tanpa_id = txt_file.rsplit(".", 1)[0]
    
    # Cari gambar mentah yang cocok
    for img_file in all_raw_images:
        nama_img_tanpa_ext = os.path.splitext(img_file)[0]
        
        # Jika nama file mentah cocok dengan nama di file teks Label Studio
        if nama_img_tanpa_ext == nama_asli_tanpa_id:
            ext_img = os.path.splitext(img_file)[1]
            nama_img_baru = os.path.splitext(txt_file)[0] + ext_img
            
            src_path = os.path.join(dir_mentah, img_file)
            dst_path = os.path.join(dir_target_images, nama_img_baru)
            
            # Salin file dan ubah namanya secara otomatis
            shutil.copy(src_path, dst_path)
            terjodohkan += 1
            break

print(f"Beres, Fir! Berhasil menjodohkan {terjodohkan} foto ke folder dataset/train/images")