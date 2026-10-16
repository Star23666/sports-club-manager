<template>
  <Vcode :show="isShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onSubmitLogin"
         @close="close"
  />
  <van-toast v-model:show="disabled" type="loading" overlay="true" duration="0"
             forbid_click="true" message="正在登录..."></van-toast>
  <van-nav-bar
      title="登录"
      left-text="返回"
      left-arrow
      fixed
      @click-left="this.$router.push('/inbox');"
  />
  <div style="margin-top: 7vh">
    <center>
      <van-image
          width="180"
          height="180"
          :src="require('@/assets/badminton.png')"
      />
      <h2 style="margin-bottom: -15px">体育俱乐部</h2>
      <h4>活动与会员管理</h4>
      <h3>账号密码登录</h3>
    </center>
    <center>
      <div :style="{maxWidth: '400px', marginTop: '15px'}">
        <van-form @submit="onLogin">
        <van-cell-group inset>
          <van-field
              v-model="username"
              required
              left-icon="user"
              placeholder="用户名"
              :rules="[{ required: true, message: '请输入用户名' }]"
          />
          <van-field
              v-model="password"
              type="password"
              required
              left-icon="lock"
              placeholder="密码"
              :rules="[{ required: true, message: '请输入密码' }]"
          />
        </van-cell-group>
          <br/>
          <van-button round block icon="certificate" :disabled="disabled" type="primary" native-type="submit" style="width: 80%; max-width: 320px">登录</van-button>
        </van-form>
      </div>
      <p style="font-size: 9pt; margin-top: 11pt">
        忘记用户名或密码？<br>你可以
        <router-link to="/findAccount" style="font-size: 9.5pt" >找回用户名</router-link>或
        <router-link to="/resetPassword" style="font-size: 9.5pt" >重置密码</router-link>
      </p>
    </center>
  </div>
</template>

<script>
import Cookies from "js-cookie";
import {showToast, showSuccessToast, showFailToast, showDialog  } from "vant";
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';


export default {
  created(){
    const token = Cookies.get('token');
    if(token != null){
      this.$http.post('/user/verify?token='+ Cookies.get('token'))
          .then(response =>{
            if(response.data.status === 3)
              this.$router.push('/staff');
            else if(response.data.status > 0 && response.data.status < 3)
              this.$router.push('/main');
          }).
      catch(error =>{
      });
    }
  },
  data() {
    return {
      username: '',
      password: '',
      isShow: false,
      disabled: false,
      loading: false
    };
  },
  methods: {
    onLogin() {
      if (skipPuzzleForLocalDemo()) this.onSubmitLogin();
      else this.isShow = true;
    },
    onSubmitLogin(){
      this.isShow = false;
      this.disabled = true;
      this.$http({
        method: 'POST',
        url: '/user/login',
        data: { username: this.username, password: this.password },
      }).then((response) => {
        this.disabled = false;
        if(response.data.status === -2){
          showFailToast('用户名或密码错误');
          return;
        }
        if(response.data.status === -1){
          showFailToast('账号仍在审核中');
          return;
        }
        if(response.data.status === 0){
          showFailToast('账号已被限制，请联系管理员');
          return;
        }
        if(response.data.status > 3){
          showToast('管理员账号请前往管理后台登录');
          return;
        }
        Cookies.set('token', response.data.data);
        if(response.data.status === 3)
          this.$router.push('/staff');
        else
          this.$router.push('/main');
        if(response.data.status === 1){
          showDialog({
            title: '账号参加活动受限',
            message: '由于多次报名后缺席，你暂时无法直接报名或候补，只能通过指定转让参加活动。如需恢复，请联系俱乐部管理员。',
            confirmButtonText: '我知道了'
          }).then(() => {
            // on close
          });
        }else{
          showSuccessToast('登录成功');
        }
      }).catch((error) => {
            console.log(error);
            showFailToast('网络异常，请稍后重试');
        this.disabled = false;
          }
      );
    },
    close(){
      this.isShow = false;
    }
  }
};
</script>
