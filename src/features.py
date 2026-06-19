# src/features.py

import pandas as pd
import numpy as np


def build_run_features(
    df_runs: pd.DataFrame,
    df_stages: pd.DataFrame,
    df_rooms: pd.DataFrame,
    df_pstates: pd.DataFrame,
    df_inventory: pd.DataFrame,
    df_passive: pd.DataFrame,
    df_pactive: pd.DataFrame,
    df_ptrinket: pd.DataFrame,
    df_rmonster: pd.DataFrame,
    df_rboss: pd.DataFrame,
) -> pd.DataFrame:
    """
    Construit un DataFrame de features agrégées par run_id
    en exploitant l'ensemble des tables de la base de données.
    """
    features = []

    for _, run in df_runs.iterrows():
        run_id = run["id"]
        f = {"run_id": run_id}

        # ── Infos de base ──────────────────────────────────────────────
        f["victory"]    = int(run.get("Victory", 0) or 0)
        f["difficulty"] = run.get("Difficulty", 0) or 0
        f["character"]  = run.get("Character", 0) or 0
        duration        = run.get("Duration", 0) or 0
        f["duration"]   = duration

        # ── Stages ─────────────────────────────────────────────────────
        stages         = df_stages[df_stages["id_run"] == run_id]
        f["nb_stages"] = len(stages)
        f["nb_curses"] = stages["Curses"].fillna(0).astype(int).sum()

        # ── Rooms ──────────────────────────────────────────────────────
        rooms                   = df_rooms[df_rooms["id_run"] == run_id]
        f["nb_rooms"]           = len(rooms)
        f["nb_rooms_cleared"]   = rooms["Cleared"].fillna(False).astype(int).sum()
        f["clear_rate"]         = (
            f["nb_rooms_cleared"] / f["nb_rooms"] if f["nb_rooms"] > 0 else 0
        )
        f["avg_clear_duration"] = rooms["ClearDurationFrames"].fillna(0).mean()
        f["nb_room_types"]      = rooms["RoomType"].nunique()

        # ── Bosses rencontrés ──────────────────────────────────────────
        room_ids       = rooms["id"].tolist()
        bosses         = df_rboss[df_rboss["id_room"].isin(room_ids)]
        f["nb_bosses"] = len(bosses)

        # ── Monstres ───────────────────────────────────────────────────
        monsters          = df_rmonster[df_rmonster["id_room"].isin(room_ids)]
        f["nb_monsters"]  = len(monsters)
        f["avg_monster_hp"] = (
            monsters["MaxHp"].fillna(0).mean() if len(monsters) > 0 else 0
        )

        # ── PlayerState ────────────────────────────────────────────────
        pstates = df_pstates[df_pstates["id_run"] == run_id].sort_values("Frame")

        if len(pstates) > 0:
            last  = pstates.iloc[-1]
            first = pstates.iloc[0]

            f["final_damage"]     = last.get("Damage", 0) or 0
            f["final_fire_delay"] = last.get("FireDelay", 0) or 0
            f["final_shot_speed"] = last.get("ShotSpeed", 0) or 0
            f["final_tear_range"] = last.get("TearRange", 0) or 0
            f["final_move_speed"] = last.get("MoveSpeed", 0) or 0
            f["final_luck"]       = last.get("Luck", 0) or 0
            f["final_hearts"]     = (
                (last.get("Hearts", 0) or 0)
                + (last.get("SoulHearts", 0) or 0)
                + (last.get("BlackHearts", 0) or 0)
            )
            f["final_coins"]          = last.get("Coins", 0) or 0
            f["final_bombs"]          = last.get("Bombs", 0) or 0
            f["final_keys"]           = last.get("Keys", 0) or 0
            f["total_damage_taken"]   = pstates["DamageTaken"].fillna(0).max()

            # Deltas début → fin
            f["delta_damage"]     = f["final_damage"]     - (first.get("Damage", 0) or 0)
            f["delta_luck"]       = f["final_luck"]       - (first.get("Luck", 0) or 0)
            f["delta_move_speed"] = f["final_move_speed"] - (first.get("MoveSpeed", 0) or 0)

            # DPS proxy
            fd             = f["final_fire_delay"]
            f["dps_proxy"] = (
                f["final_damage"] / fd if fd and fd > 0 else f["final_damage"]
            )

        else:
            for col in [
                "final_damage", "final_fire_delay", "final_shot_speed",
                "final_tear_range", "final_move_speed", "final_luck",
                "final_hearts", "final_coins", "final_bombs", "final_keys",
                "total_damage_taken", "delta_damage", "delta_luck",
                "delta_move_speed", "dps_proxy",
            ]:
                f[col] = 0

        # ── Inventaire passif ──────────────────────────────────────────
        ps_ids = pstates["id"].tolist()
        inv    = df_inventory[df_inventory["id_playerstate"].isin(ps_ids)]

        if len(inv) > 0 and len(df_passive) > 0:
            inv_merged = inv.merge(
                df_passive[["id", "Quality"]],
                left_on="id_passiveitem", right_on="id", how="left"
            )
            f["nb_passive_items"]       = inv["id_passiveitem"].nunique()
            f["avg_passive_quality"]    = inv_merged["Quality"].fillna(0).mean()
            f["total_passive_quality"]  = inv_merged["Quality"].fillna(0).sum()
        else:
            f["nb_passive_items"]       = 0
            f["avg_passive_quality"]    = 0
            f["total_passive_quality"]  = 0

        # ── Items actifs ───────────────────────────────────────────────
        pact = df_pactive[df_pactive["id_playerstate"].isin(ps_ids)]

        if len(pact) > 0 and len(df_pactive) > 0:
            pact_merged = pact.merge(
                df_pactive[["id", "Quality"]] if "Quality" in df_pactive.columns
                else pd.DataFrame(columns=["id", "Quality"]),
                left_on="id_activeitem", right_on="id", how="left"
            )
            f["nb_active_items"]    = pact["id_activeitem"].nunique()
            f["avg_active_quality"] = pact_merged["Quality"].fillna(0).mean() if "Quality" in pact_merged.columns else 0
        else:
            f["nb_active_items"]    = 0
            f["avg_active_quality"] = 0

        # ── Trinkets ───────────────────────────────────────────────────
        ptri = df_ptrinket[df_ptrinket["id_playerstate"].isin(ps_ids)]

        if len(ptri) > 0 and len(df_ptrinket) > 0:
            ptri_merged = ptri.merge(
                df_ptrinket[["id", "Quality"]] if "Quality" in df_ptrinket.columns
                else pd.DataFrame(columns=["id", "Quality"]),
                left_on="id_trinket", right_on="id", how="left"
            )
            f["nb_trinkets"]         = ptri["id_trinket"].nunique()
            f["avg_trinket_quality"] = ptri_merged["Quality"].fillna(0).mean() if "Quality" in ptri_merged.columns else 0
        else:
            f["nb_trinkets"]         = 0
            f["avg_trinket_quality"] = 0

        # ── Efficacité temporelle ──────────────────────────────────────
        f["rooms_per_frame"] = (
            f["nb_rooms_cleared"] / duration if duration and duration > 0 else 0
        )

        features.append(f)

    return pd.DataFrame(features)
