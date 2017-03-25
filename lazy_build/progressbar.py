import shutil
import sys
import threading
import time


def best_unit(num):
    for unit in (
        ('TB', 2**40),
        ('GB', 2**30),
        ('MB', 2**20),
        ('KB', 2**10),
    ):
        if num > unit[1]:
            return unit
    else:
        return ('B ', 1)


def progressbar(cur, total, speed, precision=1, file=sys.stderr):
    """Draw a progress bar.

    It looks like this:
    [=======>        ] 10.1MB / 30.2MB |   5.2 MB/s
    """
    if not file.isatty():
        return ''

    precision_fmt = '{{:.{}f}}'.format(precision)
    percent = cur / total

    progress_unit = best_unit(total)
    cur /= progress_unit[1]
    cur = precision_fmt.format(cur) + progress_unit[0]
    total /= progress_unit[1]
    total = precision_fmt.format(total) + progress_unit[0]

    speed_unit = best_unit(speed)
    speed /= speed_unit[1]
    speed = precision_fmt.format(speed) + speed_unit[0]

    # Do the actual drawing!
    width = shutil.get_terminal_size().columns

    width -= len('[>]  /  | /s')
    width -= len(total) * 2
    # Technically the speed could suddenly become more than 3 digits (unlike
    # the total, which is fixed) and cause the progress bar to move, but that's
    # unlikely (4-digit TB/s?).
    speed_width = max(3 + 1 + precision + len(speed_unit[0]), len(speed))
    width -= speed_width

    if width < 0:
        return ''

    bar = (('=' * int(width * percent)) + '>').ljust(width + 1)

    line = '[{bar}] {cur} / {total} | {speed}/s'.format(
        bar=bar,
        cur=cur.rjust(len(total)),
        total=total,
        speed=speed.rjust(speed_width)
    )
    return '\r' + line


class Progress:

    def __init__(self, total_bytes):
        self.history = []
        self.so_far = 0
        self.total_bytes = total_bytes
        self.lock = threading.Lock()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        if sys.stderr.isatty():
            print(file=sys.stderr, flush=True)
        else:
            pass  # pragma: no cover

    def __call__(self, cur_bytes):
        with self.lock:
            self.so_far += cur_bytes

            now = time.time()
            self.history.append((now, self.so_far))

            if len(self.history) > 1:
                first = self.history[0]
                speed = (self.so_far - first[1]) / (now - first[0])
            else:
                speed = 0

            while len(self.history) > 0 and now - self.history[0][0] > 5:
                del self.history[0]

            print(
                progressbar(
                    self.so_far,
                    self.total_bytes,
                    speed,
                    file=sys.stderr,
                ),
                file=sys.stderr,
                flush=True,
                end='',
            )
