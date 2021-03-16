import Fun from "./function"

export default {
    socket(o) {
        var oj = Fun.extend({
            ip: "127.0.0.1",
            port: 50000,
            reinit() {
                setTimeout(() => {
                    this.init()
                }, 1000)
            },
            init() {
                try {
                    this.socket = new WebSocket("ws://" + this.ip + ":" + this.port)
                } catch (e) {
                    this.socket = null
                    console.log("websocket error", e)
                }
                if (this.socket == null) {
                    return this.reinit()
                }
                this.socket.onopen = (e) => {
                    console.log(this, "websocket onopen", e)
                    this.id && this.send_json({ id: this.id })
                    this.open_success && this.open_success()
                }
                this.socket.onmessage = (e) => {
                    console.log(this, "websocket onmessage", e)
                    if (this.recv_json) {
                        this.recv_json(JSON.parse(e.data))
                    }

                }
                this.socket.onclose = (e) => {
                    console.log(this, "websocket onclose", e)
                    this.reinit()
                }
                this.socket.onerror = (e) => {
                    console.log(this, "websocket onerror", e)
                }
            },
            send_json(v) {
                this.socket.send(JSON.stringify(v))
            }
        }, o)
        oj.init()
        return oj
    }
}