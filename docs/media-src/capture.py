#!/usr/bin/env python3
"""
Record the animations as video: docs/media/fold.mp4, records.mp4 and a GIF of each.

    ./capture.py [fold] [records]

Serves docs/ on a local port, opens capture.html in headless Chrome, and takes each frame as
it is posted. Frames are positions, not a screen recording, so the video runs at the
animation's own pace whatever this machine managed. Needs Chrome and ffmpeg.
"""
import http.server, pathlib, shutil, subprocess, sys, tempfile, threading, time

HERE = pathlib.Path(__file__).resolve().parent
DOCS = HERE.parent
FRAMES = HERE / "local" / "frames"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 8743
done = {}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(DOCS), **k)
    def log_message(self, *a): pass
    def do_POST(self):
        _, kind, scene, n = self.path.split("/")
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if kind == "frame":
            (FRAMES / scene / f"{n}.png").write_bytes(body)
        else:
            done[scene] = int(n)
        self.send_response(204); self.end_headers()


def record(scene):
    d = FRAMES / scene
    shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as profile:
        p = subprocess.Popen([CHROME, "--headless=new", "--use-gl=angle", "--use-angle=swiftshader",
                              "--enable-unsafe-swiftshader", "--no-sandbox", f"--user-data-dir={profile}",
                              "--window-size=1920,1080", "--remote-debugging-port=0",
                              f"http://127.0.0.1:{PORT}/media-src/capture.html?scene={scene}"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0, last = time.time(), 0
        while scene not in done and time.time() - t0 < 1500:
            time.sleep(5)
            n = len(list(d.glob("*.png")))
            if n != last: last = n
            elif n == 0 and time.time() - t0 > 90: break
        p.kill(); p.wait()
    n = len(list(d.glob("*.png")))
    if done.get(scene) != n or not n:
        sys.exit(f"{scene}: {n} frames saved, {done.get(scene)} expected")
    out = DOCS / "media"
    ff = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", str(d / "%05d.png")]
    subprocess.run(ff + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow",
                         "-movflags", "+faststart", str(out / f"{scene}.mp4")], check=True)
    subprocess.run(ff + ["-vf", "fps=30,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160[p];"
                                "[b][p]paletteuse=dither=bayer:bayer_scale=4", str(out / f"{scene}.gif")], check=True)
    print(f"{scene}: {n} frames, {n / 60:.1f}s ->", (out / f"{scene}.mp4").relative_to(DOCS.parent),
          f"{(out / f'{scene}.mp4').stat().st_size // 1024}k,", f"gif {(out / f'{scene}.gif').stat().st_size // 1024}k")


srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
for s in (sys.argv[1:] or ["fold", "records"]):
    record(s)
srv.shutdown()
