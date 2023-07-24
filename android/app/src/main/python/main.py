import threading
import time
import sys
import random
import webview


html = """
<!DOCTYPE html>
<html>
<head lang="en">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    #response-container {
        display: none;
        padding: 3rem;
        margin: 3rem 5rem;
        font-size: 120%;
        border: 5px dashed #ccc;
    }

    label {
        margin-left: 0.3rem;
        margin-right: 0.3rem;
    }

    button {
        font-size: 100%;
        padding: 0.5rem;
        margin: 0.3rem;
        text-transform: uppercase;
    }

    .top-bar {
        width:100%;
        position:fixed;
        -webkit-backface-visibility: hidden;
        top:0px;
        left: 0px;
        z-index:1000;
        height:56px;
        background-color:#1976D2;
        color: white;
        display: flex;
        align-items: center;
        padding-left: 0.5em;
        font-size: 24px;
        box-shadow: 0 5px 2px -2px rgba(0,0,0,.2);
    }
    .header {
        height:56px;
    }
    .content {
        margin-right: 0;
        height: calc(100vh - 60px);
        overflow: scroll;
    }
</style>
</head>
<body>
<div class="header">
    <div class="top-bar">
        EXAMPLE_APP_NAME
    </div>
</div>
<div class="content">
    <p>JS API Example</p>
    <p id='pywebview-status'><i>pywebview</i> is not ready</p>

    <button onClick="initialize()">Hello Python</button><br/>
    <button id="heavy-stuff-btn" onClick="doHeavyStuff()">Perform a heavy operation</button><br/>
    <button onClick="getRandomNumber()">Get a random number</button><br/>
    <label for="name_input">Say hello to:</label><input id="name_input" placeholder="put a name here">
    <button onClick="greet()">Greet</button><br/>
    <button onClick="catchException()">Catch Exception</button><br/>
    
    
    <div id="response-container"></div>
</div>

<script>
    window.addEventListener('pywebviewready', function() {
        var container = document.getElementById('pywebview-status')
        container.innerHTML = '<i>pywebview</i> is ready'
    })

    function showResponse(response) {
        var container = document.getElementById('response-container')

        container.innerText = response.message
        container.style.display = 'block'
    }

    function initialize() {
        pywebview.api.init().then(showResponse)
    }

    function doHeavyStuff() {
        var btn = document.getElementById('heavy-stuff-btn')

        pywebview.api.doHeavyStuff().then(function(response) {
            showResponse(response)
            btn.onclick = doHeavyStuff
            btn.innerText = 'Perform a heavy operation'
        })

        showResponse({message: 'Working...'})
        btn.innerText = 'Cancel the heavy operation'
        btn.onclick = cancelHeavyStuff
    }

    function cancelHeavyStuff() {
        pywebview.api.cancelHeavyStuff()
    }

    function getRandomNumber() {
        pywebview.api.getRandomNumber().then(showResponse)
    }

    function greet() {
        var name_input = document.getElementById('name_input').value;
        pywebview.api.sayHelloTo(name_input).then(showResponse)
    }

    function catchException() {
        pywebview.api.error().catch(showResponse)
    }

</script>
</body>
</html>
"""


class Api:
    def __init__(self):
        self.cancel_heavy_stuff_flag = False

    def init(self):
        response = {
            'message': 'Hello from Python {0}'.format(sys.version)
        }
        return response

    def getRandomNumber(self):
        response = {
            'message': 'Here is a random number courtesy of randint: {0}'.format(random.randint(0, 100000000))
        }
        return response

    def doHeavyStuff(self):
        time.sleep(0.1)  # sleep to prevent from the ui thread from freezing for a moment
        now = time.time()
        self.cancel_heavy_stuff_flag = False
        for i in range(0, 1000000):
            _ = i * random.randint(0, 1000)
            if self.cancel_heavy_stuff_flag:
                response = {'message': 'Operation cancelled'}
                break
        else:
            then = time.time()
            response = {
                'message': 'Operation took {0:.1f} seconds on the thread {1}'.format((then - now), threading.current_thread())
            }
        return response

    def cancelHeavyStuff(self):
        time.sleep(0.1)
        self.cancel_heavy_stuff_flag = True

    def sayHelloTo(self, name):
        response = {
            'message': 'Hello {0}!'.format(name)
        }
        return response

    def error(self):
        raise Exception('This is a Python exception')


def main():
    """Main."""
    api = Api()
    window = webview.create_window('API example', html=html, js_api=api)
    webview.start()

    
if __name__ == '__main__':
    main()