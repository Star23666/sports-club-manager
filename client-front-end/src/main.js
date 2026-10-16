import { createApp } from 'vue'
import Vant, {Locale, showFailToast} from 'vant'
import zhCN from 'vant/es/locale/lang/zh-CN'
import App from './App.vue'
import router from './router'
import store from './store'
import VueQrcode from 'vue-qrcode'
import Vcode from 'vue3-puzzle-vcode'
import QrReader from 'vue3-qr-reader'
import Cookies from 'js-cookie'
import axios from 'axios'
import FingerprintJS from '@fingerprintjs/fingerprintjs'

import '@/assets/global.css'
import 'vant/lib/index.css'

Locale.use('zh-CN', zhCN)


axios.defaults.timeout = 2000
// axios.defaults.baseURL = 'https://api.your-club.com/api'
// axios.defaults.baseURL = 'http://localhost:8081/api'
axios.defaults.baseURL = "/api"
axios.defaults.retry = 3;

// Existing views still build token query strings. Strip them before any request
// leaves the browser and send the credential through the standard auth header.
axios.interceptors.request.use((config) => {
    const url = config.url || '';
    const queryStart = url.indexOf('?');
    if (queryStart !== -1) {
        const query = new URLSearchParams(url.slice(queryStart + 1));
        const token = query.get('token');
        if (token) {
            query.delete('token');
            const remainingQuery = query.toString();
            config.url = url.slice(0, queryStart) + (remainingQuery ? `?${remainingQuery}` : '');
            config.headers = config.headers || {};
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

axios.interceptors.response.use(undefined, function axiosRetryInterceptor(err) {
    const config = err.config;
    if (config && config.retry) {
        config.__retryCount = config.__retryCount || 0;
        if (config.__retryCount >= config.retry) {
            return Promise.reject(err);
        }
        config.__retryCount += 1;
        const backoff = new Promise(function(resolve) {
            setTimeout(resolve, config.__retryCount * 1000);
        });
        return backoff.then(function() {
            return axios(config);
        });
    }
    return Promise.reject(err);
});


const app = createApp(App)
    .use(store)
    .use(router)
    .use(Vant)
    .use(Cookies)
    .use(QrReader)
    .component('Vcode', Vcode)
    .component('vue-qrcode', VueQrcode)

app.config.globalProperties.$http = axios
app.config.globalProperties.$finger = async function(){
    const fpPromise = await FingerprintJS.load();
    const result = await fpPromise.get();
    // Exclude a couple components
    const { fonts, languages, audio, ...components } = result.components;
    // Add a few custom components
    const extendedComponents = {
        ...components,
        foo: { value: 'whatever' },
    };
    const fingerprintId = FingerprintJS.hashComponents(extendedComponents);
    return fingerprintId;
}

app.config.globalProperties.$memberVerify = function (){
    const token = Cookies.get('token');
    if(token == null)
    this.$router.push('/inbox');
    else
        this.$http.post('/user/verify?token=' + Cookies.get('token'))
                  .then(response =>{
                      if(response.status !== 200){
                          Cookies.remove('token');
                          this.$router.push('/inbox');
                      }
                      else if(response.data.status <= 0){
                          showFailToast("账号状态已变化，请重新登录");
                          Cookies.remove('token');
                          this.$router.push('/inbox');
                      }
                      else if(response.data.status > 3){
                          Cookies.remove('token');
                          this.$router.push('/inbox');
                      }
                      else if(response.data.data.state === 3)
                          this.$router.push('/staff');
                  }).
                  catch(error =>{
                      Cookies.remove('token');
                      this.$router.push('/inbox');
                  });
}

app.config.globalProperties.$staffVerify = function (){
    const token = Cookies.get("token");
    if(token == null)
        this.$router.push('/inbox');
    else
        this.$http.post('/user/verify?token=' + Cookies.get('token'))
            .then(response =>{
                if(response.status !== 200){
                    Cookies.remove('token');
                    this.$router.push('/inbox');
                }
                else if(response.data.status <= 0){
                    showFailToast("账号状态已变化，请重新登录");
                    Cookies.remove('token');
                    this.$router.push('/inbox');
                }
                else if(response.data.data.state > 0 && response.data.data.state < 3)
                    this.$router.push('/main');
            }).
        catch(error =>{
            Cookies.remove('token');
            this.$router.push('/inbox');
        });
}

app.mount('#app')
