<template>
    <div>
        <div class="header">社团活动管理</div>
        <div class="body">
            <!-- 操作区 -->
            <div class="operate">
                <el-select v-model="clubId" placeholder="选择社团" style="width: 200px">
                    <el-option 
                        v-for="club in clubList" 
                        :key="club.club_id" 
                        :label="club.club_name" 
                        :value="club.club_id"
                    ></el-option>
                </el-select>
                <el-input 
                    placeholder="搜索活动名称" 
                    v-model="searchName" 
                    style="width: 300px; margin-left: 20px"
                    @keyup.enter.native="getActivityList"
                >
                    <el-button slot="append" icon="el-icon-search" @click="getActivityList"></el-button>
                </el-input>
                <el-button type="primary" @click="showAddDialog" style="margin-left: auto">新增活动</el-button>
            </div>

            <!-- 活动表格 -->
            <el-table 
                :data="activityList" 
                border 
                style="width: 100%; margin-top: 20px"
            >
                <el-table-column prop="activity_id" label="活动ID" width="100" align="center"></el-table-column>
                <el-table-column prop="activity_name" label="活动名称" width="200" align="center"></el-table-column>
                <el-table-column prop="club_name" label="所属社团" width="150" align="center"></el-table-column>
                <el-table-column prop="start_time" label="开始时间" width="180" align="center"></el-table-column>
                <el-table-column prop="location" label="活动地点" width="200" align="center"></el-table-column>
                <el-table-column prop="status" label="状态" width="120" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="scope.row.status === '进行中' ? 'success' : 'info'">
                            {{ scope.row.status }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="250" align="center">
                    <template slot-scope="scope">
                        <el-button @click="handleEdit(scope.row)" type="text">编辑</el-button>
                        <el-button @click="handleDelete(scope.row.activity_id)" type="text" style="color: #f56c6c">
                            删除
                        </el-button>
                        <el-button 
                            @click="changeStatus(scope.row)" 
                            type="text" 
                            :style="scope.row.status === '进行中' ? 'color: #faad14' : 'color: #52c41a'"
                        >
                            {{ scope.row.status === '进行中' ? '结束活动' : '开始活动' }}
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 新增/编辑活动对话框 -->
            <el-dialog title="活动信息" :visible.sync="dialogVisible" width="600px">
                <el-form :model="activityForm" label-width="120px">
                    <el-form-item label="活动名称" prop="activity_name">
                        <el-input v-model="activityForm.activity_name"></el-input>
                    </el-form-item>
                    <el-form-item label="所属社团" prop="club_id">
                        <el-select v-model="activityForm.club_id">
                            <el-option 
                                v-for="club in clubList" 
                                :key="club.club_id" 
                                :label="club.club_name" 
                                :value="club.club_id"
                            ></el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="活动时间" prop="start_time">
                        <el-date-picker 
                            v-model="activityForm.start_time" 
                            type="datetime" 
                            placeholder="选择日期时间"
                        ></el-date-picker>
                    </el-form-item>
                    <el-form-item label="活动地点" prop="location">
                        <el-input v-model="activityForm.location"></el-input>
                    </el-form-item>
                    <el-form-item label="活动描述" prop="description">
                        <el-input type="textarea" v-model="activityForm.description" rows="4"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitForm">确定</el-button>
                </div>
            </el-dialog>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            clubList: [],
            clubId: '',
            searchName: '',
            activityList: [],
            dialogVisible: false,
            activityForm: {
                activity_id: '',
                activity_name: '',
                club_id: '',
                start_time: '',
                location: '',
                description: '',
                status: '未开始'
            }
        };
    },
    created() {
        this.getClubList();
        this.getActivityList();
    },
    methods: {
        // 获取社团列表
        getClubList() {
            this.$axios.get('/api/manager/clubs').then(res => {
                if (res.data.status === 200) {
                    this.clubList = res.data.data;
                }
            });
        },
        // 获取活动列表
        getActivityList() {
            this.$axios.get('/api/manager/activities', {
                params: {
                    club_id: this.clubId,
                    name: this.searchName
                }
            }).then(res => {
                if (res.data.status === 200) {
                    this.activityList = res.data.data;
                }
            });
        },
        // 显示新增对话框
        showAddDialog() {
            this.activityForm = {
                activity_id: '',
                activity_name: '',
                club_id: this.clubId || '',
                start_time: '',
                location: '',
                description: '',
                status: '未开始'
            };
            this.dialogVisible = true;
        },
        // 编辑活动
        handleEdit(row) {
            this.activityForm = { ...row };
            this.activityForm.start_time = new Date(row.start_time);
            this.dialogVisible = true;
        },
        // 提交表单
        submitForm() {
            if (this.activityForm.activity_id) {
                // 编辑
                this.$axios.put('/api/manager/activities', this.activityForm).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('修改成功');
                        this.dialogVisible = false;
                        this.getActivityList();
                    }
                });
            } else {
                // 新增
                this.$axios.post('/api/manager/activities', this.activityForm).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('新增成功');
                        this.dialogVisible = false;
                        this.getActivityList();
                    }
                });
            }
        },
        // 删除活动
        handleDelete(id) {
            this.$confirm('确定删除该活动吗？', '提示', {
                type: 'warning'
            }).then(() => {
                this.$axios.delete(`/api/manager/activities/${id}`).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('删除成功');
                        this.getActivityList();
                    }
                });
            });
        },
        // 更改活动状态
        changeStatus(row) {
            const newStatus = row.status === '进行中' ? '已结束' : '进行中';
            this.$axios.put('/api/manager/activities/status', {
                activity_id: row.activity_id,
                status: newStatus
            }).then(res => {
                if (res.data.status === 200) {
                    this.$message.success(`活动已${newStatus}`);
                    this.getActivityList();
                }
            });
        }
    }
}
</script>

<style scoped>
.header {
    width: 100%;
    height: 60px;
    line-height: 60px;
    font-size: 20px;
    font-weight: 800;
    border-bottom: 1px solid #e3e3e3;
}
.body {
    padding: 20px;
}
.operate {
    display: flex;
    align-items: center;
}
</style>