<template>
  <lay-layer v-model="loading" type="3" shade-close="false"/>
  <lay-row style="width: 100%">
    <lay-col md="24" style="width: 100%">
      <div style="height: 265px; width: 100%; background-color: white; display: block;">
        <div style="width: calc(100% - 30pt);">
          <br/>
        </div>
        <div style="width: calc(60% - 30pt); margin-top: 10px;">
          <lay-breadcrumb style="padding-left: 25pt">
            <lay-breadcrumb-item title="Home"></lay-breadcrumb-item>
          </lay-breadcrumb>
        </div>
        <div style="width: calc(100% - 30pt); margin-top: 55px">
          <lay-row space="10">
            <lay-col md="16">
              <p style="font-size: 23pt; color: dimgray; padding-left: 70pt">Club Admin Dashboard</p>
              <p style="font-size: 15pt; color: #16b9a9; padding-left: 70pt; margin-top: 15pt;">
                Welcome to the Sports Club Management System — Admin Backstage
              </p>
            </lay-col>
            <lay-col md="8" style="padding-top: -15pt; text-align: right;">
              <router-link to="/main/action/create">
                <lay-button type="primary" prefix-icon="layui-icon-release">Create New Action</lay-button>
              </router-link>
              &nbsp;&nbsp;
              <lay-button border="green" prefix-icon="layui-icon-refresh" style="margin-right: 4%;" @click="this.$router.go(0)">Refresh</lay-button>
            </lay-col>
          </lay-row>
        </div>
      </div>
    </lay-col>

    <lay-col md="24" style="padding-top: 20pt; padding-left: 15pt; font-size: 11pt; color: #59c1bd; font-weight: bold">
      Date Display >
    </lay-col>
    <lay-col md="4">
      <center>
      <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
        <h3 style="color: #59c1bd;">Total Members</h3>
        <br/>
        <p style="font-size: 16pt; color: dimgray;">
          <lay-count-up :startVal="0" :endVal="totalMembers" suffix=" PPL" :duration="600"></lay-count-up>
        </p>
      </lay-panel>
      </center>
    </lay-col>
    <lay-col md="4">
      <center>
        <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
          <h3 style="color: #59c1bd;">Total Stuffs</h3>
          <br/>
          <p style="font-size: 16pt; color: dimgray;">
            <lay-count-up :startVal="0" :endVal="totalStuffs" suffix=" FTE" :duration="600"></lay-count-up>
          </p>
        </lay-panel>
      </center>
    </lay-col>
    <lay-col md="4">
      <center>
        <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
          <h3 style="color: #59c1bd;">Total Actions</h3>
          <br/>
          <p style="font-size: 16pt; color: dimgray;">
            <lay-count-up :startVal="0" :endVal="totalActions" suffix=" Times" :duration="600"></lay-count-up>
          </p>
        </lay-panel>
      </center>
    </lay-col>
    <lay-col md="4">
      <center>
        <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
          <h3 style="color: #59c1bd;">Participate Times</h3>
          <br/>
          <p style="font-size: 16pt; color: dimgray;">
            <lay-count-up :startVal="0" :endVal="totalRecords" suffix=" Times" :duration="600"></lay-count-up>
          </p>
        </lay-panel>
      </center>
    </lay-col>
    <lay-col md="4">
      <center>
        <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
          <h3 style="color: #59c1bd;">Avarage Duties</h3>
          <br/>
          <p style="font-size: 16pt; color: dimgray;">
            <lay-count-up :startVal="0" :endVal="avaregeWorkTimes" suffix=" Times" :duration="600" :decimalPlaces="2"></lay-count-up>
          </p>
        </lay-panel>
      </center>
    </lay-col>
    <lay-col md="4">
      <center>
        <lay-panel style="margin-top: 12pt; width: 80%; text-align: center;">
          <h3 style="color: #59c1bd;">Dishonest Records</h3>
          <br/>
          <p style="font-size: 16pt; color: dimgray;">
            <lay-count-up :startVal="0" :endVal="totalUnsignedRecords" suffix=" Records" :duration="600"></lay-count-up>
          </p>
        </lay-panel>
      </center>
    </lay-col>

    <lay-col md="24">
      <br/>
    </lay-col>
    <lay-col md="8" style="margin-top: -4pt; padding-left: 15pt; font-size: 11pt; color: #59c1bd; font-weight: bold">
      Account Information >
    </lay-col>
    <lay-col md="8" style="margin-top: -4pt; font-size: 11pt; color: #59c1bd; font-weight: bold">
      Dishonest Ranking Top5 >
    </lay-col>
    <lay-col md="8" style="margin-top: -4pt; font-size: 12pt; color: #59c1bd; font-weight: bold">
      Duties Ranking Top5 >
    </lay-col>
    <lay-col md="8">
      <center>
        <lay-panel style="margin-top: 15pt; width: 85%; text-align: center;" :border="true">
          <lay-descriptions v-if="userInf != null" :border="true" size="md" number="1" style="margin-top: -12pt">
            <lay-descriptions-item label="Username" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.username}}</lay-descriptions-item>
            <lay-descriptions-item label="Name" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.name}}</lay-descriptions-item>
            <lay-descriptions-item label="Student ID" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.student_id}}</lay-descriptions-item>
            <lay-descriptions-item label="Phone" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.phone}}</lay-descriptions-item>
            <lay-descriptions-item label="Wechat ID" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.wechat_id}}</lay-descriptions-item>
            <lay-descriptions-item label="Email" span="3" labelStyle="width: 30%;" align="center" labelAlign="center"> {{userInf.email === '' ? 'Not Registered' : userInf.email}}</lay-descriptions-item>
          </lay-descriptions>
        </lay-panel>
      </center>
    </lay-col>
    <lay-col md="8">
      <lay-panel style="margin-top: 15pt; width: 95%; font-size: 11.5pt;" :border="true">
        <ul class="ranking-list">
          <li v-for="(item, index) in unsignMemberList">
            <span class="ranking-number">Top {{ index + 1 }}</span>
            <span class="ranking-name">{{ item.name }}</span>
            <span class="ranking-time">Dishonesty: {{ item.unsigned_num }}</span>
          </li>
        </ul>
      </lay-panel>
    </lay-col>
    <lay-col md="8">
      <lay-panel style="margin-top: 15pt; width: 95%; font-size: 11.5pt" :border="true">
        <ul class="ranking-list">
          <li v-for="(item, index) in stuffMemberList">
            <span class="ranking-number">Top {{ index + 1 }}</span>
            <span class="ranking-name">{{ item.name }}</span>
            <span class="ranking-times">Duty Times: {{ item.unsigned_num }}</span>
          </li>
        </ul>
      </lay-panel>
    </lay-col>
  </lay-row>
</template>

<script>
import Cookies from "js-cookie";

export default {
  created() {
    this.loading = true;
    this.$http.post('/member/queryInboxData?token=' + Cookies.get("token"))
    .then(response => {
      this.loading = false;
      if(response.status !== 200){
        return;
      }
      if(response.data.status === -1){
        this.$clear();
        return;
      }
      this.totalActions = response.data.data.totalActions;
      this.avaregeWorkTimes = response.data.data.avarageWorkTimes;
      this.totalUnsignedRecords = response.data.data.totalUnsignedRecords;
      this.totalStuffs = response.data.data.totalStuffs;
      this.totalMembers = response.data.data.totalMembers;
      this.totalRecords = response.data.data.totalRecords;
      this.userInf = response.data.data.user_inf;
      this.stuffMemberList = response.data.data.stuffMemberList;
      this.unsignMemberList = response.data.data.unsignMemberList;

    }).catch(error => {
      this.loading = false;
    })
  },
  data(){
    return{
      loading: false,
      userInf: null,
      totalActions: 0,
      totalRecords: 0,
      totalMembers: 0,
      totalStuffs: 0,
      totalUnsignedRecords: 0,
      avaregeWorkTimes: 0.0,
      stuffMemberList:[],
      unsignMemberList:[]
    };
  }
}
</script>

<style>
body {
  font-family: Arial, sans-serif;
}

.ranking-list {
  width: 100%;
  margin: 0;
  padding: 0;
  list-style: none;
}

.ranking-list li {
  display: flex;
  align-items: center;
  padding: 14px;
  border-bottom: 1px solid #ddd;
}

.ranking-list li:last-child {
  border-bottom: none;
}

.ranking-number {
  width: 60px;
  color: #16b9a9;
  font-weight: bold;
  text-align: center;
}

.ranking-name {
  width: calc(18vw - 100px);
  text-align: center;
  color: dimgray;
}

.ranking-time {
  color: #31BDEC;
  font-weight: bold;
  width: 100px;
  text-align: center;
  font-size: 11pt;
}

.ranking-times {
  color: #FFB800;
  width: 100px;
  font-weight: bold;
  font-size: 11pt;
  text-align: center;
}
</style>