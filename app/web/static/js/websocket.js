let socket = null;


function connectWebSocket() {

    const token = localStorage.getItem("token");

    socket = new WebSocket(
        `ws://localhost:8001/ws?token=${token}`
    );

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onclose = () => {
        console.log("WebSocket disconnected");

        setTimeout(
            connectWebSocket,
            3000,
        );
    };

    socket.onerror = (e) => {
        console.log(e);
    };

    socket.onmessage = (event) => {

        const message = JSON.parse(event.data);

        console.log(message);

    };

}