def sort_seasons(data, season_order) -> dict:
    """
    data["seasons"]를 season_order 순서대로 정렬한 새 dict를 반환합니다.
    season_order에 없는 시즌은 원래 순서대로 뒤에 붙습니다.
    """
    seasons = data.get("seasons", {})

    # 지정한 순서대로 먼저 배치
    sorted_seasons = {
        season: seasons[season]
        for season in season_order
        if season in seasons
    }

    # 리스트에 없는 나머지 시즌은 기존 순서 유지하며 뒤에 추가
    for season, value in seasons.items():
        if season not in sorted_seasons:
            sorted_seasons[season] = value

    # 원본 보존용 새 dict 생성
    #new_data = data.copy()
    data["seasons"] = sorted_seasons
    return data