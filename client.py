import requests
import config
from PIL import Image
from io import BytesIO
import sys


def server(debug=False):
    r = requests.get('{}/refresh?token={}'.format(
        config.SERVER_DOMAIN,
        config.SERVER_TOKEN
    ))

    if r.status_code == requests.codes.ok:
        data = requests.get('{}/red.bmp?token={}'.format(
            config.SERVER_DOMAIN,
            config.SERVER_TOKEN
        ))

        image = Image.open(BytesIO(data.content))

        image.save('red.bmp')

        data = requests.get('{}/black.bmp?token={}'.format(
            config.SERVER_DOMAIN,
            config.SERVER_TOKEN
        ))

        image = Image.open(BytesIO(data.content))

        image.save('black.bmp')

        if debug:
            data = requests.get('{}/debug.bmp?token={}'.format(
                config.SERVER_DOMAIN,
                config.SERVER_TOKEN
            ))

            image = Image.open(BytesIO(data.content))

            image.save('debug.bmp')

        return True

    else:
        return False


def client(clear=False):
    from waveshare_epd import epd7in5bc_V2

    black_layer = Image.open('black.bmp')
    red_layer = Image.open('red.bmp')

    epd = epd7in5bc_V2.EPD()
    epd.init()

    if clear:
        epd.Clear()

    epd.display(epd.getbuffer(black_layer), epd.getbuffer(red_layer))

    epd.sleep()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('python3 eink.py [server [debug]] [client [clear]]')

    if len(sys.argv) >= 2:
        if 'server' in sys.argv:
            red_image, black_image = server(debug=('debug' in sys.argv))

        if 'client' in sys.argv:
            if 'clear' in sys.argv:
                client(clear=True)
            else:
                client(clear=False)
