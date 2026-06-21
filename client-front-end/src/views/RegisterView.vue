<template>
  <div>
    <Vcode :show="isShow"
           slider-text="Drag Slider to Complete Puzzle"
           fail-text="Verification Failed, Please Try Again"
           success-text="Verification Passed"
           :range="5"
           @success="success"
           @close="close"
    />
  </div>
  <van-nav-bar
      title="Create New Account"
      left-text="Back"
      left-arrow
      fixed
      @click-left="onClickLeft"
  />
  <br/>
  <br/>
  <br/>
  <van-cell-group inset>
    <van-cell title="Information Registration" label="Welcome! Please fill in the following information to complete your account registration. After approval, you can sign up and participate in club activities!" />
  </van-cell-group>
  <br/>
  <van-form @submit="onSubmit">
    <van-cell-group inset>
      <van-cell title="Account Information"/>
      <van-field
          v-model="username"
          name="賬號"
          label="Username"
          placeholder="only consist letters and numbers"
          :rules="[{ required: true, message: 'Please fill username' }]"
      />
      <van-field
          v-model="password"
          type="password"
          name="密碼"
          label="Password"
          placeholder="Setting your password"
          :rules="[{ required: true, message: 'Please fill password' }]"
      />
      <van-field
          v-model="password_confirm"
          type="password"
          name="密碼"
          label="Comfirm"
          placeholder="Input your password again"
          :rules="[{ required: true, message: 'Please fill password again' }]"
      />
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="Personal Information"/>
      <van-field
          v-model="student_name"
          name="Name"
          label="Name"
          placeholder="Name on identity document"
          :rules="[{ required: true, message: 'Please fill your name' }]"
      />
      <van-field
          v-model="student_id"
          name="Student ID"
          label="Student ID"
          placeholder="Numbers on student ID card"
          :rules="[{ required: true, message: 'Please fill your student ID' }]"
      />
      <van-field
          v-model="member_id"
          name="會員卡號"
          label="Member ID"
          placeholder="Number on Membership Card"
          :rules="[{ required: true, message: 'Please fill your Member ID' }]"
      />
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="Contact Details"/>
      <van-field
          v-model="phone"
          type="tel"
          name="Phone"
          label="Phone"
          placeholder="Need to add prefix (+86, +853)"
          :rules="[{ required: true, message: 'Please fill phone number！' }]"
      />
      <van-field
          v-model="wechat_id"
          name="Wechat ID"
          label="Wechat ID"
          placeholder="Use to contact for daily activities"
          :rules="[{ required: true, message: 'Please fill Wechat ID！' }]"
      />
      <van-field
          v-model="email"
          name="Email"
          label="Email"
          placeholder="Allow to be empty"
      />
    </van-cell-group>
    <br/>
    <van-row justify="center">
      <van-space :size="20">
        <van-button round block type="warning" :disabled="disabled" native-type="submit" icon="guide-o" >
          Submit Registration
        </van-button>
        <van-button round block type="default" :disabled="disabled" icon="replay" @click="onRewrite">
          Rewrite
        </van-button>
      </van-space>
    </van-row>
  </van-form>
  <br/>
</template>

<script>
import {showFailToast, showSuccessToast, showToast, Toast} from 'vant';
export default {
  setup() {
    const onClickLeft = () => history.back();
    return {
      onClickLeft,
    };
  },
  data() {
    return{
      username: '',
      password: '',
      password_confirm: '',
      student_name: '',
      student_id:'',
      member_id:'',
      phone:'',
      email:'',
      wechat_id:'',
      isShow: false,
      disabled: false
    };
  },
  methods: {
    onSubmit(){
      if(this.password !== this.password_confirm){
        this.password = this.password_confirm = "";
        showFailToast("The passwords you entered twice do not match. Please re-enter.\n");
        return;
      }
      this.isShow = true;
    },
    onRewrite(){
      this.username = '';
      this.password = '';
      this.password_confirm = '';
      this.student_name = '';
      this.member_id = '';
      this.student_id = '';
      this.wechat_id = '';
      this.phone = '';
      this.email = '';
    },
    success() {
      this.disabled = true;
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.password) === false){
        this.disabled = false;
        showToast("The currently set password does not meet the rules: The password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special symbols");
        this.isShow = false;
        return;
      }
      this.$http.post(`/user/register?username=${encodeURIComponent(this.username)}&password=${encodeURIComponent(this.password)}&name=${encodeURIComponent(this.student_name)}&card_id=${encodeURIComponent(this.member_id)}&phone=${encodeURIComponent(this.phone)}&wechat_id=${encodeURIComponent(this.wechat_id)}
&student_id=${encodeURIComponent(this.student_id)}&email=${encodeURIComponent(this.email)}`)
          .then(data => {
            console.log(data);
            if(data.status !== 200){
              showFailToast("System Error");
            }
            if(data.data.status === -1){
              showFailToast(data.data.data);
              this.password = this.password_confirm = '';
            }
            if(data.data.status === 0){
              showSuccessToast(data.data.data);
              this.$router.push("/login");
            }
            this.disabled = false;
          })
          .catch(error =>{
            showFailToast("Internet Error");
            this.disabled = false;
          });
      this.isShow = false; // 通过验证后，需要手动隐藏模态框
    },
    close() {
      this.isShow = false;
    }
  }
};
</script>