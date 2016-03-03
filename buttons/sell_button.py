from button import Button


class SellButton(Button):
    def __init__(self, image, x, y, parent):
        super(SellButton, self).__init__(image, x, y, parent)

    def get_clicked(self):
        self.parent.sell_tower()