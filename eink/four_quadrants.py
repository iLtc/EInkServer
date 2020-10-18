from .generator import progress_area, debug, calendar_prepare, task_prepare, habitica_prepare, set_root_path
from pytz import timezone, utc
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 800
EPD_HEIGHT = 480

HEADER_HEIGHT = 30

eastern = timezone('US/Eastern')

root_path = ''


def quadrant_card(items, width, height):
    width = int(width)
    height = int(height)

    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 1)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    font = ImageFont.truetype(root_path + 'fonts/timr45w.ttf', 17)
    h_offset = -8

    if len(items) == 0:
        text = 'All down! Good job!'

        w, h = font.getsize(text)
        x = width / 2 - w / 2
        y = h / 2 + h_offset

        black_layer_draw.text((x, y), text, font=font, fill=0)

        h_offset += 30

        black_layer_draw.line((0, h_offset, width, h_offset), 0, 1)

        h_offset += -6

    count = 0

    for item in items:
        count += 1

        mw, h = font.getsize(item['main'])
        y = h / 2 + h_offset

        lw, _ = font.getsize(item['left'])
        lx = 1

        rw, _ = font.getsize(item['right'])
        rx = width - rw

        space = (3 if lw > 0 else 0) + (3 if rw > 0 else 0)

        while width - lw - rw - space < mw:
            item['main'] = item['main'][:-4] + '...'
            mw, _ = font.getsize(item['main'])

        if 'main_x' not in item:
            if lw > 0:
                mx = lw + 5
            else:
                mx = 1
        else:
            mx = item['main_x']

        if item['left_red']:
            red_layer_draw.text((lx, y), item['left'], font=font, fill=0)
        else:
            black_layer_draw.text((lx, y), item['left'], font=font, fill=0)

        if item['main_red']:
            red_layer_draw.text((mx, y), item['main'], font=font, fill=0)
        else:
            black_layer_draw.text((mx, y), item['main'], font=font, fill=0)

        if item['right_red']:
            red_layer_draw.text((rx, y), item['right'], font=font, fill=0)
        else:
            black_layer_draw.text((rx, y), item['right'], font=font, fill=0)

        h_offset += 30

        if height - h_offset > h:
            black_layer_draw.line((0, h_offset, width, h_offset), 0, 1)

        h_offset += -6

        if h_offset + 2.5 * h >= height and len(items) - count > 1:
            text = 'And {} more ...'.format(len(items) - count)

            w, h = font.getsize(text)
            x = width / 2 - w / 2
            y = (height - h_offset) / 2 + h_offset - h / 2

            red_layer_draw.text((x, y), text, font=font, fill=0)

            break

    return red_layer, black_layer, items[count:]


def main_content(data, width, height, header_h=HEADER_HEIGHT, even_day=True):
    urgent_important = []
    urgent_not_important = []
    not_urgent_important = []
    not_urgent_not_important = []

    items = calendar_prepare(data['calendar']['events'])
    items += task_prepare(data['omnifocus']['tasks'])
    items += habitica_prepare(data['habitica']['data'])

    for item in items:
        if item['important']:
            if item['urgent']:
                urgent_important.append(item)
            else:
                not_urgent_important.append(item)

        else:
            if item['urgent']:
                urgent_not_important.append(item)
            else:
                not_urgent_not_important.append(item)

    red_layer = Image.new('1', (EPD_WIDTH, height), 1)
    black_layer = Image.new('1', (EPD_WIDTH, height), 1)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    font_title = ImageFont.truetype(root_path + 'fonts/Roboto-Regular.ttf', 20)

    titles = [{'text': 'Urgent',
               'x': ((width - header_h) / 4 + header_h) if even_day else ((width - header_h) / 4),
               'y': (header_h / 2) if even_day else (height - (header_h / 2)),
               'rotate': False},
              {'text': 'Not Urgent',
               'x': ((width - header_h) / 4 * 3 + header_h) if even_day else ((width - header_h) / 4 * 3),
               'y': (header_h / 2) if even_day else (height - (header_h / 2)),
               'rotate': False},
              {'text': 'Important',
               'x': (header_h / 2) if even_day else (width - header_h / 2),
               'y': ((height - header_h) / 4 + header_h) if even_day else ((height - header_h) / 4),
               'rotate': True},
              {'text': 'Not Important',
               'x': (header_h / 2) if even_day else (width - header_h / 2),
               'y': ((height - header_h) / 4 * 3 + header_h) if even_day else ((height - header_h) / 4 * 3),
               'rotate': True}]

    for title in titles:
        w, h = font_title.getsize(title['text'])

        if not title['rotate']:
            x = int(title['x'] - w / 2)
            y = int(title['y'] - h / 2)

            black_layer_draw.text((x, y), title['text'], font=font_title)
        else:
            temp_img = Image.new('1', (w, w), 1)
            temp_draw = ImageDraw.Draw(temp_img)

            temp_draw.text((0, w / 2 - h / 2), title['text'], font=font_title)

            temp_img = temp_img.rotate(90) if even_day else temp_img.rotate(-90)

            x = int(title['x'] - w / 2)
            y = int(title['y'] - w / 2)

            black_layer.paste(temp_img, (x, y))

    cards = [{'data': urgent_important,
              'x': (header_h + 2) if even_day else 0,
              'y': (header_h + 2) if even_day else 0,
              'accept_left': False},
             {'data': urgent_not_important,
              'x': (header_h + 2) if even_day else 0,
              'y': (header_h + (height - header_h) / 2 + 2) if even_day else ((height - header_h) / 2 + 2),
              'accept_left': True},
             {'data': not_urgent_important,
              'x': (header_h + (width - header_h) / 2 + 2) if even_day else ((width - header_h) / 2),
              'y': (header_h + 2) if even_day else 0,
              'accept_left': False},
             {'data': not_urgent_not_important,
              'x': (header_h + (width - header_h) / 2 + 2) if even_day else ((width - header_h) / 2),
              'y': (header_h + (height - header_h) / 2 + 2) if even_day else ((height - header_h) / 2 + 2),
              'accept_left': True}]

    tasks_left = []

    for card in cards:
        if not card['accept_left']:
            tasks_left = []

        red_card_layer, black_card_layer, tasks_left = quadrant_card(
            tasks_left + card['data'],
            (width - header_h) / 2 - 2,
            (height - header_h) / 2 - 4)

        red_layer.paste(red_card_layer, (int(card['x']), int(card['y'])))
        black_layer.paste(black_card_layer, (int(card['x']), int(card['y'])))

    if even_day:
        black_layer_draw.line((0, header_h, width, header_h), 0, 2)
        black_layer_draw.line((header_h, 0, header_h, height), 0, 2)
        black_layer_draw.line((0, header_h + (height - header_h) / 2, width, header_h + (height - header_h) / 2), 0, 2)
        black_layer_draw.line((header_h + (width - header_h) / 2, 0, header_h + (width - header_h) / 2, height), 0, 2)
    else:
        black_layer_draw.line((0, height - header_h, width, height - header_h), 0, 2)
        black_layer_draw.line((width - header_h - 2, 0, width - header_h - 2, height), 0, 2)
        black_layer_draw.line((0, (height - header_h) / 2, width, (height - header_h) / 2), 0, 2)
        black_layer_draw.line(((width - header_h) / 2 - 2, 0, (width - header_h) / 2 - 2, height), 0, 2)

    return red_layer, black_layer


def generator(data, path=''):
    global root_path
    root_path = path

    set_root_path(path)

    red_layer = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
    black_layer = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
    black_layer_draw = ImageDraw.Draw(black_layer)

    red_card, black_card = progress_area(
        data['toggl']['categories'],
        int(EPD_HEIGHT / len(data['toggl']['categories'])),
        EPD_HEIGHT)
    red_layer.paste(red_card, (0, 0))
    black_layer.paste(black_card, (0, 0))

    black_layer_draw.line(
        (int(EPD_HEIGHT / len(data['toggl']['categories'])),
         0,
         int(EPD_HEIGHT / len(data['toggl']['categories'])),
         EPD_HEIGHT), 0, 2)

    red_card, black_card = main_content(data, EPD_WIDTH - int(EPD_HEIGHT / len(data['toggl']['categories'])) - 2, EPD_HEIGHT)
    red_layer.paste(red_card, (int(EPD_HEIGHT / len(data['toggl']['categories'])) + 2, 0))
    black_layer.paste(black_card, (int(EPD_HEIGHT / len(data['toggl']['categories'])) + 2, 0))

    black_layer.save(root_path + 'black.bmp')
    red_layer.save(root_path + 'red.bmp')
    debug(red_layer, black_layer, save=True)

    return True
