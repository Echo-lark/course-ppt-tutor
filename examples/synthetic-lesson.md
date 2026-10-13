# Synthetic two-page teaching demonstration

This example was written for this repository. It shows the **kind of explanation** the skill aims for; it is not a fixed page-length requirement. A real lesson must be checked against the learner's actual rendered slides.

## Imaginary source slides

**Slide 1 — Average speed.** A graph has time `t` (seconds) on the horizontal axis and distance `s` (meters) on the vertical axis. A straight line runs from `(0 s, 0 m)` to `(20 s, 120 m)`. The slide states `v = Δs / Δt`.

**Slide 2 — Example and conversion.** “A cyclist travels 120 m in 20 s. Find the average speed in m/s and km/h.” The slide shows `120 / 20 = 6 m/s` and `6 × 3.6 = 21.6 km/h` without explaining the conversion.

## Example explanation in one Markdown document

### Page 1 · What the distance–time graph actually tells us

Before using the formula, distinguish **distance** from **time**. Distance `s` tells us how far the cyclist has traveled; its unit here is meters (`m`). Time `t` tells us how long the trip has taken; its unit is seconds (`s`). Average speed asks: over the chosen interval, how much distance was covered **per unit of time**?

The graph's horizontal axis is time, so moving right means a later moment. Its vertical axis is accumulated distance, so moving up means more ground covered. The line starts at `(0 s, 0 m)` and reaches `(20 s, 120 m)`. We therefore know both the change in distance and the change in time:

```text
Δs = 120 m − 0 m = 120 m
Δt = 20 s − 0 s = 20 s
```

The symbol `Δ` means “change in.” The fraction `Δs / Δt` divides the distance gained by the time used. Here it gives `120 m / 20 s = 6 m/s`: on average, the cyclist covers 6 meters each second. The straight line has a constant slope, so this particular graph also depicts constant speed. For a curved graph, the same two-endpoint calculation would give the **average over the interval**, not the speed at every instant.

Why does the graph's slope equal speed? Slope is vertical change divided by horizontal change. On this graph, vertical change is `Δs` and horizontal change is `Δt`; hence the slope is exactly `Δs / Δt`. The unit check agrees: meters divided by seconds gives meters per second. A horizontal line would have `Δs = 0`, so its slope and speed would both be zero.

### Page 2 · Calculate the speed and explain the conversion

The previous page established `v = Δs / Δt`. The example gives `Δs = 120 m` and `Δt = 20 s`, so substitute those values **with their units**:

```text
v = Δs / Δt
  = 120 m / 20 s
  = 6 m/s
```

The slide also states `6 × 3.6 = 21.6 km/h`. Where does `3.6` come from? One kilometer is `1000 m`, and one hour is `3600 s`. Convert both the numerator and denominator without changing the speed itself:

```text
6 m/s × (1 km / 1000 m) × (3600 s / 1 h)
= 6 × (3600 / 1000) km/h
= 6 × 3.6 km/h
= 21.6 km/h
```

The `m` and `s` units cancel in the first line, leaving `km/h`. This explains the conversion factor rather than asking you to memorize it. As a reasonableness check, `21.6 km/h` is greater than `6 m/s` as a **number** because an hour contains many seconds; they still describe the same physical speed in different units. The answer depends on the slide's assumption that the stated distance and time refer to the same trip interval.
