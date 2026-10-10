# MiniContes Studio — V1

Application Streamlit locale pour créer des histoires illustrées pour enfants en français, arabe et anglais.

## Démarrage rapide
- Installer Python 3.10+
- Installer FFmpeg et vérifier `ffmpeg -version`
- `pip install -r requirements.txt`
- `streamlit run app.py`

Le scénario fonctionne hors ligne avec des modèles intégrés. Les scènes visuelles sont créées localement par Pillow. La narration utilise `pyttsx3` si des voix système compatibles sont installées. Aucune clé API payante n'est nécessaire.

La version en ligne dépend de l'hébergeur et peut ne pas disposer de FFmpeg ou de voix TTS. Pour l'export MP4 le plus fiable, utiliser la version locale.
