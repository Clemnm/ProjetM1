import cv2
import numpy as np

# Vidéo ------------------------------------------------------------
def process_video(video_path):
    """
    Traite une vidéo pour détecter les contours et dessiner des carrés avec leurs centres.

    Args:
        video_path (str): Le chemin vers le fichier vidéo.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erreur lors de l'ouverture de la vidéo")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, th2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:
                    cv2.drawContours(frame, [contour], 0, (0, 255, 0), 2)
                    
                    M = cv2.moments(contour)
                    if M['m00'] != 0:
                        cX = int(M['m10'] / M['m00'])
                        cY = int(M['m01'] / M['m00'])
                    else:
                        cX, cY = 0, 0

                    cv2.circle(frame, (cX, cY), 5, (255, 0, 0), -1)
                    cv2.putText(frame, f"({cX}, {cY})", (cX - 50, cY - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Video', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()

# Appel de la fonction pour traiter la vidéo
process_video('/Users/clementine/Desktop/test_bouton.mp4')


# Image ------------------------------------------------------------
"""
def process_image(image_path):
    \"""
    Traite une image pour détecter les contours et dessiner des carrés avec leurs centres.

    Args:
        image_path (str): Le chemin vers le fichier image.
    \"""
    # Charger l'image à partir du fichier
    image = cv2.imread(image_path)

    # Vérifier si l'image a bien été chargée
    if image is None:
        print("Erreur lors du chargement de l'image")
        return

    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuillage d'Otsu pour binariser l'image
    _, th2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Trouver les contours dans l'image binaire
    contours, _ = cv2.findContours(th2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Parcourir les contours trouvés
    for contour in contours:
        epsilon = 0.05 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Si le contour a 4 sommets, il s'agit d'un carré
        if len(approx) == 4:
            cv2.drawContours(image, [contour], 0, (0, 255, 0), 2)
            
            # Calculer les moments pour obtenir le centre du carré
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cX = int(M['m10'] / M['m00'])
                cY = int(M['m01'] / M['m00'])
            else:
                cX, cY = 0, 0

            # Dessiner un cercle au centre du carré et afficher les coordonnées
            cv2.circle(image, (cX, cY), 5, (255, 0, 0), -1)
            cv2.putText(image, f"({cX}, {cY})", (cX - 50, cY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Afficher l'image avec les carrés détectés et leurs centres
    cv2.imshow('Image', image)

    # Attendre une touche pour fermer la fenêtre
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Appel de la fonction pour traiter l'image
process_image('/Users/clementine/Desktop/test.png')
"""