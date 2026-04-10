# 🎬 AI Movie Script Generator

## Sirf 4 Steps mein chalu karo:

### Step 1 — Setup karo (sirf pehli baar)
`setup.bat` pe **double-click** karo
- Automatically saare packages install ho jayenge

### Step 2 — API Key daalo
`.env` file kholo aur apni OpenAI key daalo:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```
Key yahan se lo: https://platform.openai.com/api-keys

### Step 3 — Apne scripts daalo
`scripts_data/` folder mein apni movie scripts daalo (.txt ya .pdf)
(2 sample scripts pehle se hain test ke liye)

### Step 4 — Run karo!
1. `1_ingest.bat` pe double-click karo → Scripts vector DB mein jayengi
2. `2_generate.bat` pe double-click karo → Apni movie ka details daalo → Script ready!

---

## Folder Structure
```
ai_movie_script_generator/
├── setup.bat              ← Pehle yeh chalao (packages install)
├── 1_ingest.bat           ← Scripts ko DB mein daalo
├── 2_generate.bat         ← Naya script generate karo
├── script_generator.py    ← Main code
├── requirements.txt       ← Dependencies
├── .env                   ← Apni OpenAI API key yahan daalo
├── scripts_data/          ← Apni scripts yahan daalo (.txt / .pdf)
│   ├── sample_thriller.txt
│   └── sample_drama.txt
├── chroma_db/             ← Auto-banta hai ingest ke baad
└── output/                ← Generated screenplays yahan save honge
```

---

## Tips
- Jitni zyada scripts daalo, utna better output
- Same genre ki scripts daalo best results ke liye
- Output folder mein .txt file milegi generated script ki
