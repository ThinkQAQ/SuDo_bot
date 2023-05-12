import json


class BankSys:
    @staticmethod
    def open_account(user):
        users = BankSys.get_bank_data()
        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["wallet"] = 0
            users[str(user.id)]["bank"] = 0
            users[str(user.id)]["bag"] = []

        with open("json/bank.json", "w") as f:
            json.dump(users, f, indent=4)
        return True

    @staticmethod
    def get_bank_data():
        with open("json/bank.json", "r") as f:
            users = json.load(f)
        return users

    @staticmethod
    def get_user_bank_data(user):
        users = BankSys.get_bank_data()
        return users[str(user.id)]

    @staticmethod
    def update_bank(user, change=0, mode="wallet"):
        users = BankSys.get_bank_data()
        users[str(user.id)][mode] += change

        with open("json/bank.json", "w") as f:
            json.dump(users, f, indent=4)

        money = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
        return money
