import os
from core.tasks import load_data, save_data, get_tasks_file_path

USER_INFO_FILE_PATH = get_tasks_file_path("user_info.json")


def user_goal_check(user_info_path=USER_INFO_FILE_PATH):
    user_goal_data = {"goal": []}

    if os.path.exists(user_info_path):
        loaded_data = load_data(user_info_path)
        if loaded_data is not None:
            user_goal_data = loaded_data
    if not user_goal_data.get("goal"):
        print("User goals should not be empty")
        goal_list = []
        while True:
            user_goal = input("Please enter your goal keywords, Example: reading cooking writing\n(type q to quit) :\n")
            if user_goal == "q":
                break
            goal_list.append(user_goal)
        user_goal_data["goal"] = goal_list
        save_data(user_info_path, user_goal_data)
        print(f"User goal saved to user_info.json")
        return goal_list

    return user_goal_data["goal"]


def user_edit_goal(user_info_path=USER_INFO_FILE_PATH):
    user_goal_data = user_goal_check(user_info_path)
    print(f"Your current goal information is : {user_goal_data}")
    while True:
        goal_operation = input("Enter(d to delete,a to add a goal keyword,q to quit to main menu)\n:")
        if goal_operation == "d":
            del_input = input("Enter the keyword that you would like to delete \n:")
            if del_input in user_goal_data:
                user_goal_data.remove(del_input)
                print(f"Successfully deleted '{del_input}'. New list is: {user_goal_data}")
            else:
                print(f"ERROR: '{del_input}' is not found in the current goal list.")
        elif goal_operation == "a":
            add_input = input("Enter the keyword that you would like to add\n:")
            if add_input in user_goal_data:
                print(f"{add_input} keyword already exists in user_info.json")
            else:
                user_goal_data.append(add_input)
                print(f"User goal keyword added to user_info.json : \nNew list is {user_goal_data}")
        elif goal_operation == "q":
            break
        else:
            print("Invalid input. Please try again.")
    save_data(user_info_path, {"goal": user_goal_data})