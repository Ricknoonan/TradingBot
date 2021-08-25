from flask import Flask, request, abort

app = Flask(__name__)


@app.route('https://webhook.site/6069786f-51d4-44e4-acc6-fc9d44a2577b/webhook', methods=['POST'])
def get_webhook():
    if request.method == 'POST':

        print("received data: ", request.json)

        return 'success', 200
    else:

        abort(400)


if __name__ == '__main__':
    app.run()


