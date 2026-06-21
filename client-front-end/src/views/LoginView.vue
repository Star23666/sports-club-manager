<template>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onSubmitLogin"
         @close="close"
  />
  <van-toast v-model:show="disabled" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <van-nav-bar
      title="Login"
      left-text="Back"
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
      <h2 style="margin-bottom: -15px">My Club</h2>
      <h4>Sports Activity Management</h4>
      <h3>Login with Password</h3>
    </center>
    <center>
      <div :style="{maxWidth: '400px', marginTop: '15px'}">
        <van-form @submit="onLogin">
        <van-cell-group inset>
          <van-field
              v-model="username"
              required
              left-icon="user"
              placeholder="Username"
              :rules="[{ required: true, message: 'Username can\'t be null!' }]"
          />
          <van-field
              v-model="password"
              type="password"
              required
              left-icon="lock"
              placeholder="Password"
              :rules="[{ required: true, message: 'Password can\'t be null!' }]"
          />
        </van-cell-group>
          <br/>
          <van-button round block icon="certificate" :disabled="disabled" type="primary" native-type="submit" style="width: 80%; max-width: 320px">Login</van-button>
        </van-form>
      </div>
      <p style="font-size: 9pt; margin-top: 11pt">
        Forget Username or Password? <br> You can
        <router-link to="/findAccount" style="font-size: 9.5pt" >Query Username</router-link> or
        <router-link to="/resetPassword" style="font-size: 9.5pt" >Reset Password</router-link>
      </p>
    </center>
  </div>
</template>

<script>
import Cookies from "js-cookie";
import {showToast, showSuccessToast, showFailToast, showDialog  } from "vant";


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
      this.isShow = true;
    },
    onSubmitLogin(){
      this.isShow = false;
      this.disabled = true;
      this.$http({
        method: 'POST',
        url: `/user/login?username=${encodeURIComponent(this.username)}&password=${encodeURIComponent(this.password)}`,
      }).then((response) => {
        this.disabled = false;
        if(response.data.status === -2){
          showFailToast('Username or Password Invalid');
          return;
        }
        if(response.data.status === -1){
          showFailToast('The current account is still pending.');
          return;
        }
        if(response.data.status === 0){
          showFailToast('Current account has been blocked, please contact customer service.');
          return;
        }
        if(response.data.status > 3){
          showToast('The current account is an administrator account, please go to the backstage.');
          return;
        }
        Cookies.set('token', response.data.data);
        if(response.data.status === 3)
          this.$router.push('/staff');
        else
          this.$router.push('/main');
        if(response.data.status === 1){
          showDialog({
            title: 'Account Restrictions',
            message: 'Hello, we are very sorry to inform you that due to your repeated participation but absence, you are temporarily unable to participate in our activities directly or by alternate, and no designated account transfer, and are only allowed to participate through designated account transfer. Please contact our customer service for a solution!',
            confirmButtonText: 'I Understand'
          }).then(() => {
            // on close
          });
        }else{
          showSuccessToast('Login Successfully');
        }
      }).catch((error) => {
            console.log(error);
            showFailToast('Internet Error');
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
