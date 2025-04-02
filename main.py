from PyQt5 import QtWidgets, QtGui, QtCore
import sys
from api_discord import DiscordBot
from interface_test import MainWindow

def main():
    """
    Point d'entrée principal de l'application.

    Cette fonction initialise le bot Discord, crée l'application Qt et la fenêtre principale, 
    et démarre la boucle d'événements Qt. 

    Modules importés :
    - PyQt5.QtWidgets : Modules PyQt5 pour créer l'interface graphique.
    - sys : Module pour interagir avec l'environnement d'exécution Python.
    - api_discord.DiscordBot : Module personnalisé pour gérer un bot Discord.
    - interface_test.MainWindow : Module personnalisé pour la fenêtre principale de l'application.

    L'application crée une instance de `DiscordBot`, initialise la `QApplication` avec les arguments de la ligne de commande,
    crée et affiche la `MainWindow`, et démarre la boucle d'événements principale de l'application.
    """
    discord_bot = DiscordBot()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(discord_bot)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()