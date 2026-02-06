---
marp: true
theme: cdl-theme
---

# Multi-Animation Test

```animate
height: 500
quality: high

write equation "E = mc^2" as eq1 at center
wait 0.5
write equation "\\frac{1}{2}mv^2" as eq2 below eq1
wait 0.3
transform eq1 -> eq2
fade-in eq2
```
