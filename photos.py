from PyQt5 import QtWidgets, QtGui, QtCore
import os

class PhotoSlideshow(QtWidgets.QWidget):
    """
    Classe pour créer un diaporama de photos.

    Hérite de QWidget pour créer un widget avec des boutons de navigation (précédent, suivant)
    et un affichage d'image avec des bords arrondis. Les images sont chargées depuis un dossier spécifié.

    Attributs :
        image_folder (str) : Chemin du dossier contenant les images.
        image_files (list) : Liste des chemins des fichiers image.
        current_index (int) : Index de l'image actuellement affichée.
        main_layout (QHBoxLayout) : Layout principal pour organiser les widgets.
        prev_button (QPushButton) : Bouton pour afficher l'image précédente.
        image_label (QLabel) : Label pour afficher l'image avec des bords arrondis.
        next_button (QPushButton) : Bouton pour afficher l'image suivante.
        timer (QTimer) : Timer pour changer d'image automatiquement toutes les 3 minutes.
    """

    def __init__(self, image_folder, parent=None):
        """
        Initialise la classe PhotoSlideshow.

        Args:
            image_folder (str): Chemin du dossier contenant les images.
            parent (QWidget, optional): Widget parent. Par défaut None.
        """
        super().__init__(parent)

        self.image_folder = image_folder
        self.image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg", ".JPG"))]
        self.current_index = 0

        self.setFixedSize(600, 350)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        
        self.prev_button = QtWidgets.QPushButton("◀")
        self.prev_button.setFixedSize(50, 50)
        self.prev_button.setStyleSheet(self.button_style())
        self.prev_button.clicked.connect(self.show_prev_image)
        self.main_layout.addWidget(self.prev_button, alignment=QtCore.Qt.AlignLeft)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setFixedSize(450, 300)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.image_label, alignment=QtCore.Qt.AlignCenter)

        self.next_button = QtWidgets.QPushButton("▶")
        self.next_button.setFixedSize(50, 50)
        self.next_button.setStyleSheet(self.button_style())
        self.next_button.clicked.connect(self.show_next_image)
        self.main_layout.addWidget(self.next_button, alignment=QtCore.Qt.AlignRight)

        # Timer pour changer d'image automatiquement
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.show_next_image)
        self.timer.start(180000) 

        self.show_image()

    def button_style(self):
        """
        Retourne le style des boutons de navigation.

        Returns:
            str: Style CSS pour les boutons de navigation.
        """
        return """
            QPushButton {
                background-color: rgba(80, 179, 194, 180);
                color: white;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(58, 143, 160, 200);
            }
        """

    def show_image(self):
        """
        Affiche l'image actuelle avec des bords arrondis.
        """
        if self.image_files:
            pixmap = QtGui.QPixmap(self.image_files[self.current_index])
            pixmap = pixmap.scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

            rounded_pixmap = QtGui.QPixmap(pixmap.size())
            rounded_pixmap.fill(QtCore.Qt.transparent)

            painter = QtGui.QPainter(rounded_pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            path = QtGui.QPainterPath()
            path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 20, 20)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            self.image_label.setPixmap(rounded_pixmap)

    def show_next_image(self):
        """
        Passe à l'image suivante.
        """
        if self.image_files:
            self.current_index = (self.current_index + 1) % len(self.image_files)
            self.show_image()

    def show_prev_image(self):
        """
        Revient à l'image précédente.
        """
        if self.image_files:
            self.current_index = (self.current_index - 1) % len(self.image_files)
            self.show_image()