# **Welcome to TitanScout**

This program is used for the most elite scouting for FRC.

Manny Machado - "There's too many stats." I agree so too but I prefer having more statistics and numbers.

## What is TitanScout?

TitanScout is a free, browser-based scouting tool for FIRST Robotics Competition (FRC) teams. It tracks where robots drive during matches, builds heatmaps, and pulls event data from The Blue Alliance to give per-team stats and match predictions.

It runs in any browser on a phone, tablet, or computer. There is no account or install, and your scouting data stays on your own device.

## Features

- **Scout:** Record a robot's start position and path during auto and teleop by tapping and dragging on a picture of the field. Matches are saved on the device. Field images are included for the 2022 to 2026 seasons.
- **Heatmap:** See where a team spends its time on the field. Filter by auto or teleop and replay any match at up to 4x speed.
- **Event bar:** Enter your TBA key once and pick an event by name, code, city, or state. Every tab then shows that one event.
- **Event rankings:** Live qualification standings for the selected event.
- **Team Stats:** OPR plus estimated per-team values for fuel counts, tower points, fouls, RP, and more. Sort and filter the table, choose your columns, and build bar or bubble charts from any stats.
- **Event Predictor:** Every match at the event with a projected score, a win-chance meter, and a confidence level, shown next to the real winner once the match is played.
- **Custom Predictor:** Enter any six teams and the app pulls their results for a chosen season from TBA to project a score and a winner. It does not need an event selected.
- **Statbotics (EPA):** EPA for the event's teams, read from data saved in this repo by a scheduled GitHub Action, with the live Statbotics API as a fallback.
- **Heatmap Import/Export:** Move scouted match data between devices as JSON.
- **Settings:** Light, dark, or system theme with an animated switch, and a language picker: English, Spanish, French, German, Italian, Japanese, Arabic, Portuguese, and Mandarin Chinese.

### How the stats work

TBA only publishes totals for each alliance, not for each robot. Per-team stats and predictions are therefore estimates from match results, using the same least-squares method as OPR. They become more reliable as more matches are played. The predictors show a confidence level, and it stays low until there is enough data.

## Setup

### 1. Get a TBA key

1. Create a free account at [thebluealliance.com/account](https://www.thebluealliance.com/account).
2. Create a read API key.
3. Paste it into the **TBA key** box at the top of the app and press **Save key**. It is stored only in your browser.

### 2. Run it

Open the GitHub Pages site for this repo, or open `index.html` in a browser.

### 3. Optional: Statbotics data (GitHub Action)

1. Add the event keys you want, one per line, to `data/events.txt` (for example `2026caasv`).
2. In the repo go to **Settings → Actions → General → Workflow permissions** and choose **Read and write permissions**.
3. Optional but recommended: add your TBA key as a repository secret named `TBA_KEY` under **Settings → Secrets and variables → Actions**.
4. Open the **Actions** tab, choose **Update Statbotics data**, and press **Run workflow**. After that it runs every 3 hours and whenever `data/events.txt` changes.

The Action saves one JSON file per event in `data/statbotics/`, and the app reads it from there.

## Repo layout

```
index.html                  the whole app
favicon.png
images/                     field images (field22.png to field26.png)
data/events.txt             events for the Statbotics Action
data/statbotics/            JSON saved by the Action
scripts/fetch_statbotics.py Python script the Action runs
.github/workflows/statbotics.yml
```

## Fixes and Features

### Future Updates:      
- Strategy Whiteboard
- Automated Heatmap tracking
- Define robot types in event tab. (Turret, Dumper, Telescope, With climber)
- Ability to upload data to a database to use later, so data no longer relies on the device that logged it
- Have a legitimate website instead of relying on GitHub Pages

### Bugs that are known or things in need of change
- Issues to pull data from Statbotics

## Credits

Created by MystiqueCanDoThings. Event data from [The Blue Alliance](https://www.thebluealliance.com) and [Statbotics](https://www.statbotics.io).
