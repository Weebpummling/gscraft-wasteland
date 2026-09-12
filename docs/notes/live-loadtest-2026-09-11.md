# Live load test, 2026-09-11

- live load test 2026-09-11 19:11
- idle with the platform loaded: 1.575 ms per tick
- director bench: bench: 20 passes for 1 present: 0.420 ms mean, 0.015 min, 4.903 max per pass; creatures 1 -> 7
- 24 idle fighters (no enemy): 24 fighters placed; samples (s, ms per tick, alive) [(16, 2.265, 24), (31, 2.242, 24)]; worst 2.265 ms
- 24 v 24 firefight: 48 fighters placed; samples (s, ms per tick, alive) [(22, 3.953, 47), (43, 3.979, 47), (65, 3.758, 47)]; worst 3.979 ms
- 48 v 48 firefight: 96 fighters placed; samples (s, ms per tick, alive) [(22, 5.992, 94), (43, 5.116, 94), (65, 5.165, 94)]; worst 5.992 ms
- cleanup: fighters left in the area 0; platform removed; forceload removed; director running
- after cleanup: 1.109 ms per tick
