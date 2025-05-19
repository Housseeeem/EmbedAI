import os

def trouver_fichier(racine_projet, nom_fichier_recherche):
    for dossier, sous_dossiers, fichiers in os.walk(racine_projet):
        for fichier in fichiers:
            if fichier == nom_fichier_recherche:
                chemin_complet = os.path.abspath(os.path.join(dossier, fichier))
                return chemin_complet
    return None

def afficher_arborescence(racine_projet, chemin_cible, prefix=""):
    for item in os.listdir(racine_projet):
        chemin_item = os.path.join(racine_projet, item)
        est_cible = os.path.abspath(chemin_item) == os.path.abspath(chemin_cible)

        if os.path.isdir(chemin_item):
            print(f"{prefix}📁 {item}/")
            afficher_arborescence(chemin_item, chemin_cible, prefix + "    ")
        else:
            if est_cible:
                print(f"{prefix}➡️  {item}  ✅")
            else:
                print(f"{prefix}📄 {item}")

# Utilisation
projet = "C:\\Users\\Dell\\Desktop\\dev"
nom_fichier = "sample2.c"

chemin = trouver_fichier(projet, nom_fichier)

if chemin:
    print("\n✅ Fichier trouvé :", chemin)
    print("\n📂 Arborescence du projet (fichier cible indiqué avec ✅) :\n")
    afficher_arborescence(projet, chemin)
    print("\n✅ Fichier trouvé :", chemin)



else:
    print(f"❌ Fichier '{nom_fichier}' non trouvé dans le projet '{projet}'.")
