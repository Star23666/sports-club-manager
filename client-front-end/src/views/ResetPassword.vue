<template>
  <van-toast v-model:show="disabled" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onSubmitQuery"
         @close="close"
  />
  <van-nav-bar
      title="Reset Password"
      left-text="Back"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
      v-if="$route.path !== '/adminResetPassword'"
  />
  <van-steps :active="step" style="margin-top: 12pt; width: 60%; margin-left: 17.5%">
    <van-step>Send Verification Email</van-step>
    <van-step>Reset Password</van-step>
  </van-steps>
  <br/>
  <div v-if="step === 0">
    <van-cell-group inset>
      <van-cell title="Please fill in the following information to send a verification email"/>
      <van-field
          v-model="username"
          name="賬號"
          label="Username"
          placeholder="Please fill in your username"
      />
      <van-field
          v-model="student_name"
          name="真實姓名"
          label="Name"
          placeholder="Please fill in your real name"
      />
      <van-field
          v-model="student_id"
          name="學號"
          label="Student ID"
          placeholder="Please fill in your student id"
      />
      <van-cell center title="Send to Campus Email">
        <template #right-icon>
          <van-switch v-model="useStudentEmail" />
        </template>
      </van-cell>
    </van-cell-group>
    <br/><br/>
    <van-button round block icon="envelop-o" style="width: 50%; margin-left: 25%" type="primary" @click="onSubmitCheck" :disabled="disabled">Send Email</van-button>
    <center>
      <p style="font-size: 9pt" v-if="!useStudentEmail">
       Registered Email is Unavailable? <a @click="this.useStudentEmail = true" style="cursor: pointer; text-decoration: underline">Send to Campus Email</a>
      </p>
      <p style="font-size: 9pt" v-if="useStudentEmail">
        Too Troublesome to Login on Campus? <a @click="this.useStudentEmail = false" style="cursor: pointer; text-decoration: underline">Send to Registered Email</a>
      </p>
      <p style="font-size: 9pt; margin-top: -7pt">
        Received the verification email? <a @click="this.step = 1" style="cursor: pointer; text-decoration: underline">Click Here to Reset Directly</a>
      </p>
    </center>
  </div>
  <div v-if="step === 1">
    <van-cell-group inset>
      <van-cell title="Please fill in the following information to reset your password"/>
      <van-field
          label-width="8em"
          v-model="verify_code"
          name="驗證碼"
          label="Verification Code"
          placeholder="Please Fill in It in Email"
      />
      <van-field
          label-width="8em"
          v-model="password"
          name="重置密碼"
          label="Reset Password"
          placeholder="Enter Reset Password"
          type="password"
      />
      <van-field
          label-width="9em"
          v-model="password_confirm"
          name="密碼確認"
          label="Password Comfirm"
          placeholder="Enter Password Again"
          type="password"
      />
    </van-cell-group>
    <br/>
    <br/>
    <van-button round block icon="setting-o" style="width: 50%; margin-left: 25%" type="warning" @click="onCheckReset" :disabled="disabled">Reset Password</van-button>
    <center>
      <p style="font-size: 9pt">Didn't receive the email or it has expired? <a @click="this.step = 0" style="cursor: pointer; text-decoration: underline">Back to Previous Step</a></p>
    </center>
  </div>

</template>

<script>
import {showToast, showSuccessToast, showFailToast, showConfirmDialog, showDialog} from 'vant';

export default {
  setup() {
    const getUrlKey = function (name) {
      return decodeURIComponent(
          (new RegExp('[?|&]'+name+'='+'([^&;]+?)(&|#|;|$)').exec(location.href)||[,""])[1].replace(/\+/g,'%20'))||null;
    }
    const onClickLeft = () => history.back();
    return {
      onClickLeft,
      getUrlKey
    };
  },
  data(){
    return {
      step: 0,
      student_name: '',
      student_id: '',
      username: '',
      verify_code: '',
      password: '',
      password_confirm: '',
      state: -2,
      account: '',
      isShow: false,
      disabled: false,
      useStudentEmail: false,
      loading: false,
      call: 0
    };
  },
  methods: {
    onSuccess(){
      if(this.step === 0)
        this.onSubmitQuery();
      if(this.step === 1)
        this.onSubmitReset();
    },
    onSubmitQuery() {
      this.isShow = false;
      this.disabled = true;
      if(this.useStudentEmail){
        this.sendToStudentEmail();
        return;
      }
      this.$http.post(`/find/sendResetEmail?student_id=${encodeURIComponent(this.student_id)}&name=${encodeURIComponent(this.student_name)}&username=${encodeURIComponent(this.username)}`, {}, {timeout: 10000})
          .then(response => {
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("System Error!");
              return;
            }
            if(response.data.status === -2){
              showFailToast("Incorrectly filled in account information");
              return;
            }
            if(response.data.status === -1){
              showToast("Email has been sent, please do not resubmit within 2 minutes");
              this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
              this.useStudentEmail = false;
              this.step = 1;
              return;
            }
            if(response.data.status === 0){
              showConfirmDialog({
                title: 'Mistake in Register Email',
                message:
                    'The current account is not registered email or the registration email format is wrong, you can choose to send an email to your campus email or cancel the operation and contact customer service to reset your password, please choose.',
                confirmButtonText: 'Send to Campus Email',
                cancelButtonText: 'Cancel'
              })
                  .then(() => {
                    this.sendToStudentEmail();
                  })
                  .catch(() => {
                    if(this.$route.path !== '/adminResetPassword')
                      this.$router.push('/inbox');
                    showDialog({
                      message: 'The online password reset operation has been cancelled, please contact customer service with a copy of your ID card to reset your password!',
                      confirmButtonText: 'Ok'
                    });
                  });
              //
              return;
            }
            showSuccessToast("Email sent successfully, please continue to reset password");
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
            this.step = 1;
          }).catch(error => {
            this.disabled = false;
            showFailToast('Internet Error');
          });
    },
    onSubmitCheck() {
      if (this.username.length === 0) {
        showToast({
          message: 'Username cannot be empty',
          position: 'top',
        });
        return;
      }
      if (this.student_name.length === 0) {
        showToast({
          message: 'Name cannot be empty',
          position: 'top',
        });
        return;
      }
      if (this.student_id.length === 0) {
        showToast({
          message: 'The student ID cannot be empty.',
          position: 'top',
        });
        return;
      }
      this.isShow = true;
    },
    onSubmitReset(){
      this.isShow = false;
      this.disabled = true;
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.password) === false){
        this.disabled = false;
        showToast("The currently set password does not meet the rules: The password must be at least 8 characters long and contain uppercase and lowercase letters, numbers, and special symbols");
        return;
      }
      this.$http.post(`/find/resetPassword?code=${encodeURIComponent(this.verify_code)}&password=${encodeURIComponent(this.password)}`)
          .then(response =>{
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("System Error");
              return;
            }
            if(response.data.status === -2){
              showFailToast("Incorrectly filled in verification code");
              return;
            }
            if(response.data.status === -1){
              showFailToast("The validity of the verification code has expired, please resend the email.");
              this.step = 0;
              this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
              this.useStudentEmail = false;
              return;
            }
            showSuccessToast("Password reset successfully, please use it to register and keep it safe.");
            if(this.$route.path !== '/adminResetPassword')
              this.$router.push("/login");
            this.step = 0;
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
          }).
      catch(error =>{
        this.disabled = false;
        showFailToast('Internet Error');
      });
    },
    onCheckReset(){
      if(this.verify_code.length === 0){
        showToast({
          message: 'The verification code cannot be empty.',
          position: 'top',
        });
        return;
      }
      if(this.password.length === 0){
        showToast({
          message: 'Reset password cannot be empty',
          position: 'top',
        });
        return;
      }
      if(this.password !== this.password_confirm){
        showToast({
          message: 'The passwords entered are not the same.',
          position: 'top',
        });
        return;
      }
      this.isShow = true;
    },
    sendToStudentEmail(){
      this.isShow = false;
      this.disabled = true;
      this.$http.post(`/find/sendResetEmail?student_id=${encodeURIComponent(this.student_id)}&name=${encodeURIComponent(this.student_name)}&username=${encodeURIComponent(this.username)}&StudentEmail=1`, {}, {timeout: 10000})
          .then(response => {
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("System Error");
              return;
            }
            if(response.data.status === -2){
              showFailToast("Incorrectly filled in account information");
              return;
            }
            if(response.data.status === -1){
              showToast("Email has been sent, please do not resubmit within 2 minutes");
              this.verify_code = this.password = this.password_confirm = '';
              this.useStudentEmail = false;
              this.step = 1;
              return;
            }
            showSuccessToast("The verification code email has been sent to your campus email, please continue to reset your password.");
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
            this.step = 1;
          }).catch(error => {
        this.disabled = false;
        showFailToast('Internet Error');
      });
    }
  }
}
</script>

<style scoped lang="scss">

</style>