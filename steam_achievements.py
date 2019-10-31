import requests
from pprint import pprint

STEAM_KEY = "D137328A565EE900F5AA6C872240D609"
USER_ID = "76561198071507067"
STEAM_HEADER = "http://api.steampowered.com/"
OWNED_GAMES = "IPlayerService/GetOwnedGames/v0001/"
FRIENDSLIST = "ISteamUser/GetFriendList/v0001/"
ACHIEVEMENTS = "ISteamUserStats/GetPlayerAchievements/v0001/"

def get_owned_games_url(steam_id):
    return create_url(OWNED_GAMES, steam_id, format='json')

def get_achievements_for_game_url(steam_id, game_id):
    return create_url(ACHIEVEMENTS, steam_id, format='json', appid=game_id)

def create_url(header, steam_id, **querydict):
    return f"{STEAM_HEADER}{header}?key={STEAM_KEY}&steamid={steam_id}&{'&'.join(['='.join(item) for item in querydict.items()])}"

def main():
    print("Steam id? ")
    steam_id = input()
    # steam_id = USER_ID
    games_res = requests.get(get_owned_games_url(steam_id))
    games = games_res.json()['response']['games']
    achievements = {}
    game_names = {}
    for game in games:
        app_id = game['appid']
        res = requests.get(create_url("ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/", steam_id, format='json', gameid=str(app_id)))
        achievement_percentage = {info_dict['name']: info_dict['percent']
            for info_dict in res.json()['achievementpercentages']['achievements']}
        achievements[app_id] = (achievement_percentage, [])
        store_res = requests.get(f"https://store.steampowered.com/api/appdetails?appids={app_id}")
        try:
            game_names[app_id] = store_res.json()[str(app_id)]['data']['name']
            print(store_res.json()[str(app_id)]['data']['name'])
        except:
            print(store_res.text)
        achievements_res = requests.get(get_achievements_for_game_url(steam_id, str(app_id)))
        achievements_dict = achievements_res.json()
        if 'achievements' in achievements_dict["playerstats"]:
            for achievement in achievements_dict["playerstats"]['achievements']:
                if achievement['achieved'] == 1:
                    print(achievement)
                    achievements[app_id][1].append(achievement)
        else:
            pprint(achievements_dict)
    
    pprint(achievements)

    result_list = []

    for app_id, (achievement_percentages, achievements) in achievements.items():
        for achievement in achievements:
            result_list.append((achievement_percentages[achievement['apiname']], achievement['apiname'], game_names[app_id]))
    sorted_list = sorted(result_list)
    pprint(sorted_list)
    with open('out', 'w') as file_out:
        file_out.write(str(sorted_list))

if __name__ == '__main__':
    main()