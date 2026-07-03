# config/scoring_config.py

SCORING_CONFIG = {
    # Performance générale
    # Le statut de victoire n'est pas pris en compte dans le scoring.
    "nb_stages":            {"weight": 25.0,  "direction": +1},
    "clear_rate":           {"weight": 6.0,  "direction": +1},

    # Combat & stats
    "dps_proxy":            {"weight": 8.0,  "direction": +1},
    "final_damage":         {"weight": 5.0,  "direction": +1},
    "final_move_speed":     {"weight": 3.0,  "direction": +1},
    "final_luck":           {"weight": 3.0,  "direction": +1},
    "final_tear_range":     {"weight": 2.0,  "direction": +1},
    "final_shot_speed":     {"weight": 2.0,  "direction": +1},
    "delta_damage":         {"weight": 4.0,  "direction": +1},
    "delta_luck":           {"weight": 2.0,  "direction": +1},

    # Survie
    "final_hearts":         {"weight": 5.0,  "direction": +1},
    "total_damage_taken":   {"weight": 8.0,  "direction": -1},

    # Inventaire
    "nb_passive_items":     {"weight": 4.0,  "direction": +1},
    "avg_passive_quality":  {"weight": 5.0,  "direction": +1},
    "total_passive_quality":{"weight": 3.0,  "direction": +1},
    "nb_active_items":      {"weight": 2.0,  "direction": +1},
    "avg_active_quality":   {"weight": 2.0,  "direction": +1},
    "avg_trinket_quality":  {"weight": 1.0,  "direction": +1},

    # Ressources finales
    "final_coins":          {"weight": 1.5,  "direction": +1},
    "final_bombs":          {"weight": 1.0,  "direction": +1},
    "final_keys":           {"weight": 1.0,  "direction": +1},

    # Efficacité
    "rooms_per_frame":      {"weight": 4.0,  "direction": +1},
    "nb_curses":            {"weight": 3.0,  "direction": -1},
    "nb_bosses":            {"weight": 2.0,  "direction": +1},
}
