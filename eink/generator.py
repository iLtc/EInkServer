from PIL import Image, ImageDraw, ImageFont
import datetime

EPD_WIDTH = 800
EPD_HEIGHT = 480

SIDEBAR_WIDTH = 300


def today_calendar(width, height):
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()

    red_layer = Image.new('1', (width, height), 1)
    black_layer = Image.new('1', (width, height), 0)

    red_layer_draw = ImageDraw.Draw(red_layer)
    black_layer_draw = ImageDraw.Draw(black_layer)

    week_day_name = now.strftime("%A")
    day_number = now.strftime("%d")
    month_year_str = now.strftime("%b") + ' ' + now.strftime("%Y")

    font_week_day_name = ImageFont.truetype('fonts/Roboto-Regular.ttf', 40)
    font_day_number = ImageFont.truetype('fonts/Roboto-Black.ttf', 110)
    font_month_year_str = ImageFont.truetype('fonts/Roboto-Regular.ttf', 40)

    w_week_day_name, h_week_day_name = font_week_day_name.getsize(week_day_name)
    x_week_day_name = (width / 2) - (w_week_day_name / 2)

    w_day_number, h_day_number = font_day_number.getsize(day_number)
    x_day_number = (width / 2) - (w_day_number / 2)

    w_month_year_str, h_month_year_str = font_month_year_str.getsize(month_year_str)
    x_month_year_str = (width / 2) - (w_month_year_str / 2)

    black_layer_draw.text((x_week_day_name, 5), week_day_name, font=font_week_day_name, fill=255)
    black_layer_draw.text((x_day_number, 40), day_number, font=font_day_number, fill=255)
    red_layer_draw.text((x_day_number, 40), day_number, font=font_day_number, fill=0)
    black_layer_draw.text((x_month_year_str, 150), month_year_str, font=font_month_year_str, fill=255)

    return red_layer, black_layer


def sidebar(width, height):
    red_card, black_card = today_calendar(width, 200)

    debug(red_card, black_card, show=True)


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
        debug_image.save('debug.bmp')
    if show:
        debug_image.show()


def generator():
    sidebar(SIDEBAR_WIDTH, EPD_HEIGHT)


if __name__ == '__main__':
    generator()
