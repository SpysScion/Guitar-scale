import streamlit as st
import matplotlib.pyplot as plt
import io

# Define chromatic notes
notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Guitar tuning (standard EADGBE)
tuning = ["E", "A", "D", "G", "B", "E"]

# Base scale formulas
base_scale_formulas = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "blues": [0, 3, 5, 6, 7, 10],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "diminished_whole_half": [0, 2, 3, 5, 6, 8, 9, 11],
    "diminished_half_whole": [0, 1, 3, 4, 6, 7, 9, 10]
}

# Mode lists
melodic_minor_mode_names = [
    "melodic_minor", "dorian_b2", "lydian_augmented", "lydian_dominant",
    "mixolydian_b6", "locrian_nat2", "altered_super_locrian"
]

harmonic_minor_mode_names = [
    "harmonic_minor", "locrian_nat6", "ionian_augmented",
    "dorian_augmented4", "phrygian_dominant", "lydian_augmented9", "ultralocrian"
]

mode_names_major = ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]

# Utility: rotate scale intervals
def rotate_intervals(parent_intervals, degree):
    root = parent_intervals[degree]
    rotated = [(i - root) % 12 for i in parent_intervals[degree:]] + [(i - root) % 12 for i in parent_intervals[:degree]]
    return sorted(set(rotated))

# Build full scale formulas
scale_formulas = dict(base_scale_formulas)
mm_parent = base_scale_formulas["melodic_minor"]
for i, name in enumerate(melodic_minor_mode_names):
    scale_formulas[name] = rotate_intervals(mm_parent, i)

hm_parent = base_scale_formulas["harmonic_minor"]
for i, name in enumerate(harmonic_minor_mode_names):
    scale_formulas[name] = rotate_intervals(hm_parent, i)

major_parent = base_scale_formulas["major"]
for i, name in enumerate(mode_names_major):
    scale_formulas[name] = rotate_intervals(major_parent, i)

# Build fretboard mapping
def build_fretboard():
    fb = []
    for string in tuning:
        start = notes.index(string)
        fb.append([notes[(start + fret) % 12] for fret in range(23)])
    return fb

# Get scale notes
def get_scale(root, scale_type):
    root_index = notes.index(root)
    intervals = scale_formulas[scale_type]
    return [notes[(root_index + i) % 12] for i in intervals]

# Plot scale diagram
def plot_scale(root="A", scale_type="blues", full_fretboard=True, highlight_roots=True, dark_mode=True):
    scale_notes = get_scale(root, scale_type)
    fb = build_fretboard()

    fig, ax = plt.subplots(figsize=(22, 5))

    # Colors
    bg_color = "#3b2f2f" if dark_mode else "#f4e9dc"
    text_color = "white" if dark_mode else "black"
    nut_color = "ivory" if dark_mode else "black"

    ax.set_facecolor(bg_color)

    # Frets
    max_fret = 22 if full_fretboard else 12
    for f in range(1, max_fret+1):
        ax.plot([f, f], [0, 5], color="silver", linewidth=1.2)

    # Nut
    ax.plot([0, 0], [0, 5], color=nut_color, linewidth=4)

    # Strings
    string_widths = [3, 2.5, 2, 1.5, 1.2, 1]
    for s in range(6):
        ax.plot([0, max_fret], [s, s], color="lightgray", linewidth=string_widths[s])

    # Offset for notes
    x_offset = 0.5

    # Notes on frets
    for s in range(6):
        for f in range(1, max_fret+1):
            note = fb[5 - s][f]
            if note in scale_notes:
                circle_color = "red" if (note == root and highlight_roots) else "white"
                edge_color = "red" if (note == root and highlight_roots) else "black"
                ax.add_patch(plt.Circle((f - x_offset, s), 0.28, facecolor=circle_color,
                                        edgecolor=edge_color, linewidth=1.0, zorder=3))
                ax.text(f - x_offset, s, note, ha="center", va="center",
                        color=edge_color if circle_color == "white" else "white",
                        fontsize=11, fontweight="bold", zorder=4)

    # Open strings
    for s in range(6):
        note = fb[5 - s][0]
        if note in scale_notes:
            circle_color = "red" if (note == root and highlight_roots) else "white"
            edge_color = "red" if (note == root and highlight_roots) else "black"
            ax.add_patch(plt.Circle((-0.8, s), 0.28, facecolor=circle_color,
                                    edgecolor=edge_color, linewidth=1.0, zorder=3))
            ax.text(-0.8, s, note, ha="center", va="center",
                    color=edge_color if circle_color == "white" else "white",
                    fontsize=11, fontweight="bold", zorder=4)

    # Inlays
    inlay_frets = [3, 5, 7, 9, 12]
    for f in inlay_frets:
        x = f - 0.5
        if f == 12:
            ax.add_patch(plt.Circle((x, 1.5), 0.08, color="white"))
            ax.add_patch(plt.Circle((x, 4.5), 0.08, color="white"))
        else:
            ax.add_patch(plt.Circle((x, 2.5), 0.1, color="white"))

    ax.set_xlim(-2, max_fret+0.5)
    ax.set_ylim(-1.5, 6.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"{root} {scale_type.replace('_',' ').title()} Scale", fontsize=16, fontweight="bold", color=text_color)
    ax.invert_yaxis()
    plt.grid(False)
    return fig

# --- STREAMLIT APP ---
st.title("🎸 Guitar Scale Generator")

root = st.selectbox("Root Note", notes, index=9)  # default A
scale = st.selectbox("Scale Type", sorted(scale_formulas.keys()))
full_fretboard = st.checkbox("Show Full Fretboard", value=True)
highlight_roots = st.checkbox("Highlight Root Notes", value=True)
dark_mode = st.checkbox("Dark Mode", value=True)

if st.button("Show Scale"):
    fig = plot_scale(root, scale, full_fretboard, highlight_roots, dark_mode)
    st.pyplot(fig)

    # Download buttons
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    st.download_button("Download PNG", data=buf.getvalue(), file_name=f"{root}_{scale}.png", mime="image/png")

    buf_pdf = io.BytesIO()
    fig.savefig(buf_pdf, format="pdf", bbox_inches="tight")
    st.download_button("Download PDF", data=buf_pdf.getvalue(), file_name=f"{root}_{scale}.pdf", mime="application/pdf")
