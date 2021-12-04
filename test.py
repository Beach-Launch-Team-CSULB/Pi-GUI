class Test:
    # This holds the Vent and Abort Buttons and the Logos of the groups involved
    # Takes in as arguments the Main Frame and the Left Frame
    # The Left Frame is needed because the Vent and Abort states will need to de-enable the other states

    # Data needed to setup the button for each State
    # [ State Name, X coordinate]
    bottomButtons = [
        ["Vent", 0, 1, 20, 21],
        ["Abort", 3 / 4, 1, 22, 23]
    ]

    def __init__(self, parent):
        print("hello")
    
    def run():
        print("hello")

Test.run()