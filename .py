import argparse
import time


def gen(delay, audio, video, timestamp):
    u = int(timestamp if timestamp is not None else time.time() + delay)
    d = 666
    c = [
        [59],
        [1, 10, 24, 28, 37, 40, 48],
        [9, 13, 21, 31, 46, 53, 57],
        [14, 18, 23, 29, 56],
        [4, 11, 16, 30, 34, 42, 47, 55],
        [7, 17, 20, 33, 38, 58],
        [12, 22, 27, 41, 44, 51],
        [2, 6, 15, 36, 43, 52],
        [0, 3, 8, 26, 32, 35, 49],
        [5, 19, 25, 39, 45, 50, 54],
    ]
    s_h = [(v + u // 3600 + 1) % 24 for v in range(24)]
    s_m0X = [(v + u // 60) % 60 for v in range(60)]
    s_mX0 = [(v + u // 600) % 6 for v in range(6)]
    g_mmX = ";".join(f"amovie=minute_{v}0.wav,aloop=10:44100*60[mm{v}]" for v in s_mX0)
    g_hX = ";".join(f"amovie=hour_{v:02d}.wav,aloop=60:44100*60[h{v:02d}]" for v in s_h)
    g_s600 = f"amovie=cycle_s600.wav,aloop=-1:44100*600,atrim={u%600}[s600]"
    g_s60 = f"amovie=cycle_s60.wav,aloop=-1:44100*60,atrim={u%60}[s60]"
    g_mX = ";".join(
        f"amovie=cycle_s60_{i:02d}.wav,asplit={len(v)}"
        + "".join(f"[m{n:02d}]" for n in v)
        for i, v in enumerate(c)
    )
    g_m = f"{''.join(f'[mm{v}]'for v in s_mX0)}concat=v=0:a=1:n=6,aloop=-1:44100*60*60,atrim={u%600}[m]"
    g_hh = f"{''.join(f'[m{v:02d}]'for v in s_m0X)}concat=v=0:a=1:n=60,aloop=-1:44100*60*60,atrim={u%60}[hh]"
    g_hb = f"amovie=hour_{u//3600%24:02d}.wav,aloop={60-u//60%60}:44100*60,atrim={u%60}[hb]"
    g_dX = f"{''.join(f'[h{v:02d}]'for v in s_h)}concat=v=0:a=1:n=24,asplit={d}{''.join(f'[d{v}]'for v in range(d))}"
    g_h = f"[hb]{''.join(f'[d{v}]'for v in range(d))}concat=v=0:a=1:n={d+1}[h]"
    ss = u % 86400
    segs = filter(
        None,
        [
            f"{g_mmX};{g_hX};{g_s600};{g_s60};{g_mX};{g_m};{g_hh};{g_hb};{g_dX};{g_h};[hh][s600][s60][m][h]amix=inputs=5,volume=5,asetpts=PTS-STARTPTS"
            if audio
            else None,
            f"gradients=size=1920x1080:x0=1:x1=1919:y0=1:y1=1079:speed=0.0523598775598299:r=7[g0];gradients=size=1920x1080:x0=1919:x1=1:y0=1:y1=1079:speed=0.15707963267949:r=7[g1];[g0][g1]blend=all_mode=interpolate,drawtext=text='%{{pts\:localtime\:{ss}\:%H\\\\\:%M\\\\\:%S}}':fontsize=127:fontfile=./.ttf:box=1:boxborderw=30:boxcolor=#1f2123ff:fontcolor=white:x=(w-tw)/2:y=(h-lh)/2"
            if video
            else None,
        ],
    )
    return ";".join(f"{s}[out{i}]" for i, s in enumerate(segs))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    av = ap.add_mutually_exclusive_group()
    av.add_argument("--no-video", "-a", action="store_false", dest="video")
    av.add_argument("--no-audio", "-v", action="store_false", dest="audio")
    ap.add_argument("--timestamp", "-t", type=float, nargs="?")
    ap.add_argument(
        "delay",
        type=float,
        nargs="?",
        default=0.5,
    )
    print(gen(**ap.parse_args().__dict__))
