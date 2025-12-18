<template>
  <div class="activity-list">
    <div class="header">
      <h3>活动中心</h3>
      <el-button 
        type="primary" 
        @click="showCreateDialog = true"
        v-if="hasCreatePermission"
      >
        创建活动
      </el-button>
    </div>

    <div class="filter">
      <el-select v-model="filterClub" placeholder="筛选社团" @change="loadActivities">
        <el-option label="全部社团" value=""></el-option>
        <el-option 
          v-for="club in clubList" 
          :key="club.club_id" 
          :label="club.club_name" 
          :value="club.club_id"
        ></el-option>
      </el-select>
      <el-select v-model="filterStatus" placeholder="活动状态" @change="loadActivities">
        <el-option label="全部状态" value=""></el-option>
        <el-option label="未开始" value="0"></el-option>
        <el-option label="进行中" value="1"></el-option>
        <el-option label="已结束" value="2"></el-option>
        <!-- 只有管理员能看到待审核选项 -->
        <el-option label="待审核" value="3" v-if="user.role === 2"></el-option>
      </el-select>
    </div>

    <el-table :data="activityList" v-loading="loading">
      <el-table-column prop="title" label="活动名称"></el-table-column>
      <el-table-column prop="club_name" label="主办社团"></el-table-column>
      <el-table-column prop="location" label="活动地点"></el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.start_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="end_time" label="结束时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.end_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template slot-scope="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="primary"
            @click="handleSignup(scope.row)"
            :disabled="shouldDisableSignup(scope.row)"
            class="action-button"
          >
            {{ getSignupButtonText(scope.row) }}
          </el-button>
          <el-button 
            size="mini" 
            @click="viewActivityDetail(scope.row)"
            class="action-button"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建活动对话框 -->
    <el-dialog 
      title="创建活动" 
      :visible.sync="showCreateDialog" 
      width="600px"
      center
      @close="resetActivityForm"
    >
      <el-form :model="activityForm" :rules="activityRules" ref="activityForm" label-width="100px">
        <el-form-item label="活动名称" prop="title">
          <el-input 
            v-model="activityForm.title" 
            placeholder="请输入活动名称，如：Python编程讲座"
            maxlength="50"
            show-word-limit
          ></el-input>
        </el-form-item>
        <el-form-item label="所属社团" prop="club_id">
          <el-select 
            v-model="activityForm.club_id" 
            placeholder="请选择社团" 
            style="width: 100%"
            :disabled="myClubs.length === 0"
          >
            <el-option 
              v-for="club in myClubs" 
              :key="club.club_id" 
              :label="club.club_name" 
              :value="club.club_id"
            ></el-option>
          </el-select>
          <div v-if="myClubs.length === 0" style="color: #f56c6c; font-size: 12px; margin-top: 5px;">
            您还没有加入任何社团，请先加入社团再创建活动
          </div>
        </el-form-item>
        <el-form-item label="活动地点" prop="location">
          <el-input 
            v-model="activityForm.location" 
            placeholder="请输入活动地点，如：教学楼201教室"
          ></el-input>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker
            v-model="activityForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 100%"
            :picker-options="startTimePickerOptions"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="activityForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            value-format="yyyy-MM-dd HH:mm:ss"
            style="width: 100%"
            :picker-options="endTimePickerOptions"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="活动描述" prop="content">
          <el-input 
            type="textarea" 
            v-model="activityForm.content" 
            placeholder="请详细描述活动内容、流程、注意事项等"
            :rows="4"
            maxlength="500"
            show-word-limit
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCreateDialog = false" size="medium">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleCreateActivity" 
          size="medium"
          :disabled="myClubs.length === 0"
        >
          创建活动
        </el-button>
      </div>
    </el-dialog>

    <!-- 活动详情对话框 -->
    <el-dialog 
      :title="currentActivity ? currentActivity.title : '活动详情'" 
      :visible.sync="showDetailDialog"
      width="600px"
    >
      <div v-if="currentActivity" class="activity-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="活动名称">{{ currentActivity.title }}</el-descriptions-item>
          <el-descriptions-item label="主办社团">{{ currentActivity.club_name }}</el-descriptions-item>
          <el-descriptions-item label="活动地点">{{ currentActivity.location }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(currentActivity.start_time) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(currentActivity.end_time) }}</el-descriptions-item>
          <el-descriptions-item label="活动状态">
            <el-tag :type="getStatusType(currentActivity.status)">
              {{ getStatusText(currentActivity.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="活动描述">
            <div class="activity-content">
              {{ currentActivity.content || '暂无详细描述' }}
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div slot="footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// 导入所有需要的API函数
import { getActivities, createActivity, signupActivity } from '@/api/activity'
import { getClubs } from '@/api/club'
import { getMyClubs } from '@/api/member'
import { formatDate } from '@/utils/date'

export default {
  name: 'ActivityList',
  data() {
    // 自定义验证规则：结束时间必须晚于开始时间
    const validateEndTime = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请选择结束时间'))
        return
      }
      
      if (this.activityForm.start_time && value) {
        const startTime = new Date(this.activityForm.start_time)
        const endTime = new Date(value)
        
        if (endTime <= startTime) {
          callback(new Error('结束时间必须晚于开始时间'))
          return
        }
      }
      
      callback()
    }
    
    // 自定义验证规则：开始时间不能早于当前时间
    const validateStartTime = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请选择开始时间'))
        return
      }
      
      const selectedTime = new Date(value)
      const now = new Date()
      
      if (selectedTime < now) {
        callback(new Error('开始时间不能早于当前时间'))
        return
      }
      
      callback()
    }
    
    return {
      activityList: [],
      clubList: [],
      myClubs: [],
      loading: false,
      showCreateDialog: false,
      showDetailDialog: false,
      filterClub: '',
      filterStatus: '',
      currentActivity: null,
      activityForm: {
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
        start_time: [{ required: true, validator: validateStartTime, trigger: 'change' }],
        end_time: [{ required: true, validator: validateEndTime, trigger: 'change' }]
      },
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      // 添加已报名活动的ID集合
      signedActivityIds: new Set()
    }
  },
  computed: {
    hasCreatePermission() {
      return this.myClubs.length > 0
    },
    // 开始时间选择器选项
    startTimePickerOptions() {
      return {
        disabledDate(time) {
          // 不能选择今天之前的时间
          return time.getTime() < Date.now() - 8.64e7
        }
      }
    },
    // 结束时间选择器选项（动态依赖开始时间）
    endTimePickerOptions() {
      return {
        disabledDate: (time) => {
          // 不能选择今天之前的时间
          if (time.getTime() < Date.now() - 8.64e7) {
            return true
          }
          
          // 如果已选择开始时间，结束时间不能早于开始时间
          if (this.activityForm.start_time) {
            const startTime = new Date(this.activityForm.start_time)
            return time.getTime() <= startTime.getTime()
          }
          
          return false
        }
      }
    }
  },
  mounted() {
    this.loadActivities()
    this.loadClubs()
    this.loadMyClubs()
  },
  methods: {
    loadActivities() {
      this.loading = true
      
      // 构建查询参数 - 修复筛选参数
      const params = {}
      
      // 修复：确保参数正确传递
      if (this.filterClub && this.filterClub !== '') {
        params.club_id = this.filterClub
      }
      
      if (this.filterStatus && this.filterStatus !== '') {
        params.status = this.filterStatus
      } else if (this.user.role !== 2) {
        // 普通用户默认只显示已审核的活动（状态0,1,2）
        params.status = '0,1,2'
      }
      
      // 添加用户ID，让后端能返回报名状态
      if (this.user.id) {
        params.user_id = this.user.id
      }
      
      console.log('加载活动参数:', params) // 调试用
      
      // 使用 getActivities 函数
      getActivities(params).then(res => {
        console.log('活动数据响应:', res) // 调试用
        this.activityList = res.data || []
        
        // 重置已报名集合
        this.signedActivityIds.clear()
        
        // 遍历活动，标记已报名的活动
        this.activityList.forEach(activity => {
          // 确保有报名状态字段
          activity.is_signed = activity.is_signed || 0
          
          // 如果已经报名，添加到已报名集合
          if (activity.is_signed === 1) {
            this.signedActivityIds.add(activity.activity_id)
          }
          
          // 确保创建者ID存在
          activity.creator_id = activity.creator_id || null
        })
        
        this.loading = false
      }).catch((error) => {
        console.error('加载活动失败:', error)
        this.loading = false
        this.$message.error('加载活动失败')
      })
    },
    loadClubs() {
      // 使用 getClubs 函数
      getClubs().then(res => {
        this.clubList = res.data || []
      }).catch(error => {
        console.error('加载社团列表失败:', error)
        this.$message.error('加载社团列表失败')
      })
    },
    loadMyClubs() {
      // 使用 getMyClubs 函数
      getMyClubs(this.user.id).then(res => {
        this.myClubs = res.data.filter(club => club.audit_status === 1) || []
      }).catch(error => {
        console.error('加载我的社团失败:', error)
        this.myClubs = []
      })
    },
    handleCreateActivity() {
      this.$refs.activityForm.validate(valid => {
        if (valid) {
          // 验证结束时间是否晚于开始时间
          const startTime = new Date(this.activityForm.start_time)
          const endTime = new Date(this.activityForm.end_time)
          
          if (endTime <= startTime) {
            this.$message.error('结束时间必须晚于开始时间')
            return
          }
          
          // 添加创建者ID
          const formData = {
            ...this.activityForm,
            creator_id: this.user.id
          }
          
          // 根据用户角色设置状态：管理员直接通过，普通用户需要审核
          if (this.user.role === 2) {
            formData.status = 0 // 管理员创建直接通过
          } else {
            formData.status = 3 // 普通用户创建需要审核
          }
          
          // 使用 createActivity 函数
          createActivity(formData).then(() => {
            if (this.user.role === 2) {
              this.$message.success('创建成功')
            } else {
              this.$message.success('创建成功，等待管理员审核')
            }
            this.showCreateDialog = false
            this.resetActivityForm()
            this.loadActivities()
            // 触发刷新我的活动页面
            this.$bus.$emit('activity-created')
          }).catch(error => {
            this.$message.error('创建失败: ' + (error.message || '未知错误'))
          })
        }
      })
    },
    handleSignup(activity) {
      this.$confirm(`确定要报名参加 ${activity.title} 吗？`, '提示', {
        type: 'info'
      }).then(() => {
        // 使用 signupActivity 函数
        signupActivity({
          activity_id: activity.activity_id,
          user_id: this.user.id
        }).then(() => {
          this.$message.success('报名成功')
          
          // 关键修复：立即更新本地状态，不需要等待接口刷新
          // 1. 添加到已报名集合
          this.signedActivityIds.add(activity.activity_id)
          
          // 2. 更新当前活动的报名状态
          const index = this.activityList.findIndex(a => a.activity_id === activity.activity_id)
          if (index !== -1) {
            // 使用 Vue.set 确保响应式更新
            this.$set(this.activityList[index], 'is_signed', 1)
          }
          
          // 3. 触发事件刷新其他页面
          this.$bus.$emit('activity-signed')
        }).catch(error => {
          this.$message.error('报名失败: ' + (error.message || '未知错误'))
        })
      })
    },
    viewActivityDetail(activity) {
      this.currentActivity = activity
      this.showDetailDialog = true
    },
    // 判断是否应该禁用报名按钮
    shouldDisableSignup(activity) {
      // 1. 活动不是未开始状态
      // 2. 用户已经报名了这个活动（通过 is_signed 或 signedActivityIds 判断）
      // 3. 用户是这个活动的创建者
      // 4. 活动是待审核状态（普通用户不应该看到，但防止万一）
      return activity.status !== 0 || 
             activity.is_signed === 1 || 
             this.signedActivityIds.has(activity.activity_id) ||
             activity.creator_id === this.user.id ||
             activity.status === 3
    },
    // 获取报名按钮文本
    getSignupButtonText(activity) {
      if (activity.is_signed === 1 || this.signedActivityIds.has(activity.activity_id)) {
        return '已报名'
      } else if (activity.creator_id === this.user.id) {
        return '我创建的'
      } else if (activity.status === 3) {
        return '待审核'
      } else if (activity.status !== 0) {
        return '已过期'
      }
      return '报名'
    },
    // 重置活动表单
    resetActivityForm() {
      this.activityForm = {
        title: '',
        club_id: null,
        location: '',
        start_time: '',
        end_time: '',
        content: ''
      }
      if (this.$refs.activityForm) {
        this.$refs.activityForm.clearValidate()
      }
    },
    getStatusType(status) {
      const types = ['info', 'primary', 'success', 'warning']
      return types[status] || 'info'
    },
    getStatusText(status) {
      const texts = ['未开始', '进行中', '已结束', '待审核']
      return texts[status] || '未知'
    },
    formatDate
  }
}
</script>

<style scoped>
.activity-list .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter .el-select {
  width: 150px;
  margin-right: 10px;
}

/* 统一按钮样式 */
.activity-list >>> .action-button {
  min-width: 60px;
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
  font-size: 12px;
}

/* 确保报名和详情按钮大小一致 */
.activity-list >>> .el-button--mini {
  min-width: 60px;
  height: 28px;
  line-height: 28px;
  padding: 0 12px;
}

.activity-detail {
  padding: 10px 0;
}

.activity-content {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.5;
}
</style>