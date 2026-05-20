import os
import zipfile

def zip_project(source_dir, output_filename):
    # Les dossiers lourds ou inutiles à ignorer
    exclude_dirs = {'.venv', 'venv12', '__pycache__', '.git', '.pytest_cache'}
    exclude_files = {output_filename, 'zip_project.py'}

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Modifier la liste 'dirs' en place pour éviter que os.walk n'explore les dossiers ignorés
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files or file.endswith('.pyc'):
                    continue
                
                file_path = os.path.join(root, file)
                # Calculer le chemin relatif pour qu'il soit propre dans le zip
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                print(f"Ajouté : {arcname}")

if __name__ == '__main__':
    source_directory = '.' # Le dossier courant
    output_zip = 'Smart_Water_Quality_Projet.zip'
    print("Création du fichier ZIP du projet...")
    zip_project(source_directory, output_zip)
    print(f"\n✅ Terminé ! Le fichier {output_zip} a été créé avec succès.")
