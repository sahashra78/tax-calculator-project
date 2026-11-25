class User:
    def __init__(self, name="", annual_income=0.0, state=""):
        self.__name = ""
        self.__annual_income = 0.0
        self.__state = ""
        self.set_name(name)
        self.set_income(annual_income)
        self.set_state(state)

    def get_name(self):
        return self.__name

    def set_name(self, name):
        if isinstance(name, str):
            self.__name = name.strip()

    def get_income(self):
        return self.__annual_income

    def set_income(self, amount):
        if isinstance(amount, (int, float)) and amount >= 0:
            self.__annual_income = float(amount)
            return True
        return False

    def get_state(self):
        return self.__state

    def set_state(self, state):
        supported_states = {"PA", "PENNSYLVANIA", "FL", "FLORIDA"}
        if isinstance(state, str):
            cleaned = state.strip().upper()
            if cleaned in supported_states:
                if cleaned in {"PA", "PENNSYLVANIA"}:
                    self.__state = "PA"
                else:
                    self.__state = "FL"
                return True
        return False