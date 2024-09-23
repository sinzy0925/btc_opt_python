def send_line(linemsg):
    #動いたサンプル
    #見つけるのに苦労した
    #LINE Messaging API SDK for Pythonのv3でpush_messageする
    #公式のREADMEのコードで動かないのは、ワナだと思った。
    #https://mo22comi.com/line-messaging-api-sdk-v3/

    from linebot.v3.messaging import Configuration, MessagingApi, ApiClient, PushMessageRequest, ApiException
    import os
    from dotenv import load_dotenv
    import asyncio
    
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

if __name__ == "__main__":
    send_line('test')