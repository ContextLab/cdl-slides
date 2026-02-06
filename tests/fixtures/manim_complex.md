---
marp: true
theme: cdl-theme
---

# Manim Math Animation

```manim
# scene: MathAnimation
# height: 500
# quality: m

class MathAnimation(Scene):
    def construct(self):
        eq1 = MathTex(r"E = mc^2")
        eq2 = MathTex(r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}")

        self.play(Write(eq1))
        self.wait(0.5)
        self.play(Transform(eq1, eq2))
        self.wait()
```

---

# Multiple Animations

```manim
# scene: CircleSquare
# height: 400

class CircleSquare(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        square = Square(color=RED)

        self.play(Create(circle))
        self.play(Transform(circle, square))
        self.wait()
```
