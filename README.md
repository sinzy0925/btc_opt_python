〇アプリケーションの目的：仮想通貨取引所bybitのビットコインオプションの買値、売値などを定期的に取得すること。
bybitのビットコインオプションのURLはこちら　

＝＞　https://www.bybit.com/trade/option/usdc/BTC

〇アプリケーションの仕様書（chatGPTで作成）　

＝＞　https://chatgpt.com/share/66f08d8b-d5d4-8002-ba5a-0ad924434903

〇起動方法（ローカル）

python btc_option.py

・起動すると、下記ブラウザで表示される設定に基づき、ヘッドレスFirefoxでbybitの情報を取得します。
取得したデータは、staticフォルダに保存されます。

・予めアプリケーションフォルダ以下にstaticフォルダを作成してください。
以下のブラウザからリンクしても確認できます。

・起動後、ブラウザに　http://127.0.0.1:8080/static と入力してください。

上部には、取得したデータへのリンク一覧

下部には、データを取得するための設定などができるインプット領域があります。

〇とりあえず動かしてみる場合

・staticフォルダに添付されているファイルはそのままダウンロードしてください。

・staticフォルダの、paramDDMMYY.csvファイルを編集します。

編集方法

今日が、2024/09/25の場合 yyYY/MM/DD を DD-MM-YYに変更して、以下のように変更します。

26-09-24,27-09-24,28-09-24

〇Lineメールを送信

・チャネルアクセストークンは、　https://blog.kimizuka.org/entry/2023/11/08/232842#google_vignette　
を参考にして発行し、.envファイルに記載します。

・ユーザーIDは、　https://developers.line.biz/ja/docs/messaging-api/getting-user-ids/#get-all-friends-user-ids
を参考にして、.envファイルに記載します。

・Lineメールを発行する命令は、await send_line(linemsg)　ですが、コメントアウトしていますので、必要な方は#コメントを外してください。

・　.envの記載例（#はコメント行）
#""や''は不要です。
#参考にしたｕｒｌ https://maku77.github.io/nodejs/env/dotenv.html

・　.env

CHANNEL_TOKEN=

USER_ID=

・なお、LINE Messaging API SDK for Pythonのv3は、公式のREADMEのコードでは、動かないワナが仕掛けられているので、ご注意ください。
ここを見て、正常稼働するアプリが実装できました。　

https://mo22comi.com/line-messaging-api-sdk-v3/



以上
