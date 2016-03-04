from button import Button


class ArrowButton(Button):
    def __init__(self, image, x, y, parent, function):
        super(ArrowButton, self).__init__(image, x, y, parent)

        self.function = function

    def get_clicked(self):
        print "activated"
        self.function()