import Net from "./net"
import yui_test from "../test/yui.test"
if (Window.socket == undefined) {
    Window.socket = Net.socket({
        id: "watchfile",
        recv_json(data) {
            var myScript = document.createElement("script");
            myScript.type = "text/javascript";
            myScript.src = "/" + data.src_path
            document.body.appendChild(myScript);
            // document.append(script)
        }
    })
}
yui_test(document.getElementById("root"))