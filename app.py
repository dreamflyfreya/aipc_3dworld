from flask import Flask, request, Response
import ollama

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    def generate(message):
        stream = ollama.chat(
            model='llama3.1',
            messages=[{'role': 'user', 'content': message}],
            stream=True,
        )

        for chunk in stream:
            yield chunk['message']['content']

    user_message = request.json.get('message', '')
    print(user_message)
    return Response(generate(user_message), mimetype='text/plain', direct_passthrough=True)


if __name__ == '__main__':
    app.run(debug=True)