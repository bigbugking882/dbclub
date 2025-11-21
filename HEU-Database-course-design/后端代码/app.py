from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import auth
import random
import datetime
from config import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
CORS(app)  # 允许跨域请求

# 检查数据库连接
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("数据库连接成功")
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")

# 辅助函数：从token获取用户信息
def get_user_from_token(token):
    result = auth.verify_token(token)
    if not result['status']:
        return None
    return result['data']

# 1. 用户登录
@app.route("/api/user/login", methods=["POST"])
def user_login():
    data = request.json
    telephone = data.get("telephone", "").strip()
    password = data.get("password", "").strip()
    
    if not telephone or not password:
        return jsonify({"code": 1001, "msg": "手机号和密码不能为空"})
    
    try:
        sql = "SELECT id, username, telephone, role FROM user WHERE telephone = :tel AND password = :pwd"
        result = db.session.execute(text(sql), {"tel": telephone, "pwd": password}).first()
        
        if result:
            user_info = {
                "id": result[0],
                "username": result[1],
                "telephone": result[2],
                "role": result[3]
            }
            token = auth.generate_token(user_info)
            return jsonify({
                "code": 200,
                "msg": "登录成功",
                "token": token,
                "user": user_info
            })
        else:
            return jsonify({"code": 1002, "msg": "手机号或密码错误"})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 2. 获取验证码
@app.route("/api/user/get_vercode", methods=["POST"])
def get_vercode():
    telephone = request.json.get("telephone", "").strip()
    if not telephone:
        return jsonify({"code": 1001, "msg": "手机号不能为空"})
    
    # 生成6位验证码
    vercode = str(random.randint(100000, 999999))
    expire_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    
    try:
        # 先删除该手机号已有的验证码
        db.session.execute(text("DELETE FROM vercode_temp WHERE telephone = :tel"), {"tel": telephone})
        
        # 插入新的验证码
        sql = """
        INSERT INTO vercode_temp (telephone, vercode, expire_time)
        VALUES (:tel, :code, :expire)
        """
        db.session.execute(text(sql), {
            "tel": telephone,
            "code": vercode,
            "expire": expire_time
        })
        db.session.commit()
        
        # 实际应用中这里应该调用短信接口发送验证码
        print(f"验证码: {vercode}，有效期5分钟")
        return jsonify({"code": 200, "msg": "验证码已发送"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 3. 用户注册
@app.route("/api/user/register", methods=["POST"])
def user_register():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    telephone = data.get("telephone", "").strip()
    vercode = data.get("vercode", "").strip()
    
    if not all([username, password, telephone, vercode]):
        return jsonify({"code": 1001, "msg": "所有字段不能为空"})
    
    try:
        # 验证验证码
        sql = """
        SELECT vercode FROM vercode_temp 
        WHERE telephone = :tel AND expire_time > NOW()
        """
        result = db.session.execute(text(sql), {"tel": telephone}).first()
        
        if not result or result[0] != vercode:
            return jsonify({"code": 1002, "msg": "验证码错误或已过期"})
        
        # 检查手机号是否已注册
        check_sql = "SELECT id FROM user WHERE telephone = :tel"
        if db.session.execute(text(check_sql), {"tel": telephone}).first():
            return jsonify({"code": 1003, "msg": "该手机号已注册"})
        
        # 注册新用户
        insert_sql = """
        INSERT INTO user (username, password, telephone, role)
        VALUES (:name, :pwd, :tel, 0)
        """
        db.session.execute(text(insert_sql), {
            "name": username,
            "pwd": password,
            "tel": telephone
        })
        db.session.commit()
        
        # 删除已使用的验证码
        db.session.execute(text("DELETE FROM vercode_temp WHERE telephone = :tel"), {"tel": telephone})
        db.session.commit()
        
        return jsonify({"code": 200, "msg": "注册成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 4. 获取所有社团列表
@app.route("/api/club/list", methods=["GET"])
def get_club_list():
    try:
        sql = """
        SELECT club_id, club_name, description, founder_id, create_time, status, category
        FROM club WHERE status = 1
        """
        result = db.session.execute(text(sql)).fetchall()
        
        clubs = []
        for item in result:
            clubs.append({
                "club_id": item[0],
                "club_name": item[1],
                "description": item[2],
                "founder_id": item[3],
                "create_time": item[4].strftime("%Y-%m-%d"),
                "status": item[5],
                "category": item[6]
            })
        
        return jsonify({"code": 200, "data": clubs})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 5. 创建社团 (需要系统管理员或符合权限的用户)
@app.route("/api/club/create", methods=["POST"])
def create_club():
    token = request.headers.get("token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"code": 401, "msg": "未授权或令牌过期"})
    
    # 只有系统管理员(role=2)可以创建社团
    if user["role"] != 2:
        return jsonify({"code": 403, "msg": "没有权限创建社团"})
    
    data = request.json
    club_name = data.get("club_name", "").strip()
    description = data.get("description", "").strip()
    category = data.get("category", "").strip()
    
    if not all([club_name, category]):
        return jsonify({"code": 1001, "msg": "社团名称和类别不能为空"})
    
    try:
        # 检查社团名称是否已存在
        check_sql = "SELECT club_id FROM club WHERE club_name = :name"
        if db.session.execute(text(check_sql), {"name": club_name}).first():
            return jsonify({"code": 1002, "msg": "该社团名称已存在"})
        
        # 创建社团
        create_sql = """
        INSERT INTO club (club_name, description, founder_id, create_time, status, category)
        VALUES (:name, :desc, :founder, CURDATE(), 1, :category)
        """
        result = db.session.execute(text(create_sql), {
            "name": club_name,
            "desc": description,
            "founder": user["id"],
            "category": category
        })
        db.session.commit()
        
        # 获取新创建的社团ID
        club_id = result.lastrowid
        
        # 创始人自动加入社团，角色为社长
        join_sql = """
        INSERT INTO club_member (user_id, club_id, role, join_time, audit_status)
        VALUES (:user_id, :club_id, 1, CURDATE(), 1)
        """
        db.session.execute(text(join_sql), {
            "user_id": user["id"],
            "club_id": club_id
        })
        db.session.commit()
        
        return jsonify({"code": 200, "msg": "社团创建成功", "club_id": club_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 6. 加入社团
@app.route("/api/club/join", methods=["POST"])
def join_club():
    token = request.headers.get("token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"code": 401, "msg": "未授权或令牌过期"})
    
    data = request.json
    club_id = data.get("club_id")
    
    if not club_id:
        return jsonify({"code": 1001, "msg": "社团ID不能为空"})
    
    try:
        # 检查是否已加入该社团
        check_sql = """
        SELECT member_id FROM club_member 
        WHERE user_id = :user_id AND club_id = :club_id
        """
        if db.session.execute(text(check_sql), {
            "user_id": user["id"],
            "club_id": club_id
        }).first():
            return jsonify({"code": 1002, "msg": "已加入该社团"})
        
        # 加入社团，状态为待审核
        join_sql = """
        INSERT INTO club_member (user_id, club_id, role, join_time, audit_status)
        VALUES (:user_id, :club_id, 0, CURDATE(), 0)
        """
        db.session.execute(text(join_sql), {
            "user_id": user["id"],
            "club_id": club_id
        })
        db.session.commit()
        
        return jsonify({"code": 200, "msg": "申请已提交，请等待审核"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 7. 创建活动
@app.route("/api/activity/create", methods=["POST"])
def create_activity():
    token = request.headers.get("token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"code": 401, "msg": "未授权或令牌过期"})
    
    data = request.json
    club_id = data.get("club_id")
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    location = data.get("location", "").strip()
    
    if not all([club_id, title, start_time, end_time, location]):
        return jsonify({"code": 1001, "msg": "必填字段不能为空"})
    
    try:
        # 检查用户是否为社团管理员或社长
        check_sql = """
        SELECT role FROM club_member 
        WHERE user_id = :user_id AND club_id = :club_id 
        AND (role = 1 OR role = 2) AND audit_status = 1
        """
        if not db.session.execute(text(check_sql), {
            "user_id": user["id"],
            "club_id": club_id
        }).first():
            return jsonify({"code": 403, "msg": "没有权限创建活动"})
        
        # 创建活动
        create_sql = """
        INSERT INTO activity (club_id, title, content, start_time, end_time, location, status)
        VALUES (:club_id, :title, :content, :start, :end, :loc, 0)
        """
        db.session.execute(text(create_sql), {
            "club_id": club_id,
            "title": title,
            "content": content,
            "start": start_time,
            "end": end_time,
            "loc": location
        })
        db.session.commit()
        
        return jsonify({"code": 200, "msg": "活动创建成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

# 8. 活动报名
@app.route("/api/activity/signup", methods=["POST"])
def activity_signup():
    token = request.headers.get("token")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"code": 401, "msg": "未授权或令牌过期"})
    
    data = request.json
    activity_id = data.get("activity_id")
    
    if not activity_id:
        return jsonify({"code": 1001, "msg": "活动ID不能为空"})
    
    try:
        # 检查是否已报名
        check_sql = """
        SELECT signup_id FROM activity_signup 
        WHERE user_id = :user_id AND activity_id = :activity_id
        """
        if db.session.execute(text(check_sql), {
            "user_id": user["id"],
            "activity_id": activity_id
        }).first():
            return jsonify({"code": 1002, "msg": "已报名该活动"})
        
        # 检查活动是否存在且未结束
        activity_sql = """
        SELECT status FROM activity 
        WHERE activity_id = :activity_id AND status != 2
        """
        activity = db.session.execute(text(activity_sql), {
            "activity_id": activity_id
        }).first()
        
        if not activity:
            return jsonify({"code": 1003, "msg": "活动不存在或已结束"})
        
        # 报名活动
        signup_sql = """
        INSERT INTO activity_signup (activity_id, user_id, is_attend)
        VALUES (:activity_id, :user_id, 0)
        """
        db.session.execute(text(signup_sql), {
            "activity_id": activity_id,
            "user_id": user["id"]
        })
        db.session.commit()
        
        return jsonify({"code": 200, "msg": "报名成功"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)