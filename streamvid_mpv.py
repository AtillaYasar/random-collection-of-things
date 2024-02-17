def streamed_playback(url, x, y, width, height, panscan=None):
    # import sys, signal, subprocess
    # requires mpv and yt-dlp

    # Graceful shutdown handler for SIGINT (Ctrl-C)
    def signal_handler(sig, frame):
        print("Attempting to terminate the processes...")
        player_process.terminate()
        try:
            yt_dlp_process.terminate()
        except Exception as e:
            print("Error terminating yt-dlp process:", e)

    # Command to play video using yt-dlp and mpv
    player_command = [
        'yt-dlp',
        '-o', '-',  # Output to stdout
        '--quiet',  # Suppress the output
        url
    ]

    player_process_command = [
        'mpv',
        '--geometry={0}x{1}+{2}+{3}'.format(width, height, x, y),
        '--cache=yes',
        '--',
        '-'
    ]
    if panscan != None:
        if type(panscan) == float:
            player_process_command.insert(1, f'--panscan={panscan}')

    # Set the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    with subprocess.Popen(player_command, stdout=subprocess.PIPE) as yt_dlp_process:
        with subprocess.Popen(player_process_command, stdin=yt_dlp_process.stdout) as player_process:
            try:
                # Wait for the player process to complete
                player_process.wait()
            except KeyboardInterrupt:
                # Handle the keyboard interrupt to terminate the processes
                print("KeyboardInterrupt received.")
                signal_handler(None, None)

if 1:
  # example: with this you can run `<filename.py> <url>` , to play any video on the top left corner of the screen, resized correctly and will fill out the top and bottom of the video (via panscan, if you set it to 1.0, will fill it entirely)
  url = sys.argv[1]
  swidth, sheight = 1920, 1080
  streamed_playback(url, 0, 0, int(swidth/2), int(sheight)-50, panscan=0.8)
