
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

st.set_page_config(
    page_title="Event Poster Generator",
    page_icon="🎨",
    layout="centered"
)

st.title("🎨 Event Poster Generator")
st.write("Create a professional department event poster.")


# --------------------------------------------------
# 1. FONT LOADING
# --------------------------------------------------

def get_font(size, bold=False):

    if bold:
        font_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
        ]
    else:
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf"
        ]

    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    return ImageFont.load_default()


# --------------------------------------------------
# 2. TEXT WRAPPING USING ACTUAL PIXEL WIDTH
# --------------------------------------------------

def wrap_text(draw, text, font, max_width):

    words = text.split()
    lines = []
    current_line = ""

    for word in words:

        test_line = (
            current_line + " " + word
        ).strip()

        if draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )[2] <= max_width:

            current_line = test_line

        else:

            if current_line:
                lines.append(current_line)

            # Split very long words if necessary
            if draw.textbbox(
                (0, 0),
                word,
                font=font
            )[2] > max_width:

                part = ""

                for character in word:

                    test_part = part + character

                    if draw.textbbox(
                        (0, 0),
                        test_part,
                        font=font
                    )[2] <= max_width:

                        part = test_part

                    else:

                        if part:
                            lines.append(part)

                        part = character

                current_line = part

            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# --------------------------------------------------
# 3. AUTOMATIC TITLE FONT SIZE
# --------------------------------------------------

def get_title_layout(draw, event, max_width):

    for size in range(82, 37, -2):

        font = get_font(size, True)

        lines = wrap_text(
            draw,
            event,
            font,
            max_width
        )

        if len(lines) <= 3:
            return font, lines

    font = get_font(38, True)

    return font, wrap_text(
        draw,
        event,
        font,
        max_width
    )


# --------------------------------------------------
# 4. POSTER GENERATION
# --------------------------------------------------

def create_poster(
    event,
    date,
    time,
    venue,
    description,
    organizer
):

    width = 1080

    # Create drawing object
    image = Image.new(
        "RGB",
        (width, 1500),
        "#101B35"
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------
    # BACKGROUND GRADIENT
    # --------------------------------------------------

    height = 1500

    for y in range(height):

        ratio = y / height

        r = int(16 + ratio * 35)
        g = int(27 + ratio * 15)
        b = int(53 + ratio * 65)

        draw.line(
            (0, y, width, y),
            fill=(r, g, b)
        )

    # Decorative circles
    draw.ellipse(
        (790, -180, 1250, 280),
        fill="#254D75"
    )

    draw.ellipse(
        (-180, 1160, 300, 1640),
        fill="#234B68"
    )

    # --------------------------------------------------
    # TOP LABEL
    # --------------------------------------------------

    draw.rounded_rectangle(
        (80, 75, 440, 145),
        radius=25,
        fill="#F5A623"
    )

    draw.text(
        (105, 94),
        "DEPARTMENT EVENT",
        font=get_font(25, True),
        fill="#101B35"
    )

    # --------------------------------------------------
    # EVENT TITLE
    # --------------------------------------------------

    title_font, title_lines = get_title_layout(
        draw,
        event,
        900
    )

    title_y = 235

    title_bbox = draw.textbbox(
        (0, 0),
        "Ag",
        font=title_font
    )

    title_line_height = (
        title_bbox[3] - title_bbox[1] + 24
    )

    for line in title_lines:

        draw.text(
            (80, title_y),
            line,
            font=title_font,
            fill="#FFFFFF"
        )

        title_y += title_line_height

    # --------------------------------------------------
    # GOLD ACCENT LINE
    # --------------------------------------------------

    accent_y = title_y + 15

    draw.rounded_rectangle(
        (
            80,
            accent_y,
            300,
            accent_y + 12
        ),
        radius=6,
        fill="#F5A623"
    )

    # --------------------------------------------------
    # EVENT DESCRIPTION
    # --------------------------------------------------

    description_y = accent_y + 55

    description_font = get_font(30)

    description_lines = wrap_text(
        draw,
        description,
        description_font,
        900
    )

    description_bbox = draw.textbbox(
        (0, 0),
        "Ag",
        font=description_font
    )

    description_line_height = (
        description_bbox[3] -
        description_bbox[1] + 20
    )

    for line in description_lines:

        draw.text(
            (80, description_y),
            line,
            font=description_font,
            fill="#DCE7F5"
        )

        description_y += description_line_height

    # --------------------------------------------------
    # INFORMATION CARD
    # --------------------------------------------------

    card_top = description_y + 65

    card_left = 65
    card_right = 1015

    label_font = get_font(25, True)
    value_font = get_font(29)

    details = [
        ("DATE", date),
        ("TIME", time),
        ("VENUE", venue)
    ]

    # Calculate card height based on wrapped values
    row_data = []

    for label, value in details:

        value_lines = wrap_text(
            draw,
            value,
            value_font,
            570
        )

        row_data.append(
            (label, value_lines)
        )

    row_heights = []

    for label, lines in row_data:

        row_heights.append(
            max(75, len(lines) * 43 + 20)
        )

    card_height = sum(row_heights) + 80

    card_bottom = card_top + card_height

    # Extend poster height if necessary
    footer_y = card_bottom + 65

    final_height = max(
        1500,
        footer_y + 100
    )

    # Resize background and continue gradient
    if final_height > height:

        extra_height = final_height - height

        extra = Image.new(
            "RGB",
            (width, extra_height),
            "#32316D"
        )

        image = Image.new(
            "RGB",
            (width, final_height)
        )

        image.paste(
            image_original := Image.new(
                "RGB",
                (width, height)
            ),
            (0, 0)
        )

        # Rebuild complete background gradient
        for y in range(final_height):

            ratio = min(y / 1500, 1)

            r = int(16 + ratio * 35)
            g = int(27 + ratio * 15)
            b = int(53 + ratio * 65)

            draw.line(
                (0, y, width, y),
                fill=(r, g, b)
            )

        draw.ellipse(
            (790, -180, 1250, 280),
            fill="#254D75"
        )

        draw.ellipse(
            (-180, final_height - 340, 300, final_height + 140),
            fill="#234B68"
        )

        # Redraw existing content
        draw.rounded_rectangle(
            (80, 75, 440, 145),
            radius=25,
            fill="#F5A623"
        )

        draw.text(
            (105, 94),
            "DEPARTMENT EVENT",
            font=get_font(25, True),
            fill="#101B35"
        )

        title_y = 235

        for line in title_lines:

            draw.text(
                (80, title_y),
                line,
                font=title_font,
                fill="#FFFFFF"
            )

            title_y += title_line_height

        draw.rounded_rectangle(
            (80, accent_y, 300, accent_y + 12),
            radius=6,
            fill="#F5A623"
        )

        description_y = accent_y + 55

        for line in description_lines:

            draw.text(
                (80, description_y),
                line,
                font=description_font,
                fill="#DCE7F5"
            )

            description_y += description_line_height

    # Draw information card
    draw.rounded_rectangle(
        (
            card_left,
            card_top,
            card_right,
            card_bottom
        ),
        radius=35,
        fill="#FFFFFF"
    )

    current_y = card_top + 40

    for (label, value_lines), row_height in zip(
        row_data,
        row_heights
    ):

        draw.text(
            (110, current_y),
            label,
            font=label_font,
            fill="#54708E"
        )

        value_y = current_y - 3

        for line in value_lines:

            draw.text(
                (340, value_y),
                line,
                font=value_font,
                fill="#14243D"
            )

            value_y += 43

        current_y += row_height

    # --------------------------------------------------
    # ORGANIZER FOOTER
    # --------------------------------------------------

    organizer_font = get_font(25, True)

    organizer_text = (
        f"Organized by: {organizer}"
    )

    organizer_lines = wrap_text(
        draw,
        organizer_text,
        organizer_font,
        900
    )

    organizer_y = card_bottom + 55

    for line in organizer_lines:

        draw.text(
            (80, organizer_y),
            line,
            font=organizer_font,
            fill="#FFFFFF"
        )

        organizer_y += 38

    return image


# --------------------------------------------------
# 5. USER INPUT FORM
# --------------------------------------------------

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


# --------------------------------------------------
# 6. DISPLAY AND DOWNLOAD POSTER
# --------------------------------------------------

if submitted:

    if not all([
        event.strip(),
        date.strip(),
        time.strip(),
        venue.strip(),
        description.strip(),
        organizer.strip()
    ]):

        st.warning(
            "Please fill in all the fields."
        )

    else:

        try:

            poster = create_poster(
                event.strip(),
                date.strip(),
                time.strip(),
                venue.strip(),
                description.strip(),
                organizer.strip()
            )

            image_buffer = BytesIO()

            poster.save(
                image_buffer,
                format="PNG"
            )

            poster_bytes = image_buffer.getvalue()

            st.success(
                "Your event poster is ready!"
            )

            st.image(
                poster_bytes,
                caption="Generated Event Poster",
                use_container_width=True
            )

            st.download_button(
                label="⬇️ Download Poster",
                data=poster_bytes,
                file_name="department_event_poster.png",
                mime="image/png",
                use_container_width=True
            )

        except Exception as error:

            st.error(
                "Unable to generate poster."
            )

            st.code(repr(error))
