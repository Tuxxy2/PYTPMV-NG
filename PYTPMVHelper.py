from PyInquirer import prompt
import os.path

try:
    import PYTPMVCreator as pytpmv
except ImportError:
    print("PYTPMV.py master script must be in the same directory as the Helper.")

q_input_midifile = {
    "type": "input",
    "name": "file_source_midi",
    "message": "Input the path to the source MIDI file (try dragging and dropping).",
}
q_ask_auto = {
    "type": "confirm",
    "name": "mode",
    "message": "Choose MIDI tracks manually?",
    "default": True,
}
q_multichoice_modes = {
    "type": "checkbox",
    "name": "output_modes",
    "message": "Choose which task(s) to perform.",
    "choices": [
        {"name": "Output track(s) as separate video files"},
        {"name": "Join track(s) in a finalized collage"},
    ]
}
q_input_gridsize = {
    "type": "input",
    "name": "gridsize",
    "message": "Divide clips in how many columns?",
    "validate": lambda answer : True if answer.isdigit() and 0 < int(answer) < 6 else "Input an integer between 1 and 6 (inclusive).",
}


print("Welcome to the YTPMV Creator Helper program!")
output_modes = prompt(q_multichoice_modes)["output_modes"]
#input("task join not available, will output as separate files instead. continue (ENTER) or cancel (CTRL+C)?")

file_source_midi = prompt(q_input_midifile)['file_source_midi'].strip().strip("'")
if os.path.isfile(file_source_midi):
    all_tracks = pytpmv.get_track_names(file_source_midi)
else:
    raise SystemExit("File doesn't exist.")

q_choices = []
for i, track in enumerate(all_tracks):
    q_choices.append({"name": str(i).zfill(2) + " - " + str(track)})
q_multichoice_tracks = {
    "type": "checkbox",
    "name": "chosen_tracks",
    "message": "Which tracks to use in the final product?",
    "choices": q_choices,
    "validate": lambda answer : "Choose at least one track, or restart the Helper and choose Auto mode." if len(answer) == 0 else True
}

chosen_tracks = prompt(q_multichoice_tracks)["chosen_tracks"]
#print(chosen_tracks)

print("\nInput the path to the video clip to use for the following tracks (try dragging and dropping):")
q_input_clip = {
    "type": "input",
    "name": "input_clip",
    "message": "",
    "validate": lambda answer : "File doesn't exist." if not os.path.isfile(answer.strip().strip("'")) else True
}
chosen_clips = []
for track in chosen_tracks:
    q_input_clip["message"] = str(track)
    chosen_clips.append(prompt(q_input_clip)["input_clip"])

#print(chosen_clips)

chosen_tracks = [int(t[:2]) for t in chosen_tracks]
processed_clips = []
for track, clip in zip(chosen_tracks, chosen_clips):
    print(f"\nWorking on track #{track}...")
    processed_clip = pytpmv.render_video(clip.strip().strip("'"), *pytpmv.get_semitones_timeline(file_source_midi, track))
    if processed_clip is not None:
        if "Output track(s) as separate video files" in output_modes:
            pytpmv.save_standalone(processed_clip, f"output_singleclip_t{track}.mp4")
        if "Join track(s) in a finalized collage" in output_modes:
            processed_clips.append(processed_clip)

if len(processed_clips) != 0:
    gridsize = int(prompt(q_input_gridsize)["gridsize"])
    processed_clips = [processed_clips[i:i + gridsize] for i in range(0, len(processed_clips), gridsize)]
    if len(processed_clips[-1]) != len(processed_clips[0]):
        processed_clips[-1].extend([pytpmv.blank_clip() for i in range(gridsize-len(processed_clips[-1]))])
    #processed_clips = [processed_clips]
    print(processed_clips)
    pytpmv.save_collage(processed_clips, "output_pytpmv.mp4")

print("\nThanks! PYTPMVHelper job is done.")
