<template>
  <div class="club-table">
    <el-table :data="clubs" v-loading="loading">
      <el-table-column prop="club_name" label="社团名称"></el-table-column>
      <el-table-column prop="category" label="类别"></el-table-column>
      <el-table-column prop="description" label="简介">
        <template slot-scope="scope">
          {{ scope.row.description || '暂无简介' }}
        </template>
      </el-table-column>
      <el-table-column prop="role" label="我的角色">
        <template slot-scope="scope">
          <el-tag :type="getRoleType(scope.row.role)">
            {{ getRoleText(scope.row.role) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="audit_status" label="状态">
        <template slot-scope="scope">
          <!-- 仅待审核状态用warning，其他保持原有颜色 -->
          <el-tag :type="scope.row.audit_status === 0 ? 'warning' : getStatusType(scope.row.audit_status)">
            {{ getStatusText(scope.row.audit_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" v-if="showActions">
        <template slot-scope="scope">
          <el-button size="mini" @click="manageClub(scope.row)">管理</el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="deleteClub(scope.row)"
          >
            解散
          </el-button>
        </template>
      </el-table-column>
      <!-- 我加入的社团显示退出按钮 -->
      <el-table-column label="操作" width="100" v-else>
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="danger" 
            @click="quitClub(scope.row)"
            v-if="scope.row.role === 0 && scope.row.audit_status === 1"
          >
            退出
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 社团管理对话框 -->
    <el-dialog 
      :title="currentClub ? `管理社团 - ${currentClub.club_name}` : '社团管理'" 
      :visible.sync="showManageDialog"
      width="800px"
    >
      <div v-if="currentClub" class="club-manage-content">
        <el-tabs v-model="manageTab">
          <el-tab-pane label="基本信息" name="info">
            <el-form :model="clubForm" label-width="100px">
              <el-form-item label="社团名称">
                <el-input v-model="clubForm.club_name"></el-input>
              </el-form-item>
              <el-form-item label="社团类别">
                <el-select v-model="clubForm.category" style="width: 100%">
                  <el-option label="学术科技" value="学术科技"></el-option>
                  <el-option label="文化体育" value="文化体育"></el-option>
                  <el-option label="志愿公益" value="志愿公益"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="社团简介">
                <el-input type="textarea" v-model="clubForm.description" :rows="4"></el-input>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="成员管理" name="members">
            <div class="members-section">
              <div class="section-header">
                <h4>社团成员</h4>
              </div>
              <!-- 修复：成员列表加载状态和空数据提示 -->
              <el-table :data="clubMembers" size="small" v-loading="membersLoading" v-if="clubMembers.length > 0 || membersLoading">
                <el-table-column prop="username" label="成员姓名"></el-table-column>
                <el-table-column prop="role" label="角色">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.role === 1 ? 'danger' : 'primary'">
                      {{ getRoleText(scope.row.role) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="join_time" label="加入时间">
                  <template slot-scope="scope">
                    {{ formatDate(scope.row.join_time) || '暂无' }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120">
                  <template slot-scope="scope">
                    <el-button 
                      size="mini" 
                      type="danger"  
                      @click="removeMember(scope.row)"
                      v-if="scope.row.role !== 1 && currentClub.role === 1"
                    >
                      移除
                    </el-button>
                    <span v-else class="no-action">-</span>
                  </template>
                </el-table-column>
              </el-table>
              <div v-else class="empty-state">
                暂无成员数据
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="活动管理" name="activities">
            <div class="activities-section">
              <div class="section-header">
                <h4>社团活动</h4>
                <div>
                  <el-button size="small" type="primary" @click="openActivityDialog()">创建活动</el-button>
                </div>
              </div>
              <el-table :data="clubActivities" size="small" v-loading="activitiesLoading">
                <el-table-column prop="title" label="活动名称"></el-table-column>
                <el-table-column prop="location" label="活动地点"></el-table-column>
                <el-table-column prop="start_time" label="开始时间">
                  <template slot-scope="scope">
                    {{ formatDate(scope.row.start_time) }}
                  </template>
                </el-table-column>
                <!-- 新增：显示结束时间 -->
                <el-table-column prop="end_time" label="结束时间">
                  <template slot-scope="scope">
                    {{ formatDate(scope.row.end_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态">
                  <template slot-scope="scope">
                    <!-- 仅活动待审核（状态3）用warning，其他保持原有颜色 -->
                    <el-tag :type="scope.row.status === 3 ? 'warning' : getActivityStatusType(scope.row.status)">
                      {{ getActivityStatusText(scope.row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150">
                  <template slot-scope="scope">
                    <el-button size="mini" @click="openActivityDialog(scope.row)"
                    :disabled="[1, 2].includes(scope.row.status)"
                    >编辑</el-button>
                    <el-button 
                      size="mini" 
                      type="danger" 
                      @click="deleteClubActivity(scope.row)"
                      :disabled="[1, 2].includes(scope.row.status)"
                      v-if="currentClub.role === 1"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div v-if="!activitiesLoading && clubActivities.length === 0" class="empty-state">
                暂无活动数据
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <div slot="footer">
        <el-button @click="showManageDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="saveClubInfo"
          :loading="saving"
        >
          保存
        </el-button>
      </div>
    </el-dialog>

    <!-- 活动创建/编辑对话框 - 核心修复：添加唯一key + 新增结束时间 -->
    <el-dialog 
      :title="isEditActivity ? '编辑活动' : '创建活动'" 
      :visible.sync="showActivityDialog"
      width="600px"
      @close="resetActivityForm"
      :key="activityForm.activity_id || 'new_activity'"
    >
      <el-form 
        :model="activityForm" 
        label-width="100px" 
        ref="activityFormRef"
        :rules="activityRules"
      >
        <el-form-item label="活动名称" prop="title">
          <el-input v-model="activityForm.title" placeholder="请输入活动名称"></el-input>
        </el-form-item>
        <el-form-item label="活动地点" prop="location">
          <el-input v-model="activityForm.location" placeholder="请输入活动地点"></el-input>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-date-picker 
            v-model="activityForm.start_time" 
            type="datetime" 
            placeholder="选择开始时间" 
            style="width: 100%"
            value-format="yyyy-MM-dd HH:mm:ss"
            :picker-options="{
              disabledDate(time) {
                return time.getTime() < Date.now() - 8.64e7;
              }
            }"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker 
            v-model="activityForm.end_time" 
            type="datetime" 
            placeholder="选择结束时间" 
            style="width: 100%"
            value-format="yyyy-MM-dd HH:mm:ss"
            :picker-options="{
              disabledDate(time) {
                return time.getTime() < Date.now() - 8.64e7;
              }
            }"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="活动状态" prop="status">
          <el-select v-model="activityForm.status" style="width: 100%">
            <el-option label="未开始" value="0"></el-option>
            <el-option label="进行中" value="1"></el-option>
            <el-option label="已结束" value="2"></el-option>
            <el-option label="待审核" value="3"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="活动描述" prop="content">
          <el-input 
            type="textarea" 
            v-model="activityForm.content" 
            placeholder="请输入活动描述" 
            :rows="4"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="showActivityDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="saveActivity"
          :loading="activitySaving"
        >
          保存
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { deleteClub } from '@/api/club'
import { formatDate } from '@/utils/date'

export default {
  name: 'ClubTable',
  props: {
    clubs: {
      type: Array,
      default: () => []
    },
    showActions: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      loading: false,
      showManageDialog: false,
      currentClub: null,
      manageTab: 'info',
      clubForm: {
        club_name: '',
        category: '',
        description: ''
      },
      clubMembers: [],
      clubActivities: [],
      membersLoading: false,
      activitiesLoading: false,
      saving: false,
      user: JSON.parse(sessionStorage.getItem('user') || '{}'),
      // 活动相关配置
      showActivityDialog: false,
      isEditActivity: false,
      activityForm: {
        activity_id: '',
        title: '',
        location: '',
        start_time: '',
        end_time: '',
        status: '0',
        content: '',
        club_id: ''
      },
      activityRules: {
        title: [
          { required: true, message: '请输入活动名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        location: [
          { required: true, message: '请输入活动地点', trigger: 'blur' },
          { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
        ],
        start_time: [
          { required: true, message: '请选择开始时间', trigger: 'change' }
        ],
        end_time: [
          { required: true, message: '请选择结束时间', trigger: 'change' },
          { validator: this.validateEndTime, trigger: 'change' }
        ]
      },
      activitySaving: false
    }
  },
  methods: {
    // 验证结束时间必须晚于开始时间
    validateEndTime(rule, value, callback) {
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
    },

    // 管理社团弹窗
    manageClub(club) {
      this.currentClub = club
      this.clubForm = { ...club }
      this.showManageDialog = true
      this.clubMembers = []
      this.clubActivities = []
      // 自动加载当前标签页数据
      if (this.manageTab === 'members') {
        this.loadClubMembers() 
      } else if (this.manageTab === 'activities') {
        this.loadClubActivities()
      }
    },

    // 加载社团成员
    async loadClubMembers() {
      if (!this.currentClub) return
      this.membersLoading = true
      try {
        console.log(`加载社团ID为 ${this.currentClub.club_id} 的成员`)
        const response = await fetch(`http://127.0.0.1:5000/api/club/members?club_id=${this.currentClub.club_id}`)
        const result = await response.json()
        console.log('成员API响应:', result)
        
        if (result.status === 200) {
          this.clubMembers = result.data || []
          console.log(`加载到 ${this.clubMembers.length} 个社团成员`)
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载成员数据失败:', error)
        this.$message.error(
          error.message.includes('Failed to fetch') 
            ? '网络连接失败，请检查后端服务' 
            : '加载成员数据失败: ' + error.message
        )
        this.clubMembers = []
      } finally {
        this.membersLoading = false
      }
    },

    // 加载社团活动（过滤当前社团）
    async loadClubActivities() {
      if (!this.currentClub) return
      this.activitiesLoading = true
      try {
        console.log(`加载社团ID为 ${this.currentClub.club_id} 的活动`)
        const response = await fetch(`http://127.0.0.1:5000/api/activities?club_id=${this.currentClub.club_id}`)
        const result = await response.json()
        console.log('活动API响应:', result)
        
        if (result.status === 200) {
          // 双重过滤：后端过滤 + 前端验证
          const filteredActivities = (result.data || []).filter(activity => {
            const isSameClub = activity.club_id === this.currentClub.club_id
            if (!isSameClub) {
              console.warn(`过滤掉不属于当前社团的活动: ${activity.title} (社团ID: ${activity.club_id})`)
            }
            return isSameClub
          })
          this.clubActivities = filteredActivities
          console.log(`加载到 ${filteredActivities.length} 个属于当前社团的活动`)
        } else {
          throw new Error(result.message)
        }
      } catch (error) {
        console.error('加载活动数据失败:', error)
        this.$message.error('加载活动数据失败: ' + error.message)
        this.clubActivities = []
      } finally {
        this.activitiesLoading = false
      }
    },

    // 深度重置活动表单
    resetActivityForm() {
      // 强制创建新对象，切断所有引用
      this.activityForm = Object.assign({}, {
        activity_id: '',
        title: '',
        location: '',
        start_time: '',
        end_time: '',
        status: '0',
        content: '',
        club_id: this.currentClub?.club_id || ''
      })
      this.isEditActivity = false
      
      // 强制刷新Vue视图，确保数据更新
      this.$forceUpdate()
      
      // 重置表单验证状态+手动清空值
      this.$nextTick(() => {
        if (this.$refs.activityFormRef) {
          this.$refs.activityFormRef.clearValidate()
          this.$refs.activityFormRef.resetFields()
        }
      })
    },

    // 打开活动弹窗
    openActivityDialog(activity = null) {
      // 先强制重置所有数据
      this.resetActivityForm()
      // 打开弹窗
      this.showActivityDialog = true

      // 编辑模式：延迟赋值（等待DOM重建完成）
      if (activity) {
        setTimeout(() => {
          this.isEditActivity = true
          // 深拷贝数据，彻底切断与列表数据的引用
          this.activityForm = {
            activity_id: activity.activity_id,
            title: activity.title || '',
            location: activity.location || '',
            start_time: activity.start_time || '',
            end_time: activity.end_time || '',
            status: activity.status ? String(activity.status) : '0', 
            content: activity.content || '',
            club_id: this.currentClub.club_id
          }
          console.log('编辑活动数据:', this.activityForm)
          // 强制更新视图
          this.$forceUpdate()
        }, 50)
      } else {
        // 创建模式：设置默认状态
        this.activityForm.status = this.user.role === 2 ? '0' : '3' 
      }
    },

    // 保存活动（创建/编辑）
    async saveActivity() {
      // 表单验证
      try {
        await this.$refs.activityFormRef.validate()
      } catch (error) {
        console.log('表单验证失败:', error)
        this.$message.warning('请完善必填信息')
        return
      }

      this.activitySaving = true
      try {
        // 统一参数格式
        const formData = {
          ...this.activityForm,
          club_id: this.currentClub.club_id 
        }

        // 如果是创建活动且用户不是管理员，状态设为待审核(3)
        if (!this.isEditActivity && this.user.role !== 2) {
          formData.status = 3 
        }

        console.log('提交的活动数据:', formData)

        // 区分创建/编辑接口
        const url = this.isEditActivity 
          ? 'http://127.0.0.1:5000/api/activity/update'
          : 'http://127.0.0.1:5000/api/activity/create'

        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })

        const result = await response.json()
        console.log('保存活动响应:', result)
        
        if (result.status === 200) {
          this.$message.success(this.isEditActivity ? '活动编辑成功' : '活动创建成功')
          this.showActivityDialog = false
          this.loadClubActivities() 
        } else {
          throw new Error(result.message || '保存失败')
        }
      } catch (error) {
        console.error('保存活动失败:', error)
        this.$message.error('保存失败: ' + error.message)
      } finally {
        this.activitySaving = false
      }
    },

    // 移除社团成员
    async removeMember(member) {
      this.$confirm(`确定要移除成员 ${member.username} 吗？`, '提示', { type: 'warning' })
        .then(async () => {
          try {
            const response = await fetch('http://127.0.0.1:5000/api/member/remove', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ member_id: member.member_id })
            })
            const result = await response.json()
            if (result.status === 200) {
              this.$message.success('成员移除成功')
              this.loadClubMembers() 
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            console.error('移除失败:', error)
            this.$message.error('移除失败: ' + error.message)
          }
        })
    },

    // 保存社团信息
    async saveClubInfo() {
      if (!this.currentClub) return
      
      // 验证社团表单
      if (!this.clubForm.club_name || !this.clubForm.category) {
        this.$message.warning('请填写社团名称和类别')
        return
      }
      
      this.saving = true
      try {
        const dataToSend = {
          club_id: this.currentClub.club_id,
          club_name: this.clubForm.club_name,
          category: this.clubForm.category,
          description: this.clubForm.description || ''
        }
        
        console.log('更新社团数据:', dataToSend)
        
        const response = await fetch('http://127.0.0.1:5000/api/club/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dataToSend)
        })
        
        const result = await response.json()
        console.log('更新社团响应:', result)
        
        if (result.status === 200) {
          this.$message.success('社团信息更新成功')
          this.showManageDialog = false
          this.$emit('refresh')
        } else {
          throw new Error(result.message || '更新失败')
        }
      } catch (error) {
        console.error('更新失败:', error)
        this.$message.error('更新失败: ' + error.message)
      } finally {
        this.saving = false
      }
    },

    // 删除社团活动
    async deleteClubActivity(activity) {
      this.$confirm(`确定要删除活动 "${activity.title}" 吗？`, '提示', { type: 'warning' })
        .then(async () => {
          try {
            const response = await fetch(`http://127.0.0.1:5000/api/activity/delete/${activity.activity_id}`, {
              method: 'DELETE'
            })
            const result = await response.json()
            if (result.status === 200) {
              this.$message.success('活动删除成功')
              this.loadClubActivities()
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            console.error('删除失败:', error)
            this.$message.error('删除失败: ' + error.message)
          }
        })
    },

    // 解散社团
    async deleteClub(club) {
      this.$confirm(`确定要解散 "${club.club_name}" 吗？此操作将删除社团所有相关数据，且不可恢复！`, '警告', {
        type: 'warning',
        confirmButtonText: '确定解散',
        confirmButtonClass: 'el-button--danger'
      }).then(async () => {
        try {
          this.loading = true
          const result = await deleteClub(club.club_id)
          if (result.status === 200) {
            this.$message.success('解散社团成功')
            this.$emit('refresh')
          } else {
            throw new Error(result.message || '解散失败')
          }
        } catch (error) {
          console.error('解散失败:', error)
          this.$message.error('解散失败: ' + error.message)
        } finally {
          this.loading = false
        }
      }).catch(() => {
        this.$message.info('已取消解散操作')
      })
    },

    // 退出社团
    async quitClub(club) {
      this.$confirm(`确定要退出"${club.club_name}"吗？`, '提示', { type: 'warning' })
        .then(async () => {
          try {
            const response = await fetch('http://127.0.0.1:5000/api/member/quit', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ club_id: club.club_id, user_id: this.user.id })
            })
            const result = await response.json()
            if (result.status === 200) {
              this.$message.success('退出社团成功')
              this.$emit('refresh')
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            console.error('退出失败:', error)
            this.$message.error('退出失败: ' + error.message)
          }
        }).catch(() => {
          this.$message.info('已取消退出操作')
        })
    },

    // 角色类型映射（保持原有逻辑不变）
    getRoleType(role) {
      const types = ['', 'danger', 'success']
      return types[role] || ''
    },

    // 角色文本映射（保持原有逻辑不变）
    getRoleText(role) {
      const texts = ['社员', '社长', '管理员']
      return texts[role] || '未知'
    },

    // 审核状态类型映射（保持原有逻辑不变）
    getStatusType(status) {
      const types = ['', 'success', 'danger'] 
      return types[status] || ''
    },

    // 审核状态文本映射（保持原有逻辑不变）
    getStatusText(status) {
      const texts = ['待审核', '已通过', '已拒绝']
      return texts[status] || '待审核'
    },

    // 活动状态类型映射（保持原有逻辑不变）
    getActivityStatusType(status) {
      const types = ['info', 'primary', 'success', ''] 
      return types[status] || ''
    },

    // 活动状态文本映射（保持原有逻辑不变）
    getActivityStatusText(status) {
      const texts = ['未开始', '进行中', '已结束', '待审核']
      return texts[status] || '待审核'
    },

    // 日期格式化
    formatDate
  },
  watch: {
    // 切换标签页自动加载数据
    manageTab(newTab) {
      if (newTab === 'members' && this.currentClub) {
        this.loadClubMembers() 
      } else if (newTab === 'activities' && this.currentClub) {
        this.loadClubActivities()
      }
    },
    // 切换社团自动加载数据
    currentClub(newClub) {
      if (newClub && this.showManageDialog) {
        if (this.manageTab === 'members') {
          this.loadClubMembers()
        } else if (this.manageTab === 'activities') {
          this.loadClubActivities()
        }
      }
    }
  }
}
</script>

<style scoped>
.club-manage-content {
  padding: 10px 0;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.section-header h4 {
  margin: 0;
}
.empty-state {
  text-align: center;
  padding: 20px;
  color: #999;
}
.no-action {
  color: #999;
}
</style>