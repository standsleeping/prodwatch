def get_user_input():
    user_input = input("Enter something: ")
    print(f"You entered: {user_input}")
    return user_input

if __name__ == "__main__":
    while True:
        get_user_input()