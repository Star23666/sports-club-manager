<template>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onSubmitLogin"
         @close="close"
  />
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <div style="margin-top: 7vh">
    <center>
      <van-image
          width="180"
          height="180"
          :src="require('@/assets/badminton.png')"
      />
      <!-- Customize: your club name -->
      <h2 style="margin-bottom: -15px">My Club</h2>
      <h4>Sports Activity Management</h4>
      <h3>Welcome! You can</h3>
    </center>
    <center>
      <van-button round block icon="sign" :disabled="disabled" type="success" @click="onLogin" style="width: 80%; max-width: 320px; margin: 8pt; margin-top: 20pt">One-Tap Fast Login</van-button>
      <van-button round block icon="manager-o" :disabled="disabled" type="success" @click="this.$router.push('/login');"
                  style="width: 80%; max-width: 320px; margin: 8pt; background-color: dodgerblue; border-color: dodgerblue">Login with Password</van-button>
      <van-button round block icon="add-o" :disabled="disabled" type="warning" @click="onRegister" style="width: 80%; max-width: 320px; margin: 8pt">Create New Account</van-button>
    </center>
  </div>

  <p style="font-size: 7pt; text-align: center; position: fixed; bottom: 5vh; width: 100%;">
    Sports Club Management System — Member Portal<br/>
    Copyright © 2024 My Club
  </p>
</template>

<script>
import Cookies from "js-cookie";
import {showToast, showSuccessToast, showFailToast, showDialog} from "vant";
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
      loading: false,
      time_call: new Date('2023-01-01T00:00:00Z')
    };
  },
  methods: {
    onLogin() {
      const now = new Date();
      if(Math.abs(now.getTime() - this.time_call.getTime()) < 5000){
        this.isShow = true;
      }
      else
        this.onSubmitLogin();
    },
    onRegister(){
      this.$router.push('/register');
    },
    async onSubmitLogin(){
      this.loading = true;
      this.time_call = new Date();
      console.log(this.$finger());
      this.isShow = false;
      this.disabled = true;
      this.username = await this.$finger();
      this.$http({
        method: 'POST',
        url: `/user/loginByEquip?equip_id=${encodeURIComponent(this.username)}`,
      }).then((response) => {
        this.disabled = false;
        if(response.data.status === -2){
          this.loading = false;
          showDialog({
                message: "Currently, “One-Tap Fast Login” is not enabled on your device, you can set “One-Tap Fast Login” in “One-Tap Login Management” of “My Account” after login!",
                confirmButtonText: 'Ok'
          });
          return;
        }
        if(response.data.status === -1){
          this.loading = false;
          showFailToast('The current account is still pending.');
          return;
        }
        if(response.data.status === 0){
          this.loading = false;
          showFailToast('Current account has been blocked, please contact customer service.');
          return;
        }
        if(response.data.status > 3){
          this.loading = false;
          showToast('The current account is an administrator account, please go to the backstage.');
          return;
        }
        this.loading = false;
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
          this.loading = false;
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
