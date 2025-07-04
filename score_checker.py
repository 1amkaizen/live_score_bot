def check_conditions(match: dict, user_config: dict) -> list[str]:
    results = []

    home = match["homeName"]
    away = match["awayName"]
    home_score = match["homeScore"]
    away_score = match["awayScore"]
    total_goals = home_score + away_score
    half_home = match["homeHalfScore"]
    half_away = match["awayHalfScore"]
    minute = match.get("extraExplain", {}).get("minute", 0)

    info = f"Checking: {home} vs {away} | Skor: {home_score}-{away_score} | Menit: {minute}"
    print(info)

    # 1. Total 5 gol
    if total_goals == 5 and user_config.get("notif_5goal"):
        results.append(f"⚽ Total 5 gol: {home} vs {away} → {home_score}-{away_score}")

    # 2. 4 gol di babak 1
    if (half_home + half_away) == 4 and user_config.get("notif_4goal_half1"):
        results.append(f"⚽ 4 gol babak 1: {home} vs {away} → {half_home}-{half_away}")

    # 3. 0-0 menit 60
    if home_score == 0 and away_score == 0 and minute >= 60 and user_config.get("notif_00_60min"):
        results.append(f"🕐 0-0 di menit {minute}: {home} vs {away}")

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
