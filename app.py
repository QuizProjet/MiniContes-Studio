# MiniContes Studio — première version locale, sans API payante obligatoire
# Lancement : pip install -r requirements.txt && streamlit run app.py

from pathlib import Path
import json, re, math, shutil, subprocess, tempfile, textwrap, random
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

APP_DIR = Path(__file__).parent
PROJECTS_DIR = APP_DIR / "projects"
OUTPUT_DIR = APP_DIR / "exports"
PROJECTS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="MiniContes Studio", page_icon="✨", layout="wide")

LANGS = {
    "Français": "fr",
    "العربية": "ar",
    "English": "en",
}
THEMES = {
    "Magie": {
        "fr": ("La petite étoile perdue", "Une petite étoile tombe dans une forêt enchantée. Luna, une jeune renarde curieuse, décide de l'aider à retrouver sa famille."),
        "ar": ("النجمة الصغيرة الضائعة", "سقطت نجمة صغيرة في غابة ساحرة. قررت لونا الثعلبة الصغيرة مساعدتها على العودة إلى عائلتها."),
        "en": ("The Little Lost Star", "A tiny star falls into an enchanted forest. Luna, a curious young fox, decides to help it find its family."),
    },
    "Amitié": {
        "fr": ("Le pont de l'amitié", "Luna la renarde et Milo le lapin doivent réparer un petit pont avant que leurs amis ne puissent se retrouver."),
        "ar": ("جسر الصداقة", "تحتاج لونا الثعلبة وميلو الأرنب إلى إصلاح جسر صغير حتى يتمكن أصدقاؤهما من اللقاء."),
        "en": ("The Friendship Bridge", "Luna the fox and Milo the rabbit must repair a little bridge so their friends can meet again."),
    },
    "Courage": {
        "fr": ("Le dragon qui avait peur", "Un petit dragon fait beaucoup de bruit pendant l'orage. Luna découvre qu'il a peur et l'aide à se sentir en sécurité."),
        "ar": ("التنين الذي كان خائفًا", "يصدر تنين صغير أصواتًا عالية أثناء العاصفة. تكتشف لونا أنه خائف وتساعده على الشعور بالأمان."),
        "en": ("The Dragon Who Was Afraid", "A little dragon makes loud noises during a storm. Luna discovers that he is frightened and helps him feel safe."),
    },
    "Partage": {
        "fr": ("Le panier magique", "Luna trouve un panier de fruits magiques et découvre que le partage rend tout le monde plus heureux."),
        "ar": ("السلة السحرية", "تعثر لونا على سلة فواكه سحرية وتكتشف أن المشاركة تجعل الجميع أكثر سعادة."),
        "en": ("The Magic Basket", "Luna finds a basket of magical fruit and discovers that sharing makes everyone happier."),
    },
}
MORALS = {
    "Magie": {"fr":"La gentillesse peut illuminer le monde.", "ar":"اللطف قادر على إنارة العالم.", "en":"Kindness can brighten the world."},
    "Amitié": {"fr":"Ensemble, nous pouvons accomplir davantage.", "ar":"معًا نستطيع إنجاز المزيد.", "en":"Together, we can do more."},
    "Courage": {"fr":"Le courage commence parfois par demander de l’aide.", "ar":"تبدأ الشجاعة أحيانًا بطلب المساعدة.", "en":"Courage sometimes begins by asking for help."},
    "Partage": {"fr":"Partager apporte de la joie à tous.", "ar":"المشاركة تجلب الفرح للجميع.", "en":"Sharing brings joy to everyone."},
}

def make_story(title, premise, moral, lang, age, minutes, custom_idea=""):
    # A template-based generator works offline; users can edit every scene.
    if custom_idea.strip():
        premise = custom_idea.strip()
    if lang == "fr":
        paragraphs = [
            f"Dans un royaume caché derrière les nuages, vivait Luna, une petite renarde qui adorait découvrir de nouvelles choses. Un matin, elle remarqua un étrange scintillement près du vieux chêne.",
            f"En s'approchant, Luna découvrit un nouvel ami qui avait besoin d'aide. « Ne t'inquiète pas, nous allons chercher une solution ensemble », promit-elle.",
            f"Le chemin traversait une prairie de fleurs lumineuses, puis un ruisseau chantant. À chaque étape, Luna rencontrait quelqu'un qui connaissait un petit morceau de la réponse.",
            f"Au début, tout semblait compliqué. Luna voulut se dépêcher, mais elle comprit qu'il fallait écouter ses amis et réfléchir calmement. Chacun proposa une idée, et leurs idées se complétèrent.",
            f"Enfin, ils trouvèrent une solution. La forêt s'illumina, les oiseaux se mirent à chanter et leur nouvel ami retrouva le sourire. Luna sentit une chaleur joyeuse dans son cœur.",
            f"Avant de rentrer, Luna remercia tous ceux qui l'avaient aidée. Elle savait désormais qu'une aventure devient plus belle quand on fait preuve de patience, d'écoute et de bonté.",
            f"Et depuis ce jour, chaque fois qu'une lumière mystérieuse apparaissait dans la forêt, Luna était prête à partir pour une nouvelle aventure."
        ]
        ending = f"Et n'oublie pas : {moral}"
    elif lang == "ar":
        paragraphs = [
            "في مملكة صغيرة تختبئ خلف الغيوم، عاشت لونا، الثعلبة الصغيرة التي تحب اكتشاف الأشياء الجديدة. وفي صباح جميل، رأت ضوءًا غريبًا قرب شجرة البلوط القديمة.",
            "اقتربت لونا فوجدت صديقًا جديدًا يحتاج إلى المساعدة. قالت له بلطف: «لا تقلق، سنبحث عن حل معًا».",
            "مرّ الطريق عبر مرج مليء بالزهور المضيئة، ثم بجانب جدول صغير يغني. وفي كل مكان، قابلت لونا صديقًا يعرف جزءًا من الإجابة.",
            "في البداية، بدا الأمر صعبًا. أرادت لونا أن تتسرع، لكنها فهمت أن عليها الاستماع إلى أصدقائها والتفكير بهدوء. اقترح كل واحد فكرة، واجتمعت الأفكار لتصبح حلًا جميلًا.",
            "وأخيرًا، وجدوا الحل. أضاءت الغابة، وغرّدت الطيور، وعاد الابتسام إلى وجه صديقهم الجديد. شعرت لونا بالفرح في قلبها.",
            "قبل العودة إلى البيت، شكرت لونا كل من ساعدها. وعرفت أن المغامرة تصبح أجمل عندما نتحلى بالصبر ونستمع إلى الآخرين ونكون لطفاء.",
            "ومنذ ذلك اليوم، كلما ظهر ضوء غامض في الغابة، كانت لونا مستعدة لخوض مغامرة جديدة."
        ]
        ending = f"وتذكّر دائمًا: {moral}"
    else:
        paragraphs = [
            "In a little kingdom hidden behind the clouds lived Luna, a young fox who loved discovering new things. One bright morning, she noticed a strange sparkle near the old oak tree.",
            "When Luna came closer, she found a new friend who needed help. “Don't worry. We'll find a solution together,” she promised.",
            "The path crossed a meadow of glowing flowers and then followed a singing stream. At every stop, Luna met someone who knew a small part of the answer.",
            "At first, the problem seemed difficult. Luna wanted to hurry, but she realized she needed to listen to her friends and think calmly. Everyone shared an idea, and the ideas fit together.",
            "At last, they found a solution. The forest glowed, the birds began to sing, and their new friend smiled again. Luna felt a warm happiness in her heart.",
            "Before going home, Luna thanked everyone who had helped. She now knew that an adventure becomes more wonderful when we are patient, listen carefully, and show kindness.",
            "From that day on, whenever a mysterious light appeared in the forest, Luna was ready for another adventure."
        ]
        ending = f"And remember: {moral}"
    # For requested duration, repeat a gentle reflection/interactive moment rather than empty padding.
    target = max(5, min(10, round(minutes * 2.2)))
    scenes = []
    for i in range(target):
        if i < len(paragraphs):
            body = paragraphs[i]
        else:
            body = {
                "fr": "Luna prit un instant pour regarder les étoiles et se demanda quelle nouvelle aventure l'attendait demain. Peut-être qu'un ami aurait besoin d'elle, ou qu'un nouveau mystère se cacherait derrière les arbres.",
                "ar": "توقفت لونا قليلًا لتنظر إلى النجوم، وتساءلت عن المغامرة الجديدة التي تنتظرها غدًا. ربما يحتاج صديق إلى مساعدتها، أو يختبئ لغز جديد خلف الأشجار.",
                "en": "Luna paused to look at the stars and wondered what adventure might be waiting tomorrow. Perhaps a friend would need her help, or a new mystery would be hiding beyond the trees."
            }[lang]
        scenes.append({"number": i+1, "title": f"Scene {i+1}", "text": body})
    scenes[-1]["text"] += "\n\n" + ending
    return {"title": title, "language": lang, "age": age, "minutes": minutes, "moral": moral, "premise": premise, "scenes": scenes}

def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for f in candidates:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            pass
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0,0), trial, font=font)[2] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def create_scene_image(title, body, index, total, lang, outpath, size=(1280,720)):
    w,h = size
    im = Image.new("RGB", size)
    pix = im.load()
    # Gradient midnight blue -> purple
    for y in range(h):
        for x in range(w):
            t = y / h
            pix[x,y] = (int(13+24*t), int(25+10*t), int(68+70*t))
    d = ImageDraw.Draw(im)
    # stars
    rng = random.Random(index * 101 + 7)
    for _ in range(110):
        x, y = rng.randint(0,w-1), rng.randint(0,int(h*.62))
        r = rng.choice([1,2,3,4])
        d.ellipse((x-r,y-r,x+r,y+r), fill=(255,220+rng.randint(0,30),130))
    # moon
    d.ellipse((w-210,50,w-100,160), fill=(255,229,155))
    d.ellipse((w-180,30,w-70,140), fill=(28,35,85))
    # hills
    d.ellipse((-160, h*.55, w*.65, h*1.2), fill=(20,74,75))
    d.ellipse((w*.25, h*.62, w*1.15, h*1.2), fill=(29,91,76))
    # simple fox mascot
    cx, cy = int(w*.18), int(h*.58)
    d.ellipse((cx-82,cy-55,cx+82,cy+100), fill=(238,116,48), outline=(255,205,125), width=5)
    d.polygon([(cx-62,cy-50),(cx-72,cy-130),(cx-20,cy-76)], fill=(238,116,48), outline=(255,205,125))
    d.polygon([(cx+20,cy-76),(cx+72,cy-130),(cx+62,cy-50)], fill=(238,116,48), outline=(255,205,125))
    d.ellipse((cx-55,cy-42,cx+55,cy+28), fill=(255,222,177))
    d.ellipse((cx-30,cy-24,cx-12,cy-2), fill=(30,25,38))
    d.ellipse((cx+12,cy-24,cx+30,cy-2), fill=(30,25,38))
    d.ellipse((cx-7,cy+2,cx+7,cy+14), fill=(40,25,30))
    # magical star
    sx, sy = int(w*.34), int(h*.40)
    pts=[]
    for j in range(10):
        a=-math.pi/2+j*math.pi/5
        r=42 if j%2==0 else 18
        pts.append((sx+math.cos(a)*r, sy+math.sin(a)*r))
    d.polygon(pts, fill=(255,221,76), outline=(255,248,188))
    # text panel
    panel=(int(w*.39), int(h*.23), int(w*.94), int(h*.85))
    d.rounded_rectangle(panel, radius=30, fill=(7,15,48), outline=(240,197,88), width=3)
    title_font=load_font(38, True)
    body_font=load_font(27)
    small_font=load_font(21, True)
    d.text((panel[0]+30,panel[1]+24), title, font=title_font, fill=(255,220,112))
    excerpt = body.replace("\n"," ")
    maxw=panel[2]-panel[0]-60
    lines=wrap_text(d, excerpt, body_font, maxw)[:7]
    yy=panel[1]+92
    for line in lines:
        d.text((panel[0]+30,yy), line, font=body_font, fill=(248,248,255))
        yy += 38
    d.text((40,h-50), f"MINICONTES  •  {index}/{total}", font=small_font, fill=(255,224,139))
    im.save(outpath, quality=92)

def find_ffmpeg():
    return shutil.which("ffmpeg")

def create_video(project, export_path, use_tts=True):
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("FFmpeg n'est pas installé ou n'est pas accessible. Installe FFmpeg puis relance l'application.")
    lang = project["language"]
    with tempfile.TemporaryDirectory(prefix="minicontes_") as tmp:
        tmp = Path(tmp)
        scene_files=[]
        for i, sc in enumerate(project["scenes"], 1):
            p=tmp/f"scene_{i:02d}.png"
            create_scene_image(project["title"], sc["text"], i, len(project["scenes"]), lang, p)
            scene_files.append(p)
        # optional offline TTS through pyttsx3. Video still exports with no audio if unavailable.
        audio_files=[]
        tts_ok=False
        if use_tts:
            try:
                import pyttsx3
                engine=pyttsx3.init()
                voices=engine.getProperty("voices")
                # Select a voice that looks like the language, if available.
                code={"fr":"fr","ar":"ar","en":"en"}[lang]
                for voice in voices:
                    if code in (voice.id+" "+voice.name).lower():
                        engine.setProperty("voice", voice.id)
                        break
                for i, sc in enumerate(project["scenes"],1):
                    wav=tmp/f"voice_{i:02d}.wav"
                    engine.save_to_file(sc["text"], str(wav))
                    engine.runAndWait()
                    if wav.exists() and wav.stat().st_size > 1000:
                        audio_files.append(wav)
                    else:
                        audio_files.append(None)
                tts_ok=any(audio_files)
            except Exception:
                tts_ok=False
        # Create one clip per still; concat demuxer keeps compatibility.
        durations=[]
        for i, sc in enumerate(project["scenes"]):
            words=max(12,len(sc["text"].split()))
            durations.append(max(7.0, words/2.5))
        concat=tmp/"concat.txt"
        with concat.open("w",encoding="utf-8") as f:
            for i,p in enumerate(scene_files):
                f.write(f"file '{p.as_posix()}'\n")
                f.write(f"duration {durations[i]:.2f}\n")
            f.write(f"file '{scene_files[-1].as_posix()}'\n")
        silent=tmp/"silent.mp4"
        cmd=[ffmpeg,"-y","-f","concat","-safe","0","-i",str(concat),"-vf","fps=24,format=yuv420p","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",str(silent)]
        result=subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Échec de l'export vidéo : "+result.stderr[-1200:])
        # Optional narration concatenated by ffmpeg; if pyttsx3 produced one usable file.
        usable=[p for p in audio_files if p and p.exists()]
        if usable:
            # Concatenate available narration wavs, then mux; scene timing is approximate in this v1.
            ac=tmp/"audio.txt"
            with ac.open("w",encoding="utf-8") as f:
                for p in usable:
                    f.write(f"file '{p.as_posix()}'\n")
            merged=tmp/"narration.wav"
            ar=subprocess.run([ffmpeg,"-y","-f","concat","-safe","0","-i",str(ac),"-c:a","pcm_s16le",str(merged)],capture_output=True,text=True)
            if ar.returncode==0:
                mux=subprocess.run([ffmpeg,"-y","-i",str(silent),"-i",str(merged),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-shortest",str(export_path)],capture_output=True,text=True)
                if mux.returncode==0:
                    return True
        shutil.copy2(silent, export_path)
        return False

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#f7f7ff 0%,#eef2ff 100%);}
.hero {padding: 1.3rem 1.5rem; border-radius: 22px; background: linear-gradient(120deg,#101b4c,#4532a8); color:white; margin-bottom:1rem;}
.hero h1 {color:#ffd86b; margin-bottom:.25rem;}
.note {padding:.8rem 1rem; border-radius:12px; background:#fff7dc; color:#3b3152;}
</style>
<div class="hero">
<h1>✨ MiniContes Studio</h1>
<p>Crée des histoires animées pour enfants — français, العربية, English.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://dummyimage.com/240x120/152052/ffe08a.png&text=MiniContes", use_container_width=True)
    page=st.radio("Navigation", ["Créer une histoire","Mes projets","Guide de démarrage"])
    st.caption("Version 1.0 • Priorité au gratuit et au local")

if page == "Créer une histoire":
    left,right=st.columns([0.9,1.1], gap="large")
    with left:
        st.subheader("1. Configure ton histoire")
        title=st.text_input("Titre", value="La petite étoile perdue")
        language_name=st.selectbox("Langue de narration", list(LANGS.keys()), index=0)
        lang=LANGS[language_name]
        age=st.selectbox("Âge cible", ["2–4 ans","4–6 ans","6–9 ans","9–12 ans","Famille / tous âges"], index=1)
        minutes=st.slider("Durée cible (minutes)", 2, 5, 3)
        theme=st.selectbox("Thème", list(THEMES.keys()))
        idea=st.text_area("Ton idée (facultatif)", placeholder="Ex. : Une petite renarde aide un dragon à retrouver sa voix…", height=100)
        generate=st.button("✨ Générer le scénario et les scènes", type="primary", use_container_width=True)
        st.markdown('<div class="note">Cette version crée un scénario hors ligne à partir de modèles éditables. Elle ne nécessite aucune clé API.</div>', unsafe_allow_html=True)
    with right:
        st.subheader("2. Aperçu du projet")
        if generate or "current_project" not in st.session_state:
            title_default, premise=THEMES[theme][lang]
            moral=MORALS[theme][lang]
            project=make_story(title or title_default, premise, moral, lang, age, minutes, idea)
            for i, sc in enumerate(project["scenes"],1):
                sc["title"] = f"Scène {i}"
            st.session_state.current_project=project
        project=st.session_state.current_project
        st.write(f"**{project['title']}** · {len(project['scenes'])} scènes · {project['minutes']} min visées · {project['language'].upper()}")
        st.caption("Modifie librement le texte de chaque scène avant l'export.")
        with st.form("edit_scenes"):
            new_title=st.text_input("Titre de l'histoire", value=project["title"])
            edited=[]
            for i, sc in enumerate(project["scenes"]):
                txt=st.text_area(f"Scène {i+1}", value=sc["text"], height=95, key=f"scene_edit_{i}_{project['language']}")
                edited.append({"number":i+1,"title":sc.get("title",f"Scène {i+1}"),"text":txt})
            save=st.form_submit_button("💾 Enregistrer les modifications")
        if save:
            project["title"]=new_title
            project["scenes"]=edited
            st.session_state.current_project=project
            st.success("Modifications enregistrées.")
        st.markdown("**Morale**")
        st.info(project["moral"])
        st.subheader("3. Générer la vidéo MP4")
        st.caption("L'export vidéo nécessite FFmpeg. La narration vocale hors ligne dépend des voix installées sur ton ordinateur.")
        use_tts=st.checkbox("Essayer d'ajouter une narration vocale hors ligne (pyttsx3)", value=True)
        if st.button("🎬 Exporter la vidéo MP4", type="primary", use_container_width=True):
            safe=re.sub(r"[^a-zA-Z0-9_-]+","_",project["title"]).strip("_") or "minicontes"
            dest=OUTPUT_DIR/f"{safe}_{project['language']}.mp4"
            with st.spinner("Création des scènes et assemblage de la vidéo…"):
                try:
                    narration_added=create_video(project,dest,use_tts=use_tts)
                    st.session_state.last_export=str(dest)
                    st.session_state.narration_added=narration_added
                    st.success("Vidéo créée !")
                except Exception as e:
                    st.error(str(e))
                    st.info("Pour l'export MP4, installe FFmpeg puis relance l'application. Voir le Guide de démarrage.")
        if st.session_state.get("last_export") and Path(st.session_state.last_export).exists():
            p=Path(st.session_state.last_export)
            st.video(str(p))
            st.download_button("⬇️ Télécharger la vidéo", data=p.read_bytes(), file_name=p.name, mime="video/mp4", use_container_width=True)
            if st.session_state.get("narration_added"):
                st.success("Une piste vocale a été ajoutée.")
            else:
                st.warning("Vidéo exportée sans narration vocale. Installe des voix système compatibles ou décoche l'option narration.")

        if st.button("📚 Enregistrer dans Mes projets", use_container_width=True):
            p=PROJECTS_DIR/(re.sub(r"[^a-zA-Z0-9_-]+","_",project["title"]).strip("_") or "histoire")+".json"
            p.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding="utf-8")
            st.success(f"Projet enregistré : {p.name}")

elif page == "Mes projets":
    st.subheader("📚 Mes projets")
    files=sorted(PROJECTS_DIR.glob("*.json"), key=lambda p:p.stat().st_mtime, reverse=True)
    if not files:
        st.info("Aucun projet enregistré pour le moment. Crée une histoire puis clique sur « Enregistrer dans Mes projets ».")
    else:
        for p in files:
            with st.expander(p.stem):
                try:
                    data=json.loads(p.read_text(encoding="utf-8"))
                    st.write(f"{data.get('title','Sans titre')} · {len(data.get('scenes',[]))} scènes · {data.get('language','fr')}")
                    st.download_button("Télécharger le projet JSON", p.read_bytes(), file_name=p.name, mime="application/json", key=f"dl_{p.name}")
                    if st.button("Charger ce projet", key=f"load_{p.name}"):
                        st.session_state.current_project=data
                        st.success("Projet chargé. Ouvre « Créer une histoire » pour continuer.")
                except Exception as e:
                    st.error(f"Impossible de lire ce projet : {e}")

else:
    st.subheader("Guide de démarrage")
    st.markdown("""
### Sur Windows
1. Installe Python 3.10 ou plus récent depuis [python.org](https://www.python.org/downloads/). Pendant l'installation, coche **Add Python to PATH**.
2. Installe FFmpeg depuis [ffmpeg.org](https://ffmpeg.org/download.html) ou via un gestionnaire de paquets. Vérifie dans un terminal que `ffmpeg -version` fonctionne.
3. Décompresse le dossier de MiniContes Studio.
4. Ouvre un terminal dans ce dossier et exécute :

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

### Sur macOS ou Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Pour la version en ligne
- Déploie le projet sur un hébergeur compatible avec Streamlit, par exemple Streamlit Community Cloud.
- La version en ligne peut être gratuite dans les limites de l'offre de l'hébergeur.
- Les voix système et FFmpeg ne sont pas toujours disponibles sur les hébergeurs gratuits. Le fonctionnement local reste donc le plus fiable pour exporter les vidéos.
- Cette V1 utilise des illustrations générées par code et un scénario à modèles, pas un modèle IA génératif distant. Les prochaines versions pourront ajouter des modèles locaux pour améliorer les histoires, les images et les voix sans imposer d'API payante.

### Limites connues de la V1
- Les visuels sont des cartes illustrées stylisées générées localement, pas encore de véritables dessins animés image par image.
- Le TTS hors ligne dépend des voix installées et la synchronisation narration/scènes reste approximative.
- Les exports sont en 1280×720, 24 images/seconde.
""")
