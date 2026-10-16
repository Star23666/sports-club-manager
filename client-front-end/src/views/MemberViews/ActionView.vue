<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="onSubmit"
         @close="close"
  />
  <van-pull-refresh
      pulling-text="Pull Down to Refresh..."
      loosing-text="Release to Refresh..."
      loading-text="Loading..."
      success-text="Refresh Successfully..."
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="actionList.length === 0">
      <van-empty description="No Activity to Participate in" />
    </div>
    <van-row justify="center">
      <div v-for="item in actionList">
        <van-cell-group inset style="width: 360px; max-width: calc(100vw - 32px); box-sizing: border-box">
          <van-cell :title="item.title"/>
          <van-cell title="Location">{{item.place}}</van-cell>
          <van-cell title="Date">{{item.date}}</van-cell>
          <van-cell title="Time">{{item.time_range}}</van-cell>
          <van-cell title="Maximum">{{item.max_num}} {{item.max_num > 1 ? "Persons" : "Person"}}</van-cell>
          <van-cell title="Borrow a Racket">
            <template #right-icon>
              <van-switch v-model="borrow">
              </van-switch>
            </template>
          </van-cell>
          <van-cell>
            <van-button @click="onClick(item.id)" :disabled="buttonDisabled" type="primary" size="small" icon="plus">Participate</van-button>
          </van-cell>
        </van-cell-group>
        <br/>
      </div>
    </van-row>
    <br/>
    <br/>
  </van-pull-refresh>
</template>

<script>
import Cookies from "js-cookie";
import {showFailToast, showSuccessToast} from "vant";
import { showConfirmDialog } from 'vant';

export default {
  created(){
    this.$memberVerify();
    this.loading = true;
    this.onRefresh();
  },
  data(){
    return{
      borrow: false,
      isLoading: false,
      isShow: false,
      buttonDisabled: false,
      loading: false,
      currentId: -1,
      actionList: []
    };
  },
  methods: {
    onRefresh() {
      this.isLoading = true;
      this.$http.post('/action/queryAction?token='+Cookies.get('token'))
          .then(response => {
            this.loading = false;
            this.isLoading = false;
            if(response.status === 200 && response.data.status === 1)
              this.actionList = response.data.data;
          })
          .catch(error =>{
            console.log(error);
          });
    },
    onClick(id) {
      this.currentId = id;
      this.isShow = true;
    },
    close(){
      this.isShow = false;
    },
    onSubmit(){
      this.loading = true;
      this.isShow = false;
      this.buttonDisabled = true;
      this.$http.post('/action/attendAction?token='+Cookies.get('token')
                          +`&action_id=${this.currentId}&borrow=${this.borrow}`)
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("System Error");
              this.buttonDisabled = false;
            }
            if(response.data.status === -2){
              this.$memberVerify();
            }
            if(response.data.status < 0){
              showFailToast("Your account does not allow you to directly participate in actions!\n");
              this.buttonDisabled = false;
            }
            if(response.data.status === 0){
              showFailToast("The current action has closed for participation, please refresh the page!");
              this.buttonDisabled = false;
            }
            else if(response.data.status === 1){
              showFailToast("You have already participated or are on the waiting list for this event. You cannot participate multiple times!");
              this.buttonDisabled = false;
            }
            else if(response.data.status === 2){
              showConfirmDialog({
                message:
                    'Sorry, the current activity has reached the upper limit. Would you like to join the waiting list? During the open period, if a student cancels his/her participation, priority will be given to students on the waiting list. When the event closes for participation, the waitlist records for uncompleted redemptions will be deleted. You can check the waitlist results in "Participation" after the deadline is announced!',
                confirmButtonText: 'Join Waitlist',
                cancelButtonText: 'Cancel'
              })
                  .then(() => {
                    this.addToWaitList();
                  })
                  .catch(() => {
                    this.buttonDisabled = false;
                  });
            }
            else if(response.data.status === 3){
              showSuccessToast("Participation is successful. Please go to 'Participation' to check the record. Please attend on time.");
              this.buttonDisabled = false;
            }
          })
          .catch(error =>{
            console.log(error);
            showFailToast("Internet Error");
            this.buttonDisabled = false;
          });
      //alert("报名活动：" + this.currentId);
    },
    addToWaitList(){
      this.loading = true;
      this.$http.post('/waiting/waitCreate?token='+Cookies.get('token')
          +`&action_id=${this.currentId}&borrow=${this.borrow}`)
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("System Error");
              this.buttonDisabled = false;
            }
            if(response.data.status < 0){
              showFailToast("Your account does not allow you to add to waitlist!");
              this.buttonDisabled = false;
            }
            if(response.data.status === 0){
              showFailToast("The current action cannot be rescheduled, please refresh the page\n");
              this.buttonDisabled = false;
            }
            if(response.data.status === 1){
              showFailToast("The current action has generated new quotas. Please refresh the page and participate again.");
              this.buttonDisabled = false;
            }
            if(response.data.status === 2){
              showFailToast("The current action cannot be participated in repeatedly");
              this.buttonDisabled = false;
            }
            if(response.data.status === 3){
              showSuccessToast("Already added to the waiting list, please go to 'Transfer and Wait' to view the waiting record.");
              this.buttonDisabled = false;
            }
          })
          .catch(error =>{
            console.log(error);
            showFailToast("Internet Error");
            this.buttonDisabled = false;
          });
    }
  }
}
</script>
