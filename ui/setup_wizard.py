import json
import os

import psutil
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
)


class SetupWizard(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ML Agents - Setup Wizard")
        self.setFixedSize(500, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #4daafc;
            }
            QRadioButton {
                color: #d4d4d4;
                font-size: 13px;
                padding: 5px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)

        # Get system RAM
        ram_bytes = psutil.virtual_memory().total
        self.ram_gb = round(ram_bytes / (1024**3), 2)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Header
        header = QLabel(
            f"<b>Welcome to ML Agents Universe</b><br>Detected System RAM: {self.ram_gb} GB"
        )
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(header)

        # 0. Installation / Workspace Directory
        install_group = QGroupBox("0. Installation / Workspace Directory")
        install_layout = QHBoxLayout()
        self.install_dir_input = QLineEdit()
        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ML_Agents_Universe")
        self.install_dir_input.setText(default_dir)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_directory)
        install_layout.addWidget(self.install_dir_input)
        install_layout.addWidget(self.browse_btn)
        install_group.setLayout(install_layout)
        self.main_layout.addWidget(install_group)

        # 1. Compute Unit
        compute_group = QGroupBox("1. Compute Unit (Local Execution)")
        compute_layout = QVBoxLayout()
        self.compute_btn_group = QButtonGroup(self)

        self.radio_cpu = QRadioButton("CPU Only")
        self.radio_cpu.setChecked(True)
        self.radio_gpu = QRadioButton("GPU Only")
        self.radio_both = QRadioButton("Both (CPU + GPU)")

        self.compute_btn_group.addButton(self.radio_cpu, 1)
        self.compute_btn_group.addButton(self.radio_gpu, 2)
        self.compute_btn_group.addButton(self.radio_both, 3)

        compute_layout.addWidget(self.radio_cpu)
        compute_layout.addWidget(self.radio_gpu)
        compute_layout.addWidget(self.radio_both)
        compute_group.setLayout(compute_layout)
        self.main_layout.addWidget(compute_group)

        # 2. Database/Memory Backend
        db_group = QGroupBox("2. State Checkpointer (Database Backend)")
        db_layout = QVBoxLayout()
        self.db_btn_group = QButtonGroup(self)

        self.radio_upstash = QRadioButton("Redis Cloud (Upstash)")
        self.radio_redis_cloud = QRadioButton("Redis Cloud (cloud.redis.io)")
        self.radio_redis_docker = QRadioButton("Redis Docker (Local)")

        fallback_text = "Memory (RAM)" if self.ram_gb > 6 else "SQLite"
        self.radio_auto = QRadioButton(f"Auto Fallback ({fallback_text})")
        self.radio_auto.setChecked(True)

        self.db_btn_group.addButton(self.radio_upstash, 1)
        self.db_btn_group.addButton(self.radio_redis_cloud, 2)
        self.db_btn_group.addButton(self.radio_redis_docker, 3)
        self.db_btn_group.addButton(self.radio_auto, 4)

        self.radio_upstash.toggled.connect(self.toggle_redis_input)
        self.radio_redis_cloud.toggled.connect(self.toggle_redis_input)
        self.radio_redis_docker.toggled.connect(self.toggle_redis_input)
        self.radio_auto.toggled.connect(self.toggle_redis_input)

        db_layout.addWidget(self.radio_upstash)
        db_layout.addWidget(self.radio_redis_cloud)
        db_layout.addWidget(self.radio_redis_docker)
        db_layout.addWidget(self.radio_auto)

        # Redis URL Input
        self.redis_url_input = QLineEdit()
        self.redis_url_input.setPlaceholderText(
            "Enter Redis URL (e.g., redis://user:pass@host:port)"
        )
        self.redis_url_input.setVisible(False)
        db_layout.addWidget(self.redis_url_input)

        db_group.setLayout(db_layout)
        self.main_layout.addWidget(db_group)

        # Submit Button
        self.submit_btn = QPushButton("Save & Launch")
        self.submit_btn.clicked.connect(self.save_config)
        self.main_layout.addWidget(self.submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def toggle_redis_input(self):
        # Jika bukan Auto, maka show redis input
        is_redis = not self.radio_auto.isChecked()
        self.redis_url_input.setVisible(is_redis)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Installation Directory", self.install_dir_input.text()
        )
        if directory:
            self.install_dir_input.setText(directory)

    def save_config(self):
        # Determine compute
        compute = "CPU"
        if self.radio_gpu.isChecked():
            compute = "GPU"
        elif self.radio_both.isChecked():
            compute = "BOTH"

        # Determine db backend
        db_type = "AUTO"
        if self.radio_upstash.isChecked():
            db_type = "REDIS_UPSTASH"
        elif self.radio_redis_cloud.isChecked():
            db_type = "REDIS_CLOUD"
        elif self.radio_redis_docker.isChecked():
            db_type = "REDIS_DOCKER"

        redis_url = self.redis_url_input.text().strip()
        if db_type != "AUTO" and not redis_url:
            QMessageBox.warning(self, "Warning", "Please enter a valid Redis URL!")
            return

        install_dir = self.install_dir_input.text().strip()
        if not install_dir:
            QMessageBox.warning(self, "Warning", "Please select an installation directory!")
            return

        config = {
            "install_dir": install_dir,
            "system_ram_gb": self.ram_gb,
            "compute_unit": compute,
            "database_type": db_type,
            "redis_url": redis_url if db_type != "AUTO" else None,
        }

        # Save to data/desktop_config.json
        data_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        )
        os.makedirs(data_dir, exist_ok=True)
        config_path = os.path.join(data_dir, "desktop_config.json")

        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        self.accept()
