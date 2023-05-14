import argparse
import json
import os
import textwrap
from progress.bar import Bar



from PIL import Image, ImageFont, ImageDraw
from math import floor, ceil


def prepare_card(text, card_color, deck_name, deck_logo):
    if card_color == 'white':
        background_color = '#FFFFFF'
        fill_color = '#000000'
        outline_color = '#000000'
    elif card_color == 'black':
        background_color = '#000000'
        fill_color = '#FFFFFF'
        outline_color = '#000000'

    img = Image.new('RGB', (756, 1051), background_color)
    font_text = ImageFont.truetype(font='Inter-Medium.ttf', size=60)
    font_logo_text = ImageFont.truetype(font='Inter-Medium.ttf', size=30)
    draw = ImageDraw.Draw(im=img)

    avg_char_width = 0
    for i in range(len(text)):
        avg_char_width += font_text.getlength(text[i])
    else:
        avg_char_width /= len(text)

    max_char_count = int(img.size[0] * 0.82 / avg_char_width)
    text = textwrap.fill(text=text, width=max_char_count)
    draw.text(xy=(60, 55), text=text, font=font_text, fill=fill_color, anchor='la', spacing=18)
    draw.text(xy=(120, 1000), text=deck_name, font=font_logo_text, fill=fill_color, anchor='ld')
    draw.rectangle(xy=(0, 0, img.size[0], img.size[1]), outline=outline_color, width=3)

    deck_logo = deck_logo.resize((50, 50))
    img.paste(deck_logo, (60, 955), deck_logo)

    return img


def get_deck_name(deck):
    if deck.get("packName") is not None:
        return deck.get("packName")
    else:
        return "Cards Against Humanity"


def prepare_deck(deck_path, deck_name, deck_logo):
    deck_src = read_cards_from_file(deck_path)
    if deck_name is None:
        deck_name = get_deck_name(deck_src)
    black = []
    white = []
    number_of_cards = len(deck_src['blackCards']) + len(deck_src['whiteCards'])
    with Bar('Preparing cards', max=number_of_cards) as bar:
        for text in deck_src['blackCards']:
            black.append(prepare_card(text, 'black', deck_name, deck_logo))
            bar.next()
        for text in deck_src['whiteCards']:
            white.append(prepare_card(text, 'white', deck_name, deck_logo))
            bar.next()
    return black, white


def create_deck(deck_path, deck_name, deck_logo):
    deck = prepare_deck(deck_path, deck_name, deck_logo)
    save_img_array(deck[0], "black_card_")
    save_img_array(deck[1], "white_card_")


def read_cards_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def create_pages(deck_path, deck_name, deck_logo, margin=100):
    deck = prepare_deck(deck_path, deck_name, deck_logo)
    deck = deck[0] + deck[1]
    page_dim = (2480, 3508)
    card_dim = (deck[0].size[0], deck[0].size[1])
    grid_dim = calculate_grid_size(card_dim, page_dim, margin)
    number_of_pages = ceil(len(deck) / (grid_dim[0] * grid_dim[1]))

    pages = []
    with Bar('Preparing pages', max=number_of_pages) as bar:
        while len(deck) > 0:
            pages.append(prepare_page(deck, card_dim, grid_dim))
            bar.next()

    save_img_array(pages, "page_")


def prepare_page(deck, card_dim, grid_dim, margin=100):
    page = Image.new('RGB', (2480, 3508), "#FFFFFF")
    grid_x, grid_y = grid_dim[0], grid_dim[1]
    card_x, card_y = card_dim[0], card_dim[1]

    coords_x = margin
    coords_y = margin
    for j in range(grid_y):
        for k in range(grid_x):
            if len(deck) > 0:
                page.paste(deck.pop(), (coords_x, coords_y))
            coords_x += card_x
        coords_x -= (grid_x * card_x)
        coords_y += card_y

    return page



def calculate_grid_size(card_dim, page_dim, margin):
    grid_x = floor((page_dim[0] - 2 * margin) / card_dim[0])
    grid_y = floor((page_dim[1] - 2 * margin) / card_dim[1])
    return grid_x, grid_y


def make_blank_card():
    return prepare_card("", "white", "", Image.new('RGB', (60, 60), "#FFFFFF"))


def add_filler_cards(cards, cards_on_page):
    cards_on_last_page = cards.length() % cards_on_page
    for i in range(cards_on_last_page):
        cards.append(make_blank_card())


def save_img_array(array, name):
    i = 0
    os.mkdir('cards')
    with Bar('Saving created images', max=len(array)) as bar:
        for image in array:
            image.save('./cards/{}{}.png'.format(name, i))
            i += 1
            bar.next()


argParser = argparse.ArgumentParser(description="Makes Cards Against Humanity cards from a JSON file.", add_help=True)
argParser.add_argument("-src", "--source", help="Defines the file from which to take the card texts. " +
                                                "File must be a JSON file formatted according to the All Bad Cards " +
                                                "custom deck format")
argParser.add_argument("--title", help="The title of the deck. If not defined, the script will look for it " +
                                       "in the source file. If not found there, \"Cards Against Humanity\"" +
                                       "will be used.", default=None)
argParser.add_argument("--logo", help="The logo of the deck. If not defined, default CAH logo will be used.",
                       default="./CAH_logo.png")
argParser.add_argument("--make_pages", action="store_true", help="If used, the script will arrange the cards into" +
                                                                 "printable pages." )
args = argParser.parse_args()

# deck_name = args.title
# deck_logo = Image.open(args.logo)
# cards = args.source

deck_name = "Die Transkartensammlung"
deck_logo = Image.open("./TKS_logo.png")
cards = "./cards.json"

if True:
    create_pages(cards, deck_name, deck_logo)
else:
    create_deck(cards, deck_name, deck_logo)