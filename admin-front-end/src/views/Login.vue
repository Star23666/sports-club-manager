<template>
  <VCode :show="loginVCodeShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onSubmitLogin"
         @close="loginVCodeClose"
  />
  <div class="container">
    <div class="form" >
      <center>
        <img width="130"  :src="require('@/assets/badminton.png')"/>
      </center>
      <!-- Customize: your club name -->
      <h2 style="text-align: center;">体育俱乐部</h2>
      <h2 style="text-align: center;">管理员登录</h2>
      <br/>
      <label for="username">用户名</label>
      <lay-input type="text" prefix-icon="layui-icon-username" v-on:keyup.enter="" v-model="username" placeholder="用户名"/>
      <label for="password" style="margin-top: 10pt">密码</label>
      <lay-input type="password" prefix-icon="layui-icon-password" v-on:keyup.enter="onLoginClick" v-model="password" placeholder="密码" />
      <center>
        <lay-button class="button" @click="onLoginClick" style="margin-top: 14pt" :disabled="disabled">
          <lay-icon type="layui-icon-auz"></lay-icon> 登录
        </lay-button>
        <p style="font-size: 12px; margin-top: 5pt"><a @click="openFindAccount" style="cursor: pointer;">找回账号</a> / <a @click="openResetPassword" style="cursor: pointer;">重置密码</a></p>

      </center>
      <p style="font-size: 11px; margin-top: 9pt">仅管理员可登录。普通会员请使用会员入口。</p>
    </div>
    <div>
      <p style="font-size: 10px; text-align: center; color: white" class="footer">
        体育俱乐部管理系统 · 管理后台<br/>
        Copyright &copy; 2024 体育俱乐部
      </p>
    </div>
  </div>
</template>

<script>
import { layer } from "@layui/layui-vue";
import Cookies from 'js-cookie';
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';

export default {
  data(){
    return{
      username: '',
      password: '',
      loginVCodeShow: false,
      disabled: false
    };
  },
  methods:{
    openFindAccount() {
      layer.open({
        type: "iframe",
        title: "找回账号",
        area: ['320pt','370pt'],
        content: this.$findUrl + "/adminFindAccount"
      })
    },
    openResetPassword() {
      layer.open({
        id: "reset-password",
        type: "iframe",
        title: "重置密码",
        area: ['320pt','400pt'],
        content: this.$findUrl +  "/adminResetPassword"
      })
    },
    onLoginClick(){
      if(this.username === '' || this.password === ''){
        layer.msg("请输入用户名和密码", { icon : 7, time: 1500});
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onSubmitLogin();
      else this.loginVCodeShow = true;
    },
    onSubmitLogin(){
      this.loginVCodeShow = false;
      this.disabled = true;
      this.$http({
        method: 'POST',
        url: '/user/login',
        data: { username: this.username, password: this.password },
      }).then((response) => {
        this.disabled = false;
        if(response.data.status === -2){
          layer.msg('用户名或密码错误', { icon : 2, time: 1500});
          return;
        }
        if(response.data.status === -1){
          layer.msg('当前账号不是管理员', { icon : 7, time: 1500});
          return;
        }
        //Cookies.set('token', response.data.data);
        Cookies.set('token', response.data.data);
        this.$router.push('/main');
        layer.msg('登录成功', { icon : 1, time: 1500});
      }).catch((error) => {
            // console.log(error);
            layer.msg('网络异常，请稍后重试', { icon : 2, time: 1500});
            this.disabled = false;
          }
      );
    },
    loginVCodeClose(){
      this.loginVCodeShow = false;
    }
  }
}
</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  background-image: url(@/assets/loginbg5.png);
  background-size: cover;
}

.container {
  max-width: 500px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.form {
  margin-top: -14vh;
  background-color: rgb(186, 227, 175);
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  padding: 20px;
  width: 100%;
  max-width: 400px;
  opacity: 0.92;
}

.form input {
  display: block;
  width: 94%;
  border: none;
  font-size: 16px;
}

.form button {
  display: block;
  width: 50%;
  background-color: #009688;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

.form label {
  display: block;
  font-weight: bold;
  margin-bottom: 10px;
}

.footer {
  position: fixed;
  left: 0;
  bottom: 5vh;
  width: 100%;
}
</style>
