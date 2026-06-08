"""
Pull shot chart data for Knicks & Spurs in the 2026 playoffs via nba_api.
Writes seeds/raw_shot_chart.csv if successful.
Falls back gracefully and reports what failed.
"""
import time
import sys
import pandas as pd
from nba_api.stats.endpoints import shotchartdetail, leaguegamefinder
from nba_api.stats.static import teams

# ── Team IDs ──────────────────────────────────────────────────────────────────
all_teams = teams.get_teams()
KNICKS_ID = next(t["id"] for t in all_teams if t["abbreviation"] == "NYK")
SPURS_ID  = next(t["id"] for t in all_teams if t["abbreviation"] == "SAS")
print(f"Knicks ID: {KNICKS_ID}  |  Spurs ID: {SPURS_ID}")

SEASON     = "2025-26"
SEASON_TYPE = "Playoffs"
OUT_PATH   = "seeds/raw_shot_chart.csv"

def pull_team_shots(team_id, team_name, delay=2):
    """Pull all playoff shots for a team. Returns DataFrame or None."""
    print(f"\n→ Pulling shots for {team_name}...")
    try:
        sc = shotchartdetail.ShotChartDetail(
            team_id=team_id,
            player_id=0,            # 0 = all players on the team
            season_nullable=SEASON,
            season_type_all_star=SEASON_TYPE,
            context_measure_simple="FGA",
            timeout=30,
        )
        df = sc.get_data_frames()[0]
        print(f"   ✓ {len(df)} shots returned")
        return df
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return None

# ── Pull both teams ────────────────────────────────────────────────────────────
knicks_shots = pull_team_shots(KNICKS_ID, "Knicks")
time.sleep(2)   # be polite to the API
spurs_shots  = pull_team_shots(SPURS_ID,  "Spurs")

frames = [df for df in [knicks_shots, spurs_shots] if df is not None]

if not frames:
    print("\n✗ Both pulls failed — no data to write.")
    sys.exit(1)

combined = pd.concat(frames, ignore_index=True)

# ── Keep only useful columns ───────────────────────────────────────────────────
keep = [
    "GAME_ID", "GAME_DATE", "TEAM_NAME", "PLAYER_NAME", "PERIOD",
    "MINUTES_REMAINING", "SECONDS_REMAINING",
    "ACTION_TYPE", "SHOT_TYPE", "SHOT_ZONE_BASIC", "SHOT_ZONE_AREA",
    "SHOT_ZONE_RANGE", "SHOT_DISTANCE",
    "LOC_X", "LOC_Y",
    "SHOT_ATTEMPTED_FLAG", "SHOT_MADE_FLAG",
    "HTM", "VTM",
]
keep = [c for c in keep if c in combined.columns]
combined = combined[keep].copy()

# Normalise column names to lowercase for dbt
combined.columns = [c.lower() for c in combined.columns]

combined.to_csv(OUT_PATH, index=False)
print(f"\n✓ Wrote {len(combined)} rows → {OUT_PATH}")
print(combined.head(3).to_string())
