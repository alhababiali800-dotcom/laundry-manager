import os
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QFormLayout, QDialogButtonBox, QFrame,
    QMessageBox, QTableWidgetItem, QDoubleSpinBox, QLineEdit, QCheckBox,
    QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from models.all_models import ItemTypeModel, ActivityModel
from views.base_view import DataTable, make_btn, confirm_delete, page_title, muted_label, dialog_title, h_separator
from utils.i18n import tr


class ItemTypeDialog(QDialog):
    def __init__(self, parent, user, record=None):
        super().__init__(parent)
        self.user = user
        self.record = record
        self.image_path = record.get('image_path') if record else None
        self.temp_image = None
        self.setWindowTitle(tr("edit_item") if record else tr("new_item"))
        self.setMinimumWidth(480)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.lbl_title = dialog_title(tr("edit_item") if self.record else tr("new_item"))
        layout.addWidget(self.lbl_title)
        layout.addWidget(h_separator())

        main_row = QHBoxLayout()

        # Form
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(12)
        self.inp_name = QLineEdit()
        self.inp_name.setMinimumHeight(38)
        self.inp_name.setPlaceholderText("e.g. Shirt, Trousers...")
        self.spin_wash = QDoubleSpinBox()
        self.spin_wash.setRange(0, 9999)
        self.spin_wash.setPrefix('RM ')
        self.spin_wash.setMinimumHeight(38)
        self.spin_iron = QDoubleSpinBox()
        self.spin_iron.setRange(0, 9999)
        self.spin_iron.setPrefix('RM ')
        self.spin_iron.setMinimumHeight(38)
        self.spin_dry = QDoubleSpinBox()
        self.spin_dry.setRange(0, 9999)
        self.spin_dry.setPrefix('RM ')
        self.spin_dry.setMinimumHeight(38)
        self.chk_active = QCheckBox(tr("active"))
        self.chk_active.setChecked(True)

        form.addRow(tr("item_name") + " *", self.inp_name)
        form.addRow(tr("wash_price"), self.spin_wash)
        form.addRow(tr("iron_price"), self.spin_iron)
        form.addRow(tr("dry_clean_price"), self.spin_dry)
        form.addRow("", self.chk_active)
        main_row.addWidget(form_widget, 2)

        # Image section
        img_vbox = QVBoxLayout()
        self.lbl_img_preview = QLabel()
        self.lbl_img_preview.setFixedSize(120, 120)
        self.lbl_img_preview.setStyleSheet("border: 2px dashed #cbd5e1; border-radius: 8px; background: #f8fafc;")
        self.lbl_img_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_preview()

        btn_upload = QPushButton(f"📷 {tr('upload') if 'upload' in tr('upload') else 'Upload'}")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.clicked.connect(self._upload_image)

        img_vbox.addWidget(self.lbl_img_preview)
        img_vbox.addWidget(btn_upload)
        img_vbox.addStretch()
        main_row.addLayout(img_vbox, 1)

        layout.addLayout(main_row)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Save).setObjectName("btn_primary")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("btn_secondary")
        layout.addWidget(btns)

        if self.record:
            self.inp_name.setText(self.record.get('name', ''))
            self.spin_wash.setValue(self.record.get('wash_price', 0) or 0)
            self.spin_iron.setValue(self.record.get('iron_price', 0) or 0)
            self.spin_dry.setValue(self.record.get('dry_clean_price', 0) or 0)
            self.chk_active.setChecked(bool(self.record.get('is_active', 1)))

    def _update_preview(self):
        path = self.temp_image or self.image_path
        if path and os.path.exists(path):
            pix = QPixmap(path)
            self.lbl_img_preview.setPixmap(
                pix.scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.lbl_img_preview.setText("No Image")

    def _upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.temp_image = file_path
            self._update_preview()

    def _save(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, tr("error"), tr("item_name_required"))
            return

        final_img_path = self.image_path
        if self.temp_image:
            try:
                # FIX 1: Use absolute path based on this file's location,
                #         not the current working directory (which can be anywhere).
                base_dir = Path(__file__).resolve().parent.parent
                assets_dir = base_dir / "assets" / "items"
                assets_dir.mkdir(parents=True, exist_ok=True)

                # FIX 2: Use a timestamp for a unique filename instead of
                #         the broken Qt enum expression that caused the crash.
                import time
                ts = int(time.time())
                safe_name = name.replace(' ', '_').lower()
                ext = Path(self.temp_image).suffix.lower() or ".jpg"
                dest_name = f"item_{ts}_{safe_name}{ext}"
                dest_path = assets_dir / dest_name

                shutil.copy2(self.temp_image, dest_path)
                final_img_path = str(dest_path)
            except Exception as e:
                # FIX 3: Show error to user instead of silently printing,
                #         then continue saving without the image rather than crashing.
                QMessageBox.warning(
                    self, tr("error"),
                    f"Could not save image:\n{e}\n\nItem will be saved without image."
                )

        if self.record:
            ItemTypeModel.update(
                self.record['id'], name,
                self.spin_wash.value(), self.spin_iron.value(),
                self.spin_dry.value(), int(self.chk_active.isChecked()),
                final_img_path
            )
            ActivityModel.log(self.user['id'], self.user['username'], 'UPDATE', 'item_type', self.record['id'],
                              f"Updated {name}")
        else:
            iid = ItemTypeModel.create(
                name, self.spin_wash.value(), self.spin_iron.value(),
                self.spin_dry.value(), final_img_path
            )
            ActivityModel.log(self.user['id'], self.user['username'], 'CREATE', 'item_type', iid, f"Created {name}")
        self.accept()


class CatalogView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        h = QHBoxLayout()
        self.lbl_title = page_title(tr("catalog_title"))
        h.addWidget(self.lbl_title)
        h.addStretch()
        self.btn_add = make_btn(f"+ {tr('new_item')}", "btn_primary")
        self.btn_add.clicked.connect(self._add)
        h.addWidget(self.btn_add)
        layout.addLayout(h)

        self.lbl_sub = muted_label(tr("catalog_sub"))
        self.lbl_sub.setWordWrap(True)
        layout.addWidget(self.lbl_sub)

        self.table = DataTable(
            ["", tr("item_name"), tr("col_wash_rm"), tr("col_iron_rm"), tr("col_dry_rm"), tr("col_status"),
             tr("actions")])
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(6, 140)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, self.table.horizontalHeader().ResizeMode.Fixed)
        layout.addWidget(self.table)
        self.refresh()

    def retranslate(self):
        self.lbl_title.setText(tr("catalog_title"))
        self.btn_add.setText(f"+ {tr('new_item')}")
        self.lbl_sub.setText(tr("catalog_sub"))
        self.table.setHorizontalHeaderLabels(
            ["", tr("item_name"), tr("col_wash_rm"), tr("col_iron_rm"), tr("col_dry_rm"), tr("col_status"),
             tr("actions")])
        self.refresh()

    def refresh(self):
        items = ItemTypeModel.get_all(active_only=False)
        self.table.setRowCount(len(items))
        for r, it in enumerate(items):
            # Image icon
            img_lbl = QLabel()
            img_lbl.setFixedSize(40, 40)
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_path = it.get('image_path')
            if img_path and os.path.exists(img_path):
                pix = QPixmap(img_path)
                img_lbl.setPixmap(
                    pix.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                img_lbl.setText("👕")
            self.table.setCellWidget(r, 0, img_lbl)

            self.table.setItem(r, 1, QTableWidgetItem(it.get('name', '')))
            self.table.setItem(r, 2, QTableWidgetItem(f"{it.get('wash_price', 0):.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{it.get('iron_price', 0):.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{it.get('dry_clean_price', 0):.2f}"))
            from views.base_view import colored_item
            status_key = 'active_status' if it.get('is_active') else 'inactive_status'
            self.table.setItem(r, 5, colored_item(tr(status_key), 'active' if it.get('is_active') else 'expired'))

            actions = QWidget()
            al = QHBoxLayout(actions)
            al.setContentsMargins(4, 2, 4, 2)
            al.setSpacing(4)
            be = QPushButton(f"✏ {tr('edit')}")
            be.setObjectName("btn_secondary")
            be.setFixedHeight(28)
            be.setCursor(Qt.CursorShape.PointingHandCursor)
            be.clicked.connect(lambda _, row=it: self._edit(row))
            bd = QPushButton("🗑")
            bd.setObjectName("btn_danger")
            bd.setFixedHeight(28)
            bd.setFixedWidth(32)
            bd.setCursor(Qt.CursorShape.PointingHandCursor)
            bd.clicked.connect(lambda _, iid=it['id'], n=it['name']: self._delete(iid, n))
            al.addWidget(be)
            al.addWidget(bd)
            self.table.setCellWidget(r, 6, actions)
            self.table.setRowHeight(r, 50)

    def _add(self):
        if ItemTypeDialog(self, self.user).exec():
            self.refresh()

    def _edit(self, record):
        if ItemTypeDialog(self, self.user, record).exec():
            self.refresh()

    def _delete(self, iid, name):
        if confirm_delete(self, f'"{name}"'):
            ItemTypeModel.delete(iid)
            ActivityModel.log(self.user['id'], self.user['username'], 'DELETE', 'item_type', iid, f"Deleted {name}")
            self.refresh()
