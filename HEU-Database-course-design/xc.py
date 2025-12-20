# 关键SQL查询构建
@app.route('/api/activities', methods=['GET'])
def get_activities():
    try:
        club_id, status, user_id = request.args.get('club_id'), request.args.get('status'), request.args.get('user_id')
        
        # 动态构建SQL查询语句
        sql = 'SELECT a.*, c.club_name, u.username as club_creator_name'
        sql += ', CASE WHEN asu.signup_id IS NOT NULL THEN 1 ELSE 0 END as is_signed' 
        sql += ' FROM activity a LEFT JOIN club c ON a.club_id = c.club_id LEFT JOIN user u ON c.founder_id = u.id'
        if user_id: 
            sql += ' LEFT JOIN activity_signup asu ON a.activity_id = asu.activity_id AND asu.user_id = :user_id'
        
        # 动态WHERE条件构建
        sql += ' WHERE 1=1'
        if club_id: sql += ' AND a.club_id = :club_id'
        if status:
            if ',' in status:  # 支持多状态查询
                status_list = status.split(',')
                sql += f' AND a.status IN ({",".join([f":status{i}" for i in range(len(status_list))])})'
            else: 
                sql += ' AND a.status = :status'
        
        sql += ' ORDER BY a.club_id ASC, a.start_time ASC, a.activity_id ASC'