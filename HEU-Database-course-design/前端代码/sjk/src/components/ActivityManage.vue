<template>
  <div class="activity-manage">
    <div class="header">
      <h3>活动管理</h3>
    </div>
    
    <el-table :data="activityList" v-loading="loading">
      <el-table-column prop="activity_id" label="ID" width="80"></el-table-column>
      <el-table-column prop="title" label="活动名称"></el-table-column>
      <el-table-column prop="club_name" label="所属社团"></el-table-column>
      <el-table-column prop="location" label="活动地点"></el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="180"></el-table-column>
      <el-table-column prop="end_time" label="结束时间" width="180"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template slot-scope="scope">
          <el-button size="mini" @click="editActivity(scope.row)">编辑</el-button>
          <el-button 
            size="mini" 
            type="success" 
            @click="handleAudit(scope.row, 1)"
            v-if="scope.row.status === 3"
          >
            通过
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="handleAudit(scope.row, 0)"
            v-if="scope.row.status === 3"
          >
            不通过
          </el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="deleteActivity(scope.row)"
            v-if="scope.row.status !== 3"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑活动对话框 -->
    <el-dialog 
      :title="isEdit ? '编辑活动' : '创建活动'" 
      :visible.sync="showCreateDialog"
      width="600px"
    >
      <el-form :model="activityForm" :rules="activityRules" ref="activityForm">
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="activityForm.title"></el-input>
        </el-form-item>
        <el-form-item label="所属社团" prop="club_id">
          <el-select v-model="activityForm.club_id" placeholder="请选择社团">
            <el-option 
              v-for="club in clubList" 
              :key="club.club_id" 
              :label="club.club_name" 
              :value="club.club_id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="活动地点" prop="location">
          <el-input v-model="activityForm.location"></el-input>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            value-format="yyyy-MM-dd HH:mm:ss"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            value-format="yyyy-MM-dd HH:mm:ss"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="活动描述" prop="content">
          <el-input type="textarea" v-model="activityForm.content"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveActivity">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getActivities, createActivity, updateActivity, deleteActivity } from '@/api/activity'
import { getClubs } from '@/api/club'

export default {
  name: 'ActivityManage',
  data() {
    return {
      activityList: [],
      clubList: [],
      loading: false,
      showCreateDialog: false,
      isEdit: false,
      activityForm: {
        activity_id: null,
        title: '',
        club_id: null,
        location: '',
        start_time: '',
        end_time: '',
        content: ''
      },
      activityRules: {
        title: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
        club_id: [{ required: true, message: '请选择社团', trigger: 'change' }],
        location: [{ required: true, message: '请输入活动地点', trigger: 'blur' }],
        start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
        end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
      }
    }
  },
  mounted() {
    this.loadActivities()
    this.loadClubs()
  },
  methods: {
    loadActivities() {
      this.loading = true
      getActivities().then(res => {
        this.activityList = res.data || []
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    loadClubs() {
      getClubs().then(res => {
        this.clubList = res.data || []
      })
    },
    editActivity(activity) {
      this.isEdit = true
      this.activityForm = { ...activity }
      this.showCreateDialog = true
    },
    handleSaveActivity() {
      this.$refs.activityForm.validate(valid => {
        if (valid) {
          const saveMethod = this.isEdit ? updateActivity : createActivity
          saveMethod(this.activityForm).then(() => {
            this.$message.success(this.isEdit ? '更新成功' : '创建成功')
            this.showCreateDialog = false
            this.loadActivities()
            this.resetForm()
          })
        }
      })
    },
    // 审核活动
    handleAudit(activity, auditStatus) {
      const action = auditStatus === 1 ? '通过' : '不通过'
      this.$confirm(`确定要${action} "${activity.title}" 的申请吗？`, '提示', {
        type: 'warning'
      }).then(() => {
        this.loading = true
        fetch('http://127.0.0.1:5000/api/activity/audit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            activity_id: activity.activity_id,
            audit_status: auditStatus
          })
        })
        .then(response => response.json())
        .then(result => {
          this.loading = false
          if (result.status === 200) {
            this.$message.success(result.message)
            this.loadActivities()
          } else {
            throw new Error(result.message)
          }
        })
        .catch(error => {
          this.loading = false
          this.$message.error('审核失败：' + (error.message || '未知错误'))
        })
      }).catch(() => {
        this.$message.info('已取消操作')
      })
    },
    deleteActivity(activity) {
      this.$confirm('确定要删除这个活动吗？', '提示', {
        type: 'warning'
      }).then(() => {
        deleteActivity(activity.activity_id).then(() => {
          this.$message.success('删除成功')
          this.loadActivities()
        })
      })
    },
    getStatusType(status) {
      const types = {
        0: 'info',    // 未开始
        1: 'primary', // 进行中
        2: 'success', // 已结束
        3: 'warning'  // 待审核
      }
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = {
        0: '未开始',
        1: '进行中',
        2: '已结束',
        3: '待审核'
      }
      return texts[status] || '未知'
    },
    resetForm() {
      this.activityForm = {
        activity_id: null,
        title: '',
        club_id: null,
        location: '',
        start_time: '',
        end_time: '',
        content: ''
      }
      this.isEdit = false
      this.$refs.activityForm.resetFields()
    }
  }
}
</script>

<style scoped>
.activity-manage .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>