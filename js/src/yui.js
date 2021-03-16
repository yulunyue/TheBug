import Fun from "./function"
Window.yuiid = Window.yuiid || 0
export function Base() {
    Window.yuiid += 1
    return {
        _id: Window.yuiid,
        _margin: [6, 6, 6, 6],
        _space: 6,
        set(key, v) {
            if (v != this["_" + key]) {
                this["_" + key] = v
                if (this._el) {
                    this.renderBefore()
                    if (["x", "y", "width", "height", "el"].indexOf(key) != -1) {
                        if (this._width && this._height) {
                            this.renderPosition()
                        }
                    }
                    this.render()
                }
            }
            return this
        },
        renderBefore() {
            this._el.style.background = this._color
            if (this._color == "#000") {
                this._el.style.color = "#fff"
            }
        },
        renderPosition() {
            this._el.style.position = "absolute"
            this._el.style.left = this._x
            this._el.style.top = this._y
            this._el.style.width = this._width
            this._el.style.height = this._height
            this.onPositionChnaged()
        },
        _x: 0,
        x(v) {
            return this.set("x", v)
        },
        _y: 0,
        y(v) {
            return this.set("y", v)
        },
        _width: 0,
        width(v) {
            return this.set("width", v)
        },
        _height: 0,
        height(v) {
            return this.set("height", v)
        },
        _stretch: 0,
        stretch(v) {
            return this.set("stretch", v)
        },
        _el: null,
        el(v) {
            return this.set("el", v)
        },
        _color: "transparent",
        color(v) {
            return this.set("color", v)
        },
        _parent: null,
        parent(v) {
            this._parent = v
            return this
        },
        log(p) {
            console.log(p, "id:" + this._id + ",x:" + this._x + ",y:" + this._y + ",w:" + this._width + ",h:" + this._height + ",p:" + (this._parent ? this._parent._id : "??"))
        },
        create(v) {
            var c = document.createElement(v || "div")
            this._el.appendChild(c)
            return c
        },
        render() {

        },
        onPositionChnaged() {

        },
    }
}
export function QL() {
    return Fun.extend(Base(), {
        _html: arguments[0] || "",
        _type: "ql",
        render() {
            this._el.style.lineHeight = this._height + "px"
            this._el.style.textAlign = "center"
            this._el.innerHTML = this._html
        }
    })
}
export function QH() {
    var base = Base()
    return Fun.extend(
        base,
        {
            _type: "qh",
            _v_h: 1,
            _children: Fun.list(arguments).map((v1) => v1.parent(base)),
            v_h(v) {
                this._type = v == 0 ? "qv" : "qh"
                this._v_h = v
                return this
            },

            scalaChild(child) {
                child._scala = null
                if (this._v_h == 0) {
                    if (child._width && this._width) {
                        child._scala = child._width / this._width
                    }
                } else {
                    if (child._height && this._height) {
                        child._scala = child._height / this._height
                    }
                }
            },
            onPositionChnaged() {
                var x = this._margin[0]
                var y = this._margin[1]
                var stretch_all = 0
                for (var i = 0; i < this._children.length; i++) {
                    if (this._el.children[i] == undefined) {
                        this._children[i].el(this.create())
                    } else {
                        this._children[i].el(this._el.children[i])
                    }
                    this.scalaChild(this._children[i])
                    if (this._children[i]._scala == null) {
                        this._children[i]._scala = this._children[i]._stretch || 1
                    }
                    stretch_all += this._children[i]._scala
                }
                if (this._v_h == 1) {
                    this.width_height = this._width - this._margin[0] - this._margin[2]
                }
                else {
                    this.width_height = this._height - this._margin[1] - this._margin[3]
                }
                if (stretch_all) {
                    this.stretch_value = (this.width_height - (stretch_all - 1) * this._space) / stretch_all
                }
                this.log("parent")
                for (var i = 0; i < this._el.children.length; i++) {
                    if (i < this._children.length) {
                        this._children[i].x(x)
                        this._children[i].y(y)
                        var w = this._children[i]._scala * this.stretch_value
                        if (this._v_h == 1) {
                            x += w + this._space
                            this._children[i].width(w)
                            this._children[i].height(this._height - this._margin[1] - this._margin[3])
                        } else {
                            y += w + this._space
                            this._children[i].height(w)
                            this._children[i].width(this._width - this._margin[0] - this._margin[2])

                        }
                        this._el.children[i].style.display = ""
                        this._children[i].log(this._children[i]._html || "")
                    }
                    else {
                        this._el.children[i].style.display = "none"
                    }
                }

                return this
            }

        }
    )
}
export function QV() {
    return QH.apply(this, arguments).v_h(0)
}
function TreeItem() {
    return Fun.extend(
        Base(),
        {

        }

    )
}
export function Tree(v) {
    var basetree = Fun.treeLoad(arguments)
    function fold_one(v) {
        v.expanded = false
        if (v.node) {
            v.node.style.display = "none"
        }
        v.children.map(fold_one)
    }
    function expand_one(v) {
        v.expanded = true
        v.node.style.display = ""
    }
    return Fun.extend(
        Base(),
        {
            _treeNode: basetree.array,
            _treeoj: basetree.data,
            render() {
                this._el.innerHTML = ""
                this._treeNode.map(v1 => {
                    // v1.expanded = v1.expanded == false ? true : false
                    v1.node = this.create("p")
                    v1.node.style.marginLeft = v1.deepth * 20
                    v1.node.innerHTML = v1.name + (v1.children.length == 0 ? "" : '[%s]'.f(v1.children.length))
                    v1.node.style.display = v1.expanded == false ? "none" : ""
                    v1.expanded = v1.node.style.display == "" ? true : false
                    v1.node.style.cursor = "pointer"
                    v1.node.onclick = () => {
                        this.click(v1)
                    }
                })
            },
            click(v) {
                v.children.map((v1) => {
                    if (v1.node.style.display == "none") {
                        expand_one(v1)
                    } else {
                        fold_one(v1)
                    }

                })
            },
            fold() {
                for (var i = 0; i < arguments.length; i++) {
                    this._treeoj[arguments[i]].children.map(fold_one)
                }
                return this
            }
        }
    )
}
export function Input(value) {
    return Fun.extend(Base(), {
        _value: value || "",
        render() {
            this._el.innerHTML = ""
            this._input = this.create("input")
            this._input.style.borderLeft = "none"
            this._input.style.borderRight = "none"
            this._input.style.borderTop = "none"
            this._input.style.borderBottom = "2px solid #fff"
            this._input.style.color = "#fff"
            this._input.style.background = "transparent"
            this._input.style.outline = "none"
            this._input.value = this._value
        }
    })
}