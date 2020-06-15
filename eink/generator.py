from PIL import Image, ImageDraw, ImageFont
import datetime
from . import utils
from pytz import timezone, utc

EPD_WIDTH = 800
EPD_HEIGHT = 480

SIDEBAR_WIDTH = 270

eastern = timezone('US/Eastern')

root_path = ''


def today_card(width, height):
    now = datetime.datetime.now(eastern)

    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 1)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    week_day_name = now.strftime("%A")
    day_number = now.strftime("%d")
    month_year_str = now.strftime("%b") + ' ' + now.strftime("%Y")

    font_week_day_name = ImageFont.truetype(root_path + 'fonts/Roboto-Regular.ttf', 40)
    font_day_number = ImageFont.truetype(root_path + 'fonts/Roboto-Black.ttf', 110)
    font_month_year_str = ImageFont.truetype(root_path + 'fonts/Roboto-Regular.ttf', 40)

    w_week_day_name, h_week_day_name = font_week_day_name.getsize(week_day_name)
    x_week_day_name = (width / 2) - (w_week_day_name / 2)

    w_day_number, h_day_number = font_day_number.getsize(day_number)
    x_day_number = (width / 2) - (w_day_number / 2)

    w_month_year_str, h_month_year_str = font_month_year_str.getsize(month_year_str)
    x_month_year_str = (width / 2) - (w_month_year_str / 2)

    black_layer_draw.text((x_week_day_name, 5), week_day_name, font=font_week_day_name, fill=0)
    black_layer_draw.text((x_day_number, 40), day_number, font=font_day_number, fill=0)
    red_layer_draw.text((x_day_number, 40), day_number, font=font_day_number, fill=0)
    black_layer_draw.text((x_month_year_str, 150), month_year_str, font=font_month_year_str, fill=0)

    return red_layer, black_layer


def weather_card(icon, title, temp, indicator, width, height):
    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 1)

    indicator_height = 30
    height -= indicator_height

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    black_layer_draw.rectangle((0, 0, width, indicator_height), 0)

    red_icon_layer, black_icon_layer = utils.open_weather_map_icon(icon, root_path)
    red_layer.paste(red_icon_layer, (0, int(height / 2 - red_icon_layer.size[1] / 2 + indicator_height)))
    black_layer.paste(black_icon_layer, (0, int(height / 2 - black_icon_layer.size[1] / 2 + indicator_height)))

    black_layer_draw.line((red_icon_layer.size[0], height / 2 + indicator_height, width, height / 2 + indicator_height), 0, 1)

    title = title.title()

    title_size = 30

    font_title = ImageFont.truetype(root_path + 'fonts/Roboto-Regular.ttf', title_size)

    w_title, h_title = font_title.getsize(title)

    while w_title > width - red_icon_layer.size[0]:
        title_size -= 1

        font_title = ImageFont.truetype(root_path + 'fonts/Roboto-Light.ttf', title_size)

        w_title, h_title = font_title.getsize(title)

    x_title = (width - red_icon_layer.size[0]) / 2 - (w_title / 2) + red_icon_layer.size[0]
    y_title = height / 4 - h_title / 2 + indicator_height

    font_temp = ImageFont.truetype(root_path + 'fonts/Roboto-Light.ttf', 18)

    w_temp, h_temp = font_temp.getsize(temp)
    x_temp = (width - red_icon_layer.size[0]) / 2 - (w_temp / 2) + red_icon_layer.size[0]
    y_temp = height / 4 * 3 - h_temp / 2 + indicator_height

    font_subtitle = ImageFont.truetype(root_path + 'fonts/Roboto-Light.ttf', 15)

    w_subtitle, h_subtitle = font_subtitle.getsize(indicator)

    x_subtitle = width / 2 - (w_subtitle / 2)
    y_subtitle = h_subtitle / 2

    black_layer_draw.text((x_title, y_title), title, font=font_title, fill=0)
    black_layer_draw.text((x_temp, y_temp), temp, font=font_temp, fill=0)
    black_layer_draw.text((x_subtitle, y_subtitle), indicator, font=font_subtitle, fill=1)

    return red_layer, black_layer


def sidebar(weather_data, width, height):
    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 1)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    now = datetime.datetime.now(eastern)

    red_card, black_card = today_card(width, 200)

    red_layer.paste(red_card, (0, 0))
    black_layer.paste(black_card, (0, 0))

    current = weather_data['current']

    red_card, black_card = weather_card(
        current['weather'][0]['icon'],
        current['weather'][0]['description'].title(),
        '{} °F / {} °F'.format(round(current['feels_like']), round(current['temp'])),
        'Now',
        width,
        120
    )

    red_layer.paste(red_card, (0, 200))
    black_layer.paste(black_card, (0, 200))

    if now.hour < 19:
        today = weather_data['today']

        red_card, black_card = weather_card(
            today['weather'][0]['icon'],
            today['weather'][0]['description'].title(),
            '{} °F / {} °F'.format(round(today['temp']['min']), round(today['temp']['max'])),
            'Today',
            width,
            120
        )

    else:
        tomorrow = weather_data['tomorrow']

        red_card, black_card = weather_card(
            tomorrow['weather'][0]['icon'],
            tomorrow['weather'][0]['description'].title(),
            '{} °F / {} °F'.format(round(tomorrow['temp']['min']), round(tomorrow['temp']['max'])),
            'Today',
            width,
            120
        )

    red_layer.paste(red_card, (0, 320))
    black_layer.paste(black_card, (0, 320))

    black_layer_draw.rectangle((0, 440, width, height), 0)

    font_status = ImageFont.truetype(root_path + 'fonts/Roboto-Light.ttf', 18)

    status_text = 'Updated: ' + now.strftime('%H:%M:%S')
    w_status, h_status = font_status.getsize(status_text)

    black_layer_draw.text(
        (width / 2 - w_status / 2, height - 30),
        status_text,
        font=font_status, fill=255)

    return red_layer, black_layer


def calendar_prepare(events):
    now = datetime.datetime.now(eastern)
    items = []

    for event in events:
        start = datetime.datetime.strptime(event['start']['dateTime'].replace('-04:00','-0400'), '%Y-%m-%dT%H:%M:%S%z')
        end = datetime.datetime.strptime(event['end']['dateTime'].replace('-04:00','-0400'), '%Y-%m-%dT%H:%M:%S%z')

        items.append({
            'left': '[{}-{}]'.format(start.strftime('%I:%M'), end.strftime('%I:%M')),
            'left_red': True if start <= (now + datetime.timedelta(hours=3)) else False,
            'main': event['summary'] if now < start else '>>> {} <<<'.format(event['summary']),
            'main_red': True if now >= start else False,
            'right': '[{}]'.format(event['calendar']),
            'right_red': False,
            'type': 'calendar'
        })

    return items


def task_prepare(tasks):
    now = datetime.datetime.now(eastern)
    today = datetime.datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=eastern)
    yesterday = today - datetime.timedelta(days=1)

    items = []

    for task in tasks:
        due = None if task['dueDate'] == '' else datetime.datetime.strptime(task['dueDate']+'-0400', '%Y-%m-%dT%H:%M:%S%z')

        if due is None:
            left_string = ''
            left_red = False
        elif due <= yesterday:
            left_string = '[{}]'.format(due.strftime('%m/%d'))
            left_red = True
        elif due <= now:
            left_string = '[{}]'.format(due.strftime('%I:%M'))
            left_red = True
        elif due <= today:
            left_string = '[{}]'.format(due.strftime('%I:%M'))
            left_red = False
        else:
            left_string = '[{}]'.format(due.strftime('%m/%d'))
            left_red = False

        items.append({
            'left': left_string,
            'left_red': left_red,
            'main': task['name'],
            'main_red': False,
            'right': '[{}]'.format('Inbox' if task['inInbox'] else task['containingProjectName']),
            'right_red': False,
            'type': 'task'
        })

    return items


def habitica_prepare(tasks):
    now = datetime.datetime.now(eastern)
    items = []

    for task in tasks:
        if task['type'] != 'daily' or not task['isDue'] or task['completed']:
            continue

        items.append({
            'left': now.strftime('%m/%d'),
            'left_red': False,
            'main': task['text'],
            'main_red': False,
            'right': '[Habitica]',
            'right_red': False,
            'type': 'habitica'
        })

    return items


def main_content(data, width, height):
    items = calendar_prepare(data['calendar']['events'])
    items += task_prepare(data['omnifocus']['tasks'])
    items += habitica_prepare(data['habitica']['data'])

    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 1)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    font = ImageFont.truetype(root_path + 'fonts/Roboto-Light.ttf', 17)
    h_offset = -8

    for i in range(len(items)):
        item = items[i]

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

        h_offset += 32

        if height - h_offset > h:
            if i < len(items) - 1:
                if item['type'] != items[i + 1]['type']:
                    black_layer_draw.line((0, h_offset, width, h_offset), 0, 3)
                else:
                    black_layer_draw.line((0, h_offset, width, h_offset), 0, 1)

        h_offset += -6

        if h_offset + 2.5 * h >= height and len(items) - i > 1:
            text = 'And {} more ...'.format(len(items) - i)

            w, h = font.getsize(text)
            x = width / 2 - w / 2
            y = (height - h_offset) / 2 + h_offset - h / 2

            red_layer_draw.text((x, y), text, font=font, fill=0)

            break

    return red_layer, black_layer


def debug(red_image, black_image, save=False, show=False):
    debug_image = Image.new('RGB', red_image.size, (255, 255, 255))
    pixels = debug_image.load()

    for i in range(debug_image.size[0]):
        for j in range(debug_image.size[1]):
            if red_image.getpixel((i, j)) == 0:
                pixels[i, j] = (255, 0, 0)
            elif black_image.getpixel((i, j)) == 0:
                pixels[i, j] = (0, 0, 0)

    if save:
        debug_image.save(root_path + 'debug.bmp')
    if show:
        debug_image.show()


def generator(data, path=''):
    global root_path
    root_path = path

    red_layer = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)
    black_layer = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 1)

    red_card, black_card = sidebar(data['weather'], SIDEBAR_WIDTH, EPD_HEIGHT)
    red_layer.paste(red_card, (0, 0))
    black_layer.paste(black_card, (0, 0))

    red_card, black_card = main_content(data, EPD_WIDTH - SIDEBAR_WIDTH, EPD_HEIGHT)
    red_layer.paste(red_card, (SIDEBAR_WIDTH, 0))
    black_layer.paste(black_card, (SIDEBAR_WIDTH, 0))

    black_layer.save(root_path + 'black.bmp')
    red_layer.save(root_path + 'red.bmp')
    debug(red_layer, black_layer, save=True)

    return True


if __name__ == '__main__':
    data = {}
    generator(data)
