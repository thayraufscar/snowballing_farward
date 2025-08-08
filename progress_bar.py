def print_progress(current, total):
    percent = 100 * (current / total)
    bar = '#' * int(percent // 2) + '-' * (50 - int(percent // 2))
    print(f"\rProgress: |{bar}| {percent:.1f}% ({current}/{total})", end='', flush=True)
