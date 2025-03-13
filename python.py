from PIL import Image, ImageDraw, ImageFont

# Constants
CARD_WIDTH = 800
CARD_HEIGHT = 1200
TOP_SECTION_HEIGHT = int(CARD_HEIGHT * 0.25)
BOTTOM_SECTION_HEIGHT = CARD_HEIGHT - TOP_SECTION_HEIGHT
PLAYER_PHOTO_SIZE = 200
OUTLINE_WIDTH = 10
TEXT_OUTLINE_WIDTH = 4
FONT_PATH = "verdana.ttf"

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

    # Create mask
    mask = Image.new("L", (PLAYER_PHOTO_SIZE, PLAYER_PHOTO_SIZE), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, PLAYER_PHOTO_SIZE, PLAYER_PHOTO_SIZE), fill=255)

    # Create circular image with outline
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

def create_gradient(width, height, start_color, end_color):
    """Creates a horizontal gradient."""
    gradient = Image.new("RGB", (width, height), start_color)
    draw = ImageDraw.Draw(gradient)

    for x in range(width):
        r = start_color[0] + (end_color[0] - start_color[0]) * x // width
        g = start_color[1] + (end_color[1] - start_color[1]) * x // width
        b = start_color[2] + (end_color[2] - start_color[2]) * x // width
        draw.line([(x, 0), (x, height)], fill=(r, g, b))

    return gradient

def draw_text_with_outline(draw, position, text_lines, font, text_color="white", outline_color="black", outline_width=TEXT_OUTLINE_WIDTH, align="left"):
    """Draws text with an outline."""
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

def create_player_card(background_img, player_photo, player_name, deck_archetype, mainboard, sideboard, output_file="player_card.jpg"):
    # Load and process images
    bg = Image.open(background_img).resize((CARD_WIDTH, TOP_SECTION_HEIGHT))
    player_img = Image.open(player_photo)
    player_img = crop_center(player_img, PLAYER_PHOTO_SIZE)
    player_img = make_circle(player_img)

    # Create blank card
    card = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), "white")

    # Paste background at the top
    card.paste(bg, (0, 0))

    # Paste player photo
    player_x = (CARD_WIDTH - player_img.size[0]) // 2
    player_y = (TOP_SECTION_HEIGHT - player_img.size[1]) // 2
    card.paste(player_img, (player_x, player_y), player_img)

    # Draw text
    draw = ImageDraw.Draw(card)
    try:
        font = ImageFont.truetype(FONT_PATH, 42)
        small_font = ImageFont.truetype(FONT_PATH, 36)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # **Text Positions**
    text_y = player_y + player_img.size[1] // 2 - 40
    name_x = player_x - 40
    deck_x = player_x + player_img.size[0] + 40

    # **Draw player name & deck archetype**
    draw_text_with_outline(draw, (name_x, text_y), player_name.split(" "), font, align="right")
    draw_text_with_outline(draw, (deck_x, text_y), deck_archetype.split(" "), font, align="left")

    # **Create bottom section with gradient**
    gradient_bg = create_gradient(CARD_WIDTH, BOTTOM_SECTION_HEIGHT, (0, 0, 80), (0, 0, 255))
    card.paste(gradient_bg, (0, TOP_SECTION_HEIGHT))

    # **Column Positions**
    column_spacing = 100
    mainboard_x = column_spacing
    sideboard_x = CARD_WIDTH // 2 + column_spacing
    bottom_text_y = TOP_SECTION_HEIGHT + 50

    # **Draw Headers**
    draw_text_with_outline(draw, (mainboard_x, bottom_text_y), ["Mainboard"], font, align="left")
    draw_text_with_outline(draw, (sideboard_x, bottom_text_y), ["Sideboard"], font, align="left")

    # **Draw Cards List**
    card_spacing = 40
    for i, card_name in enumerate(mainboard):
        draw_text_with_outline(draw, (mainboard_x, bottom_text_y + 60 + i * card_spacing), [card_name], small_font, align="left")

    for i, card_name in enumerate(sideboard):
        draw_text_with_outline(draw, (sideboard_x, bottom_text_y + 60 + i * card_spacing), [card_name], small_font, align="left")

    # Save result
    card.save(output_file)
    print(f"✅ Player card saved as {output_file}")

# Example usage
mainboard_cards = ["Card 1", "Card 2", "Card 3", "Card 4"]
sideboard_cards = ["Card A", "Card B", "Card C", "Card D"]

create_player_card(
    "background.jpg",
    "player.jpg",
    "John Doe",
    "Amulet Titan",
    mainboard_cards,
    sideboard_cards
)
