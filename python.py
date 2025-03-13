from PIL import Image, ImageDraw, ImageFont

# ========== CONFIGURABLE VARIABLES ==========
CARD_WIDTH = 1000  # Width of the player card
CARD_HEIGHT = 1400  # Height of the player card

TOP_SECTION_HEIGHT = int(CARD_HEIGHT * 0.25)  # Height of the top section (background + player photo)
BOTTOM_SECTION_HEIGHT = CARD_HEIGHT - TOP_SECTION_HEIGHT  # Height of the decklist section

PLAYER_PHOTO_SIZE = 275  # Size of the player's circular photo
OUTLINE_WIDTH = 5  # Thickness of the circular photo outline

TEXT_OUTLINE_WIDTH = 2  # Thickness of the text outline for better visibility
FONT_PATH = "verdana.ttf"  # Path to the font file

COLUMN_FONT_SIZE = 30  # Font size for Mainboard & Sideboard cards
PLAYER_NAME_FONT_SIZE = 74  # Font size for player name and deck archetype
COLUMN_TITLE_FONT_SIZE = 50  # Font size for column titles (Mainboard & Sideboard)

DECKLIST_FILE = "decklist.txt"  # File containing decklist info

MAINBOARD_X_OFFSET = 100  # Horizontal position for Mainboard column
SIDEBOARD_X_OFFSET = CARD_WIDTH // 2 + 100  # Horizontal position for Sideboard column
TEXT_START_Y = TOP_SECTION_HEIGHT + 50  # Vertical starting position for text in the decklist section

TOP_BACKGROUND_IMAGE = "background.jpg"  # Background image for the top section
BOTTOM_BACKGROUND_IMAGE = "bottom_background.jpg"  # Background image for the bottom section

SPONSOR_LOGO_SIZE = (350, 175)  # Size of the sponsor logo (width, height)
SPONSOR_LOGO_1_IMAGE = "sponsor_logo1.png"  # Sponsor logo image file
SPONSOR_LOGO_1_Y = CARD_HEIGHT - 250  # Vertical position of the sponsor logo
SPONSOR_LOGO_2_IMAGE = "sponsor_logo2.png"  # Sponsor logo image file
SPONSOR_LOGO_2_Y = CARD_HEIGHT - 450  # Vertical position of the sponsor logo


OUTPUT_FILE = "player_card.jpg"  # Output file name

# ========== FUNCTION DEFINITIONS ==========
def crop_center(image, size):
    """Crops the image to a square from the center and resizes it."""
    width, height = image.size
    min_side = min(width, height)
    left = (width - min_side) // 2
    top = (height - min_side) // 2
    image = image.crop((left, top, left + min_side, top + min_side))
    return image.resize((size, size))

def make_circle(image):
    """Creates a perfectly circular image with a black outline."""
    image = image.convert("RGBA")
    size = (PLAYER_PHOTO_SIZE + OUTLINE_WIDTH * 2, PLAYER_PHOTO_SIZE + OUTLINE_WIDTH * 2)

    mask = Image.new("L", (PLAYER_PHOTO_SIZE, PLAYER_PHOTO_SIZE), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, PLAYER_PHOTO_SIZE, PLAYER_PHOTO_SIZE), fill=255)

    circular_img = Image.new("RGBA", size, (0, 0, 0, 0))
    outline_mask = Image.new("L", size, 0)
    outline_draw = ImageDraw.Draw(outline_mask)
    outline_draw.ellipse((0, 0, size[0], size[1]), fill=255)
    
    outline_layer = Image.new("RGBA", size, (0, 0, 0, 255))
    outline_layer.putalpha(outline_mask)
    circular_img.paste(outline_layer, (0, 0), outline_layer)

    image = image.resize((PLAYER_PHOTO_SIZE, PLAYER_PHOTO_SIZE))
    circular_img.paste(image, (OUTLINE_WIDTH, OUTLINE_WIDTH), mask)

    return circular_img

def parse_decklist(file_path):
    """Parses decklist.txt into player name, deck archetype, mainboard, and sideboard lists."""
    mainboard = []
    sideboard = []
    section = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    if len(lines) < 2:
        raise ValueError("Decklist must have at least 2 lines: player name and deck archetype.")

    player_name = lines[0]
    deck_archetype = lines[1]

    for line in lines[2:]:  
        if line.lower().startswith("mainboard:"):
            section = "mainboard"
            continue
        elif line.lower().startswith("sideboard:"):
            section = "sideboard"
            continue

        if section:
            parts = line.split(" ", 1)
            formatted_line = f"{parts[0]}x {parts[1]}" if len(parts) == 2 else parts[0]
            (mainboard if section == "mainboard" else sideboard).append(formatted_line)

    return player_name, deck_archetype, mainboard, sideboard

def draw_text_with_outline(draw, position, text_lines, font, text_color="white", outline_color="black", outline_width=TEXT_OUTLINE_WIDTH, align="left"):
    """Draws text with an outline for better readability."""
    x, y = position

    for i, line in enumerate(text_lines):
        line_y = y + i * (font.size + 5)
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        if align == "right":
            x_pos = x - text_width
        else:
            x_pos = x

        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x_pos + dx, line_y + dy), line, font=font, fill=outline_color)
        
        draw.text((x_pos, line_y), line, font=font, fill=text_color)

def create_player_card(player_photo, decklist_file, output_file=OUTPUT_FILE):
    """Creates a player card using data from decklist.txt."""
    player_name, deck_archetype, mainboard, sideboard = parse_decklist(decklist_file)

    # Load and process images
    bg_top = Image.open(TOP_BACKGROUND_IMAGE).resize((CARD_WIDTH, TOP_SECTION_HEIGHT))
    bg_bottom = Image.open(BOTTOM_BACKGROUND_IMAGE).resize((CARD_WIDTH, BOTTOM_SECTION_HEIGHT))
    sponsor_logo1 = Image.open(SPONSOR_LOGO_1_IMAGE).resize(SPONSOR_LOGO_SIZE)
    sponsor_logo2 = Image.open(SPONSOR_LOGO_2_IMAGE).resize(SPONSOR_LOGO_SIZE)
    sponsor_logo1 = sponsor_logo1.convert("RGBA")
    sponsor_logo2 = sponsor_logo2.convert("RGBA")
    
    player_img = Image.open(player_photo)
    player_img = crop_center(player_img, PLAYER_PHOTO_SIZE)
    player_img = make_circle(player_img)

    # Create blank card
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")

    # Paste backgrounds
    card.paste(bg_top, (0, 0))
    card.paste(bg_bottom, (0, TOP_SECTION_HEIGHT))

    # Paste player photo
    player_x = (CARD_WIDTH - player_img.size[0]) // 2
    player_y = (TOP_SECTION_HEIGHT - player_img.size[1]) // 2
    card.paste(player_img, (player_x, player_y), player_img)

    # Draw text
    draw = ImageDraw.Draw(card)
    try:
        name_font = ImageFont.truetype(FONT_PATH, PLAYER_NAME_FONT_SIZE)
        column_title_font = ImageFont.truetype(FONT_PATH, COLUMN_TITLE_FONT_SIZE)
        small_font = ImageFont.truetype(FONT_PATH, COLUMN_FONT_SIZE)
    except:
        name_font = ImageFont.load_default()
        column_title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()


    # **Text Positions**
    draw_text_with_outline(draw, (MAINBOARD_X_OFFSET, TEXT_START_Y), ["Mainboard"], column_title_font, align="center")
    draw_text_with_outline(draw, (SIDEBOARD_X_OFFSET, TEXT_START_Y), ["Sideboard"], column_title_font, align="center")

    # **Draw Cards List**
    card_spacing = COLUMN_FONT_SIZE + 10
    for i, card_name in enumerate(mainboard):
        draw_text_with_outline(draw, (MAINBOARD_X_OFFSET, TEXT_START_Y + 60 + i * card_spacing), [card_name], small_font, align="center")

    for i, card_name in enumerate(sideboard):
        draw_text_with_outline(draw, (SIDEBOARD_X_OFFSET, TEXT_START_Y + 60 + i * card_spacing), [card_name], small_font, align="center")

    # **Paste Sponsor Logo**
    sponsor_1 = SIDEBOARD_X_OFFSET - SPONSOR_LOGO_SIZE[0] // 2 + 120
    card.paste(sponsor_logo1, (sponsor_1, SPONSOR_LOGO_1_Y), sponsor_logo1)

        # **Paste Sponsor Logo**
    sponsor_2 = SIDEBOARD_X_OFFSET - SPONSOR_LOGO_SIZE[0] // 2 + 120
    card.paste(sponsor_logo2, (sponsor_2, SPONSOR_LOGO_2_Y), sponsor_logo2)

        # **Text Positions**
    text_y = player_y + player_img.size[1] // 2 - 80
    name_x = player_x - 40
    deck_x = player_x + player_img.size[0] + 40

    # **Draw player name & deck archetype**
    draw_text_with_outline(draw, (name_x, text_y), player_name.split(" "), name_font, align="right")
    draw_text_with_outline(draw, (deck_x, text_y), deck_archetype.split(" "), name_font, align="left")

    # Save result
    card.save(output_file)
    print(f"✅ Player card saved as {output_file}")

# ========== SCRIPT EXECUTION ==========
create_player_card("player.jpg", DECKLIST_FILE)