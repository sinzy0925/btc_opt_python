アプリケーションの目的：仮想通貨取引所bybitのビットコインオプションの買値、売値などを定期的に取得すること。
bybitのビットコインオプションのURLはこちら　
＝＞　https://www.bybit.com/trade/option/usdc/BTC

アプリケーションの仕様書をchatGPTで作成した。　
＝＞　https://chatgpt.com/share/66f08d8b-d5d4-8002-ba5a-0ad924434903

ローカル　起動方法
python btc_option.py

起動すると、下記ブラウザで表示される設定に基づき、ヘッドレスFirefoxでbybitの情報を取得します。

起動後、ブラウザに　http://127.0.0.1:8080/static と入力してください。
上部には、取得したデータへのリンク一覧
下部には、データを取得するための設定などができるインプット領域があります。




