# config.py
from pathlib import Path
from dataclasses import dataclass

# ── general ──────────────────────────────────────────────────────────
WINDOW_TITLE      = "Miscrits"
BASE_DIR          = Path(__file__).resolve().parent
SCREEN_REGION     = (0, 0, 2880, 1800)   # left, top, width, height
LOOP_ITERATIONS   = 2000
OCR_LANGUAGES     = ["en"]

# ── capture strat ──────────────────────────────────────────────────────────
CAPTURE_STRAT = 1

# ── template folders -------------------------------------------------
TEMPLATE_DIR      = BASE_DIR / "Elements"
TEMPLATES = {
    # buttons / UI
    "account_button":            TEMPLATE_DIR / "AccountButton",
    "capture_button":            TEMPLATE_DIR / "CaptureButton",
    "close_button":              TEMPLATE_DIR / "CloseButton",
    "continue_button":           TEMPLATE_DIR / "ContinueButton",
    "heal_now_button":           TEMPLATE_DIR / "HealNowButton",
    "keep_button":               TEMPLATE_DIR / "KeepButton",
    "next_menu_page":            TEMPLATE_DIR / "NextMenuPage",
    "okay_button":               TEMPLATE_DIR / "OkayButton",
    "prev_menu_page":            TEMPLATE_DIR / "PrevMenuPage",
    "release_button":            TEMPLATE_DIR / "ReleaseButton",
    "retry_button":              TEMPLATE_DIR / "RetryButton",
    "train_button":              TEMPLATE_DIR / "TrainButton",
    "train_now_button":          TEMPLATE_DIR / "TrainNowButton",
    "yes_button":                TEMPLATE_DIR / "YesButton",
    "ready_to_train":            TEMPLATE_DIR / "ReadyToTrain",

    # status / notifications
    "ready_to_train":            TEMPLATE_DIR / "ReadyToTrain",
    "rankup":                    TEMPLATE_DIR / "Rankup",
    "quest_completion":          TEMPLATE_DIR / "QuestCompletion",
    "evolve_diag":               TEMPLATE_DIR / "EvolveDiag",
    "enchant_ability":           TEMPLATE_DIR / "EnchantAbility",
    "gold_to_enchant_ability":   TEMPLATE_DIR / "GoldToEnchantAbility",

    # environment targets
    "all_season_bush":           TEMPLATE_DIR / "AllSeasonBush",
    "big_pond_sunfall_shore":    TEMPLATE_DIR / "BigPondSunfallShore",
    "blighted_bush":             TEMPLATE_DIR / "BlightedBush",
    "blighted_flower":           TEMPLATE_DIR / "BlightedFlower",
    "bluebobs":                  TEMPLATE_DIR / "bluebobs",
    "coal_pile":                 TEMPLATE_DIR / "CoalPile",
    "dark_magic_flower":         TEMPLATE_DIR / "DarkMagicFlower",
    "football":                  TEMPLATE_DIR / "FootBall",
    "golden_gem":                TEMPLATE_DIR / "GoldenGem",
    "green_puddle":              TEMPLATE_DIR / "GreenPuddle",
    "icy_crate":                 TEMPLATE_DIR / "IcyCrate",
    "icy_rock_shore":            TEMPLATE_DIR / "IcyRockShore",
    "lightning_bones":           TEMPLATE_DIR / "LightningBones",
    "masks_cave":                TEMPLATE_DIR / "MasksCave",
    "pink_shell":                TEMPLATE_DIR / "PinkShell",
    "red_palm_tree_beach":       TEMPLATE_DIR / "RedPalmTreeBeach",
    "sand_castle":               TEMPLATE_DIR / "SandCastle",
    "stat_bonus":                TEMPLATE_DIR / "StatBonus",
    "stats_list":                TEMPLATE_DIR / "StatsList",
    "white_cloth_attic":         TEMPLATE_DIR / "WhiteClothAttic",
}

# ── image-matching thresholds (cv2.matchTemplate) ────────────────────
MATCH_THRESHOLD   = 0.80

# ── timed delays (seconds) ───────────────────────────────────────────
CLICK_HOLD        = 0.25
DELAY_AT_END_OF_LOOP = 2
DELAY_AFTER_ATTACK = 5
DELAY_AFTER_HEAL   = 3
# …

# ── click coordinates *relative to the window’s* top-left corner ────
@dataclass(frozen=True)
class ClickPoint:
    x: int
    y: int


ATTACK_BUTTONS = {
    1: ClickPoint(680, 1665),
    2: ClickPoint(1196,1665),
    3: ClickPoint(1721,1665),
    4: ClickPoint(2251,1665),
}



# ── anything else that was hard-coded… ───────────────────────────────
