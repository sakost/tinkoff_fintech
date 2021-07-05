import asyncio

from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse

from .connection import manager as con_mgr
from .redis import manager as redis_mgr
from .schemas import MessageModel

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <input type="text" id="destinationId" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            function httpGet(theUrl){
                var xmlHttp = new XMLHttpRequest();
                xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
                xmlHttp.send( null );
                return xmlHttp.responseText;
            }


            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                let messages = document.getElementById('messages');
                let message = document.createElement('li');
                let parsed = JSON.parse(JSON.parse(event.data));

                let content = document.createTextNode("#" + parsed.sender.client_id + ": " + parsed.text);
                let firstE = messages.firstChild;
                message.appendChild(content);
                messages.insertBefore(message, firstE);
            };

            var json_messages = JSON.parse(httpGet("/last_messages"))["messages"];

            for(i = 0; i < json_messages.length; i++){
                let messages = document.getElementById('messages');
                let message = document.createElement('li');

                let content = document.createTextNode("#" + json_messages[i].sender.client_id + ": " + json_messages[i].text);
                let firstE = messages.firstChild;
                message.appendChild(content);
                messages.insertBefore(message, firstE);
            }

            function sendMessage(event) {
                let destinationId = parseInt(document.getElementById("destinationId").value)
                let input = document.getElementById("messageText")
                let text = input.value
                console.log("Sending to " + destinationId + " " + text)
                let to_send = JSON.stringify({"sender": {"client_id": client_id}, "destination": {"client_id": destinationId}, "text": text})
                console.log("Raw data: " + to_send)
                ws.send(to_send)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.websocket('/ws/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    await con_mgr.connect(client_id, websocket)
    await redis_mgr.connect(client_id)

    con_task = asyncio.create_task(con_mgr.get_next_message(client_id))
    redis_task = asyncio.create_task(redis_mgr.get_next_message(client_id))
    while True:  # pylint: disable=too-many-nested-blocks
        done, _ = await asyncio.wait(  # type: ignore[var-annotated]
            [con_task, redis_task], return_when=asyncio.FIRST_COMPLETED  # type: ignore[arg-type]
        )

        break_loop = False
        for future in done:
            if future is con_task:
                if (message := await future) is None:
                    break_loop = True
                    break
                await redis_mgr.send_personal_message(message)
                con_task = asyncio.create_task(con_mgr.get_next_message(client_id))
            elif future is redis_task:
                result = await future
                await con_mgr.send_personal_message(result)
                redis_task = asyncio.create_task(redis_mgr.get_next_message(client_id))
        if break_loop:
            redis_task.cancel()
            break

    await redis_mgr.disconnect(client_id)
    await con_mgr.disconnect(client_id)


@router.get('/last_messages')
async def connect() -> dict[str, list[MessageModel]]:
    return {'messages': await redis_mgr.get_last_messages()}


@router.get('/')
async def get() -> HTMLResponse:
    return HTMLResponse(html)  # pragma: no cover
