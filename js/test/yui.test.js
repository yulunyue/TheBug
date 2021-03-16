import { QL, QV, QH, Tree, Input } from "../src/yui"
export default function (el) {
    var root = QH(
        Tree(
            "a/b/c",
            "a/c",
            "b/c",
            "b/d/e"
        ).fold(
            "a/b",
            "b"
        ),
        Input("34").color("#000"),
        QV(
            QL("88").color("#777").height(20),
            QL("99").color("#999")
        ).color("#444")
    ).width(document.body.clientWidth).height(document.body.clientHeight)
        .el(el).color("#000")
    document.body.onresize = () => {
        root.width(document.body.clientWidth).height(document.body.clientHeight)
    }
}