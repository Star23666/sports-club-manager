<template>
  <van-toast v-model:show="disabled" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加载中..."></van-toast>
  <Vcode :show="isShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onSuccess"
         @close="close"
  />
  <van-nav-bar
      title="重置密码"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
      v-if="$route.path !== '/adminResetPassword'"
  />
  <van-steps :active="step" style="margin-top: 12pt; width: 60%; margin-left: 17.5%">
    <van-step>发送验证邮件</van-step>
    <van-step>设置新密码</van-step>
  </van-steps>
  <br/>
  <div v-if="step === 0">
    <van-cell-group inset>
      <van-cell title="请填写账号信息，以发送验证邮件"/>
      <van-field
          v-model="username"
          name="賬號"
          label="用户名"
          placeholder="填写用户名"
      />
      <van-field
          v-model="student_name"
          name="真實姓名"
          label="姓名"
          placeholder="填写真实姓名"
      />
      <van-field
          v-model="student_id"
          name="學號"
          label="学号"
          placeholder="填写学号"
      />
      <van-cell center title="发送到校园邮箱">
        <template #right-icon>
          <van-switch v-model="useStudentEmail" />
        </template>
      </van-cell>
    </van-cell-group>
    <br/><br/>
    <van-button round block icon="envelop-o" style="width: 50%; margin-left: 25%" type="primary" @click="onSubmitCheck" :disabled="disabled">发送邮件</van-button>
    <center>
      <p style="font-size: 9pt" v-if="!useStudentEmail">
       注册邮箱不可用？<a @click="this.useStudentEmail = true" style="cursor: pointer; text-decoration: underline">改发校园邮箱</a>
      </p>
      <p style="font-size: 9pt" v-if="useStudentEmail">
        不方便登录校园邮箱？<a @click="this.useStudentEmail = false" style="cursor: pointer; text-decoration: underline">改发注册邮箱</a>
      </p>
      <p style="font-size: 9pt; margin-top: -7pt">
        已收到验证邮件？<a @click="this.step = 1" style="cursor: pointer; text-decoration: underline">直接填写验证码</a>
      </p>
    </center>
  </div>
  <div v-if="step === 1">
    <van-cell-group inset>
      <van-cell title="填写验证码和新密码"/>
      <van-field
          label-width="8em"
          v-model="verify_code"
          name="驗證碼"
          label="验证码"
          placeholder="填写邮件中的验证码"
      />
      <van-field
          label-width="8em"
          v-model="password"
          name="重置密碼"
          label="新密码"
          placeholder="输入新密码"
          type="password"
      />
      <van-field
          label-width="9em"
          v-model="password_confirm"
          name="密碼確認"
          label="确认密码"
          placeholder="再次输入新密码"
          type="password"
      />
    </van-cell-group>
    <br/>
    <br/>
    <van-button round block icon="setting-o" style="width: 50%; margin-left: 25%" type="warning" @click="onCheckReset" :disabled="disabled">重置密码</van-button>
    <center>
      <p style="font-size: 9pt">没收到邮件或验证码已过期？<a @click="this.step = 0" style="cursor: pointer; text-decoration: underline">返回上一步</a></p>
    </center>
  </div>

</template>

<script>
import {showToast, showSuccessToast, showFailToast, showConfirmDialog, showDialog} from 'vant';
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';

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
      this.$http.post('/find/sendResetEmail', {
        student_id: this.student_id, name: this.student_name, username: this.username
      }, {timeout: 10000})
          .then(response => {
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("系统异常，请稍后重试");
              return;
            }
            if(response.data.status === -2){
              showFailToast("账号信息不匹配");
              return;
            }
            if(response.data.status === -3){
              showFailToast("尝试次数过多，请稍后再试");
              return;
            }
            if(response.data.status === -1){
              showToast("邮件已发送，请勿在两分钟内重复提交");
              this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
              this.useStudentEmail = false;
              this.step = 1;
              return;
            }
            if(response.data.status === 0){
              showConfirmDialog({
                title: '注册邮箱不可用',
                message:
                    '此账号未登记有效邮箱。你可以改发校园邮箱，或取消后联系管理员重置密码。',
                confirmButtonText: '发送到校园邮箱',
                cancelButtonText: '取消'
              })
                  .then(() => {
                    this.sendToStudentEmail();
                  })
                  .catch(() => {
                    if(this.$route.path !== '/adminResetPassword')
                      this.$router.push('/inbox');
                    showDialog({
                      message: '已取消在线重置。如仍需帮助，请联系管理员核验身份。',
                      confirmButtonText: '知道了'
                    });
                  });
              //
              return;
            }
            showSuccessToast("邮件已发送，请继续重置密码");
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
            this.step = 1;
          }).catch(error => {
            this.disabled = false;
            showFailToast('网络异常，请稍后重试');
          });
    },
    onSubmitCheck() {
      if (this.username.length === 0) {
        showToast({
          message: '请输入用户名',
          position: 'top',
        });
        return;
      }
      if (this.student_name.length === 0) {
        showToast({
          message: '请输入姓名',
          position: 'top',
        });
        return;
      }
      if (this.student_id.length === 0) {
        showToast({
          message: '请输入学号',
          position: 'top',
        });
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onSubmitQuery();
      else this.isShow = true;
    },
    onSubmitReset(){
      this.isShow = false;
      this.disabled = true;
      const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}/;
      if(pattern.test(this.password) === false){
        this.disabled = false;
        showToast("密码至少 8 位，且须包含大小写字母、数字和特殊符号");
        return;
      }
      this.$http.post('/find/resetPassword', { code: this.verify_code, password: this.password })
          .then(response =>{
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("系统异常，请稍后重试");
              return;
            }
            if(response.data.status === -2){
              showFailToast("验证码错误");
              return;
            }
            if(response.data.status === -3){
              showFailToast("尝试次数过多，请稍后再试");
              return;
            }
            if(response.data.status === -1){
              showFailToast("验证码已过期，请重新发送邮件");
              this.step = 0;
              this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
              this.useStudentEmail = false;
              return;
            }
            showSuccessToast("密码重置成功，请妥善保存并重新登录");
            if(this.$route.path !== '/adminResetPassword')
              this.$router.push("/login");
            this.step = 0;
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
          }).
      catch(error =>{
        this.disabled = false;
        showFailToast('网络异常，请稍后重试');
      });
    },
    onCheckReset(){
      if(this.verify_code.length === 0){
        showToast({
          message: '请输入验证码',
          position: 'top',
        });
        return;
      }
      if(this.password.length === 0){
        showToast({
          message: '请输入新密码',
          position: 'top',
        });
        return;
      }
      if(this.password !== this.password_confirm){
        showToast({
          message: '两次输入的密码不一致',
          position: 'top',
        });
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onSubmitReset();
      else this.isShow = true;
    },
    sendToStudentEmail(){
      this.isShow = false;
      this.disabled = true;
      this.$http.post('/find/sendResetEmail', {
        student_id: this.student_id, name: this.student_name,
        username: this.username, StudentEmail: 1
      }, {timeout: 10000})
          .then(response => {
            this.disabled = false;
            if(response.status !== 200){
              showFailToast("系统异常，请稍后重试");
              return;
            }
            if(response.data.status === -2){
              showFailToast("账号信息不匹配");
              return;
            }
            if(response.data.status === -3){
              showFailToast("尝试次数过多，请稍后再试");
              return;
            }
            if(response.data.status === -1){
              showToast("邮件已发送，请勿在两分钟内重复提交");
              this.verify_code = this.password = this.password_confirm = '';
              this.useStudentEmail = false;
              this.step = 1;
              return;
            }
            showSuccessToast("验证码已发送到校园邮箱，请继续重置密码");
            this.verify_code = this.password = this.password_confirm = this.student_name = this.username = this.student_id = '';
            this.useStudentEmail = false;
            this.step = 1;
          }).catch(error => {
        this.disabled = false;
        showFailToast('网络异常，请稍后重试');
      });
    }
  }
}
</script>

<style scoped lang="scss">

</style>
