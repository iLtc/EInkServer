import requests
from PIL import Image
from io import BytesIO
from os import path


def open_weather_map_icon(code, root_path):
    if path.exists(root_path + 'icons/{}@2x.png'.format(code)):
        image = Image.open(root_path + 'icons/{}@2x.png'.format(code))
    else:
        icon = requests.get('https://openweathermap.org/img/wn/{}@2x.png'.format(code))

        image = Image.open(BytesIO(icon.content))

        image.save(root_path + 'icons/{}@2x.png'.format(code))

    # image.show()

    canvas = Image.new('RGB', image.size, (255, 255, 255))

    canvas.paste(image, mask=image)

    canvas = canvas.crop((15, 15, canvas.size[0] - 15, canvas.size[1] - 15))

    # canvas.thumbnail((canvas.size[0] * 0.8, canvas.size[1] * 0.8))

    # canvas.show()

    red_image = Image.new('1', canvas.size, 1)
    black_image = Image.new('1', canvas.size, 1)

    red_pixels = red_image.load()
    black_pixels = black_image.load()

    red, green, blue = canvas.split()

    for i in range(canvas.size[0]):
        for j in range(canvas.size[1]):
            if red.getpixel((i, j)) == 255:
                continue

            if red.getpixel((i, j)) > 220 and blue.getpixel((i, j)) < 235:
                red_pixels[i, j] = 0
            else:
                black_pixels[i, j] = 0

    return red_image, black_image