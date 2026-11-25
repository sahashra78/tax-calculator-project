class TaxReport:
    def __init__(self, user, federal_tax=0.0, state_tax=0.0):
        self.__user = user
        self.__federal_tax = float(federal_tax)
        self.__state_tax = float(state_tax)

    def get_user(self):
        return self.__user

    def get_federal_tax(self):
        return self.__federal_tax

    def get_state_tax(self):
        return self.__state_tax

    def calculate_total_tax(self):
        return self.__federal_tax + self.__state_tax

    def calculate_net_income(self):
        income = self.__user.get_income()
        return income - self.calculate_total_tax()

    def display_summary(self):
        income = self.__user.get_income()
        state = self.__user.get_state()
        name = self.__user.get_name()
        total_tax = self.calculate_total_tax()
        net_income = self.calculate_net_income()

        print("\n--- Tax Summary Report ---")
        if name:
            print(f"Name: {name}")
        print(f"State: {state}")
        print(f"Annual / Taxable Income: ${income:,.2f}")
        print(f"Federal Tax:             ${self.__federal_tax:,.2f}")
        print(f"State Tax:               ${self.__state_tax:,.2f}")
        print(f"Total Tax:               ${total_tax:,.2f}")
        print(f"Net Income After Tax:    ${net_income:,.2f}")
        print("--------------------------")