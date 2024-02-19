import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

# Define path
path = Path(os.getcwd())
tmp_path = path / Path("tmp/")
assets_path = path / Path("assets/")
graph_tmp_path = tmp_path / Path("graph.png")
font_assets_path = assets_path / Path("fonts/")
frameimg_assets_path = assets_path / Path("images/")

# Define FastAPI app
app = FastAPI()

@app.get("/")
def index():
    genImg()
    return FileResponse(path / Path("output.png"))

# Font loader
# Todo: Error handling
def font(family, size):
    if family == "Mono":
        family = font_assets_path / Path("NotoSansJP-VariableFont_wght.ttf")
    return ImageFont.truetype(family, size)

# Graph genelator
# Todo: Take real data
def genGraph():
    # 時間軸を生成
    hours = np.arange(0, 25, 1)

    # ダミーの温度データを生成
    temperature = np.random.randint(40, 60, size=25)

    # グラフを描画
    plt.figure(figsize=(10, 4))
    plt.plot(hours[:20], temperature[:20], marker='o')

    # グラフの装飾
    plt.title('Temp.')
    plt.xlabel('Hour')
    plt.ylabel('Digrees')
    plt.xticks(np.arange(0, 25, 1))
    plt.yticks(np.arange(0, 86, 10))
    plt.grid(True)
    plt.legend()

    # 19時の時点でのグラフを想定して20時から24時までを空白にする
    plt.fill_between(hours[19:], 0, 85, color='white')

    plt.subplots_adjust(left=0.05, right=0.995, bottom=0.2, top=0.995)
    plt.savefig(graph_tmp_path)
    plt.close()

# Response image genelator
# Todo: write todo here
def genImg():
    tz = datetime.timezone(datetime.timedelta(hours=9))
    dtdtnow = datetime.datetime.now(tz)
    
    # 画像データを生成
    size = (758, 1024)
    img = Image.new("L", size, "#FFF")

    # 要素配置準備
    draw = ImageDraw.Draw(img)

    ## 時計
    time_now = dtdtnow.strftime("%H:%M")
    draw.text((76,76),str(time_now), font=font("Mono",60))

    ## 日付
    date_str = dtdtnow.strftime("%b %d (%a)\n%Y")
    draw.text((480, 76),str(date_str), align="right", font=font("Mono", 35))

    ## 罫線(1)
    draw.line((76, 174, 682, 174), fill="#000", width=5)

    ## 画像
    frame_image = Image.open(frameimg_assets_path / Path("image01.jpg"))
    frame_image = frame_image.resize((300, 300), Image.LANCZOS) # LANCZOSは処理方式
    img.paste(frame_image, (76, 200))

    ## タイトル
    draw.text((400, 210),str("Headline"), align="right", font=font("Mono", 32))

    ## リスト
    list_font_size=27
    list_offset=list_font_size+5
    for i in range(5):
        draw.text((400, 260+list_offset*i),str(" - Title "+str(i)), font=font("Mono", list_font_size))

    ## グラフ
    genGraph()
    graph_image = Image.open(graph_tmp_path)
    ### リサイズ→https://pynote.hatenablog.com/entry/pillow-resize
    def scale_to_width(img, width):
        height = round(img.height * width / img.width)
        return img.resize((width, height))

    graph_image = scale_to_width(graph_image, 606)
    img.paste(graph_image, (76, 520))

    ## 罫線(2)
    draw.line((76, 953, 682, 953), fill="#000", width=5)

    # display(img.resize((379, 512), Image.LANCZOS))
    # display(img)
    img.save("output.png", quality=95)