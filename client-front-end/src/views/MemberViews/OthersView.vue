<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="Loading..."></van-toast>
  <van-tabs v-model:active="active" sticky offset-top="56" @change="onClickTab(name)" type="card" swipeable>
    <van-tab title="Waitlist" name="1">
      <van-pull-refresh
          pulling-text="Pull Down to Refresh..."
          loosing-text="Release to Refresh..."
          loading-text="Loading..."
          success-text="Refresh Successfully..."
          v-model="waitingRefresh"
          @refresh="onWaitingRefresh">
        <br/>
      <div v-if="waitingList.length === 0">
        <van-empty description="No Relevant Waiting Records" />
      </div>
      <van-row justify="center">
      <div v-for="item in waitingList">
        <van-cell-group inset style="min-width: 360px">
          <van-cell title="Action">{{item.action_title}}</van-cell>
          <van-cell title="Waiting for">{{item.action_user}}</van-cell>
          <van-cell title="Queuing Rank">{{item.wait_rank}}</van-cell>
          <van-cell><van-button @click="onCancelClick(item.id)" type="danger" size="small" icon="cross" :disabled="buttonDisabled">Quit Waiting</van-button></van-cell>
        </van-cell-group>
        <br/>
      </div>
      </van-row>
      </van-pull-refresh>
      <br/>
      <br/>
    </van-tab>
    <van-tab title="Transfer Receipt" name="2">
      <van-pull-refresh
          pulling-text="Pull Down to Refresh..."
          loosing-text="Release to Refresh..."
          loading-text="Loading..."
          success-text="Refresh Successfully..."
          v-model="transferRefresh"
          @refresh="onTransferRefresh">
      <br/>
        <div v-if="presentList.length === 0">
          <van-empty description="No Transfers Available Yet" />
        </div>
      <van-row justify="center">
      <div v-for="item in presentList">
        <van-cell-group inset style="min-width: 360px">
          <van-cell title="Action Name">{{item.action_title}}</van-cell>
          <van-cell title="Initiator">{{item.send_user}}</van-cell>
          <van-cell title="Recipient">{{item.receive_user == '' ? 'Anyone' : item.receive_user}}</van-cell>
          <van-cell>
            <van-button @click="onRefuseClick(item.id)" v-if="item.receive_user != ''" type="danger" size="small" icon="cross">Refuse</van-button>&nbsp
            <van-button @click="onAcceptClick(item.id)" type="success" size="small" icon="success">Accept</van-button>
          </van-cell>
        </van-cell-group>
        <br/>
      </div>
      </van-row>
      </van-pull-refresh>
    </van-tab>
  </van-tabs>
</template>

<script>
import Cookies from "js-cookie";
import {showConfirmDialog, showFailToast, showSuccessToast} from "vant";

export default {
  data(){
    return {
      buttonDisabled: false,
      currentId: 0,
      active: 0,
      waitingRefresh: false,
      transferRefresh: false,
      loading: false,
      waitingList: [],
      presentList: []
    };
  },
  created(){
    this.loading = true;
    this.$memberVerify();
    this.onWaitingRefresh();
  },
  methods: {
    onClickTab(name){
      if(name === 1){
        this.loading = true;
        this.$memberVerify();
        this.onWaitingRefresh();
      }else{
        this.loading = true;
        this.$memberVerify();
        this.onTransferRefresh();
      }
    },
    onCancelClick(id){
      this.currentId = id;
      showConfirmDialog({
        title: 'Alarm',
        confirmButtonText: 'Quit Waiting',
        cancelButtonText: 'Cancel',
        message:
            'After quiting waiting, you need to queue up again. Please consider carefully whether to quit from the waitlist!',
      }).then(() => {
        this.loading = true;
        this.buttonDisabled = true;
        this.$http.post('/waiting/waitDelete?token='+Cookies.get('token')
            +`&waiting_id=${this.currentId}`)
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
                showFailToast("The waiting may have been successfully added or the action may have ended. Please refresh the page.");
                this.onWaitingRefresh();
                this.buttonDisabled = false;
              }
              if(response.data.status === 0){
                showFailToast("User information does not match the alternate record");
                this.onWaitingRefresh();
                this.buttonDisabled = false;
              }
              if(response.data.status === 1){
                showSuccessToast("Cancelled the waiting list successfully");
                this.onWaitingRefresh();
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
    onRefuseClick(id){
      this.currentId = id;
      showConfirmDialog({
        title: 'Alarm',
        confirmButtonText: 'Refuse',
        cancelButtonText: 'Cancel',
        message:
            'After refusing to accept the transfer, the other party will need to initiate the transfer again. Please consider carefully.',
      }).then(() => {
        this.loading = true;
        this.$http.post(`transfer/refuseTransfer?token=${Cookies.get('token')}&transfer_id=${this.currentId}`)
            .then(response => {
              this.loading = false;
              if(response.status !== 200){
                showFailToast("系統錯誤");
                this.buttonDisabled = false;
              }
              if(response.data.status === -2){
                this.$memberVerify();
              }
              if(response.data.status === -1){
                showFailToast("The action has started or the transfer has been accepted, resulting in the transfer being invalidated. The page will be refreshed automatically.");
                this.onTransferRefresh();
                this.buttonDisabled = false;
              }
              if(response.data.status === 0){
                showFailToast("The current user information does not match, please try again later\n");
                this.buttonDisabled = false;
                this.onWaitingRefresh();
              }
              if(response.data.status === 1){
                showFailToast("You have declined to receive this registration transfer");
                this.onTransferRefresh();
                this.buttonDisabled = false;
              }
            })
            .catch(error => {
              showFailToast("Internet Error");
              this.loading = false;
              this.buttonDisabled = false;
            });
      }).catch(() => {});
    },
    onAcceptClick(id){
      this.loading = true;
      this.currentId = id;
      this.$http.post(`transfer/acceptTransfer?token=${Cookies.get('token')}&transfer_id=${this.currentId}`)
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
              showFailToast("The action has started or this transfer has been accepted by someone else, making it invalid.\n");
              this.onTransferRefresh();
              this.buttonDisabled = false;
            }
            if(response.data.status === 0){
              showFailToast("The current user has lost his credibility and cannot accept transfers without a designated recipient!\n");
              this.onTransferRefresh();
              this.buttonDisabled = false;
            }
            if(response.data.status === 1){
              showFailToast("You have already participated in this action and cannot participate in it again by receiving a transfer!\n");
              this.buttonDisabled = false;
            }
            if(response.data.status === 2){
              showSuccessToast("The transfer has been successfully received. Please check the record in 'Participation' and attend the action on time.\n");
              this.onTransferRefresh();
              this.buttonDisabled = false;
            }
          })
          .catch(error => {
            showFailToast("Internet Error");
            this.buttonDisabled = false;
          });
    },
    onWaitingRefresh(){
      this.waitingRefresh = true;
      this.$http.post('/waiting/queryWaiting?token='+Cookies.get('token'))
          .then(response => {
            this.loading = false;
            console.log(response);
            if(response.status === 200 && response.data.status > 0){}
              this.waitingList = response.data.data;
            this.waitingRefresh = false;
          })
          .catch(error =>{
            console.log(error);
            this.waitingRefresh = false;
          });
    },
    onTransferRefresh(){
      this.transferRefresh = true;
      this.$http.post('/transfer/queryTransfer?token='+Cookies.get('token'))
          .then(response => {
            this.loading = false;
            if(response.status === 200 && response.data.status > 0)
              this.presentList = response.data.data;
            this.transferRefresh = false;
          })
          .catch(error =>{
            console.log(error);
            this.loading = false;
            this.transferRefresh = false;
          });
    }
  }
}
</script>


<style scoped lang="scss">

</style>