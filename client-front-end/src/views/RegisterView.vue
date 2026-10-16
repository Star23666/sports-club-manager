<template>
  <div>
    <Vcode :show="isShow"
           slider-text="拖动滑块完成验证"
           fail-text="验证失败，请重试"
           success-text="验证通过"
           :range="5"
           @success="success"
           @close="close"
    />
  </div>
  <van-nav-bar
      title="注册新账号"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
  />
  <br/>
  <br/>
  <br/>
  <van-cell-group inset>
    <van-cell title="填写注册信息" label="请填写以下资料。审核通过后，即可报名参加俱乐部活动。" />
  </van-cell-group>
  <br/>
  <van-form @submit="onSubmit">
    <van-cell-group inset>
      <van-cell title="账号信息"/>
      <van-field
          v-model="username"
          name="賬號"
          label="用户名"
          placeholder="仅支持字母和数字"
          :rules="[{ required: true, message: '请输入用户名' }]"
      />
      <van-field
          v-model="password"
          type="password"
          name="密碼"
          label="密码"
          placeholder="设置密码"
          :rules="[{ required: true, message: '请输入密码' }]"
      />
      <van-field
          v-model="password_confirm"
          type="password"
          name="密碼"
          label="确认密码"
          placeholder="再次输入密码"
          :rules="[{ required: true, message: '请再次输入密码' }]"
      />
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="个人信息"/>
      <van-field
          v-model="student_name"
          name="姓名"
          label="姓名"
          placeholder="填写真实姓名"
          :rules="[{ required: true, message: '请输入姓名' }]"
      />
      <van-field
          v-model="student_id"
          name="学号"
          label="学号"
          placeholder="填写学生证上的学号"
          :rules="[{ required: true, message: '请输入学号' }]"
      />
      <van-field
          v-model="member_id"
          name="會員卡號"
          label="会员卡号"
          placeholder="填写会员卡号"
          :rules="[{ required: true, message: '请输入会员卡号' }]"
      />
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="联系方式"/>
      <van-field
          v-model="phone"
          type="tel"
          name="手机号"
          label="手机号"
          placeholder="请包含区号，如 +86"
          :rules="[{ required: true, message: '请输入手机号' }]"
      />
      <van-field
          v-model="wechat_id"
          name="微信号"
          label="微信号"
          placeholder="用于活动联系"
          :rules="[{ required: true, message: '请输入微信号' }]"
      />
      <van-field
          v-model="email"
          name="邮箱"
          label="邮箱"
          placeholder="可不填写"
      />
    </van-cell-group>
    <br/>
    <van-row justify="center">
      <van-space :size="20">
        <van-button round block type="warning" :disabled="disabled" native-type="submit" icon="guide-o" >
          提交注册
        </van-button>
        <van-button round block type="default" :disabled="disabled" icon="replay" @click="onRewrite">
          重填
        </van-button>
      </van-space>
    </van-row>
  </van-form>
  <br/>
</template>

<script>
import {showFailToast, showSuccessToast, showToast, Toast} from 'vant';
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';
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
        showFailToast("两次输入的密码不一致，请重新输入");
        return;
      }
      if (skipPuzzleForLocalDemo()) this.success();
      else this.isShow = true;
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
        showToast("密码至少 8 位，且须包含大小写字母、数字和特殊符号");
        this.isShow = false;
        return;
      }
      this.$http.post('/user/register', {
        username: this.username, password: this.password, name: this.student_name,
        card_id: this.member_id, phone: this.phone, wechat_id: this.wechat_id,
        student_id: this.student_id, email: this.email
      })
          .then(data => {
            if(data.status !== 200){
              showFailToast("系统异常，请稍后重试");
              this.disabled = false;
              return;
            }
            if(data.data.status === -3){
              showFailToast("注册尝试过于频繁，请稍后再试");
              this.disabled = false;
              return;
            }
            if(data.data.status === -2){
              showFailToast(data.data.data || "注册资料格式不正确");
              this.disabled = false;
              return;
            }
            if(data.data.status === -1){
              showFailToast(data.data.data === 'Invalid Password Format' ? '密码格式不符合要求' : '用户名已存在，请更换后重试');
              this.password = this.password_confirm = '';
            }
            if(data.data.status === 0){
              showSuccessToast('注册成功，请等待管理员审核');
              this.$router.push("/login");
            }
            this.disabled = false;
          })
          .catch(error =>{
            showFailToast("网络异常，请稍后重试");
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
