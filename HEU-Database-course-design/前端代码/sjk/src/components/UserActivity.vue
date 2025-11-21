<template>
    <div>
        <div class="header">活动报名</div>
        <div class="body">
            <!-- 筛选区 -->
            <div class="filter-bar">
                <el-select v-model="clubId" placeholder="选择社团" @change="getActivityList">
                    <el-option label="全部社团" value=""></el-option>
                    <el-option 
                        v-for="club in myClubs" 
                        :key="club.club_id" 
                        :label="club.club_name" 
                        :value="club.club_id"
                    ></el-option>
                </el-select>
                <el-select v-model="status" placeholder="活动状态" @change="getActivityList" style="margin-left: 20px">
                    <el-option label="全部状态" value=""></el-option>
                    <el-option label="未开始" value="未开始"></el-option>
                    <el-option label="进行中" value="进行中"></el-option>
                </el-select>
                <el-input 
                    placeholder="搜索活动名称" 
                    v-model="searchName" 
                    style="width: 300px; margin-left: 20px"
                    @keyup.enter.native="getActivityList"
                >
                    <el-button slot="append" icon="el-icon-search" @click="getActivityList"></el-button>
                </el-input>
            </div>

            <!-- 活动列表 -->
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
                <el-table-column label="操作" width="180" align="center">
                    <template slot-scope="scope">
                        <el-button 
                            @click="viewActivity(scope.row)" 
                            type="text"
                        >
                            查看详情
                        </el-button>
                        <el-button 
                            @click="signUp(scope.row.activity_id)" 
                            type="text" 
                            style="color: #52c41a"
                            :disabled="scope.row.signed || scope.row.status === '已结束'"
                        >
                            {{ scope.row.signed ? '已报名' : '报名参加' }}
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 活动详情对话框 -->
            <el-dialog title="活动详情" :visible.sync="detailVisible" width="600px">
                <div v-if="currentActivity">
                    <el-descriptions column="1" border>
                        <el-descriptions-item label="活动名称">{{ currentActivity.activity_name }}</el-descriptions-item>
                        <el-descriptions-item label="所属社团">{{ currentActivity.club_name }}</el-descriptions-item>
                        <el-descriptions-item label="活动时间">{{ currentActivity.start_time }}</el-descriptions-item>
                        <el-descriptions-item label="活动地点">{{ currentActivity.location }}</el-descriptions-item>
                        <el-descriptions-item label="活动状态">
                            <el-tag :type="currentActivity.status === '进行中' ? 'success' : 'info'">
                                {{ currentActivity.status }}
                            </el-tag>
                        </el-descriptions-item>
                        <el-descriptions-item label="报名人数">{{ currentActivity.sign_count }}人</el-descriptions-item>
                        <el-descriptions-item label="活动描述" :span="3">
                            <p style="white-space: pre-line">{{ currentActivity.description }}</p>
                        </el-descriptions-item>
                    </el-descriptions>
                </div>
            </el-dialog>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            myClubs: [],
            clubId: '',
            status: '',
            searchName: '',
            activityList: [],
            detailVisible: false,
            currentActivity: null
        };
    },
    created() {
        this.getMyClubs();
        this.getActivityList();
    },
    methods: {
        // 获取我的社团（用于筛选）
        getMyClubs() {
            this.$axios.get('/api/user/my/clubs').then(res => {
                if (res.data.status === 200) {
                    this.myClubs = res.data.data;
                }
            });
        },
        // 获取活动列表
        getActivityList() {
            this.$axios.get('/api/user/activities', {
                params: {
                    club_id: this.clubId,
                    status: this.status,
                    name: this.searchName
                }
            }).then(res => {
                if (res.data.status === 200) {
                    this.activityList = res.data.data;
                }
            });
        },
        // 查看活动详情
        viewActivity(activity) {
            this.$axios.get(`/api/user/activities/${activity.activity_id}`).then(res => {
                if (res.data.status === 200) {
                    this.currentActivity = res.data.data;
                    this.detailVisible = true;
                }
            });
        },
        // 报名参加活动
        signUp(activityId) {
            this.$axios.post('/api/user/sign/activity', { activity_id: activityId }).then(res => {
                if (res.data.status === 200) {
                    this.$message.success('报名成功');
                    this.getActivityList();
                } else {
                    this.$message.error(res.data.msg);
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
.filter-bar {
    display: flex;
    align-items: center;
}
</style>