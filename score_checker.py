def check_conditions(match: dict, user_config: dict) -> list[str]:
    results = []

    # Ambil skor terkini dari match["scores"]
    scores = match.get("scores", [])
    home_score = 0
    away_score = 0
    for s in scores:
        if s.get("description") == "CURRENT":
            if s["score"]["participant"] == "home":
                home_score = s["score"]["goals"]
            elif s["score"]["participant"] == "away":
                away_score = s["score"]["goals"]

    total_goals = home_score + away_score

    # Dummy data: nama tim & menit (jika ada)
    home = match.get("home_team_name", "Home")
    away = match.get("away_team_name", "Away")
    minute = int(match.get("minute", 0))  # nanti bisa ditambahkan dari include `state` kalau tersedia

    print(f"Checking: {home} vs {away} | Skor: {home_score}-{away_score} | Menit: {minute}")

    # 1. Total 5 gol
    if total_goals == 5 and user_config.get("notif_5goal"):
        results.append(f"⚽ Total 5 gol: {home} vs {away} → {home_score}-{away_score}")

    # 2. 4 gol di babak 1 — sementara belum tersedia half-time score di SportMonks
    half_home = match.get("home_half_score", 0)
    half_away = match.get("away_half_score", 0)
    if (half_home + half_away) == 4 and user_config.get("notif_4goal_half1"):
        results.append(f"⚽ 4 gol babak 1: {home} vs {away} → {half_home}-{half_away}")

    # 3. 0-0 di menit 60
    if home_score == 0 and away_score == 0 and 60 <= minute < 66 and user_config.get("notif_00_60min"):
        results.append(f"🕐 0-0 di menit {minute}: {home} vs {away}")
    elif home_score == 0 and away_score == 0 and 60 <= minute < 66:
        print(f"[DEBUG] Match 0-0 menit {minute}, tapi config notif_00_60min dimatikan.")

    # 4. Selisih 3 gol
    if abs(home_score - away_score) >= 3 and user_config.get("notif_diff3"):
        results.append(f"⚠️ Selisih 3 gol: {home} vs {away} → {home_score}-{away_score}")

    # 5. Skor 3-1 atau 1-3
    if (
        (home_score == 3 and away_score == 1) or
        (home_score == 1 and away_score == 3)
    ) and user_config.get("notif_3_1"):
        results.append(f"🔥 Skor 3-1 / 1-3: {home} vs {away} → {home_score}-{away_score}")

    return results
