from PyQt5 import QtWidgets, QtGui, QtCore

class CornerSquares:
    """ 
    Classe pour ajouter des carrés avec un rond au centre dans les coins d'un parent.

    Attributs :
        parent (QWidget) : Le widget parent dans lequel les carrés seront ajoutés.
        square_size (int) : La taille des carrés.
        square_color (str) : La couleur des carrés.
        circle_color (str) : La couleur des cercles.
        border_color (str) : La couleur de la bordure des carrés.
        border_width (int) : L'épaisseur de la bordure des carrés.
        squares (list) : La liste des widgets QLabel représentant les carrés.
    """

    def __init__(self, parent):
        """
        Initialise la classe CornerSquares.

        Args:
            parent (QWidget): Le widget parent dans lequel les carrés seront ajoutés.
        """
        self.parent = parent
        self.square_size = 100
        self.square_color = "#FFFFFF"
        self.circle_color = "#000000"
        self.border_color = "#000000"
        self.border_width = 15

        self.squares = [self.create_square() for _ in range(4)]
        self.update_positions()

        # Carrés au premier plan
        for square in self.squares:
            square.raise_()
            square.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        
        parent.resizeEvent = self.resize_event

    def create_square(self):
        """
        Crée un carré avec un rond au centre.

        Returns:
            QLabel: Le widget QLabel représentant le carré.
        """
        square = QtWidgets.QLabel(self.parent)
        square.setStyleSheet(f"""
            background-color: {self.square_color};
            border: {self.border_width}px solid {self.border_color};
        """)
        square.setFixedSize(self.square_size, self.square_size)

        # Ajout du rond au centre du carré
        round_label = QtWidgets.QLabel(square)
        round_label.setFixedSize(self.square_size, self.square_size)
        round_label.setStyleSheet("background: transparent;")
        round_label.paintEvent = lambda event, s=round_label: self.paint_circle(event, s)

        return square

    def paint_circle(self, event, widget):
        """
        Dessine un rond au centre du widget donné.

        Args:
            event (QPaintEvent): L'événement de peinture.
            widget (QWidget): Le widget dans lequel dessiner le rond.
        """
        painter = QtGui.QPainter(widget)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        brush = QtGui.QBrush(QtGui.QColor(self.circle_color))
        painter.setBrush(brush)
        painter.setPen(QtCore.Qt.NoPen)

        # Calcul de la taille et de la position du cercle
        radius = self.square_size // 9
        center_x = (self.square_size - radius * 2) // 2
        center_y = (self.square_size - radius * 2) // 2

        painter.drawEllipse(center_x, center_y, radius * 2, radius * 2)
        painter.end()

    def update_positions(self):
        """
        Met à jour la position des carrés dans les coins du parent.
        """
        w, h = self.parent.width(), self.parent.height()
        positions = [(0, 0), (w - self.square_size, 0), (0, h - self.square_size), (w - self.square_size, h - self.square_size)]
        
        for square, (x, y) in zip(self.squares, positions):
            square.move(x, y)

    def resize_event(self, event):
        """
        Met à jour la position des carrés lorsque le parent est redimensionné.

        Args:
            event (QResizeEvent): L'événement de redimensionnement.
        """
        self.update_positions()
        event.accept()