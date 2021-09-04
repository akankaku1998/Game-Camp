from turtle import Turtle

class Score(Turtle):

    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.score_l = 0
        self.score_r = 0
        self.update_score()

    def update_score(self):
        self.clear()
        self.goto(-80, 250)
        self.write(self.score_l, align="center", font=("Arial", 30, "normal"))
        self.goto(80, 250)
        self.write(self.score_r, align="center", font=("Arial", 30, "normal"))

    def point_l(self):
        self.score_l += 1

    def point_r(self):
        self.score_r += 1
