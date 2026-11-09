
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

st.set_page_config(
    page_title="Event Poster Generator",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Event Poster Generator")
st.write("Create a professional department event poster.")

# --------------------------------
# FONT LOADING
# --------------------------------

def get_font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold
        else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold
        else "C:/Windows/Fonts/calibri.ttf"
    ]

    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    return ImageFont.load_default()


# --------------------------------
# POSTER GENERATION
# --------------------------------

def create_poster(event, date, time, venue, description, organizer):

    width, height = 1080, 1350

    image = Image.new("RGB", (width, height), "#101B35")
    draw = ImageDraw.Draw(image)

    # Background gradient
    for y in range(height):
        ratio = y / height

        r = int(16 + ratio * 35)
        g = int(27 + ratio * 15)
        b = int(53 + ratio * 65)

        draw.line((0, y, width, y), fill=(r, g, b))

    # Decorative shapes
    draw.ellipse((790, -180, 1250, 280), fill="#254D75")
    draw.ellipse((-180, 1000, 300, 1480), fill="#234B68")

    # Top label
    draw.rounded_rectangle(
        (80, 75, 420, 145),
        radius=25,
        fill="#F5A623"
    )

    draw.text(
        (105, 92),
        "DEPARTMENT EVENT",
        font=get_font(27, True),
        fill="#101B35"
    )

    # Event title
    title_font = get_font(82, True)
    words = event.split()
    lines = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()

        if draw.textbbox((0, 0), test, font=title_font)[2] > 900:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 260

    for line in lines[:3]:
        draw.text(
            (80, y),
            line,
            font=title_font,
            fill="#FFFFFF"
        )
        y += 110

    # Accent line
    draw.rounded_rectangle(
        (80, y + 15, 300, y + 25),
        radius=5,
        fill="#F5A623"
    )

    # Description
    desc_font = get_font(34)
    desc_lines = textwrap.wrap(description, width=48)

    y += 85

    for line in desc_lines[:5]:
        draw.text(
            (80, y),
            line,
            font=desc_font,
            fill="#DCE7F5"
        )
        y += 52

    # Information card
    card_top = 850

    draw.rounded_rectangle(
        (65, card_top, 1015, 1190),
        radius=35,
        fill="#FFFFFF"
    )

    info_font = get_font(34, True)
    value_font = get_font(32)

    details = [
        ("DATE", date),
        ("TIME", time),
        ("VENUE", venue)
    ]

    y = card_top + 45

    for label, value in details:
        draw.text(
            (110, y),
            label,
            font=get_font(23, True),
            fill="#54708E"
        )

        draw.text(
            (340, y - 3),
            value[:35],
            font=value_font,
            fill="#14243D"
        )

        y += 90

    # Organizer footer
    draw.text(
        (80, 1250),
        f"Organized by: {organizer}",
        font=get_font(28, True),
        fill="#FFFFFF"
    )

    return image


# --------------------------------
# USER INPUT FORM
# --------------------------------

with st.form("poster_form"):

    event = st.text_input(
        "Event Name",
        placeholder="Example: AI Innovation Workshop"
    )

    date = st.text_input(
        "Event Date",
        placeholder="Example: 20 November 2026"
    )

    time = st.text_input(
        "Event Time",
        placeholder="Example: 10:00 AM"
    )

    venue = st.text_input(
        "Venue",
        placeholder="Example: Seminar Hall"
    )

    description = st.text_area(
        "Event Description",
        placeholder="Enter a short description of the event."
    )

    organizer = st.text_input(
        "Organized By",
        placeholder="Example: Department of AI and Analytics"
    )

    submitted = st.form_submit_button(
        "Generate Poster",
        use_container_width=True
    )


# --------------------------------
# DISPLAY AND DOWNLOAD
# --------------------------------

if submitted:

    if not all([
        event.strip(),
        date.strip(),
        time.strip(),
        venue.strip(),
        description.strip(),
        organizer.strip()
    ]):
        st.warning("Please fill in all the fields.")

    else:

        poster = create_poster(
            event.strip(),
            date.strip(),
            time.strip(),
            venue.strip(),
            description.strip(),
            organizer.strip()
        )

        image_buffer = BytesIO()
        poster.save(image_buffer, format="PNG")
        poster_bytes = image_buffer.getvalue()

        st.success("Your event poster is ready!")

        st.image(poster_bytes, caption="Generated Event Poster")

        st.download_button(
            label="⬇️ Download Poster",
            data=poster_bytes,
            file_name="department_event_poster.png",
            mime="image/png",
            use_container_width=True
        )
