# MoviePy clip metadata notes

`VideoFileClip` exposes width, height, duration, fps, and an optional `audio` track.
`AudioFileClip` exposes duration and audio fps.
This task only requires inspection; no rendering or writing is needed.
Use MoviePy classes directly rather than shelling out to ffmpeg.
