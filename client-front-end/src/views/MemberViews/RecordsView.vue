<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <Vcode :show="isShow"
         slider-text="Drag Slider to Complete Puzzle"
         fail-text="Verification Failed, Please Try Again"
         success-text="Verification Passed"
         :range="5"
         @success="send_transfor"
         @close="close"
  />
  <van-action-sheet v-model:show="transfor_show" title="Initiate a Transfer" z-index="100">
    <van-cell-group>
      <van-cell title="Transfer Instructions" label="If you are unable to participate in an activity for which registration is closed, you may try to transfer your registration to a student who needs it. However, please note that once a transfer is made, it cannot be withdrawn, and the enrollment will be automatically changed from your account after the other person accepts the transfer! Please fill in the full username of the student you want to receive, so that the student you want to receive can check the “Transfer and Wait” after the transfer is initiated. If you don\'t want to specify a specific student to be accepted, you can leave the “username” field blank, which will allow any non-blocked student, including yourself, to accept your transfer!"/>
      <van-field
          v-model="username"
          name="username"
          label="Username"
          placeholder="Account to be Received"
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="success" @click="send_transfor_first" icon="guide-o" style="width: 200px">
          Transfer Initiation
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="wechat_show" title="Join WeChat Group" z-index="100">
    <van-cell-group>
      <van-cell title="Notice">
        <template #label>
          Please long press the QR code below and select “Scan QR Code” to join the wechat group after the jump.
          Please use your registered WeChat {{wechat_id}} join this group. If you join under a different account, you may be removed from the chat by the administrator.
          If your WeChat account has changed, please update your contact information in a timely manner.
        </template>
      </van-cell>
      <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 10pt; color: gray">
        <vue-qrcode :value="wechat_url" :width="300"/>
      </van-row>
      <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 8pt; color: gray">
        *Long press QR code to join the group, for account owner only
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-pull-refresh
      pulling-text="Pull Down to Refresh..."
      loosing-text="Release to Refresh..."
      loading-text="Loading..."
      success-text="Refresh Successfully..."
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="recordList.length === 0">
      <van-empty description="No Participation Record" />
    </div>
    <van-row justify="center">
      <div v-for="item in recordList">
        <van-cell-group inset style="width: 360px; max-width: calc(100vw - 32px); box-sizing: border-box">
          <van-row justify="center" style="margin: 10px 0px 0px 0px;">
            <van-image
                width="90"
                height="90"
                :src="require('@/assets/badminton.png')"
            />
          </van-row>
          <van-row justify="center" style="margin: 5px 0px 5px 0px; font-size: 12pt">
            {{item.action_title}}
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 9pt; color: gray">
            Time: {{item.action_time_range}} &nbsp; {{item.action_date}}
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 9pt; color: gray">
            Location: {{item.action_place}} &nbsp; &nbsp; Racket: {{item.borrow ? 'Borrowed' : 'Unborrowed'}}
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 9pt; color: gray">
            {{item.account_name}}({{item.account_student_id}})
          </van-row>
          <van-divider/>
          <van-row justify="center" style="margin: 10px 0px 0px 0px; font-size: 8pt;">
            {{item.sign_code}}
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 10pt; font-weight: bold; color: gray">
            <vue-qrcode :value="item.sign_code" :width="240"/>
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 10px 0px; font-size: 8pt; color: gray">
            *Please show this code to verify, for account owner only
          </van-row>

          <van-divider/>
          &nbsp&nbsp
          <van-cell style="margin: -38px 0px 10px 0px;">
            <template #title>
              <div style="font-size: 9pt; margin: 6px 0px 0px 10px; font-weight: bold;">
                {{item.state == 1 ? "Signed" : "Unsigned"}}
              </div>
            </template>
            <div v-if="item.action_state < 4">
              <van-button v-if="item.action_state === 3" @click="onTransforClick(item.id)" type="warning" size="mini" icon="share-o">Transfer</van-button>&nbsp
              <van-button v-if="item.action_state === 3" @click="onWechatClick(item.id)" type="success" size="mini" icon="chat-o">WeChat</van-button>
              <van-button v-if="item.action_state < 3" @click="onCanclClick(item.id)" type="danger" size="mini" icon="cross" :disabled="buttonDisabled">Quit Participation</van-button>
            </div>
            <div v-else-if="item.action_state == 4" style="font-size: 8pt; color: red; font-weight: bold; margin: 7px 0px 0px 0px;">
              In Progress
            </div>
            <div v-else style="font-size: 8pt; color: black; margin: 7px 0px 0px 0px;">
              Terminated
            </div>
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
import VueQrcode from 'vue-qrcode';
import {showConfirmDialog, showFailToast, showSuccessToast} from 'vant';
import Cookies from "js-cookie";

export default {
  components: {VueQrcode},
  created(){
    this.loading = true;
    this.onRefresh();
  },
  data(){
    return{
      buttonDisabled: false,
      isLoading: false,
      isShow: false,
      currentId: -1,
      recordList: [ ],
      wechat_id: '',
      wechat_url: '',
      wechat_show: false,
      transfor_show: false,
      transfor_account: '',
      loading: false,
      username: ''
    };
  },
  methods: {
    onRefresh() {
      this.isLoading = true;
      this.$http.post('/action/queryRecord?token='+Cookies.get('token'))
          .then(response => {
            this.loading = false;
            this.isLoading = false;
            if(response.status === 200){
              if(response.data.status <= 0){
                this.$memberVerify();
                return;
              }
              this.recordList = response.data.data;
            }
          })
          .catch(error =>{
            this.loading = false;
            this.isLoading = false;
            console.log(error);
          });
      /*this.recordList = [
        {id:0, action_title: '8月13日打球活動（前半場）', action_place:'東亞運體育館', action_date: '2024年8月13日', action_time_range: '14:00~15:00', account_student_id: '122003047', account_name: '費才軒', sign_code: 'd66067b8-122e-4e3f-9d7e-fa7abe3bbda0', borrow: false, action_state: 3, state: 0},
        {id:1, action_title: '8月22日打球活動（后半場）', action_place:'科大體育館J座', action_date: '2024年8月22日', action_time_range: '15:00~16:00', account_student_id: '122003047', account_name: '費才軒', sign_code: '4d93f326-3f48-4a43-929d-b6489f4754b5', borrow: true, action_state: 2, state: 0},
        {id:2, action_title: '7月12日打球活動（后半場）', action_place:'科大體育館J座', action_date: '2024年7月12日', action_time_range: '15:00~16:00', account_student_id: '122003047', account_name: '費才軒', sign_code: 'a98f184e-976c-25a7-5258-57570a66d6d7', borrow: true, action_state: 4, state: 1},
        {id:3, action_title: '7月5日打球活動（后半場）', action_place:'科大體育館J座', action_date: '2024年7月5日', action_time_range: '15:00~16:00', account_student_id: '122003047', account_name: '費才軒', sign_code: 'b98f184e-976c-25a7-5258-57570a66d6d7', borrow: true, action_state: 5, state: 1}
      ]*/
    },
    onTransforClick(id) {
      this.currentId = id;
      this.username = '';
      this.transfor_show = true;
    },
    onCanclClick(id) {
      this.currentId = id;
      showConfirmDialog({
        title: 'Alarm',
        confirmButtonText: 'Continue',
        cancelButtonText: 'Cancel',
        message:
            'After you quiting the participation, the vacant quota will be given to students on the waiting list in order of priority when there are students on the waiting list. This may result in you being unable to re-participate, so please consider carefully whether to continue!',
      }).then(() => {
            this.buttonDisabled = true;
            this.loading = true;
            this.$http.post('/action/cancelAction?token='+Cookies.get('token')
                +`&record_id=${this.currentId}`)
                .then(response => {
                  this.loading = false;
                  if(response.status !== 200){
                    showFailToast("System Error");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === -2){
                    this.$memberVerify();
                  }
                  if(response.data.status === -1){
                    showFailToast("The record does not exist, please refresh the page");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 0){
                    showFailToast("The current action has ended for participation and cannot be canceled");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 1){
                    showFailToast("User information does not match records");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 2){
                    showSuccessToast("Quit participation successful!");
                    this.onRefresh();
                    this.buttonDisabled = false;
                  }
                })
                .catch(error => {
                  this.loading = false;
                  console.log(error);
                  showFailToast("Internet Error");
                  this.buttonDisabled = false;
                });
      }).catch(() => {});
    },
    onWechatClick(id){
      this.loading = true;
      this.currentId = id;
      this.buttonDisabled = true;
      this.$http.post('/action/queryWechatGroup?token='+Cookies.get('token')
          +`&record_id=${this.currentId}`)
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("System Error");
              this.buttonDisabled = false;
            }
            if(response.data.status <= 0){
              showFailToast("Please refresh the page and try again");
              this.buttonDisabled = false;
            }
            if(response.data.status > 0){
              this.wechat_id = response.data.data.wechat_id;
              this.wechat_url = response.data.data.wechat_url;
              this.wechat_show = true;
            }
          })
          .catch(error => {
            this.loading = false;
            showFailToast("Internet Error");
            this.buttonDisabled = false;
          })

    },
    close(){
      this.isShow = false;
    },
    send_transfor_first(){
      this.isShow = true;
    },
    send_transfor(){
      this.loading = true;
      this.isShow = false;
      this.buttonDisabled = true;
      this.$http.post(`transfer/transferRecord?token=${Cookies.get('token')}&record_id=${this.currentId}`, {
        receive_user: this.username
      })
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              showFailToast("System Error");
              this.buttonDisabled = false;
            }
            if(response.data.status === -2){
              this.$memberVerify();
            }
            if(response.data.status === -1){
              showFailToast("Please refresh the page and try again");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 0){
              showFailToast("The current action is already in progress/has terminated, so the transfer cannot be initiated.");
              this.buttonDisabled = false;
              this.transfor_show = false;
              this.onRefresh();
            }
            if(response.data.status === 1){
              showFailToast("The account does not match, please refresh the page and try again");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 2){
              showFailToast("The current record has been transferred. Please wait patiently for the receiving user to complete the operation.");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 3){
              showFailToast("The receiving user message was not found. Please check carefully whether the username is complete and correct.");
              this.buttonDisabled = false;
            }
            if(response.data.status === 4){
              showSuccessToast("The transfer is successful and the other party will receive your transfer");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
          })
          .catch(error => {
            this.loading = false;
            showFailToast("Internet Error");
            this.buttonDisabled = false;
          });
    }
  }
}
</script>
