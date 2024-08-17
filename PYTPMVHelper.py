import os.path
import questionary

with_audio = ""

try:
    import PYTPMVCreator as pytpmv
except ImportError:
    print("PYTPMV.py master script must be in the same directory as the Helper.")

print("Welcome to the YTPMV Creator Helper program!")

output_modes = questionary.checkbox("Choose which task(s) to perform.", choices=[
    "Output track(s) as separate video files",
    "Join track(s) in a finalized collage",
]).ask()

#with_audio = questionary.confirm("Include audio in the output video(s)?").ask()

file_source_midi = questionary.text("Input the path to the source MIDI file (try dragging and dropping).").ask().strip().strip("'")
if os.path.isfile(file_source_midi):
    all_tracks = pytpmv.get_track_names(file_source_midi)
else:
    raise SystemExit("File doesn't exist.")

q_choices = []
for i, track in enumerate(all_tracks):
    q_choices.append(f"{i:02} - {track}")

while True:
    chosen_tracks = questionary.checkbox("Which tracks to use in the final product?", choices=q_choices).ask()
    if chosen_tracks:
        break
    print("Choose at least one track, or restart the Helper and choose Auto mode.")

chosen_tracks_list = []
for track in chosen_tracks:
    track_num = int(track[:2])
    chosen_tracks_list.append(track_num)

print("\nInput the path to the video clip to use for the following tracks (try dragging and dropping):")
chosen_clips = []
for track in chosen_tracks:
    clip = questionary.text(f"Input clip for track {track}:").ask()
    if not os.path.isfile(clip.strip().strip("'")):
        raise SystemExit("File doesn't exist.")
    chosen_clips.append(clip)

processed_clips = []
for track, clip in zip(chosen_tracks_list, chosen_clips):
    print(f"\nWorking on track #{track}...")

    output_file = f"output_singleclip_t{track}.mp4"
    tmp_output_file = f"{output_file}_tmp"  # Add _tmp prefix
    pytpmv.render_video(clip.strip().strip("'"), pytpmv.get_semitones_timeline(file_source_midi, track), output_file=None, with_audio=(True if with_audio else False))
    if "Output track(s) as separate video files" in output_modes:
        pytpmv.save_standalone(tmp_output_file, output_file)  # Remove _tmp prefix
    if "Join track(s) in a finalized collage" in output_modes:
        processed_clips.append(output_file)

if len(processed_clips) != 0:
    while True:
        gridsize = questionary.text("Divide clips in how many columns?").ask()
        if gridsize.isdigit() and 1 <= int(gridsize) <= 6:
            gridsize = int(gridsize)
            break
        print("Input an integer between 1 and 6 (inclusive).")
    processed_clips = [processed_clips[i:i + gridsize] for i in range(0, len(processed_clips), gridsize)]
    if len(processed_clips[-1]) != len(processed_clips[0]):
        processed_clips[-1].extend([pytpmv.blank_clip() for i in range(gridsize-len(processed_clips[-1]))])
    pytpmv.save_collage(processed_clips, "output_pytpmv.mp4", with_audio=(True if with_audio else False))

print("\nThanks! PYTPMVHelper job is done.")
