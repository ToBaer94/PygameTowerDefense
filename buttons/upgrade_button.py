from button import Button


class UpgradeButton(Button):
    def __init__(self, image, x, y, parent, upgrade_function):
        super(UpgradeButton, self).__init__(image, x, y, parent)
        self.upgrade_function = upgrade_function

    def get_clicked(self):
        self.upgrade_function()