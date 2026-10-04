"""
=============================================================
 SISTEMA DE FACTURACIÓN - PULPERÍA L&M
 Examen Sección 21 - CRUD completo con PySide6
 Base de datos: archivo "db" (SQLite) en la carpeta del programa
 Acceso: login con usuario y contraseña
=============================================================
"""
import sys
import os
import sqlite3
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QDoubleSpinBox, QSpinBox,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QMessageBox,
    QGroupBox, QHeaderView, QAbstractItemView, QComboBox, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QColor

# -------------------------------------------------------------
# RUTAS: todo relativo a la carpeta del programa
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db")                 # <-- LA BASE DE DATOS VA EN "db"
LOGO_PATH = os.path.join(BASE_DIR, "logo_lm.png")      # logo de la pulpería

# Usuarios del sistema (usuario, contraseña, nombre completo)
USUARIOS = {
    "admin": ("lm2026", "Propietario Pulpería L&M"),
    "vendedor": ("1234", "Vendedor L&M"),
}

# -------------------------------------------------------------
# BASE DE DATOS (SQLite en archivo "db")
# -------------------------------------------------------------
def conectar():
    return sqlite3.connect(DB_PATH)

def crear_db():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            cliente TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )
    """)
    cur.execute("SELECT COUNT(*) FROM productos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
            [
                ("Coca Cola 600ml", 18.00, 24),
                ("Pan de barra", 25.00, 15),
                ("Huevos (unidad)", 4.50, 120),
                ("Arroz 1lb", 14.00, 30),
                ("Frijoles 1lb", 16.00, 25),
                ("Aceite 500ml", 42.00, 10),
                ("Azúcar 1lb", 13.00, 20),
                ("Galleta paquete", 8.00, 40),
            ]
        )
    con.commit()
    con.close()

# -------------------------------------------------------------
# VENTANA DE LOGIN (usuario y contraseña)
# -------------------------------------------------------------
class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de sesión - Pulpería L&M")
        self.setFixedSize(420, 480)
        self.usuario_ok = None
        self.setStyleSheet("background-color: white; color: black;")   # FONDO BLANCO + LETRAS NEGRAS

        lay = QVBoxLayout(self)

        # Logo
        logo = QLabel()
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH).scaled(
                340,
                140,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo)

        titulo = QLabel("Iniciar sesión")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #1b5e20;")
        lay.addWidget(titulo)

        form = QFormLayout()
        self.txt_user = QLineEdit()
        self.txt_user.setPlaceholderText("Usuario")
        self.txt_pass = QLineEdit()
        self.txt_pass.setPlaceholderText("Contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass.returnPressed.connect(self.intentar_login)
        form.addRow("👤 Usuario:", self.txt_user)
        form.addRow("🔑 Contraseña:", self.txt_pass)
        lay.addLayout(form)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #c62828;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lbl_error)

        self.btn_login = QPushButton("INGRESAR")
        self.btn_login.setStyleSheet("background:#2e7d32;color:white;font-weight:bold;padding:12px;font-size:14px;")
        self.btn_login.clicked.connect(self.intentar_login)
        lay.addWidget(self.btn_login)

        info = QLabel("Usuarios de prueba:<br>👤 admin / 🔑 lm2026<br>👤 vendedor / 🔑 1234")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #666; font-size: 11px;")
        lay.addWidget(info)

    def intentar_login(self):
        u = self.txt_user.text().strip()
        p = self.txt_pass.text().strip()
        if u in USUARIOS and USUARIOS[u][0] == p:
            self.usuario_ok = (u, USUARIOS[u][1])
            self.accept()
        else:
            self.lbl_error.setText("❌ Usuario o contraseña incorrectos")
            self.txt_pass.clear()

# -------------------------------------------------------------
# VENTANA PRINCIPAL
# -------------------------------------------------------------
class VentanaPrincipal(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Pulpería L&M - Sistema de Facturación  |  👤 {usuario[1]}")
        self.resize(1050, 680)
        self.setStyleSheet("background-color: white; color: black;")   # FONDO BLANCO + LETRAS NEGRAS

        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 10))
        tabs.addTab(self.tab_facturacion(), "🧾 Facturación")
        tabs.addTab(self.tab_productos(), "📦 Productos (CRUD)")
        tabs.addTab(self.tab_historial(), "📊 Historial de Ventas")
        self.setCentralWidget(tabs)

    # =========================================================
    # PESTAÑA 1: FACTURACIÓN (punto de venta)
    # =========================================================
    def tab_facturacion(self):
        w = QWidget()
        w.setStyleSheet("background-color: white;")
        lay = QHBoxLayout(w)

        # ---- Columna izquierda: logo + datos del cliente ----
        izq = QVBoxLayout()
        logo = QLabel()
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH).scaled(
                320,
                130,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("border: 2px solid #1b5e20; border-radius: 8px; padding: 4px; background: white;")
        izq.addWidget(logo)

        bienvenida = QLabel(f"👤 Sesión: <b>{self.usuario[1]}</b>")
        bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        izq.addWidget(bienvenida)

        grp_cli = QGroupBox("Datos de la venta")
        grp_cli.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #bbb; border-radius: 6px; margin-top: 8px; padding-top: 20px; background: white; }")
        form = QFormLayout(grp_cli)
        self.txt_cliente = QLineEdit("Cliente general")
        self.combo_prod = QComboBox()
        self.combo_prod.currentIndexChanged.connect(self.mostrar_precio)
        self.txt_precio = QLineEdit()
        self.txt_precio.setReadOnly(True)
        self.spin_cant = QSpinBox()
        self.spin_cant.setMinimum(1)
        self.spin_cant.setMaximum(9999)
        form.addRow("Cliente:", self.txt_cliente)
        form.addRow("Producto:", self.combo_prod)
        form.addRow("Precio (L):", self.txt_precio)
        form.addRow("Cantidad:", self.spin_cant)
        izq.addWidget(grp_cli)

        self.btn_agregar = QPushButton("➕ Agregar al carrito")
        self.btn_agregar.setStyleSheet("background:#1565c0;color:white;font-weight:bold;padding:10px;")
        self.btn_agregar.clicked.connect(self.agregar_carrito)
        izq.addWidget(self.btn_agregar)

        self.btn_finalizar = QPushButton("✅ FINALIZAR VENTA / FACTURAR")
        self.btn_finalizar.setStyleSheet("background:#2e7d32;color:white;font-weight:bold;padding:12px;font-size:13px;")
        self.btn_finalizar.clicked.connect(self.finalizar_venta)
        izq.addWidget(self.btn_finalizar)

        self.btn_limpiar = QPushButton("🗑️ Vaciar carrito")
        self.btn_limpiar.clicked.connect(self.vaciar_carrito)
        izq.addWidget(self.btn_limpiar)
        izq.addStretch()
        lay.addLayout(izq, 1)

        # ---- Columna derecha: carrito ----
        der = QVBoxLayout()
        der.addWidget(QLabel("<h3>Carrito de compra</h3>"))
        self.tabla_carrito = QTableWidget(0, 5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Precio", "Cant.", "Subtotal", "Quitar"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_carrito.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_carrito.setAlternatingRowColors(True)
        self.tabla_carrito.setStyleSheet("background-color: white; alternate-background-color: #f5f5f5;")
        der.addWidget(self.tabla_carrito)

        self.lbl_total = QLabel("TOTAL: L 0.00")
        self.lbl_total.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color:#2e7d32;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        der.addWidget(self.lbl_total)
        lay.addLayout(der, 2)

        self.carrito = []
        self.cargar_productos_combo()
        return w

    def cargar_productos_combo(self):
        self.combo_prod.clear()
        con = conectar(); cur = con.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos WHERE stock > 0")
        for pid, nom, pre, st in cur.fetchall():
            self.combo_prod.addItem(f"{nom} (stock: {st})", (pid, nom, pre, st))
        con.close()
        self.mostrar_precio()

    def mostrar_precio(self):
        data = self.combo_prod.currentData()
        self.txt_precio.setText(f"{data[2]:.2f}" if data else "")

    def agregar_carrito(self):
        data = self.combo_prod.currentData()
        if not data:
            QMessageBox.warning(self, "Atención", "No hay productos con stock.")
            return
        pid, nom, pre, st = data
        cant = self.spin_cant.value()
        if cant > st:
            QMessageBox.warning(self, "Stock insuficiente", f"Solo hay {st} unidades de {nom}.")
            return
        self.carrito.append([pid, nom, pre, cant])
        self.refrescar_carrito()

    def refrescar_carrito(self):
        self.tabla_carrito.setRowCount(0)
        total = 0
        for i, (pid, nom, pre, cant) in enumerate(self.carrito):
            sub = pre * cant
            total += sub
            self.tabla_carrito.insertRow(i)
            for j, val in enumerate([nom, f"{pre:.2f}", str(cant), f"{sub:.2f}"]):
                self.tabla_carrito.setItem(i, j, QTableWidgetItem(val))
            btn = QPushButton("❌")
            btn.clicked.connect(lambda _, r=i: self.quitar_del_carrito(r))
            self.tabla_carrito.setCellWidget(i, 4, btn)
        self.lbl_total.setText(f"TOTAL: L {total:.2f}")

    def quitar_del_carrito(self, fila):
        del self.carrito[fila]
        self.refrescar_carrito()

    def vaciar_carrito(self):
        self.carrito = []
        self.refrescar_carrito()

    def finalizar_venta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Carrito vacío", "Agregue productos primero.")
            return
        cliente = self.txt_cliente.text().strip() or "Cliente general"
        total = sum(p * c for _, _, p, c in self.carrito)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con = conectar(); cur = con.cursor()
        cur.execute("INSERT INTO ventas (fecha, cliente, total) VALUES (?, ?, ?)",
                    (fecha, cliente, total))
        venta_id = cur.lastrowid
        for pid, nom, pre, cant in self.carrito:
            cur.execute("INSERT INTO detalle_venta (venta_id, producto, cantidad, precio, subtotal) VALUES (?,?,?,?,?)",
                        (venta_id, nom, cant, pre, pre * cant))
            cur.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (cant, pid))
        con.commit(); con.close()

        detalle = "\n".join(f"  {nom} x{cant}  =  L {pre*cant:.2f}" for _, nom, pre, cant in self.carrito)
        QMessageBox.information(self, "Factura - Pulpería L&M",
            f"🧾 FACTURA #{venta_id}\nFecha: {fecha}\nCliente: {cliente}\nAtendió: {self.usuario[1]}\n\n{detalle}\n\nTOTAL: L {total:.2f}\n\n¡Gracias por su compra!")
        self.vaciar_carrito()
        self.cargar_productos_combo()
        self.txt_cliente.setText("Cliente general")

    # =========================================================
    # PESTAÑA 2: PRODUCTOS (CRUD COMPLETO)
    # =========================================================
    def tab_productos(self):
        w = QWidget()
        w.setStyleSheet("background-color: white;")
        lay = QVBoxLayout(w)

        grp = QGroupBox("Gestión de productos — CRUD")
        grp.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #bbb; border-radius: 6px; margin-top: 8px; padding-top: 20px; background: white; }")
        form = QFormLayout(grp)
        self.txt_id = QLineEdit(); self.txt_id.setReadOnly(True); self.txt_id.setPlaceholderText("se llena solo al seleccionar")
        self.txt_nombre = QLineEdit(); self.txt_nombre.setPlaceholderText("Ej: Coca Cola 600ml")
        self.spin_precio = QDoubleSpinBox(); self.spin_precio.setMaximum(999999); self.spin_precio.setPrefix("L ")
        self.spin_stock = QSpinBox(); self.spin_stock.setMaximum(999999)
        form.addRow("ID:", self.txt_id)
        form.addRow("Nombre:", self.txt_nombre)
        form.addRow("Precio:", self.spin_precio)
        form.addRow("Stock:", self.spin_stock)
        lay.addWidget(grp)

        btns = QHBoxLayout()
        self.btn_crear = QPushButton("➕ Crear (C)")
        self.btn_actualizar = QPushButton("✏️ Actualizar (U)")
        self.btn_eliminar = QPushButton("🗑️ Eliminar (D)")
        self.btn_limpiar_campos = QPushButton("🧹 Limpiar campos")
        self.btn_crear.setStyleSheet("background:#2e7d32;color:white;padding:8px;font-weight:bold;")
        self.btn_actualizar.setStyleSheet("background:#1565c0;color:white;padding:8px;font-weight:bold;")
        self.btn_eliminar.setStyleSheet("background:#c62828;color:white;padding:8px;font-weight:bold;")
        self.btn_limpiar_campos.setStyleSheet("padding:8px;font-weight:bold;")
        for b in (self.btn_crear, self.btn_actualizar, self.btn_eliminar, self.btn_limpiar_campos):
            btns.addWidget(b)
        lay.addLayout(btns)

        self.btn_crear.clicked.connect(self.crear_producto)
        self.btn_actualizar.clicked.connect(self.actualizar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_limpiar_campos.clicked.connect(self.limpiar_campos)

        lay.addWidget(QLabel("<h3>Listado de productos (Read)</h3>"))
        self.tabla_prod = QTableWidget(0, 4)
        self.tabla_prod.setHorizontalHeaderLabels(["ID", "Nombre", "Precio (L)", "Stock"])
        self.tabla_prod.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_prod.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_prod.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_prod.setAlternatingRowColors(True)
        self.tabla_prod.setStyleSheet("background-color: white; alternate-background-color: #f5f5f5;")
        self.tabla_prod.itemClicked.connect(self.seleccionar_producto)
        lay.addWidget(self.tabla_prod)

        self.btn_refrescar = QPushButton("🔄 Refrescar tabla")
        self.btn_refrescar.clicked.connect(self.cargar_productos)
        lay.addWidget(self.btn_refrescar)

        self.cargar_productos()
        return w

    def cargar_productos(self):
        self.tabla_prod.setRowCount(0)
        con = conectar(); cur = con.cursor()
        cur.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY id")
        for i, fila in enumerate(cur.fetchall()):
            self.tabla_prod.insertRow(i)
            for j, val in enumerate(fila):
                item = QTableWidgetItem(str(val))
                if j == 0:
                    item.setForeground(QColor("#888888"))
                self.tabla_prod.setItem(i, j, item)
        con.close()

    def seleccionar_producto(self, item):
        fila = item.row()
        id_item = self.tabla_prod.item(fila, 0)
        nombre_item = self.tabla_prod.item(fila, 1)
        precio_item = self.tabla_prod.item(fila, 2)
        stock_item = self.tabla_prod.item(fila, 3)
        if (id_item is None or nombre_item is None or
                precio_item is None or stock_item is None):
            return
        self.txt_id.setText(id_item.text())
        self.txt_nombre.setText(nombre_item.text())
        self.spin_precio.setValue(float(precio_item.text()))
        self.spin_stock.setValue(int(stock_item.text()))

    def limpiar_campos(self):
        self.txt_id.clear(); self.txt_nombre.clear()
        self.spin_precio.setValue(0); self.spin_stock.setValue(0)

    def crear_producto(self):
        nom = self.txt_nombre.text().strip()
        if not nom:
            QMessageBox.warning(self, "Falta nombre", "Escriba el nombre del producto.")
            return
        con = conectar(); cur = con.cursor()
        cur.execute("INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
                    (nom, self.spin_precio.value(), self.spin_stock.value()))
        con.commit(); con.close()
        QMessageBox.information(self, "Éxito", f"Producto '{nom}' creado correctamente.")
        self.limpiar_campos(); self.cargar_productos(); self.cargar_productos_combo()

    def actualizar_producto(self):
        if not self.txt_id.text():
            QMessageBox.warning(self, "Seleccione", "Seleccione un producto de la tabla.")
            return
        con = conectar(); cur = con.cursor()
        cur.execute("UPDATE productos SET nombre=?, precio=?, stock=? WHERE id=?",
                    (self.txt_nombre.text().strip(), self.spin_precio.value(),
                     self.spin_stock.value(), int(self.txt_id.text())))
        con.commit(); con.close()
        QMessageBox.information(self, "Éxito", "Producto actualizado.")
        self.limpiar_campos(); self.cargar_productos(); self.cargar_productos_combo()

    def eliminar_producto(self):
        if not self.txt_id.text():
            QMessageBox.warning(self, "Seleccione", "Seleccione un producto de la tabla.")
            return
        resp = QMessageBox.question(self, "Confirmar",
            f"¿Eliminar el producto ID {self.txt_id.text()}?")
        if resp == QMessageBox.StandardButton.Yes:
            con = conectar(); cur = con.cursor()
            cur.execute("DELETE FROM productos WHERE id=?", (int(self.txt_id.text()),))
            con.commit(); con.close()
            QMessageBox.information(self, "Éxito", "Producto eliminado.")
            self.limpiar_campos(); self.cargar_productos(); self.cargar_productos_combo()

    # =========================================================
    # PESTAÑA 3: HISTORIAL DE VENTAS
    # =========================================================
    def tab_historial(self):
        w = QWidget()
        w.setStyleSheet("background-color: white;")
        lay = QVBoxLayout(w)
        lay.addWidget(QLabel("<h3>Historial de ventas</h3>"))
        self.tabla_ventas = QTableWidget(0, 4)
        self.tabla_ventas.setHorizontalHeaderLabels(["Factura #", "Fecha", "Cliente", "Total (L)"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_ventas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_ventas.setAlternatingRowColors(True)
        self.tabla_ventas.setStyleSheet("background-color: white; alternate-background-color: #f5f5f5;")
        lay.addWidget(self.tabla_ventas)
        self.lbl_ingresos = QLabel("")
        self.lbl_ingresos.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lay.addWidget(self.lbl_ingresos)
        btn = QPushButton("🔄 Refrescar historial")
        btn.clicked.connect(self.cargar_ventas)
        lay.addWidget(btn)
        self.cargar_ventas()
        return w

    def cargar_ventas(self):
        self.tabla_ventas.setRowCount(0)
        con = conectar(); cur = con.cursor()
        cur.execute("SELECT id, fecha, cliente, total FROM ventas ORDER BY id DESC")
        filas = cur.fetchall()
        total_gen = 0
        for i, (vid, fec, cli, tot) in enumerate(filas):
            total_gen += tot
            self.tabla_ventas.insertRow(i)
            for j, val in enumerate([str(vid), fec, cli, f"{tot:.2f}"]):
                self.tabla_ventas.setItem(i, j, QTableWidgetItem(val))
        con.close()
        self.lbl_ingresos.setText(f"💰 Ingresos totales: L {total_gen:.2f}   |   🧾 Ventas: {len(filas)}")

# -------------------------------------------------------------
# MAIN
# -------------------------------------------------------------
if __name__ == "__main__":
    crear_db()   # crea el archivo "db" si no existe
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QWidget { background-color: white; color: black; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget {
            background-color: white; color: black; border: 1px solid #999;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #2e7d32;
        }
        QPushButton { color: black; }
        QTabWidget::pane { border: 1px solid #bbb; }
        QHeaderView::section { background-color: #e8f5e9; color: black; font-weight: bold; }
    """)   # FONDO BLANCO + LETRAS NEGRAS

    login = Login()
    if login.exec() == QDialog.DialogCode.Accepted:
        win = VentanaPrincipal(login.usuario_ok)
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
