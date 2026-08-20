A 5-stage mental wellness game where you grow a plant by improving your mood, focus, and social confidence — one day at a time.

🚀 Setup Instructions
1. Install Python dependencies
bashcd backend
pip install -r requirements.txt
2. Start the Flask server
bashpython app.py
The server will start at http://localhost:5000
The database file (mindsprout.db) is created automatically inside the database/ folder on first run.
3. Open the game
Open frontend/index.html in your browser.

Tip: Use VS Code Live Server or any local HTTP server for best results.


🎮 Game Stages
StageNamePlant Growth1Mood Check🌰 Seed planted2Emotion Puzzle🌱 Sapling sprouts3Social Confidence🌿 Baby plant grows4Focus Training🌳 Full grown plant5Rewards & Bloom🌸 Flower blooms

🔌 API Endpoints
MethodEndpointDescriptionGET/api/healthServer health checkGET/api/user/<device_id>Get or create userPOST/api/session/startStart today's sessionPOST/api/session/progressUpdate stage progressGET/api/streak/<device_id>Get streak infoPOST/api/streak/updateUpdate streak on completionGET/api/badges/<device_id>Get all earned badgesPOST/api/badges/awardAward a badge

🏆 Badges
BadgeIconEarned ByCalm Mind🌿 
Completing Stage 2Brave Speaker
🗣️Completing Stage 3Focus Master
🎯Completing Stage 4Growth Star
✨Completing all 5 stagesFirst Bloom
🌸First ever completion7-Day Streak
🔥7 days in a row30-Day Streak
💎30 days in a row

🎵 Audio
Background music is generated dynamically using the Web Audio API — no external files needed. Each mood has its own ambient soundscape:

😡 Angry → Deep grounding bass tones
😢 Sad → Soft melancholic frequencies
😰 Anxious → Calming sine waves (396Hz, 528Hz)
😴 Tired → Gentle energizing tones
😊 Happy → Bright upbeat frequencies
😌 Calm → Soft ambient tones


📝 Notes

One session per device per day (enforced by backend + localStorage device ID)
No login required — device ID is stored in browser localStorage
SQLite database resets only if you delete database/mindsprout.db
CORS is enabled for all origins in development — restrict in production
