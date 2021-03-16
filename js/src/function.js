Date.prototype.format = function (format) {
    var date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };
    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1
                ? date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }
    return format;
}
String.prototype.f = function () {
    var str = this.valueOf();
    var index = str.indexOf("%s");
    let num = 0;
    while (index != -1 && num < arguments.length) {
        var shead = str.substring(0, index)
        var stail = str.substring(index + 2, str.length);
        str = shead + arguments[num] + stail
        index = str.indexOf('%s');
        num++;
    }
    return str;
}
Array.prototype.update = function (a_dst) {
    var a_src = this.valueOf()
    for (var i = 0; i < a_dst.length; i++) {
        if (a_src[i] != a_dst[i]) {
            a_src[i] = a_dst[i]
        }
    }
}
export default {
    list(n, b, c, d, e, f) {
        let rt = []
        if (n.length != undefined) {
            for (var i = 0; i < n.length; i++) {
                rt.push(n[i])
            }
            return rt
        }
        for (var i = 0; i < n; i++) {
            if (b) {
                rt.push(v.apply(this, i, c, d, e, f))
            } else {
                rt.push(i)
            }
        }
        return rt
    },
    extend() {
        var a = arguments[0]
        for (var i = 1; i < arguments.length; i++) {
            var b = arguments[i]
            if (typeof (b) == "object") {
                for (var key in b) {
                    a[key] = b[key]
                }
            }
        }
        return a
    },
    node(name, p) {
        let rt = {
            name: name,
            children: [],
            deepth: p == undefined ? 0 : p.deepth + 1,
            p: p
        }
        if (p) {
            p.children.push(rt)
        }
        return rt
    },
    treeLoad(p) {
        var rt = []
        var oj = {}
        for (var i = 0; i < p.length; i++) {
            var paths = p[i].split("/")
            var key = ""
            var p_oj = null
            for (var j = 0; j < paths.length; j++) {
                if (key == "") {
                    key += paths[j]
                } else {
                    key += "/" + paths[j]
                }
                if (oj[key] == undefined) {
                    oj[key] = this.node(paths[j], p_oj)
                    rt.push(oj[key])
                }
                p_oj = oj[key]
            }
        }
        return { array: rt, data: oj }
    },
    treeParse() {

    }
}