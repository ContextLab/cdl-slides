---
marp: true
theme: cdl-theme
---

# Manim Animation Test

```manim
# scene: SimpleAnimation
# height: 400

class SimpleAnimation(Scene):
    def construct(self):
        text = Text("Hello Manim!")
        self.play(Write(text))
        self.wait()
```
