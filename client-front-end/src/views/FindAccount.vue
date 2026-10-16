<template>
  <Vcode :show="isShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="onSubmitQuery"
         @close="close"
  />
  <van-nav-bar
      title="找回用户名"
      left-text="返回"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
      v-if="$route.path !== '/adminFindAccount'"
  />
  <van-steps :active="step" style="margin-top: 12pt; width: 60%; margin-left: auto; margin-right: auto;">
    <van-step>填写信息</van-step>
    <van-step>查看结果</van-step>
  </van-steps>
  <br/>
  <div v-if="step === 0">
    <van-cell-group inset>
      <van-cell title="请填写以下信息以找回用户名"/>
      <van-field
          v-model="student_name"
          name="Name"
          label="姓名"
          placeholder="填写真实姓名"
      />
      <van-field
          v-model="student_id"
          name="Student ID"
          label="学号"
          placeholder="填写学号"
      />
    </van-cell-group>
    <br/>
    <br/>
    <van-button round block icon="search" style="width: 50%; margin-left: 25%" type="primary" @click="onSubmitCheck">查询用户名</van-button>
  </div>
  <div v-if="step === 1">
    <van-empty image="search" v-if="state !== 0" :description="description" />
    <div v-if="state === 0">
      <div class="account-recovery-result">
        <h3>已找到用户名</h3>
        <p style="text-align: left; margin-left: 5pt">你的用户名是：</p>
        <ul><li style="font-size: 20pt; color: #1988f8"><strong>{{ account }}</strong></li></ul>
        <p style="text-align: left; margin-left: 5pt">请妥善保存。</p>
      </div>

      <br/>
    </div>
    <van-button round block icon="replay" style="width: 60%; margin-left: 25%; margin-bottom: 8pt" type="warning" v-if="state === -1" @click="this.step = 0">修改后重试</van-button>
    <van-button round block icon="revoke" style="width: 60%; margin-left: 25%" type="default" v-if="state !== -2 && $route.path !== '/adminFindAccount'" @click="onClickLeft">返回首页</van-button>
  </div>
  <br/>

</template>

<script>
import { showToast } from 'vant';
import Cookies from "js-cookie";
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';
export default {
  setup() {
    const onClickLeft = () => history.back();
    return {
      onClickLeft,
    };
  },
  data(){
    return {
      step: 0,
      student_name: '',
      student_id: '',
      description: '查询中...',
      state: -2,
      account: '',
      isShow: false
    };
  },
  methods:{
    onSubmitQuery(){
      this.isShow = false;
      this.step = 1;
      this.$http.post('/find/queryUserName', { student_id: this.student_id, name: this.student_name })
          .then(response =>{
            if(response.status !== 200){
              this.state = -1;
              this.description = "系统异常，请稍后重试";
            }
            if(response.data.status === -1){
              this.state = -1;
              this.description = "没有找到符合条件的账号";
            }
            if(response.data.status === -3){
              this.state = -1;
              this.description = "尝试次数过多，请稍后再试";
            }
            if(response.data.status === 0){
              this.account = response.data.data;
              this.state = 0;
            }
          }).
      catch(error =>{
        this.state = -1;
        this.description = "网络异常，请稍后重试";
      });
    },
    onSubmitCheck(){
      if(this.student_name.length === 0){
        showToast({
          message: '请输入真实姓名',
          position: 'top',
        });
        return;
      }
      if(this.student_id.length === 0){
        showToast({
          message: '请输入学号',
          position: 'top',
        });
        return;
      }
      if (skipPuzzleForLocalDemo()) this.onSubmitQuery();
      else this.isShow = true;
    }
  }
}
</script>

<style scoped lang="scss">

.account-recovery-result {
  font-size: 11pt;
  max-width: 75vw;
  margin: 0 auto 0 auto;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  background-color: #fff;
  text-align: center;
  word-break: break-word;
  overflow-wrap: break-word;
}
.account-recovery-result ul li {
  max-width: 85%;
  word-wrap: break-word;
  margin: 0 auto 0 auto;
}


</style>
