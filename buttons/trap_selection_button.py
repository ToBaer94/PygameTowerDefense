from button import Button


class TrapButton(Button):
    def __init__(self, image, x, y, parent, trap):
        super(TrapButton, self).__init__(image, x, y, parent)
        self.trap = trap

    def get_clicked(self):
        print self.trap
        self.parent.selected_trap = self.trap
