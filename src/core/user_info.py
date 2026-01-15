import os
from core.tasks import load_data, save_data,get_tasks_file_path

USER_INFO_FILE_PATH = get_tasks_file_path("user_info.json")

def user_goal_check(user_info_path=USER_INFO_FILE_PATH):
        if os.path.exists(user_info_path):
            user_goal_data = load_data(user_info_path)
            if user_goal_data is None or "goal" not in user_goal_data or not user_goal_data["goal"]:
                print("ERROR: User goal string is empty")
                goal_list=[]
                while True:
                    user_goal = input("Please enter your goal keywords, Example: reading cooking writing\n(type q to quit) :\n")
                    if user_goal == "q":
                        break
                    goal_list.append(user_goal)
                save_data(user_info_path,{"goal":goal_list})
                print(f"User goal saved to user_info.json")
                return goal_list

            return user_goal_data["goal"]
        print("ERROR: user_ info.json not found")
        return None