(()=>{"use strict";const s={list(s,e,t,o,i,n){let c=[];for(var r=0;r<s;r++)e?c.push(v.apply(this,r,t,o,i,n)):c.push(r);return c},extend(){for(var s=arguments[0],e=1;e<arguments.length;e++){var t=arguments[e];if("object"==typeof t)for(var o in t)s[o]=t[o]}return s}};({socket(e){var t=s.extend({ip:"127.0.0.1",port:5e4,reinit(){setTimeout((()=>{this.init()}),1e3)},init(){try{this.socket=new WebSocket("ws://"+this.ip+":"+this.port)}catch(s){this.socket=null,console.log("websocket error",s)}if(null==this.socket)return this.reinit();this.socket.onopen=s=>{console.log(this,"websocket onopen",s),this.id&&this.send_json({id:this.id}),this.open_success&&this.open_success()},this.socket.onmessage=s=>{console.log(this,"websocket onmessage",s)},this.socket.onclose=s=>{console.log(this,"websocket onclose",s),this.reinit()},this.socket.onerror=s=>{console.log(this,"websocket onerror",s)}},send_json(s){this.socket.send(JSON.stringify(s))}},e);return t.init(),t}}).socket({id:"watchfile"})})();