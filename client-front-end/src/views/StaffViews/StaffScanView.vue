<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加載中..."></van-toast>
  <div>
    <QrScanner v-if="showQrCodeReader" @decode="onDecodeHandler" @close="qrReaderClose" />
  </div>
  <van-nav-bar
      title="Verify & Sign"
      left-text="Back"
      left-arrow
      fixed
      @click-left="onClickLeft"
      placeholder
  />

  <van-cell-group v-if="!sign_code" inset class="scan-entry">
    <van-cell title="Check a member in" label="Scan their QR code or enter the code shown below it." />
    <van-field
        v-model.trim="manualCode"
        label="Sign-in code"
        placeholder="Enter the member's sign-in code"
        maxlength="100"
        clearable
        @keyup.enter="submitManualCode"
    />
    <div class="scan-entry-actions">
      <van-button icon="scan" plain type="primary" @click="startScan">Scan QR code</van-button>
      <van-button type="primary" @click="submitManualCode">Look up code</van-button>
    </div>
  </van-cell-group>

  <van-notice-bar left-icon="volume-o" color="#1989fa" background="#ecf9ff" v-if="sign_code && !show_sign && !isLoading"
                  style="position: fixed; z-index: 1000; width: 100%">
    <van-swipe
        vertical
        class="notice-swipe"
        :autoplay="16000"
        :touchable="false"
        :show-indicators="false"
        ref="swipe"
    >
      <van-swipe-item>{{ notice_messgae }}, this result is only used to verify the validity of this records!</van-swipe-item>
      <van-swipe-item v-if="!this.show_sign && !this.signed">If there are special circumstances that prevent you from signing in, you can send this screenshot to an administrator to complete the Re-Sign operation!</van-swipe-item>
    </van-swipe>
  </van-notice-bar>

  <br v-if="sign_code && !show_sign && !isLoading"/>
  <br v-if="sign_code && !show_sign && !isLoading"/>
  <div v-if="sign_code && isLoading">
    <van-empty image="search" description="Loading..." />
  </div>
  <br/>
  <div v-if="sign_code && !isLoading">
    <van-cell-group inset>
      <van-row justify="center" style="margin: 0px 0px 0px 0px;">
        <h4>{{actionInf.title}}&nbsp;</h4>
      </van-row>
      <van-row justify="center" style="margin: -22px 0px 0px 0px; font-size: 10pt; color: gray">
        <vue-qrcode :value="sign_code" :width="180"/>
      </van-row>
      <van-row justify="center" style="margin: 0px 0px 20px 0px; font-size: 8pt; font-weight: bold; color: gray">
        {{sign_code}}
      </van-row>
      <van-cell title="Location">{{actionInf.place}}</van-cell>
      <van-cell title="Date">{{actionInf.date}}</van-cell>
      <van-cell title="Time">{{actionInf.time_range}}</van-cell>
      <van-cell title="Racket">{{borrow ? 'Need' : 'No Need'}}</van-cell>
      <van-cell title="Status" v-if="!this.show_sign">{{signed ? 'Signed' : 'Unsigned'}}</van-cell>
      <van-cell v-if="!this.show_sign && !this.signed"></van-cell>
    </van-cell-group>
    <br/>
    <van-cell-group inset>
      <van-cell title="Participant Information"/>
      <van-cell title="Name">{{memInf.name}}</van-cell>
      <van-cell title="Student ID">{{memInf.student_id}}</van-cell>
      <van-cell title="Phone">{{memInf.phone}}</van-cell>
      <van-cell title="Email" v-if="memInf.email !== ''">{{memInf.email}}</van-cell>
      <van-cell title="Wechat ID">{{memInf.wechat_id}}</van-cell>
    </van-cell-group>
    <van-submit-bar
        v-if="show_sign"
        tip="Please check the information carefully to make sure it is correct, and then finish signing in!"
        tip-icon="info-o"
        placeholder>
      <template #button>
        <van-button icon="sign" round type="warning" @click="onSignClick">Sign</van-button>
      </template>
    </van-submit-bar>
  </div>
  <br/>
</template>

<script>
import QrScanner from '@/components/QrScanner';
import VueQrcode from 'vue-qrcode';
import Cookies from "js-cookie";
import {showFailToast, showSuccessToast, showToast, showDialog} from "vant";

export default {
  data(){
    return {
      isLoading: false,
      showQrCodeReader: false,
      sign_code: '',
      manualCode: '',
      notice_messgae: '',
      memInf: {
        name: 'loading...',
        username: 'loading...',
        student_id: 'loading...',
        phone: 'loading...',
        email: 'loading...',
        wechat_id: 'loading...',
        state: 3
      },
      borrow: false,
      signed: false,
      loading: false,
      actionInf: {
        title: 'loading...',
        place:'loading...',
        date: 'loading...',
        time_range: 'loading...'
      },
      show_sign: false
    };
  },
  components:{
    VueQrcode,
    QrScanner
  },
  created() {
    this.$staffVerify();
  },
  methods:{
    startScan(){
      this.showQrCodeReader = true;
    },
    submitManualCode(){
      if (!this.manualCode) {
        showFailToast("Enter a sign-in code first.");
        return;
      }
      this.onDecodeHandler(this.manualCode);
    },
    qrReaderClose(){
      this.showQrCodeReader = false;
    },
    resetLookup(){
      this.sign_code = '';
      this.isLoading = false;
    },
    onDecodeHandler(data){
      this.sign_code = String(data || '').trim();
      this.showQrCodeReader = false;
      if (!this.sign_code) {
        showFailToast("Enter a sign-in code first.");
        return;
      }
      this.isLoading = true;
      this.$http.post(`/staff/querySign?token=${Cookies.get('token')}`, { sign_code: this.sign_code })
          .then(response => {
            if(response.status !== 200){
              this.resetLookup();
              showFailToast("System Error");
              return;
            }
            if(response.data.status < 0) {
              this.$staffVerify();
              return;
            }
            if(response.data.status === 0){
              this.resetLookup();
              showFailToast("The current QR code information is invalid");
              return;
            }
            if(response.data.status === 2){
              this.resetLookup();
              showFailToast("You are not responsible for this action");
              return;
            }
            else{
              this.actionInf = response.data.data.act_inf;
              this.memInf = response.data.data.mem_inf;
              this.borrow = response.data.data.borrow;
              this.signed = response.data.data.signed;
              if(response.data.status === 1){
                this.notice_messgae = "The current code has been signed";
                showDialog({
                  message: 'The current QR code has been signed, this result is only used to verify the validity of this records',
                  confirmButtonText: 'Ok'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 3){
                this.notice_messgae = "The action it belongs to is not enabled for check-in, so you cannot check-in for it.";
                showDialog({
                  message: 'The action it belongs to is not enabled for check-in, so you cannot sign for it. this result is only used to verify the validity of this records!',
                  confirmButtonText: 'Ok'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 4){
                this.notice_messgae = "The action for which the current record belongs has been completed and cannot be signed for";
                showDialog({
                  message: 'The action for which the current record belongs has been completed and cannot be signed for, this result is only used to verify the validity of this records!',
                  confirmButtonText: 'Ok'
                }).then(() => {
                  // on close
                });
              }
              if(response.data.status === 5){
                this.show_sign = true;
                showToast("Please check the information carefully and make sure it is correct before signing in!");
              }
              this.isLoading = false;
            }
          })
          .catch(error =>{
            console.log(error);
            this.resetLookup();
            showFailToast("Internet Error");
          });
    },
    onClickLeft(){
      this.$router.push({path:'/staff'});
    },
    onSignClick(){
      this.loading = true;
      this.$http.post(`/staff/finishSign?token=${Cookies.get('token')}`, { sign_code: this.sign_code })
          .then(response => {
            this.loading = false;
            if(response.status !== 200){
              this.$router.push({path:'/staff'});
              showFailToast("System Error");
            }
            if(response.data.status < 0)
              this.$staffVerify();
            if(response.data.status === 0){
              this.$router.push({path:'/staff'});
              showFailToast("Information Inviled");
            }
            if(response.data.status === 1){
              this.$router.push({path:'/staff'});
              showFailToast("The current code has been signed.");
            }
            if(response.data.status === 2){
              this.$router.push({path:'/staff'});
              showFailToast("The current code does not belong to this action.");
            }
            if(response.data.status === 3){
              this.$router.push({path:'/staff'});
              showFailToast("The current action is not open for signing in.");
            }
            if(response.data.status === 4){
              this.$router.push({path:'/staff'});
              showFailToast("The current action has ended and you cannot sign in.");
            }
            if(response.data.status === 5){
              this.$router.push({path:'/staff'});
              showSuccessToast("Sign Successfully");
            }
          })
          .catch(error => {
            this.loading = false;
            console.log(error);
            this.$router.push({path:'/staff'});
            showFailToast("Internet Error");
          });
    }
  }
};
</script>
<style scoped>
.notice-swipe {
  height: 40px;
  line-height: 40px;
}
.scan-entry {
  margin-top: 20px;
}
.scan-entry-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 16px 16px;
}
.scan-entry-actions .van-button {
  flex: 1 1 130px;
}
</style>


