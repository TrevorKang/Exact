import cv2
import matplotlib.pyplot as plt
import os
from pathlib import Path
import numpy as np

mp4_path = r"Exact/exact/exact/images/test.mp4"

out_dir = "frames_uniform"
os.makedirs(out_dir, exist_ok=True)

cap = cv2.VideoCapture(mp4_path)
if not cap.isOpened():
    raise RuntimeError("Video can't be loaded.")
frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print("Total frames: ", frame_cnt)
indices = np.linspace(0, frame_cnt - 1, 5, dtype=int)

for i, idx in enumerate(indices):
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    if not ret:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    print(str(frame_rgb.dtype))
    plt.imshow(frame_rgb)
    plt.axis("off")
    plt.savefig(os.path.join(out_dir, f"frame_{i:02d}.png"))
    plt.close()

cap.release()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     cv2.imshow("video", frame)
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()