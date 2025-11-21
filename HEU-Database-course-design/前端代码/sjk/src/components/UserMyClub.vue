<template>
    <div>
        <div class="header">我的社团</div>
        <div class="body">
            <el-table 
                :data="myClubs" 
                border 
                style="width: 100%"
            >
                <el-table-column prop="club_id" label="社团ID" width="100" align="center"></el-table-column>
                <el-table-column prop="club_name" label="社团名称" width="180" align="center"></el-table-column>
                <el-table-column prop="category" label="社团类别" width="120" align="center"></el-table-column>
                <el-table-column prop="role" label="我的角色" width="120" align="center">
                    <template slot-scope="scope">
                        <el-tag :type="scope.row.role === '社长' ? 'primary' : 'success'">
                            {{ scope.row.role }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="join_time" label="加入时间" width="180" align="center"></el-table-column>
                <el-table-column prop="activity_count" label="近期活动" width="120" align="center">
                    <template slot-scope="scope">
                        <span>{{ scope.row.activity_count }}个</span>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="200" align="center">
                    <template slot-scope="scope">
                        <el-button @click="viewDetails(scope.row)" type="text">查看详情</el-button>
                        <el-button @click="leaveClub(scope.row.club_id)" type="text" style="color: #f56c6c">
                            退出社团
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 社团详情对话框 -->
            <el-dialog title="社团详情" :visible.sync="detailVisible" width="600px">
                <div v-if="currentClub">
                    <el-descriptions column="1" border>
                        <el-descriptions-item label="社团名称">{{ currentClub.club_name }}</el-descriptions-item>
                        <el-descriptions-item label="社团类别">{{ currentClub.category }}</el-descriptions-item>
                        <el-descriptions-item label="成立时间">{{ currentClub.create_time }}</el-descriptions-item>
                        <el-descriptions-item label="成员数量">{{ currentClub.member_count }}人</el-descriptions-item>
                        <el-descriptions-item label="社团简介" :span="3">
                            <p style="white-space: pre-line">{{ currentClub.description }}</p>
                        </el-descriptions-item>
                    </el-descriptions>

                    <div style="margin-top: 20px">
                        <h4>近期活动</h4>
                        <el-list v-if="currentClub.activities.length" border>
                            <el-list-item v-for="act in currentClub.activities" :key="act.activity_id">
                                <div class="activity-item">
                                    <span>{{ act.activity_name }}</span>
                                    <span style="margin-left: 20px">{{ act.start_time }}</span>
                                    <span style="margin-left: 20px">{{ act.location }}</span>
                                </div>
                            </el-list-item>
                        </el-list>
                        <p v-else class="no-activity">暂无近期活动</p>
                    </div>
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
            detailVisible: false,
            currentClub: null
        };
    },
    created() {
        this.getMyClubs();
    },
    methods: {
        // 获取我的社团
        getMyClubs() {
            this.$axios.get('/api/user/my/clubs').then(res => {
                if (res.data.status === 200) {
                    this.myClubs = res.data.data;
                }
            });
        },
        // 查看社团详情
        viewDetails(club) {
            this.$axios.get(`/api/user/clubs/${club.club_id}`).then(res => {
                if (res.data.status === 200) {
                    this.currentClub = res.data.data;
                    this.detailVisible = true;
                }
            });
        },
        // 退出社团
        leaveClub(clubId) {
            this.$confirm('确定要退出该社团吗？', '提示', {
                type: 'warning'
            }).then(() => {
                this.$axios.post('/api/user/leave/club', { club_id: clubId }).then(res => {
                    if (res.data.status === 200) {
                        this.$message.success('已退出社团');
                        this.getMyClubs();
                    } else {
                        this.$message.error(res.data.msg);
                    }
                });
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
.activity-item {
    width: 100%;
    display: flex;
    align-items: center;
}
.no-activity {
    text-align: center;
    color: #888;
    padding: 10px;
}
</style>