<template>
  <van-toast v-model:show="loading" type="loading" overlay="true" duration="0"
             forbid_click="true" message="加载中..."></van-toast>
  <Vcode :show="isShow"
         slider-text="拖动滑块完成验证"
         fail-text="验证失败，请重试"
         success-text="验证通过"
         :range="5"
         @success="send_transfor"
         @close="close"
  />
  <van-action-sheet v-model:show="transfor_show" title="发起名额转让" z-index="100">
    <van-cell-group>
      <van-cell title="转让说明" label="报名截止后如无法参加，可将名额转让给其他会员。转让发起后不能撤回，对方接受后名额会自动从你的账号转出。填写接收者的完整用户名可指定转让；留空则为公开转让，任何未被限制的会员都可接受。"/>
      <van-field
          v-model="username"
          name="username"
          label="接收用户名"
          placeholder="留空表示公开转让"
      />
      <br/>
      <van-row justify="center">
        <van-button round block type="success" @click="send_transfor_first" icon="guide-o" style="width: 200px">
          发起转让
        </van-button>
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-action-sheet v-model:show="wechat_show" title="加入活动微信群" z-index="100">
    <van-cell-group>
      <van-cell title="温馨提示">
        <template #label>
          长按下方二维码识别后加入微信群。请使用注册时填写的微信号 {{wechat_id}} 入群；若使用其他账号，管理员可能将其移出。微信号变更后请及时更新联系方式。
        </template>
      </van-cell>
      <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 10pt; color: gray">
        <vue-qrcode :value="wechat_url" :width="300"/>
      </van-row>
      <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 8pt; color: gray">
        仅供本人使用，请勿转发二维码
      </van-row>
      <br/>
    </van-cell-group>
  </van-action-sheet>
  <van-pull-refresh
      pulling-text="下拉刷新"
      loosing-text="松开刷新"
      loading-text="加载中..."
      success-text="刷新成功"
      v-model="isLoading"
      @refresh="onRefresh"
  >
    <div v-if="recordList.length === 0">
      <van-empty description="暂无报名记录" />
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
            时间：{{item.action_time_range}} &nbsp; {{item.action_date}}
          </van-row>
          <van-row justify="center" style="margin: 0px 0px 0px 0px; font-size: 9pt; color: gray">
            地点：{{item.action_place}} &nbsp; &nbsp; 球拍：{{item.borrow ? '需要借用' : '无需借用'}}
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
            签到时请出示此码，仅供本人使用
          </van-row>

          <van-divider/>
          &nbsp&nbsp
          <van-cell style="margin: -38px 0px 10px 0px;">
            <template #title>
              <div style="font-size: 9pt; margin: 6px 0px 0px 10px; font-weight: bold;">
                {{item.state == 1 ? "已签到" : "未签到"}}
              </div>
            </template>
            <div v-if="item.action_state < 4">
              <van-button v-if="item.action_state === 3" @click="onTransforClick(item.id)" type="warning" size="mini" icon="share-o">转让</van-button>&nbsp
              <van-button v-if="item.action_state === 3" @click="onWechatClick(item.id)" type="success" size="mini" icon="chat-o">微信群</van-button>
              <van-button v-if="item.action_state < 3" @click="onCanclClick(item.id)" type="danger" size="mini" icon="cross" :disabled="buttonDisabled">取消报名</van-button>
            </div>
            <div v-else-if="item.action_state == 4" style="font-size: 8pt; color: red; font-weight: bold; margin: 7px 0px 0px 0px;">
              进行中
            </div>
            <div v-else style="font-size: 8pt; color: black; margin: 7px 0px 0px 0px;">
              已结束
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
import { skipPuzzleForLocalDemo } from '@/utils/localDemo';

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
        title: '确认取消报名',
        confirmButtonText: '继续取消',
        cancelButtonText: '返回',
        message:
            '取消后，空出的名额会优先递补给候补会员，你可能无法再次报名。确定继续吗？',
      }).then(() => {
            this.buttonDisabled = true;
            this.loading = true;
            this.$http.post('/action/cancelAction?token='+Cookies.get('token')
                +`&record_id=${this.currentId}`)
                .then(response => {
                  this.loading = false;
                  if(response.status !== 200){
                    showFailToast("系统异常，请稍后重试");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === -2){
                    this.$memberVerify();
                  }
                  if(response.data.status === -1){
                    showFailToast("记录不存在，请刷新页面");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 0){
                    showFailToast("活动已截止，不能取消报名");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 1){
                    showFailToast("此报名记录不属于你");
                    this.buttonDisabled = false;
                  }
                  if(response.data.status === 2){
                    showSuccessToast("报名已取消");
                    this.onRefresh();
                    this.buttonDisabled = false;
                  }
                })
                .catch(error => {
                  this.loading = false;
                  console.log(error);
                  showFailToast("网络异常，请稍后重试");
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
              showFailToast("系统异常，请稍后重试");
              this.buttonDisabled = false;
            }
            if(response.data.status <= 0){
              showFailToast("请刷新页面后重试");
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
            showFailToast("网络异常，请稍后重试");
            this.buttonDisabled = false;
          })

    },
    close(){
      this.isShow = false;
    },
    send_transfor_first(){
      if (skipPuzzleForLocalDemo()) this.send_transfor();
      else this.isShow = true;
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
              showFailToast("系统异常，请稍后重试");
              this.buttonDisabled = false;
            }
            if(response.data.status === -2){
              this.$memberVerify();
            }
            if(response.data.status === -1){
              showFailToast("请刷新页面后重试");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 0){
              showFailToast("活动已开始或结束，不能发起转让");
              this.buttonDisabled = false;
              this.transfor_show = false;
              this.onRefresh();
            }
            if(response.data.status === 1){
              showFailToast("账号与记录不匹配，请刷新后重试");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 2){
              showFailToast("该名额已发起转让，请等待对方处理");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
            if(response.data.status === 3){
              showFailToast("找不到接收者，请核对完整用户名");
              this.buttonDisabled = false;
            }
            if(response.data.status === 4){
              showSuccessToast("转让已发起，等待对方接受");
              this.buttonDisabled = false;
              this.transfor_show = false;
            }
          })
          .catch(error => {
            this.loading = false;
            showFailToast("网络异常，请稍后重试");
            this.buttonDisabled = false;
          });
    }
  }
}
</script>
