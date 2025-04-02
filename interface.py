from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer, QDateTime
from api_domotique import ConnectedSocket
from api_discord import DiscordBot
from carres import CornerSquares
from photos import PhotoSlideshow
from lecteur_musique import MusicWindow
import config

class MainWindow(QtWidgets.QMainWindow): 
    """
    Classe principale pour la fenêtre de l'application "Med Board".

    Cette classe gère l'interface utilisateur principale de l'application, y compris
    l'intégration avec un bot Discord, la gestion de la domotique, la lecture de musique,
    et d'autres fonctionnalités interactives.

    Attributes:
        discord_bot (DiscordBot): Instance du bot Discord pour gérer les messages.
        light_on (bool): État de la lumière (allumée ou éteinte).
        button_on (bool): État du bouton (activé ou désactivé).
        music_on (bool): Indique si la musique est en cours de lecture.
        emergency_active (bool): Indique si le mode d'urgence est activé.
        connected_socket (ConnectedSocket): Instance pour gérer les prises connectées.
        calendar (QtWidgets.QCalendarWidget): Widget calendrier dans la barre latérale gauche.
        time_label (QtWidgets.QLabel): Label pour afficher l'heure actuelle.
        date_label (QtWidgets.QLabel): Label pour afficher la date actuelle.
        timer (QTimer): Timer pour mettre à jour l'heure affichée toutes les secondes.
        photo_slideshow (PhotoSlideshow): Diaporama de photos.
        conversation_text (QtWidgets.QTextEdit): Zone de texte pour afficher les conversations Discord.
        title_label (QtWidgets.QLabel): Label pour le titre de la section de conversation.
    """

    def __init__(self, discord_bot):
        super().__init__()

        # Initialise le bot Discord et définit un callback pour les messages reçus
        self.discord_bot = discord_bot
        self.discord_bot.set_message_received_callback(self.add_received_message)

        # Définition des propriétés de la fenêtre principale
        self.setWindowTitle("Med Board")
        self.resize(1200, 800)
        self.setStyleSheet("background-color:rgb(255, 255, 255);")

        # Initialisation de l'interface utilisateur
        self.initUI()
        self.light_on = False
        self.button_on = False
        self.music_on = False
        self.emergency_active = False

        # Initialisation de la prise connectée et authentification
        self.connected_socket = ConnectedSocket()
        self.connected_socket.authenticate()

    def initUI(self):
        """
        Initialise l'interface utilisateur de la fenêtre principale.

        Crée et configure les différents widgets et layouts de l'interface utilisateur,
        y compris les barres latérales, les boutons, et les sections principales.
        """
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout(main_widget)

        # Barre latérale gauche ----------------------------------------------------------------------------------------------------------
        sidebar_left = QtWidgets.QFrame()
        sidebar_left.setStyleSheet("border: none;")
        sidebar_left.setFixedWidth(300)
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar_left)

        sidebar_layout.addSpacerItem(QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Bloc supérieur "Med Board"
        med_board_widget = QtWidgets.QWidget()
        med_board_widget.setFixedHeight(310)
        med_board_widget.setStyleSheet("background-color: #cafafa; border-radius: 15px; padding: 10px;")

        med_board_layout = QtWidgets.QVBoxLayout(med_board_widget)

        med_board_title = QtWidgets.QLabel("Med Board 🩺 ")
        med_board_title.setFont(QtGui.QFont('Helvetica', 14, QtGui.QFont.Bold))
        med_board_layout.addWidget(med_board_title)

        # Texte descriptif
        med_board_description = QtWidgets.QTextEdit()
        med_board_description.setPlainText(
            "Bonjour, bienvenue sur ton interface personnalisée.\n\n "
            "Tu pourras : \n\n"
            "- écouter de la musique\n\n"
            "- interagir avec la domotique de ta chambre\n\n"
            "- envoyer des messages à ton entourage\n\n"
            "- envoyer un appel en cas d'urgence."
        )
        med_board_description.setFont(QtGui.QFont('Helvetica', 14))
        med_board_description.setReadOnly(True)
        med_board_description.setStyleSheet("background-color: transparent; border: none; color: black;")
        med_board_layout.addWidget(med_board_description)

        sidebar_layout.addWidget(med_board_widget)

        # Calendrier
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        sidebar_layout.addWidget(self.calendar)


        # Bouton d'appel d'urgence
        emergency_btn = QtWidgets.QPushButton('📞 Appel d\'urgence')
        emergency_btn.setFont(QtGui.QFont('Helvetica', 14))
        emergency_btn.setStyleSheet("color: white; background-color: #FF8C74; border: none; border-radius: 10px;")
        emergency_btn.setFixedSize(275, 150)  # Taille ajustée pour le bouton
        sidebar_layout.addWidget(emergency_btn)

        emergency_btn.clicked.connect(self.on_emergency_button_clicked)

        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar_left)

        # Section principale -----------------------------------------------------------------------------------------------------
        main_section = QtWidgets.QFrame()
        main_section.setStyleSheet("background-color: #F4F8F9; border-radius: 15px;")
        main_layout.addWidget(main_section)

        main_section_layout = QtWidgets.QVBoxLayout(main_section)
        main_section_layout.setContentsMargins(20, 20, 20, 20)
        main_section_layout.setSpacing(20)

        # En-tête
        header = QtWidgets.QFrame()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        greeting = QtWidgets.QLabel("Bonjour et bienvenue !")
        greeting.setFont(QtGui.QFont('Helvetica', 20, QtGui.QFont.Bold))
        header_layout.addWidget(greeting)

        # Heure et date
        self.time_label = QtWidgets.QLabel("", self)
        self.time_label.setFont(QtGui.QFont('Helvetica', 18))
        self.time_label.setAlignment(QtCore.Qt.AlignCenter)

        self.date_label = QtWidgets.QLabel("", self)
        self.date_label.setFont(QtGui.QFont('Helvetica', 14))
        self.date_label.setAlignment(QtCore.Qt.AlignCenter)

        header_layout.addWidget(self.time_label)
        header_layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        header_layout.addStretch()
        main_section_layout.addWidget(header)

        button_layout = QtWidgets.QHBoxLayout()

        # Bouton Musique
        music_btn = QtWidgets.QPushButton("Musique")
        music_btn.setFont(QtGui.QFont('Helvetica', 18))
        music_btn.setStyleSheet("background-color: #50b3c2; border-radius: 15px; color: white;")
        music_btn.setFixedSize(200, 60)
        music_btn.clicked.connect(self.open_music_page)
        button_layout.addWidget(music_btn)

        # Bouton Lumière
        light_btn = QtWidgets.QPushButton("Lumière")
        light_btn.setFont(QtGui.QFont('Helvetica', 18))
        light_btn.setStyleSheet("background-color: #B0E0E6; border-radius: 15px; color: white;")
        light_btn.setFixedSize(200, 60)
        light_btn.clicked.connect(self.toggle_light)
        button_layout.addWidget(light_btn)

        # Bouton Message
        message_btn = QtWidgets.QPushButton("Message")
        message_btn.setFont(QtGui.QFont('Helvetica', 18))
        message_btn.setStyleSheet("background-color: #50b3c2; border-radius: 15px; color: white;")
        message_btn.setFixedSize(200, 60)
        message_btn.clicked.connect(self.show_contact_selection)
        button_layout.addWidget(message_btn)

        main_section_layout.addLayout(button_layout)

        self.photo_slideshow = PhotoSlideshow("/Users/clementine/Desktop/proj/V5/images")  # Dossier contenant les images
        main_section_layout.addWidget(self.photo_slideshow, alignment=QtCore.Qt.AlignCenter)

        # Section de conversation
        self.title_label = QtWidgets.QLabel("Conversation")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        main_section_layout.addWidget(self.title_label)
        self.conversation_text = QtWidgets.QTextEdit()
        self.conversation_text.setReadOnly(True)
        self.conversation_text.setStyleSheet("background-color: #FFFFFF; border-radius: 15px;")
        main_section_layout.addWidget(self.conversation_text)

        # Barre latérale droite -----------------------------------------------------------------------------------------------------
        sidebar_right = QtWidgets.QFrame()
        sidebar_right.setFixedWidth(275)

        sidebar_right_layout = QtWidgets.QVBoxLayout(sidebar_right)
        sidebar_right_layout.addSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Informations patient 
        patient_info_widget = QtWidgets.QWidget()
        patient_info_widget.setStyleSheet("background-color: #cafafa; border-radius: 15px; padding: 10px;")

        patient_info_layout = QtWidgets.QVBoxLayout(patient_info_widget)
        patient_info_layout.setSpacing(5)  # Réduit l'espace entre les éléments
        patient_info_layout.setContentsMargins(10, 10, 10, 10)  # Marges autour du contenu

        patient_info_title = QtWidgets.QLabel("Informations patients")
        patient_info_title.setFont(QtGui.QFont('Helvetica', 14, QtGui.QFont.Bold))
        patient_info_layout.addWidget(patient_info_title)

        # Photo de la personne
        photo_label = QtWidgets.QLabel()
        photo = QtGui.QPixmap("image_test.png")
        photo = photo.scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        photo_label.setPixmap(photo)
        photo_label.setAlignment(QtCore.Qt.AlignCenter)
        patient_info_layout.addWidget(photo_label)

        name_label = QtWidgets.QLabel("Nom Prénom: PATIENT Numéro 1")
        dob_label = QtWidgets.QLabel("Date de naissance: 12/04/1987")
        patient_info_layout.addWidget(name_label)
        patient_info_layout.addWidget(dob_label)

        blood_group_label = QtWidgets.QLabel("Groupe sanguin: B+")
        height_label = QtWidgets.QLabel("Taille: 182 cm")
        weight_label = QtWidgets.QLabel("Poids: 75 kg")
        patient_info_layout.addWidget(blood_group_label)
        patient_info_layout.addWidget(height_label)
        patient_info_layout.addWidget(weight_label)

        sidebar_right_layout.addWidget(patient_info_widget)

        # Bloc Check-up
        checkup_widget = QtWidgets.QWidget()
        checkup_widget.setFixedHeight(155)
        checkup_widget.setStyleSheet("background-color: #cafafa; border-radius: 15px; padding: 10px;")

        checkup_block = QtWidgets.QVBoxLayout()
        checkup_title = QtWidgets.QLabel("Check-up")
        checkup_title.setFont(QtGui.QFont('Helvetica', 14, QtGui.QFont.Bold))
        checkup_block.addWidget(checkup_title)

        checkup_text = QtWidgets.QTextEdit()
        checkup_text.setPlainText("Médecin traitant : Dr Lemarchand\nDernier check-up réalisé : Sandra Gougena")
        checkup_text.setReadOnly(True)
        checkup_block.addWidget(checkup_text)

        checkup_widget.setLayout(checkup_block)
        sidebar_right_layout.addWidget(checkup_widget)

        # Bloc Préférences
        preferences_widget = QtWidgets.QWidget()
        preferences_widget.setFixedHeight(130)
        preferences_widget.setStyleSheet("background-color: #cafafa; border-radius: 15px; padding: 10px;")

        preferences_block = QtWidgets.QVBoxLayout()
        preferences_title = QtWidgets.QLabel("Préférences")
        preferences_title.setFont(QtGui.QFont('Helvetica', 14, QtGui.QFont.Bold))
        preferences_block.addWidget(preferences_title)

        preferences_text = QtWidgets.QTextEdit()
        preferences_text.setPlainText("Le patient aime sa température de bain à 38 °C")
        preferences_text.setReadOnly(True)
        preferences_block.addWidget(preferences_text)

        preferences_widget.setLayout(preferences_block)
        sidebar_right_layout.addWidget(preferences_widget)

        sidebar_right_layout.addSpacerItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        main_layout.addWidget(sidebar_right)

        # Ajout des carrés de calibration -----------------------------------------------------------------------------------------------------
        self.corner_squares = CornerSquares(main_widget)

    # Fonction qui sera appelée lors du clic sur appel d'urgence
    def on_emergency_button_clicked(self):
        if self.emergency_active:
            self.stop_emergency()
            light_color = "#FF8C74"
            self.sender().setStyleSheet(f"background-color: {light_color}; border-radius: 15px; color: white;")
        else:
            self.start_emergency()
            light_color = "#FF5A47"
            self.sender().setStyleSheet(f"background-color: {light_color}; border-radius: 15px; color: white;")

    def start_emergency(self):
        print("Bouton d'appel d'urgence cliqué !")
        self.discord_bot.send_emergency_message()
        self.connected_socket.blink_socket(5)
        self.emergency_active = True

    def stop_emergency(self):
        print("Arrêt de l'urgence")
        self.connected_socket.stop_blinking()
        self.emergency_active = False
        self.connected_socket.toggle_socket_state(5, state =0)

    def update_time(self):
        # Mise à jour de l'heure et de la date actuelles
        current_time = QDateTime.currentDateTime()
        time_text = current_time.toString("HH:mm")
        date_text = current_time.toString("dddd, dd MMMM yyyy")
        self.time_label.setText(time_text)
        self.date_label.setText(date_text)

    def open_music_page(self):
        self.music_window = MusicWindow()
        self.music_window.show()

    def toggle_light(self):
        # Allume ou éteint la lumière
        self.light_on = not self.light_on
        light_color = "#50b3c2" if self.light_on else "#B0E0E6"
        print(f"Lumière {'allumée' if self.light_on else 'éteinte'}")
        self.sender().setStyleSheet(f"background-color: {light_color}; border-radius: 15px; color: white;")
        self.connected_socket.toggle_socket_state(6)

    def show_contact_selection(self):
        # Affiche la fenêtre de sélection de contact
        self.contact_window = QtWidgets.QDialog(self)
        self.contact_window.setWindowTitle("Sélectionner un contact")
        self.contact_window.setFixedSize(600, 400)  # Agrandir la fenêtre de sélection de contact

        layout = QtWidgets.QVBoxLayout(self.contact_window)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        for contact in config.contacts.keys():
            contact_btn = QtWidgets.QPushButton(contact)
            contact_btn.setFont(QtGui.QFont('Helvetica', 16))
            contact_btn.setStyleSheet("background-color: #50b3c2; border-radius: 15px; color: white;")
            contact_btn.setFixedSize(550, 80)  # Ajuster la taille des boutons
            contact_btn.clicked.connect(lambda _, c=contact: self.show_message_window(c))
            layout.addWidget(contact_btn)
            layout.addSpacing(15)

        self.contact_window.exec_()

    def show_message_window(self, contact):
        # Affiche la fenêtre de sélection de message pour le contact sélectionné
        self.selected_contact = contact
        self.contact_window.accept()

        self.message_window = QtWidgets.QDialog(self)
        self.message_window.setWindowTitle(f"Envoyer un message à {self.selected_contact}")
        self.message_window.setFixedSize(600, 800)  # Agrandir la fenêtre de sélection de message

        layout = QtWidgets.QVBoxLayout(self.message_window)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        for message in config.messages:
            message_btn = QtWidgets.QPushButton(message)
            message_btn.setFont(QtGui.QFont('Helvetica', 14))
            message_btn.setStyleSheet("background-color: #50b3c2; border-radius: 15px; color: white; padding: 10px;")
            message_btn.setFixedSize(550, 70)  # Ajuster la taille des boutons
            message_btn.clicked.connect(lambda _, m=message: self.send_message(m))
            layout.addWidget(message_btn)
            layout.addSpacing(15)

        self.message_window.exec_()

    def send_message(self, selected_message):
        # Envoie le message sélectionné au contact choisi via Discord
        if not self.selected_contact:
            return

        print(f"Message envoyé à {self.selected_contact}: {selected_message}")

        self.discord_bot.send_message(self.selected_contact, selected_message)
        self.message_window.accept()

        self.add_conversation_message(f"Moi → {self.selected_contact}: {selected_message}")

    def add_conversation_message(self, message):
        # Ajoute un message à la section de conversation
        self.conversation_text.append(message)
        self.conversation_text.moveCursor(QtGui.QTextCursor.End)
        self.conversation_text.ensureCursorVisible()

    def add_received_message(self, message):
        # Ajoute un message reçu à la section de conversation
        self.conversation_text.append(f"Reçu: {message}")
        self.conversation_text.moveCursor(QtGui.QTextCursor.End)
        self.conversation_text.ensureCursorVisible()
