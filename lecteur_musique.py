import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
import pygame

class MusicWindow(QtWidgets.QDialog):
    """
    Classe pour créer une fenêtre de lecteur de musique locale.

    Hérite de QDialog pour créer une boîte de dialogue avec une liste de fichiers musicaux,
    des contrôles de lecture (play, pause, suivant, précédent), et l'affichage des couvertures d'album.

    Attributs :
        music_list (QListWidget) : Liste des fichiers musicaux.
        music_files (list) : Liste des chemins des fichiers musicaux.
        cover_label (QLabel) : Label pour afficher la couverture de l'album.
        song_label (QLabel) : Label pour afficher le nom de la musique en cours de lecture.
        prev_btn (QPushButton) : Bouton pour passer à la musique précédente.
        play_btn (QPushButton) : Bouton pour lire ou mettre en pause la musique.
        pause_btn (QPushButton) : Bouton pour mettre la musique en pause.
        next_btn (QPushButton) : Bouton pour passer à la musique suivante.
        exit_btn (QPushButton) : Bouton pour quitter l'application.
        is_paused (bool) : Indique si la musique est en pause.
        current_music (str) : Chemin du fichier musical en cours de lecture.
        current_item (QListWidgetItem) : Élément de la liste correspondant à la musique en cours de lecture.
    """

    def __init__(self):
        super().__init__()

        # Initialisation de pygame mixer pour lire la musique
        pygame.mixer.init()

        self.setWindowTitle("Local Music Player")
        self.resize(600, 600)

        layout = QtWidgets.QVBoxLayout()

        self.music_list = QtWidgets.QListWidget()
        self.music_files = []
        self.load_music_files()
        self.music_list.itemClicked.connect(self.select_music)
        layout.addWidget(self.music_list)

        self.cover_label = QtWidgets.QLabel()
        self.cover_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.cover_label)

        self.song_label = QtWidgets.QLabel("Aucune musique sélectionnée")
        self.song_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.song_label)

        controls_layout = QtWidgets.QHBoxLayout()

        self.prev_btn = QtWidgets.QPushButton("Previous")
        self.prev_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.prev_btn.clicked.connect(self.prev_track)
        controls_layout.addWidget(self.prev_btn)

        self.play_btn = QtWidgets.QPushButton("Play")
        self.play_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.play_btn.clicked.connect(self.play_pause)
        controls_layout.addWidget(self.play_btn)

        self.pause_btn = QtWidgets.QPushButton("Pause")
        self.pause_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pause_btn.clicked.connect(self.pause_music)
        controls_layout.addWidget(self.pause_btn)

        self.next_btn = QtWidgets.QPushButton("Next")
        self.next_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.next_btn.clicked.connect(self.next_track)
        controls_layout.addWidget(self.next_btn)

        layout.addLayout(controls_layout)

        self.exit_btn = QtWidgets.QPushButton("Exit")
        self.exit_btn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)

        self.setLayout(layout)

        self.is_paused = False
        self.current_music = None
        self.current_item = None

    def load_music_files(self):
        """
        Charge les fichiers musicaux depuis le dossier spécifié et les ajoute à la liste de lecture.
        """
        music_folder = "/Users/clementine/Desktop/proj/V5/musique"
        if not os.path.exists(music_folder):
            QtWidgets.QMessageBox.critical(self, "Erreur", "Le dossier de musique spécifié n'existe pas.")
            return

        for file in os.listdir(music_folder):
            if file.endswith(".mp3"):
                item = QtWidgets.QListWidgetItem(file)
                item.setData(QtCore.Qt.UserRole, os.path.join(music_folder, file))
                self.music_list.addItem(item)
                self.music_files.append(os.path.join(music_folder, file))

    def select_music(self, item):
        """
        Sélectionne une musique dans la liste et met à jour l'affichage de la couverture et du nom de la musique.

        Args:
            item (QListWidgetItem): Élément de la liste correspondant à la musique sélectionnée.
        """
        self.current_music = item.data(QtCore.Qt.UserRole)
        self.current_item = item

        self.song_label.setText(f"Now Playing: {item.text()}")

        image_path = "/Users/clementine/Desktop/proj/V7/musique/image_playlist.png"
        if os.path.exists(image_path):
            image = QtGui.QImage(image_path)
            self.cover_label.setPixmap(QtGui.QPixmap(image))
        else:
            self.cover_label.setPixmap(QtGui.QPixmap(100, 100).fill(QtGui.QColor('gray')))

        self.highlight_current_item()

    def play_pause(self):
        """
        Lit ou met en pause la musique sélectionnée.
        """
        if not self.current_music:
            QtWidgets.QMessageBox.critical(self, "Erreur", "Aucune musique sélectionnée. Veuillez en sélectionner une.")
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play()
            self.is_paused = False

        self.highlight_current_item()

    def pause_music(self):
        """
        Met la musique en pause.
        """
        pygame.mixer.music.pause()
        self.is_paused = True

    def next_track(self):
        """
        Passe à la musique suivante dans la liste de lecture.
        """
        if self.current_music:
            current_index = self.music_files.index(self.current_music)
            next_index = (current_index + 1) % len(self.music_files)
            self.current_music = self.music_files[next_index]
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play()

            # Mettre à jour le texte de la musique et l'élément de la liste
            self.song_label.setText(f"Now Playing: {os.path.basename(self.current_music)}")
            self.update_current_item(next_index)

    def prev_track(self):
        """
        Passe à la musique précédente dans la liste de lecture.
        """
        if self.current_music:
            current_index = self.music_files.index(self.current_music)
            prev_index = (current_index - 1) % len(self.music_files)
            self.current_music = self.music_files[prev_index]
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play()

            self.song_label.setText(f"Now Playing: {os.path.basename(self.current_music)}")
            self.update_current_item(prev_index)
    

    def highlight_current_item(self):
        """
        Met en surbrillance l'élément de la liste correspondant à la musique en cours de lecture.
        """
        for i in range(self.music_list.count()):
            item = self.music_list.item(i)
            if item == self.current_item:
                item.setBackground(QtGui.QColor(200, 200, 255))
            else:
                item.setBackground(QtGui.QColor(255, 255, 255))

    def update_current_item(self, index):
        """
        Met à jour l'élément de la liste correspondant à la musique en cours de lecture.

        Args:
            index (int): Index de l'élément dans la liste.
        """
        self.current_item = self.music_list.item(index)
        self.highlight_current_item()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MusicWindow()
    window.show()
    sys.exit(app.exec_())
