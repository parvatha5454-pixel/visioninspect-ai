from pathlib import Path
import cv2

out_root = Path("deploy_images/dataset_images")
count = 0
missing = 0
for line in open("seeded_paths.txt"):
    p = line.strip()
    if not p.startswith("dataset_images/"):
        continue
    src = Path(p)
    img = cv2.imread(str(src)) if src.exists() else None
    if img is None:
        missing += 1
        continue
    h, w = img.shape[:2]
    s = 256 / max(h, w)
    if s < 1:
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    dst = out_root / Path(p).relative_to("dataset_images")
    dst.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dst), img)
    count += 1
print("thumbnails:", count, "| missing:", missing)