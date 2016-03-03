from button import Button


class TowerButton(Button):
    def __init__(self, image, x, y, parent, tower):
        super(TowerButton, self).__init__(image, x, y, parent)

        self.tower = tower

    def get_clicked(self):
        print self.tower
        self.parent.selected_tower = self.tower
