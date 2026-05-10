import sys
import cv2
import numpy as np
import os
import datetime
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, 
                             QCheckBox, QRadioButton, QButtonGroup, QGridLayout, QFrame)
from PyQt6.QtCore import Qt

class ColorHunter(QWidget):
    def __init__(self):
        super().__init__()
        self.input_path = ""
        self.COLOR_RANGES = {
            "red": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (180, 255, 255))],
            "orange": [((11, 120, 70), (24, 255, 255))], "yellow": [((25, 120, 70), (35, 255, 255))],
            "lime": [((36, 120, 120), (50, 255, 255))], "green": [((51, 60, 60), (85, 255, 255))],
            "turquoise": [((86, 60, 60), (95, 255, 255))], "cyan": [((96, 60, 60), (100, 255, 255))],
            "sky_blue": [((101, 80, 80), (110, 255, 255))], "blue": [((111, 80, 60), (130, 255, 255))],
            "navy": [((131, 80, 40), (140, 255, 180))], "purple": [((125, 60, 40), (155, 255, 255))],
            "magenta": [((156, 80, 80), (165, 255, 255))], "pink": [((166, 50, 70), (169, 255, 255))],
            "brown": [((8, 80, 20), (25, 255, 200))], "beige": [((15, 20, 150), (35, 80, 255))],
            "white": [((0, 0, 200), (180, 40, 255))], "light_gray": [((0, 0, 120), (180, 30, 199))],
            "gray": [((0, 0, 60), (180, 40, 119))], "dark_gray": [((0, 0, 30), (180, 50, 59))],
            "black": [((0, 0, 0), (180, 255, 29))],
        }
        self.initUI()
        self.load_settings_from_file()

    def initUI(self):
        self.setWindowTitle('Color Hunter')
        self.setFixedWidth(550)
        main_layout = QVBoxLayout()
        
        top_btns_layout = QHBoxLayout()
        btn_save_settings = QPushButton("Зберегти налаштування")
        btn_save_settings.clicked.connect(self.save_settings_to_file)
        btn_reset_settings = QPushButton("Скинути налаштування")
        btn_reset_settings.clicked.connect(self.reset_settings)
        top_btns_layout.addWidget(btn_save_settings)
        top_btns_layout.addStretch()
        top_btns_layout.addWidget(btn_reset_settings)
        main_layout.addLayout(top_btns_layout)

        self.radio_single = QRadioButton("Обробка 1 фото")
        self.radio_folder = QRadioButton("Обробка теку фото")
        self.radio_single.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_single)
        self.mode_group.addButton(self.radio_folder)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.radio_single)
        mode_layout.addWidget(self.radio_folder)
        main_layout.addLayout(mode_layout)

        path_layout = QHBoxLayout()
        self.btn_select_path = QPushButton("Обрати файл/теку")
        self.btn_select_path.clicked.connect(self.select_path)
        self.lbl_path = QLabel("Шлях не обрано")
        path_layout.addWidget(self.btn_select_path)
        path_layout.addWidget(self.lbl_path)
        main_layout.addLayout(path_layout)

        main_layout.addWidget(QLabel("<b>Оберіть кольори:</b>"))
        self.preset_frame = QFrame()
        grid = QGridLayout(self.preset_frame)
        self.color_checkboxes = {}
        for i, name in enumerate(self.COLOR_RANGES.keys()):
            cb = QCheckBox(name)
            self.color_checkboxes[name] = cb
            grid.addWidget(cb, i // 5, i % 5)
        main_layout.addWidget(self.preset_frame)

        self.cb_show_results = QCheckBox("Показати вікна з координатами та контурами знайдених об'єктів")
        self.cb_show_masks = QCheckBox("Показати вікна з масками знайдених об'єктів")
        self.cb_save_img = QCheckBox("Зберігати зображення")
        self.cb_save_img.setChecked(True)
        
        main_layout.addWidget(self.cb_show_results)
        main_layout.addWidget(self.cb_show_masks)
        main_layout.addWidget(self.cb_save_img)
        
        self.btn_run = QPushButton("Запустити")
        self.btn_run.setFixedHeight(40)
        self.btn_run.clicked.connect(self.run_process)
        main_layout.addWidget(self.btn_run)
        
        self.setLayout(main_layout)

    def reset_settings(self):
        self.radio_single.setChecked(True)
        for cb in self.color_checkboxes.values():
            cb.setChecked(False)
        self.cb_show_results.setChecked(False)
        self.cb_show_masks.setChecked(False)
        self.cb_save_img.setChecked(True)
        self.input_path = ""
        self.lbl_path.setText("Шлях не обрано")
        self.save_settings_to_file(silent=True)
        QMessageBox.information(self, "Color Hunter", "Налаштування скинуто")

    def select_path(self):
        if self.radio_folder.isChecked():
            p = QFileDialog.getExistingDirectory(self)
        else:
            p = QFileDialog.getOpenFileName(self)[0]
        if p:
            self.input_path = p
            self.lbl_path.setText(os.path.basename(p))

    def save_settings_to_file(self, silent=False):
        s = {
            "mode": "single" if self.radio_single.isChecked() else "folder",
            "selected_preset": [n for n, cb in self.color_checkboxes.items() if cb.isChecked()],
            "show_results": self.cb_show_results.isChecked(),
            "show_masks": self.cb_show_masks.isChecked(),
            "save_img": self.cb_save_img.isChecked()
        }
        try:
            with open(sys.argv[0], "r", encoding="utf-8") as f: lines = f.readlines()
            with open(sys.argv[0], "w", encoding="utf-8") as f:
                found = False
                for l in lines:
                    if l.strip().startswith("# settings ="):
                        f.write(f"# settings = {json.dumps(s)}\n")
                        found = True
                    else: f.write(l)
                if not found: f.write(f"\n# settings = {json.dumps(s)}\n")
            if not silent: QMessageBox.information(self, "Color Hunter", "Налаштування збережено")
        except: pass

    def load_settings_from_file(self):
        try:
            with open(sys.argv[0], "r", encoding="utf-8") as f:
                for l in f:
                    if l.strip().startswith("# settings ="):
                        d = json.loads(l.strip().replace("# settings =", ""))
                        self.radio_single.setChecked(d.get("mode") == "single")
                        self.radio_folder.setChecked(d.get("mode") == "folder")
                        for n, cb in self.color_checkboxes.items():
                            cb.setChecked(n in d.get("selected_preset", []))
                        self.cb_show_results.setChecked(d.get("show_results", False))
                        self.cb_show_masks.setChecked(d.get("show_masks", False))
                        self.cb_save_img.setChecked(d.get("save_img", True))
                        return
        except: pass

    def run_process(self):
        if not self.input_path: return
        
        is_folder = self.radio_folder.isChecked()
        if is_folder:
            files = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) 
                     if f.lower().endswith(('.png','.jpg','.jpeg'))]
            if self.cb_save_img.isChecked():
                if not os.path.exists("output"): os.makedirs("output")
        else:
            files = [self.input_path]

        total_session_objects = 0
        
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"\n=== {datetime.datetime.now()} ===\n")
            
            for idx, f_path in enumerate(files, 1):
                image = cv2.imread(f_path)
                if image is None: continue
                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                valid_colors = [n for n, cb in self.color_checkboxes.items() if cb.isChecked()]
                if not valid_colors: continue
                
                full_mask = np.zeros(hsv.shape[:2], np.uint8)
                file_objects_count = 0
                
                log.write(f"File: {f_path}\n")
                print(f"File: {f_path}")
                
                for current_color in valid_colors:
                    color_mask = np.zeros(hsv.shape[:2], np.uint8)
                    for lower, upper in self.COLOR_RANGES[current_color]:
                        color_mask = cv2.bitwise_or(color_mask, cv2.inRange(hsv, np.array(lower), np.array(upper)))
                    
                    kernel = np.ones((5, 5), np.uint8)
                    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
                    color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
                    full_mask = cv2.bitwise_or(full_mask, color_mask)
                    
                    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for contour in contours:
                        if cv2.contourArea(contour) > 300:
                            file_objects_count += 1
                            total_session_objects += 1
                            M = cv2.moments(contour)
                            if M["m00"] == 0: continue
                            cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                            x, y, w, h = cv2.boundingRect(contour)
                            
                            log_entry = f"Object {file_objects_count} X: {cx} Y: {cy}"
                            log.write(log_entry + "\n")
                            print(log_entry)
                            
                            cv2.drawContours(image, [contour], -1, (0, 0, 0), 2)
                            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2)
                            cv2.circle(image, (cx, cy), 5, (0, 0, 0), -1)
                            
                            text = f'x={cx}, y={cy}'
                            (tw, th), bl = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                            tx, ty = x, y - 10
                            if ty - th < 0: ty = y + h + th + 10
                            if tx + tw > image.shape[1]: tx = image.shape[1] - tw - 5
                            cv2.rectangle(image, (tx - 2, ty - th - 2), (tx + tw + 2, ty + bl), (255, 255, 255), -1)
                            cv2.putText(image, text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                if self.cb_save_img.isChecked():
                    if is_folder:
                        cv2.imwrite(os.path.join("output", f"output_{idx}.jpg"), image)
                    else:
                        cv2.imwrite("output.jpg", image)
                
                if self.cb_show_results.isChecked():
                    cv2.imshow(f"Result - {os.path.basename(f_path)}", image)
                if self.cb_show_masks.isChecked():
                    cv2.imshow(f"Mask - {os.path.basename(f_path)}", full_mask)
                
                if self.cb_show_results.isChecked() or self.cb_show_masks.isChecked():
                    cv2.waitKey(500)

            print(f"Detected objects: {total_session_objects}")
            msg = f"Обробка виконана, результати збережено в log.txt"
            if self.cb_save_img.isChecked():
                msg += f" та {'теці output' if is_folder else 'output.jpg'}"
            
            QMessageBox.information(self, "Завершено", f"{msg}\nДетектовано об'єктів: {total_session_objects}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ColorHunter()
    ex.show()
    sys.exit(app.exec())
