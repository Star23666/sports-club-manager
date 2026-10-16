<template>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onSubmitQuery"
         @close="close"
  />
  <van-nav-bar
      title="Query Username"
      left-text="Back"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
      v-if="$route.path !== '/adminFindAccount'"
  />
  <van-steps :active="step" style="margin-top: 12pt; width: 60%; margin-left: auto; margin-right: auto;">
    <van-step>Fill in Information</van-step>
    <van-step>Getting Results</van-step>
  </van-steps>
  <br/>
  <div v-if="step === 0">
    <van-cell-group inset>
      <van-cell title="Please fill in the following information for username enquiry"/>
      <van-field
          v-model="student_name"
          name="Name"
          label="Name"
          placeholder="Please fill in the name on your ID"
      />
      <van-field
          v-model="student_id"
          name="Student ID"
          label="Student ID"
          placeholder="Please fill in your student ID"
      />
    </van-cell-group>
    <br/>
    <br/>
    <van-button round block icon="search" style="width: 50%; margin-left: 25%" type="primary" @click="onSubmitCheck">Query Username</van-button>
  </div>
  <div v-if="step === 1">
    <van-empty image="search" v-if="state !== 0" :description="description" />
    <div v-if="state === 0">
      <div class="account-recovery-result">
        <h3>Username has been found</h3>
        <p style="text-align: left; margin-left: 5pt">Upon inquiry, your username is:</p>
        <ul><li style="font-size: 20pt; color: #1988f8"><strong>{{ account }}</strong></li></ul>
        <p style="text-align: left; margin-left: 5pt">Please take good care of it!</p>
      </div>

      <br/>
    </div>
    <van-button round block icon="replay" style="width: 60%; margin-left: 25%; margin-bottom: 8pt" type="warning" v-if="state === -1" @click="this.step = 0">Modify for Re-Enquiry</van-button>
    <van-button round block icon="revoke" style="width: 60%; margin-left: 25%" type="default" v-if="state !== -2 && $route.path !== '/adminFindAccount'" @click="onClickLeft">Return to Homepage</van-button>
  </div>
  <br/>

</template>

<script>
import { showToast } from 'vant';
import Cookies from "js-cookie";
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
      description: 'Querying...',
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
              this.description = "System Error";
            }
            if(response.data.status === -1){
              this.state = -1;
              this.description = "No records have been found";
            }
            if(response.data.status === 0){
              this.account = response.data.data;
              this.state = 0;
            }
          }).
      catch(error =>{
        this.state = -1;
        this.description = "Internet Error";
      });
    },
    onSubmitCheck(){
      if(this.student_name.length === 0){
        showToast({
          message: 'A real name cannot be empty.',
          position: 'top',
        });
        return;
      }
      if(this.student_id.length === 0){
        showToast({
          message: 'The student ID cannot be empty.',
          position: 'top',
        });
        return;
      }
      this.isShow = true;
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
