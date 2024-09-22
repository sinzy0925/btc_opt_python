from flask import Flask, request, send_file, abort, send_from_directory, redirect, url_for
from playwright.async_api import async_playwright,Page
from linebot.v3.messaging import MessagingApi, TextMessage
from dotenv import load_dotenv
from datetime import datetime
import os
import csv
import asyncio
import traceback
import threading





# 環境変数の読み込み
load_dotenv()

app = Flask(__name__)

# 静的ファイルのルート
urlpath = 'static/'


@app.route('/' + urlpath + 'zdownload.html')
def static_files():
    filename = f'zdownload.html'
    return app.send_static_file(filename)

@app.route('/' + urlpath + 'download')
def download_file():
    file_path = f'{urlpath}zdownload.html'
    print('urlpath: ' + file_path)
    return send_file(file_path, as_attachment=True)


@app.route('/del', methods=['GET'])
def delete_files():
    print('Start app.get(/del)')
    delete_files_msg = ""
    files = os.listdir(urlpath)
    filter_files = [f for f in files if f.endswith('.html')]  # HTMLファイルのみ抽出

    for file in filter_files:
        os.remove(os.path.join(urlpath, file))
        print(file)
        delete_files_msg += f'<br>{file} is Deleted.\n'
    
    print(delete_files_msg)
    return f'<a href="/{urlpath}"> Home </a>' + delete_files_msg

@app.route('/' + urlpath, methods=['GET'])
def home():
    print("Start app.get()")
    
    arr_result = readfile0()
    line_alert = arr_result[0]
    arr_kenri = arr_result[1]
    arr_ddmmyy = arr_result[2]
    print('line_alert: ' + str(line_alert))
    print('arr_kenri: ' + str(arr_kenri))
    print('arr_ddmmyy: ' + str(arr_ddmmyy))   
    html_tag = maketag(line_alert, arr_kenri, arr_ddmmyy, urlpath)
    
    return html_tag

@app.route('/', methods=['POST'])
def handle_post():
    print('Start app.post("/")')
    for key, value in request.form.items():
        print(f'key: {key}, value: {value}')

    writefile0(line_alert, arr_kenri, arr_ddmmyy, request)

    print('END app.post("/")')
    return redirect(url_for('home'))


def run_flask():
    app.run(port=8080,use_reloader=False)



arr_ddmmyy = ['22-09-24', '23-09-24', '27-09-24']

cnt = -1

line_cnt = [
    [[0, 0, 0, 0, 0] for _ in range(3)],  # C
    [[0, 0, 0, 0, 0] for _ in range(3)],  # P
]

line_alert = [
    [[0, 0, 0, 0, 0] for _ in range(3)],  # C
    [[0, 0, 0, 0, 0] for _ in range(3)],  # P
]

arr_kenri = [
    [[0, 0, 0, 0, 0] for _ in range(3)],  # C
    [[0, 0, 0, 0, 0] for _ in range(3)],  # P
]





async def start():
    async with async_playwright() as p:

        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        timeout = 30000
        page.set_default_timeout(timeout)

        await page.set_viewport_size({"width": 1300, "height": 1800})

        print("page.goto() Start")
        await page.goto('https://www.bybit.com/trade/option/usdc/BTC')
        await asyncio.sleep(6)  # 6000ミリ秒
        print("page.goto('https://www.bybit.com/trade/option/usdc/BTC');")
        print("page.goto() End")

        timeout = 20000
        page.set_default_timeout(timeout)

        for l in range(5):
            arrResult = readfile0()
            line_alert = arrResult[0]
            arrKenri = arrResult[1]
            arrDDMMYY = arrResult[2]
            

            print(f"loop l[0-4] {l}, cnt: {cnt}")

            for j in range(len(arrDDMMYY)):
                await asyncio.sleep(0.5)  # 500ミリ秒
                test1 = await page.query_selector('._delivery-time_nlm51_18')

                if test1 is not None:
                    try:
                        await page.locator('._delivery-time_nlm51_18', has_text=arrDDMMYY[j]).click()
                        await asyncio.sleep(2)  # 2000ミリ秒

                        ddmmyy = arrDDMMYY[j]
                        genshi = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[3]

                        if genshi == "0.00":
                            print("genshi err")
                            await asyncio.sleep(0.5)
                            genshi = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[3]

                        if genshi == "0.00":
                            break

                        dd, mm, yy = ddmmyy.split('-')
                        arrMM = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
                        mm = arrMM[int(mm)]
                        dd = int(dd)

                        print(f"\ndd-mm-yy: {ddmmyy}, {dd}{mm}{yy}, genshisan: {genshi}\n")

                        await callput(page, dd, mm, yy, j, arrDDMMYY, l, cnt, line_cnt, line_alert, arrKenri)

                    except Exception as e:
                        print(f'for(let j = 0 ; j < arrDDMMYY.length ; j++) err: {str(e)}')

        page.close()
        context.close()
        browser.close()













async def callput(page, dd, mm, yy, j, arr_ddmmyy, l, cnt, line_cnt, line_alert, arr_kenri):
    path = ''
    meigara = ''





    # 権利行使価
    arr_kenri_c = arr_kenri[0][j][:5]  # Call
    arr_kenri_p = arr_kenri[1][j][:5]  # Put

    # Call処理
    for i in range(5):
        await page.wait_for_timeout(500)

        btc_c = f"{dd}{mm}{yy}-{arr_kenri_c[i]}"
        btc_c_line = f"BTC-Options\n{arr_ddmmyy[j]}\n-{arr_kenri_c[i]}000[C]"
        meigara = f"{arr_ddmmyy[j].split('-')[2]}{arr_ddmmyy[j].split('-')[1]}{arr_ddmmyy[j].split('-')[0]}C-{arr_kenri_c[i]}"
        path = f"{urlpath}{meigara}.html"  # 例：urlpath

        # コール側をクリックできるか確認

        test1 = await page.query_selector(f"#BTC-{btc_c}000")
        
        if test1 is not None:
            try:
                print(f"Start async function CALL[{i}] #{btc_c}000")
                await page.wait_for_timeout(500)
                await page.locator(f"#BTC-{btc_c}000 canvas").click(position={'x': 200, 'y': 15})
                await page.wait_for_timeout(2000)

                # 権利行使価格
                kenri = await page.locator('//*[@id="orderContainer"]/div[2]/div[1]/div/div[2]').inner_text()

                # 日付
                ymd = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')

                # 原資産
                genshi = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[3]
                genshi = int(genshi.replace(',', '').split('.')[0])

                # ボラティリティ
                vola = await page.locator('//*[@id="orderContainer"]/div[2]/div[2]/div[1]').inner_text()
                vola = int(vola.split('\n')[3].split('%')[0].split('.')[0])

                # 価格
                kakaku = await page.locator('//*[@id="orderContainer"]/div[2]/div[2]/div[2]/div[1]/div/div[1]').inner_text()
                sell = kakaku.split('\n')[17].replace(',', '').split('.')[0]
                mark = kakaku.split('\n')[16].replace(',', '').split('.')[0]
                buy = kakaku.split('\n')[11].replace(',', '').split('.')[0]

                # 価格の変換
                sell = int(sell) if sell.isdigit() else 0
                mark = int(mark) if mark.isdigit() else 0
                buy = int(buy) if buy.isdigit() else 0

                # 残り時間
                nokori = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[11:14]
                nokori = ' '.join(nokori).split('min')[0]

                res_c = f"{ymd},{nokori},<br>," + f"{genshi},<font color='red'>[,{sell},]</font>,{mark},{buy},{vola}," + f"{meigara},<br>\n"
                
                if not isinstance(sell, float) and not isinstance(sell, int):
                    print(f"{meigara} sell is NaN")
                else:
                    with open(path, 'a') as f:
                        f.write(res_c)
                    sorted_data = sort_func(path)  # sort_funcは別途定義
                    with open(path, 'w') as f:
                        f.write(sorted_data)

                    with open(f'{urlpath}zdownload.html', 'a') as f:
                        f.write(res_c)

                await page.wait_for_timeout(500)

                line_count = line_cnt[0][j][i]

                line_alert[0][j][i] = int(line_alert[0][j][i]) if line_alert[0][j][i].isdigit() else 0

                if sell > line_alert[0][j][i] and line_count < 5:
                    linemsg = (f"[SELL Alert]>{line_alert[0][j][i]}\n\n"
                                f"{btc_c_line}\n[Sell]:{sell}\n[原資産]:{genshi}\n{ymd}\nCount:{line_count + 1}")
                    #await send_line(linemsg)  # send_lineは別途定義
                    print(linemsg)
                    line_cnt[0][j][i] += 1

                print(f"{meigara} Alert {line_alert[0][j][i]} CountC{i} {line_count}")

            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()

    # Put処理
    for i in range(5):
        await page.wait_for_timeout(500)

        btc_p = f"{dd}{mm}{yy}-{arr_kenri_p[i]}"
        btc_p_line = f"BTC-Options\n{arr_ddmmyy[j]}\n-{arr_kenri_p[i]}000[P]"
        meigara = f"{arr_ddmmyy[j].split('-')[2]}{arr_ddmmyy[j].split('-')[1]}{arr_ddmmyy[j].split('-')[0]}P-{arr_kenri_p[i]}"
        path = f"{urlpath}{meigara}.html"

        # Put側をクリックできるか確認
        test1 = await page.query_selector(f"#BTC-{btc_p}000")

        if test1 is not None:
            try:
                print(f"Start async function PUT[{i}] #{btc_p}000")
                await page.wait_for_timeout(500)
                await page.locator(f"#BTC-{btc_p}000 canvas").click(position={'x': 600, 'y': 15})
                await page.wait_for_timeout(2000)

                # 権利行使価格
                kenri = await page.locator('//*[@id="orderContainer"]/div[2]/div[1]/div/div[2]').inner_text()

                # 日付
                ymd = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S')

                # 原資産
                genshi = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[3]
                genshi = int(genshi.replace(',', '').split('.')[0])

                # ボラティリティ
                vola = await page.locator('//*[@id="orderContainer"]/div[2]/div[2]/div[1]').inner_text()
                vola = int(vola.split('\n')[3].split('%')[0].split('.')[0])

                # 価格
                kakaku = await page.locator('//*[@id="orderContainer"]/div[2]/div[2]/div[2]/div[1]/div/div[1]').inner_text()
                sell = kakaku.split('\n')[17].replace(',', '').split('.')[0]
                mark = kakaku.split('\n')[16].replace(',', '').split('.')[0]
                buy = kakaku.split('\n')[11].replace(',', '').split('.')[0]

                # 価格の変換
                sell = int(sell) if sell.isdigit() else 0
                mark = int(mark) if mark.isdigit() else 0
                buy = int(buy) if buy.isdigit() else 0


                # 残り時間
                nokori = (await page.locator('//*[@id="quote_list"]').inner_text()).split(' ')[11:14]
                nokori = ' '.join(nokori).split('min')[0]

                res_c = f"{ymd},{nokori},<br>," + f"{genshi},<font color='red'>[,{sell},]</font>,{mark},{buy},{vola}," + f"{meigara},<br>\n"

                if not isinstance(sell, float) and not isinstance(sell, int):
                    print(f"{meigara} sell is NaN")
                else:
                    with open(path, 'a') as f:
                        f.write(res_c)
                    sorted_data = sort_func(path)
                    with open(path, 'w') as f:
                        f.write(sorted_data)

                    with open(f'{urlpath}zdownload.html', 'a') as f:
                        f.write(res_c)
                    if i == 4:
                        sorted1 = sort_func(f'{urlpath}zdownload.html')
                        with open(f'{urlpath}zdownload.html', 'w') as f:
                            f.write(sorted1)

                await page.wait_for_timeout(500)

                line_count = line_cnt[1][j][i]

                
                line_alert[1][j][i] = int(line_alert[1][j][i]) if line_alert[1][j][i].isdigit() else 0

                if sell > line_alert[1][j][i] and line_count < 5:

                    linemsg = (f"[SELL Alert]>{line_alert[1][j][i]}\n\n"
                                f"{btc_p_line}\n[Sell]:{sell}\n[原資産]:{genshi}\n{ymd}\nCount:{line_count + 1}")
                    #await send_line(linemsg)
                    print(linemsg)
                    line_cnt[1][j][i] += 1


                print(f"{meigara} Alert {line_alert[1][j][i]} CountP{i} {line_count}")

            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()







async def send_line(linemsg):
    #動いたサンプル
    #見つけるのに苦労した
    #LINE Messaging API SDK for Pythonのv3でpush_messageする
    #公式のREADMEのコードで動かないのは、ワナだと思った。
    #https://mo22comi.com/line-messaging-api-sdk-v3/

    from linebot.v3.messaging import Configuration, MessagingApi, ApiClient, PushMessageRequest, ApiException
    import os
    from dotenv import load_dotenv
    
    load_dotenv()

    CHANNEL_TOKEN = os.getenv('CHANNEL_TOKEN')
    USER_ID = os.getenv('USER_ID')
    MY_ID = os.getenv('MY_ID')

    configuration = Configuration(
        access_token = CHANNEL_TOKEN
    )

    message_dict = {
        'to': USER_ID,
        'messages': [
            {'type': 'text', 
             'text': f'[Bybit]\n[USDCオプション]\n{linemsg}'
             }
        ]
    }

    with ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = MessagingApi(api_client)
        push_message_request = PushMessageRequest.from_dict(message_dict)

        try:
            push_message_result = api_instance.push_message_with_http_info(push_message_request, _return_http_data_only=False)
            print(f'送信メッセージ ： \n{message_dict.get('messages')[0].get('text')}')
            print(f'送信成功 -> status code => {push_message_result.status_code}')

        except ApiException as e:
            print('Exception when calling MessagingApi->push_message: %s\n' % e)




def readfile0():
    print("Start readfile0()")
    
    line_alert = [[[0, 0, 0, 0, 0] for _ in range(3)] for _ in range(2)]  # CとP
    arr_kenri = [[[0, 0, 0, 0, 0] for _ in range(3)] for _ in range(2)]  # CとP
    arr_ddmmyy = ['0', '0', '0']  # DDMMYY用の配列

    try:

        # CSVファイルの読み込み
        files = [
            "paramAlertC0.csv", "paramAlertC1.csv", "paramAlertC2.csv",
            "paramAlertP0.csv", "paramAlertP1.csv", "paramAlertP2.csv",
            "paramKenriC0.csv", "paramKenriC1.csv", "paramKenriC2.csv",
            "paramKenriP0.csv", "paramKenriP1.csv", "paramKenriP2.csv",
            "paramDDMMYY.csv"
        ]

        # ファイルパスの設定
        file_paths = [os.path.join(urlpath, f) for f in files]

        # 各ファイルを読み込む
        for i in range(3):
            with open(file_paths[i], 'r', encoding='utf-8') as f:
                line_alert[0][i] = list(csv.reader(f))[0][:-1]

        print(f"line_alert[0][0]: {line_alert[0][0]}")





        for i in range(3):
            with open(file_paths[i + 3], 'r', encoding='utf-8') as f:
                line_alert[1][i] = list(csv.reader(f))[0][:-1]

        for i in range(3):
            with open(file_paths[i + 6], 'r', encoding='utf-8') as f:
                arr_kenri[0][i] = list(csv.reader(f))[0][:-1]
        
        for i in range(3):
            with open(file_paths[i + 9], 'r', encoding='utf-8') as f:
                arr_kenri[1][i] = list(csv.reader(f))[0][:-1]

        # DDMMYYの読み込み
        with open(file_paths[-1], 'r', encoding='utf-8') as f:
            arr_ddmmyy = list(csv.reader(f))[0]

        # デバッグ用出力
        for i in range(3):
            print(f'read paramAlertC{i}.csv => AlertC{i}: {line_alert[0][i]}')
            print(f'read paramAlertP{i}.csv => AlertP{i}: {line_alert[1][i]}')
        for i in range(3):
            print(f'read paramKenriC{i}.csv => KenriC{i}: {arr_kenri[0][i]}')
            print(f'read paramKenriP{i}.csv => KenriP{i}: {arr_kenri[1][i]}')
        print(f'read paramDDMMYY.csv => DDMMYY: {arr_ddmmyy}')

        # arr_ddmmyyの長さを確認し、足りない場合はデフォルト値を追加
        while len(arr_ddmmyy) < 3:
            arr_ddmmyy.append('0')

    except Exception as e:
        print(e)

    print("End readfile0()")
    return [line_alert, arr_kenri, arr_ddmmyy]


def writefile0(line_alert, arr_kenri, arr_ddmmyy, req):
    print("Start writefile0(lineAlert, arrKenri, arrDDMMYY, req)")

    # POSTリクエストからデータを取得
    arr_ddmmyy[0] = req.form.getlist('ddmmyy0')
    arr_ddmmyy[1] = req.form.getlist('ddmmyy1')
    arr_ddmmyy[2] = req.form.getlist('ddmmyy2')

    for i in range(5):
        arr_kenri[0][0][i] = req.form.getlist('kenriC0')[i] 
        line_alert[0][0][i] = req.form.getlist('alertC0')[i]
        arr_kenri[1][0][i] = req.form.getlist('kenriP0')[i]
        line_alert[1][0][i] = req.form.getlist('alertP0')[i]
        arr_kenri[0][1][i] = req.form.getlist('kenriC1')[i]
        line_alert[0][1][i] = req.form.getlist('alertC1')[i]
        arr_kenri[1][1][i] = req.form.getlist('kenriP1')[i]
        line_alert[1][1][i] = req.form.getlist('alertP1')[i]
        arr_kenri[0][2][i] = req.form.getlist('kenriC2')[i]
        line_alert[0][2][i] = req.form.getlist('alertC2')[i]
        arr_kenri[1][2][i] = req.form.getlist('kenriP2')[i]
        line_alert[1][2][i] = req.form.getlist('alertP2')[i]

    la = [['' for _ in range(3)] for _ in range(2)]
    ke = [['' for _ in range(3)] for _ in range(2)]

    for k in range(2):  # Call PUT
        for j in range(3):  # DAY
            for i in range(5):
                la[k][j] += line_alert[k][j][i] + ','
                ke[k][j] += arr_kenri[k][j][i] + ','

    # CSVファイルへの書き込み
    with open(os.path.join(urlpath, "paramDDMMYY.csv"), 'w', encoding='utf-8') as f:
        f.write(arr_ddmmyy[0][0] + ',' + arr_ddmmyy[1][0] + ',' + arr_ddmmyy[2][0])

    for i in range(3):
        with open(os.path.join(urlpath, f"paramAlertC{i}.csv"), 'w', encoding='utf-8') as f:
            f.write(la[0][i])
        with open(os.path.join(urlpath, f"paramAlertP{i}.csv"), 'w', encoding='utf-8') as f:
            f.write(la[1][i])
    
    for i in range(3):
        with open(os.path.join(urlpath, f"paramKenriC{i}.csv"), 'w', encoding='utf-8') as f:
            f.write(ke[0][i])
        with open(os.path.join(urlpath, f"paramKenriP{i}.csv"), 'w', encoding='utf-8') as f:
            f.write(ke[1][i])

    # デバッグ用出力
    for i in range(3):
        print(f"write paramKenriC{i}.csv: {ke[0][i]}")
        print(f"write paramAlertC{i}.csv: {la[0][i]}")
        print(f"write paramKenriP{i}.csv: {ke[1][i]}")
        print(f"write paramAlertP{i}.csv: {la[1][i]}")

    print("END writefile0(lineAlert, arrKenri, arrDDMMYY, req)")





def maketag(line_alert, arr_kenri, arr_ddmmyy, urlpath):
    print("Start maketag(lineAlert, arrKenri, arrDDMMYY)")

    # arr_ddmmyyの長さを確認し、足りない場合はデフォルト値を追加
    while len(arr_ddmmyy) < 4:
        arr_ddmmyy.append('0-0-0')

    # ディレクトリ内のファイルを取得
    files = os.listdir(urlpath)
    filter_files = [f for f in files if f.endswith('.html')]  # .html拡張子のファイルを抽出


    print('1arr_ddmmyy:',arr_ddmmyy)
    # 各要素が正しい形式であることを確認し、必要に応じてデフォルト値を設定
    arr_ddmmyy = [ddmmyy if len(ddmmyy.split('-')) == 3 else '0-0-0' for ddmmyy in arr_ddmmyy]
    print('2arr_ddmmyy:',arr_ddmmyy)

    day0c = [f for f in files if f.startswith(arr_ddmmyy[0].split('-')[2] + arr_ddmmyy[0].split('-')[1] + arr_ddmmyy[0].split('-')[0] + 'C')]
    day0p = [f for f in files if f.startswith(arr_ddmmyy[0].split('-')[2] + arr_ddmmyy[0].split('-')[1] + arr_ddmmyy[0].split('-')[0] + 'P')]
    day1c = [f for f in files if f.startswith(arr_ddmmyy[1].split('-')[2] + arr_ddmmyy[1].split('-')[1] + arr_ddmmyy[1].split('-')[0] + 'C')]
    day1p = [f for f in files if f.startswith(arr_ddmmyy[1].split('-')[2] + arr_ddmmyy[1].split('-')[1] + arr_ddmmyy[1].split('-')[0] + 'P')]
    day2c = [f for f in files if f.startswith(arr_ddmmyy[2].split('-')[2] + arr_ddmmyy[2].split('-')[1] + arr_ddmmyy[2].split('-')[0] + 'C')]
    day2p = [f for f in files if f.startswith(arr_ddmmyy[2].split('-')[2] + arr_ddmmyy[2].split('-')[1] + arr_ddmmyy[2].split('-')[0] + 'P')]

    # 最後の要素を無視
    filter_files = filter_files[:-1] 

    # HTMLリンクの生成
    def generate_links(day_files):
        return ''.join(f'<td><a href="{f}">{f}</a></td>\n' for f in day_files)

    sq0C = generate_links(day0c)
    sq0P = generate_links(day0p)
    sq1C = generate_links(day1c)
    sq1P = generate_links(day1p)
    sq2C = generate_links(day2c)
    sq2P = generate_links(day2p)

    # テーブルの生成
    pathtext = '<table><tbody>'
    pathtext += f'<tr><td>{arr_ddmmyy[0]}</td></tr>\n'
    pathtext += f'<tr>\n{sq0C}</tr>\n'
    pathtext += f'<tr>\n{sq0P}</tr>\n'
    pathtext += f'<tr></tr><tr><td>{arr_ddmmyy[1]}</td></tr><tr></tr>\n'
    pathtext += f'<tr>\n{sq1C}</tr>\n'
    pathtext += f'<tr>\n{sq1P}</tr>\n'
    pathtext += f'<tr></tr><tr><td>{arr_ddmmyy[2]}</td></tr><tr></tr>\n'
    pathtext += f'<tr>\n{sq2C}</tr>\n'
    pathtext += f'<tr>\n{sq2P}</tr>\n'
    pathtext += '</tbody></table>\n'

    # 入力フィールドの生成
    def generate_inputs(arr_kenri, line_alert, index,type):
        inputs = ''
        if type == 'C':
            for i in range(5):
                inputs += f'<input type="text" size="1" name="kenriC{index}" value="{arr_kenri[0][index][i]}">\n'
            inputs += ' Alert '
            for i in range(5):
                inputs += f'<input type="text" size="2" name="alertC{index}" value="{line_alert[0][index][i]}">\n'

        else:
            for i in range(5):
                inputs += f'<input type="text" size="1" name="kenriP{index}" value="{arr_kenri[1][index][i]}">\n'
            inputs += ' Alert '
            for i in range(5):
                inputs += f'<input type="text" size="2" name="alertP{index}" value="{line_alert[1][index][i]}">\n'

        return inputs

    sq0Cc = generate_inputs(arr_kenri, line_alert, 0,'C')
    sq1Cc = generate_inputs(arr_kenri, line_alert, 1,'C')
    sq2Cc = generate_inputs(arr_kenri, line_alert, 2,'C')
    sq0Cp = generate_inputs(arr_kenri, line_alert, 0,'P')
    sq1Cp = generate_inputs(arr_kenri, line_alert, 1,'P')
    sq2Cp = generate_inputs(arr_kenri, line_alert, 2,'P')

    # HTMLフォームの生成
    htmltag = (
        '<br><a href="zdownload.html">データ表示　：全データファイル</a>\n'
        '<br><a href="download">/download ダウンロード：全データファイル</a>\n'
        '<br><a href="../del">/del ファイル削除：全データファイル（ダウンロード後）</a>\n'
        '<br><form action="/" method="post">\n'
        'パラメータ設定　※注意：ＳＱ日以外は、すべて数値で入力してください！\n'
        f'<br>ＳＱ日０ : \n<input type="text" size="4" name="ddmmyy0" value="{arr_ddmmyy[0]}">\n'
        f'<br>ＣＡＬＬ 権利行使価格 : {sq0Cc}'
        f'<br>ＰＵＴ　 権利行使価格 : {sq0Cp}'
        f'<br>ＳＱ日１ : \n<input type="text" size="4" name="ddmmyy1" value="{arr_ddmmyy[1]}">\n'
        f'<br>ＣＡＬＬ 権利行使価格 : {sq1Cc}'
        f'<br>ＰＵＴ　 権利行使価格 : {sq1Cp}'
        f'<br>ＳＱ日２ : \n<input type="text" size="4" name="ddmmyy2" value="{arr_ddmmyy[2]}">\n'
        f'<br>ＣＡＬＬ 権利行使価格 : {sq2Cc}'
        f'<br>ＰＵＴ　 権利行使価格 : {sq2Cp}'
        '<br><input type="submit" value="送信！">\n'
        '</form>\n'
    )

    print(pathtext + htmltag)
    print("END maketag(lineAlert, arrKenri, arrDDMMYY)")
  
    return pathtext + htmltag

def sort_func(path):
    # ファイルの読み込み
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        #print(["1",lines])

    # 最後の空行を削除

    lines = lines[:-1] if lines[-1] == '\n' else lines
    #print(["2",lines])

    # 降順にソート
    sorted_lines = sorted(lines, reverse=True)
    #print(["3",sorted_lines])


    # 行をカンマ区切りで再構成
    result = ''.join(','.join(line.strip().split(',')) + '\n' for line in sorted_lines)
    #print(["4",result])

    return result


if __name__ == "__main__":
    #chatGPTに聞いた「pythonで一つの.pyファイルにflaskとmainを入れて、同時に実行したい」
    # Flaskアプリケーションを別スレッドで実行
    threading.Thread(target=run_flask).start()
    asyncio.run(start())





