import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import LayUI, {layer} from '@layui/layui-vue'
import '@layui/layui-vue/lib/index.css'
import Cookies from 'js-cookie'
import VCode from "vue3-puzzle-vcode";

const app = createApp(App)
    .use(store)
    .use(router)
    .use(LayUI)
    .use(Cookies)
    .component('layer', layer)
    .component('VCode', VCode);

// Set via public/config.js — points to the client (member) frontend URL
app.config.globalProperties.$findUrl = window.__FIND_URL__ || "http://localhost:8080";
app.config.globalProperties.$http = router.Axios;
app.config.globalProperties.$clear = function (){
    if(Cookies.get('token') !== undefined){
        Cookies.remove('token');
        layer.msg("The status changed, please login again");
    }else{
        layer.msg("Current account has been logged out, please login again");
    }
    this.$router.push('/login');
}

app.config.errorHandler = function (err, vm, info) {
    // 输出错误和提供更多信息
    console.error(`捕获到错误：${err.toString()}\n信息：${info}`);
};

app.mount('#app');
