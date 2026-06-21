import { createApp } from 'vue'
import Vant, {showFailToast} from 'vant'
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


axios.defaults.timeout = 2000
// axios.defaults.baseURL = 'https://api.your-club.com/api'
// axios.defaults.baseURL = 'http://localhost:8081/api'
axios.defaults.baseURL = "/api"
axios.defaults.retry = 3;

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
                          showFailToast("The current user status has changed, please log in again!\n");
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
                    showFailToast("The current user status has changed, please log in again!\n");
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
